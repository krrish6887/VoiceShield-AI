import os
import glob
import numpy as np
import torch

from feature_extraction import extract_features


MODEL_PATH = "../models/voice_detector_v3.pth"
AUDIO_DIR = "../audio"


# ======================================
# LOAD CHECKPOINT
# ======================================

checkpoint = torch.load(
    MODEL_PATH,
    map_location="cpu"
)

means = np.array(
    checkpoint["means"],
    dtype=np.float32
)

stds = np.array(
    checkpoint["stds"],
    dtype=np.float32
)

feature_count = checkpoint["feature_count"]

print("\n======================================")
print("V3 FEATURE PIPELINE DIAGNOSTIC")
print("======================================")

print("Expected features:", feature_count)

print(
    "Training mean range:",
    float(means.min()),
    "to",
    float(means.max())
)

print(
    "Training std range:",
    float(stds.min()),
    "to",
    float(stds.max())
)


# ======================================
# CHECK AUDIO FILES
# ======================================

audio_files = sorted(
    glob.glob(
        os.path.join(
            AUDIO_DIR,
            "*.wav"
        )
    )
)

print("\nAudio files:", len(audio_files))


for filepath in audio_files:

    print("\n--------------------------------------")
    print(
        os.path.basename(filepath)
    )
    print("--------------------------------------")

    try:

        features = extract_features(filepath)

        features = np.asarray(
            features,
            dtype=np.float32
        )

        print(
            "Feature count:",
            len(features)
        )

        print(
            "Raw feature min:",
            float(features.min())
        )

        print(
            "Raw feature max:",
            float(features.max())
        )

        print(
            "Raw feature mean:",
            float(features.mean())
        )

        print(
            "Raw feature std:",
            float(features.std())
        )

        # Standardize
        normalized = (
            features - means
        ) / (stds + 1e-8)

        print(
            "Normalized min:",
            float(normalized.min())
        )

        print(
            "Normalized max:",
            float(normalized.max())
        )

        print(
            "Normalized mean:",
            float(normalized.mean())
        )

        print(
            "Normalized std:",
            float(normalized.std())
        )

        # Check for problematic values

        print(
            "NaN values:",
            int(np.isnan(normalized).sum())
        )

        print(
            "Inf values:",
            int(np.isinf(normalized).sum())
        )

        # Show first 10 features

        print(
            "First 10 normalized features:"
        )

        print(
            normalized[:10]
        )

    except Exception as e:

        print(
            "ERROR:",
            e
        )


print("\n======================================")
print("DIAGNOSTIC COMPLETE")
print("======================================")