import csv
import random
import math
import os

import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader


# ============================================
# SETTINGS
# ============================================

DATASET_FILE = "../datasets/features_v2.csv"
MODEL_FILE = "../models/voice_detector_v3.pth"

RANDOM_SEED = 42

TRAIN_RATIO = 0.80

EPOCHS = 100
BATCH_SIZE = 32

LEARNING_RATE = 0.001


# ============================================
# REPRODUCIBILITY
# ============================================

random.seed(RANDOM_SEED)
torch.manual_seed(RANDOM_SEED)


# ============================================
# DEVICE
# ============================================

device = torch.device("cpu")

print("\n======================================")
print("VoiceShield-AI V3 TRAINING")
print("======================================")

print("\nDevice:", device)


# ============================================
# LOAD CSV
# ============================================

print("\nLoading dataset...")

X = []
y = []

with open(
    DATASET_FILE,
    "r",
    encoding="utf-8"
) as f:

    reader = csv.reader(f)

    header = next(reader)

    for row in reader:

        if not row:
            continue

        features = [
            float(value)
            for value in row[:-1]
        ]

        label = int(float(row[-1]))

        X.append(features)
        y.append(label)


print("Total samples:", len(X))
print("Number of features:", len(X[0]))


# ============================================
# SHUFFLE
# ============================================

combined = list(zip(X, y))

random.shuffle(combined)

X, y = zip(*combined)

X = list(X)
y = list(y)


# ============================================
# TRAIN / TEST SPLIT
# ============================================

split_index = int(
    len(X) * TRAIN_RATIO
)

X_train = X[:split_index]
y_train = y[:split_index]

X_test = X[split_index:]
y_test = y[split_index:]


print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# ============================================
# STANDARDIZATION
# ============================================

print("\nStandardizing features...")


num_features = len(X_train[0])

means = []
stds = []


for j in range(num_features):

    values = [
        row[j]
        for row in X_train
    ]

    mean = sum(values) / len(values)

    variance = sum(
        (value - mean) ** 2
        for value in values
    ) / len(values)

    std = math.sqrt(variance)

    if std < 1e-8:
        std = 1.0

    means.append(mean)
    stds.append(std)


def standardize(data):

    result = []

    for row in data:

        new_row = []

        for j in range(num_features):

            value = (
                row[j] - means[j]
            ) / stds[j]

            new_row.append(value)

        result.append(new_row)

    return result


X_train = standardize(X_train)
X_test = standardize(X_test)


# ============================================
# CONVERT TO PYTORCH TENSORS
# ============================================

X_train_tensor = torch.tensor(
    X_train,
    dtype=torch.float32
)

y_train_tensor = torch.tensor(
    y_train,
    dtype=torch.float32
).view(-1, 1)


X_test_tensor = torch.tensor(
    X_test,
    dtype=torch.float32
)

y_test_tensor = torch.tensor(
    y_test,
    dtype=torch.float32
).view(-1, 1)


# ============================================
# DATA LOADER
# ============================================

train_dataset = TensorDataset(
    X_train_tensor,
    y_train_tensor
)

train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True
)


# ============================================
# NEURAL NETWORK
# ============================================

class VoiceDetector(nn.Module):

    def __init__(self, input_size):

        super().__init__()

        self.network = nn.Sequential(

            nn.Linear(input_size, 128),

            nn.ReLU(),

            nn.Dropout(0.25),

            nn.Linear(128, 64),

            nn.ReLU(),

            nn.Dropout(0.20),

            nn.Linear(64, 32),

            nn.ReLU(),

            nn.Linear(32, 1)
        )


    def forward(self, x):

        return self.network(x)


# Create model
model = VoiceDetector(
    num_features
).to(device)


# ============================================
# LOSS + OPTIMIZER
# ============================================

criterion = nn.BCEWithLogitsLoss()

