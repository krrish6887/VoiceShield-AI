import sys
import os
import pickle
import numpy as np

from feature_extraction import extract_features


# ==========================================
# Configuration
# ==========================================

MODEL_FILE = "../models/voice_detector.pkl"


# ==========================================
# Check audio argument
# ==========================================

if len(sys.argv) < 2:

    print("\nUsage:")
    print("python predict.py ../audio/test.wav")

    sys.exit()


audio_file = sys.argv[1]


# ==========================================
# Check files
# ==========================================

if not os.path.exists(audio_file):

    print("\nERROR: Audio file not found!")
    print("File:", audio_file)

    sys.exit()


if not os.path.exists(MODEL_FILE):

    print("\nERROR: Model not found!")
    print("Train the model first.")

    sys.exit()


# ==========================================
# Load model
# ==========================================

print("\nLoading VoiceShield model...")

with open(
    MODEL_FILE,
    "rb"
) as file:

    model = pickle.load(file)


weights = model["weights"]
bias = model["bias"]

mean = model["mean"]
std = model["std"]


# ==========================================
# Extract features
# ==========================================

print("Analyzing audio...")

features = extract_features(
    audio_file
)


# ==========================================
# Prepare features
# ==========================================

features = np.array(
    features,
    dtype=np.float64
)


features = (
    features - mean
) / std


features = features.reshape(
    1,
    -1
)


# ==========================================
# Calculate synthetic score
# ==========================================

z = np.dot(
    features,
    weights
) + bias


z = np.clip(
    z,
    -500,
    500
)


synthetic_score = (
    1 /
    (
        1 +
        np.exp(-z)
    )
)


synthetic_score = float(
    synthetic_score[0]
)


# ==========================================
# Prediction
# ==========================================

if synthetic_score >= 0.5:

    prediction = "SYNTHETIC"

else:

    prediction = "REAL"


# ==========================================
# Risk Level
# ==========================================

if synthetic_score >= 0.80:

    risk = "HIGH"

elif synthetic_score >= 0.50:

    risk = "MEDIUM"

elif synthetic_score >= 0.20:

    risk = "LOW"

else:

    risk = "VERY LOW"


# ==========================================
# Display result
# ==========================================

print("\n")
print("======================================")
print("          VOICESHIELD AI")
print("======================================")

print("\nAudio analyzed:")
print(audio_file)

print("\n--------------------------------------")

print("Prediction:")
print(prediction)

print(
    f"\nSynthetic score: "
    f"{synthetic_score * 100:.2f}%"
)

print(
    f"Risk level: {risk}"
)

print("--------------------------------------")

print("\nInterpretation:")

if prediction == "SYNTHETIC":

    print(
        "The current model detected "
        "features associated with synthetic speech."
    )

    print(
        "Consider secondary verification "
        "before sensitive actions."
    )

else:

    print(
        "The current model detected "
        "features more consistent with real speech."
    )

    print(
        "This does NOT guarantee that the caller "
        "is genuine."
    )

print("\n======================================")