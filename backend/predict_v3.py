import os
import glob
import torch
import numpy as np

from feature_extraction import extract_features


# ======================================
# MODEL DEFINITION
# ======================================

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
# PATHS
# ======================================

MODEL_PATH = "../models/voice_detector_v3.pth"
AUDIO_DIR = "../audio"


# ======================================
# LOAD MODEL
# ======================================

print("\n======================================")
print("VoiceShield-AI V3 INFERENCE")
print("======================================")

print("\nLoading model...")

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

threshold = float(
    checkpoint["threshold"]
)

print("Feature count:", feature_count)
print("Decision threshold:", threshold)


model = VoiceDetector(feature_count)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model.eval()

print("Model loaded successfully.")


# ======================================
# RISK LEVEL
# ======================================

def get_risk_level(score):

    if score >= 0.80:
        return "HIGH"

    elif score >= 0.50:
        return "MEDIUM"

    elif score >= 0.20:
        return "LOW"

    else:
        return "VERY LOW"


# ======================================
# PREDICT ONE AUDIO FILE
# ======================================

def predict_audio(filepath):

    print("\n--------------------------------------")
    print("File:", os.path.basename(filepath))
    print("--------------------------------------")

    try:

        # Extract the SAME 88 features used during training
        features = extract_features(filepath)

        features = np.asarray(
            features,
            dtype=np.float32
        )

        # Check feature count
        if len(features) != feature_count:

            print(
                "ERROR: Feature count mismatch!"
            )

            print(
                "Expected:",
                feature_count
            )

            print(
                "Got:",
                len(features)
            )

            return

        # Standardize using training statistics
        features = (
            features - means
        ) / (stds + 1e-8)

        # Convert to PyTorch tensor
        x = torch.tensor(
            features,
            dtype=torch.float32
        ).unsqueeze(0)

        # Inference
        with torch.no_grad():

            logit = model(x)

            score = torch.sigmoid(
                logit
            ).item()

        # Prediction
        if score >= threshold:

            prediction = "SYNTHETIC / AI"

        else:

            prediction = "REAL"

        risk = get_risk_level(score)

        print(
            f"AI Score: {score * 100:.2f}%"
        )

        print(
            "Prediction:",
            prediction
        )

        print(
            "Risk Level:",
            risk
        )

    except Exception as e:

        print(
            "ERROR:",
            e
        )


# ======================================
# FIND AUDIO FILES
# ======================================

audio_extensions = [
    "*.wav",
    "*.flac",
    "*.mp3",
    "*.m4a"
]

audio_files = []

for extension in audio_extensions:

    audio_files.extend(
        glob.glob(
            os.path.join(
                AUDIO_DIR,
                extension
            )
        )
    )

audio_files = sorted(
    audio_files
)


# ======================================
# RUN PREDICTIONS
# ======================================

print("\nAudio files found:", len(audio_files))

if len(audio_files) == 0:

    print(
        "\nNo audio files found in:"
    )

    print(AUDIO_DIR)

else:

    for filepath in audio_files:

        predict_audio(filepath)


# ======================================
# COMPLETE
# ======================================

print("\n======================================")
print("V3 INFERENCE COMPLETE")
print("======================================")