optimizer = torch.optim.Adam(
    model.parameters(),
    lr=LEARNING_RATE
)


# ============================================
# TRAINING
# ============================================

print("\n======================================")
print("Training neural network...")
print("======================================")

print("Epochs:", EPOCHS)
print("Batch size:", BATCH_SIZE)
print("Learning rate:", LEARNING_RATE)


for epoch in range(EPOCHS):

    model.train()

    total_loss = 0.0

    for batch_X, batch_y in train_loader:

        batch_X = batch_X.to(device)
        batch_y = batch_y.to(device)

        # Clear gradients
        optimizer.zero_grad()

        # Forward pass
        outputs = model(batch_X)

        # Calculate loss
        loss = criterion(
            outputs,
            batch_y
        )

        # Backpropagation
        loss.backward()

        # Update weights
        optimizer.step()

        total_loss += loss.item()


    average_loss = (
        total_loss /
        len(train_loader)
    )


    if (
        (epoch + 1) % 10 == 0
        or epoch == 0
    ):

        print(
            f"Epoch {epoch + 1:3d}/{EPOCHS} "
            f"Loss: {average_loss:.4f}"
        )


# ============================================
# EVALUATION
# ============================================

print("\n======================================")
print("Evaluating V3 model...")
print("======================================")


model.eval()


with torch.no_grad():

    logits = model(
        X_test_tensor.to(device)
    )

    probabilities = torch.sigmoid(
        logits
    )

    predictions = (
        probabilities >= 0.5
    ).int()


# ============================================
# METRICS
# ============================================

predictions_list = (
    predictions
    .cpu()
    .numpy()
    .flatten()
    .tolist()
)

actual_list = (
    y_test_tensor
    .numpy()
    .flatten()
    .tolist()
)

TP = 0
TN = 0
FP = 0
FN = 0


for actual, predicted in zip(
    actual_list,
    predictions_list
):

    actual = int(actual)
    predicted = int(predicted)

    if actual == 1 and predicted == 1:
        TP += 1

    elif actual == 0 and predicted == 0:
        TN += 1

    elif actual == 0 and predicted == 1:
        FP += 1

    elif actual == 1 and predicted == 0:
        FN += 1


total = len(actual_list)


accuracy = (
    (TP + TN) / total
    if total > 0
    else 0
)


precision = (
    TP / (TP + FP)
    if TP + FP > 0
    else 0
)


recall = (
    TP / (TP + FN)
    if TP + FN > 0
    else 0
)


f1 = (
    2 * precision * recall
    / (precision + recall)
    if precision + recall > 0
    else 0
)


# ============================================
# RESULTS
# ============================================

print("\n======================================")
print("V3 MODEL RESULTS")
print("======================================")

print(
    f"Accuracy:  {accuracy * 100:.2f}%"
)

print(
    f"Precision: {precision * 100:.2f}%"
)

print(
    f"Recall:    {recall * 100:.2f}%"
)

print(
    f"F1 Score:  {f1 * 100:.2f}%"
)


print("\nConfusion Matrix")

print(
    "                 Predicted"
)

print(
    "              REAL    AI"
)

print(
    f"Actual REAL    {TN:4d}   {FP:4d}"
)

print(
    f"Actual AI      {FN:4d}   {TP:4d}"
)


# ============================================
# SAVE MODEL
# ============================================

os.makedirs(
    "../models",
    exist_ok=True
)


checkpoint = {

    "model_state_dict":
        model.state_dict(),

    "feature_count":
        num_features,

    "means":
        means,

    "stds":
        stds,

    "threshold":
        0.5,

    "accuracy":
        accuracy,

    "precision":
        precision,

    "recall":
        recall,

    "f1":
        f1
}


torch.save(
    checkpoint,
    MODEL_FILE
)


print("\n======================================")
print("V3 MODEL SAVED")
print("======================================")

print(
    "Model:",
    MODEL_FILE
)

print("\nV3 training complete!")