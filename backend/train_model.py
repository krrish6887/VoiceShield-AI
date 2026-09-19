import csv
import math
import pickle
import random


# ============================================
# FILE PATHS
# ============================================

DATASET_FILE = "../datasets/features_v2.csv"
MODEL_FILE = "../models/voice_detector_v2.pkl"


# ============================================
# LOAD DATASET
# ============================================

print("\n======================================")
print("VoiceShield-AI V2 MODEL TRAINING")
print("======================================")

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

        label = int(row[-1])

        X.append(features)
        y.append(label)


print("Total samples:", len(X))
print("Number of features:", len(X[0]))


# ============================================
# SHUFFLE DATA
# ============================================

combined = list(zip(X, y))

random.seed(42)
random.shuffle(combined)

X, y = zip(*combined)

X = [list(row) for row in X]
y = list(y)


# ============================================
# TRAIN / TEST SPLIT
# ============================================

split_index = int(len(X) * 0.80)

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
        X_train[i][j]
        for i in range(len(X_train))
    ]

    mean = sum(values) / len(values)

    variance = sum(
        (v - mean) ** 2
        for v in values
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
# SIGMOID
# ============================================

def sigmoid(z):

    # Prevent overflow
    if z < -500:
        return 0.0

    if z > 500:
        return 1.0

    return 1.0 / (1.0 + math.exp(-z))


# ============================================
# LOGISTIC REGRESSION
# ============================================

weights = [0.0] * num_features
bias = 0.0

learning_rate = 0.01
epochs = 1000


print("\nTraining logistic regression...")
print("Epochs:", epochs)
print("Learning rate:", learning_rate)


for epoch in range(epochs):

    gradients = [0.0] * num_features
    bias_gradient = 0.0

    loss = 0.0

    for i in range(len(X_train)):

        z = bias

        for j in range(num_features):

            z += (
                weights[j]
                * X_train[i][j]
            )

        prediction = sigmoid(z)

        error = prediction - y_train[i]

        for j in range(num_features):

            gradients[j] += (
                error
                * X_train[i][j]
            )

        bias_gradient += error

        # Binary cross entropy
        p = min(
            max(prediction, 1e-15),
            1 - 1e-15
        )

        loss -= (
            y_train[i] * math.log(p)
            +
            (1 - y_train[i])
            * math.log(1 - p)
        )


    # Update weights

    n = len(X_train)

    for j in range(num_features):

        weights[j] -= (
            learning_rate
            * gradients[j]
            / n
        )

    bias -= (
        learning_rate
        * bias_gradient
        / n
    )


    if (epoch + 1) % 100 == 0:

        print(
            f"Epoch {epoch + 1}/{epochs} "
            f"Loss: {loss / n:.4f}"
        )


# ============================================
# PREDICTIONS
# ============================================

def predict_probability(row):

    z = bias

    for j in range(num_features):

        z += (
            weights[j]
            * row[j]
        )

    return sigmoid(z)


probabilities = []

predictions = []


for row in X_test:

    probability = predict_probability(row)

    probabilities.append(probability)

    if probability >= 0.5:
        predictions.append(1)
    else:
        predictions.append(0)


# ============================================
# METRICS
# ============================================

TP = 0
TN = 0
FP = 0
FN = 0


for actual, predicted in zip(
    y_test,
    predictions
):

    if actual == 1 and predicted == 1:
        TP += 1

    elif actual == 0 and predicted == 0:
        TN += 1

    elif actual == 0 and predicted == 1:
        FP += 1

    elif actual == 1 and predicted == 0:
        FN += 1


total = len(y_test)

accuracy = (
    (TP + TN) / total
    if total > 0
    else 0
)


precision = (
    TP / (TP + FP)
    if (TP + FP) > 0
    else 0
)


recall = (
    TP / (TP + FN)
    if (TP + FN) > 0
    else 0
)


f1 = (
    2 * precision * recall
    / (precision + recall)
    if (precision + recall) > 0
    else 0
)


# ============================================
# RESULTS
# ============================================

print("\n======================================")
print("V2 MODEL RESULTS")
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

model = {

    "weights": weights,

    "bias": bias,

    "mean": means,

    "std": stds,

    "feature_count": num_features,

    "threshold": 0.5

}


with open(
    MODEL_FILE,
    "wb"
) as f:

    pickle.dump(
        model,
        f
    )


print("\n======================================")
print("MODEL SAVED")
print("======================================")

print(
    "Model:",
    MODEL_FILE
)

print("\nV2 training complete!")