import os
import glob
import torch
import numpy as np

from feature_extraction import extract_features


MODEL_PATH = "../models/voice_detector_v3.pth"
AUDIO_DIR = "../audio"


class VoiceDetector(torch.nn.Module):

    def __init__(self, input_size):
        super().__init__()

        self.network = torch.nn.Sequential(
            torch.nn.Linear(input_size, 128),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.25),

            torch.nn.Linear(128, 64),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.20),

            torch.nn.Linear(64, 32),
            torch.nn.ReLU(),

            torch.nn.Linear(32, 1)
        )

    def forward(self, x):
        return self.network(x)


# ======================================
# LOAD MODEL
# ======================================

checkpoint = torch.load(
    MODEL_PATH,
    map_location="cpu"
)

feature_count = checkpoint["feature_count"]

means = np.array(
    checkpoint["means"],
    dtype=np.float32
)

stds = np.array(
    checkpoint["stds"],
    dtype=np.float32
)

model = VoiceDetector(feature_count)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model.eval()


# ======================================
# TEST
# ======================================

files = sorted(
    glob.glob(
        os.path.join(
            AUDIO_DIR,
            "*.wav"
        )
    )
)

print("\n======================================")
print("V3 RAW SCORE DIAGNOSTIC")
print("======================================")

for filepath in files:

    features = np.asarray(
        extract_features(filepath),
        dtype=np.float32
    )

    features = (
        features - means
    ) / (stds + 1e-8)

    x = torch.tensor(
        features,
        dtype=torch.float32
    ).unsqueeze(0)

    with torch.no_grad():

        logit = model(x).item()

        score = torch.sigmoid(
            torch.tensor(logit)
        ).item()

    print("\nFile:", os.path.basename(filepath))

    print(
        "Raw model logit:",
        f"{logit:.6f}"
    )

    print(
        "AI score:",
        f"{score:.10f}"
    )

print("\n======================================")
print("DIAGNOSTIC COMPLETE")
print("======================================")