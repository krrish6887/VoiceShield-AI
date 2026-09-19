import os
import torch
import librosa

from transformers import (
    AutoFeatureExtractor,
    AutoModelForAudioClassification
)


# ======================================
# SETTINGS
# ======================================

MODEL_NAME = "garystafford/wav2vec2-deepfake-voice-detector"

AUDIO_DIR = "../audio"


# ======================================
# LOAD MODEL
# ======================================

print("\n======================================")
print("VoiceShield-AI")
print("PRETRAINED WAV2VEC2 MODEL TEST")
print("======================================")

print("\nModel:")
print(MODEL_NAME)

print("\nLoading feature extractor...")

feature_extractor = AutoFeatureExtractor.from_pretrained(
    MODEL_NAME
)

print("Feature extractor loaded.")

print("\nLoading model...")

model = AutoModelForAudioClassification.from_pretrained(
    MODEL_NAME
)

model.eval()

print("\nModel loaded successfully.")


# ======================================
# SHOW LABELS
# ======================================

print("\nModel labels:")

for key, value in model.config.id2label.items():

    print(
        key,
        "=",
        value
    )


# ======================================
# PREDICT ONE FILE
# ======================================

def predict_audio(filepath):

    print("\n--------------------------------------")
    print(
        "File:",
        os.path.basename(filepath)
    )
    print("--------------------------------------")

    # Load audio
    audio, sr = librosa.load(
        filepath,
        sr=16000,
        mono=True
    )

    print(
        "Duration:",
        f"{len(audio) / sr:.2f}s"
    )

    # Feature extraction
    inputs = feature_extractor(
        audio,
        sampling_rate=16000,
        return_tensors="pt",
        padding=True
    )

    # Model inference
    with torch.no_grad():

        outputs = model(
            **inputs
        )

        probabilities = torch.softmax(
            outputs.logits,
            dim=-1
        )[0]

    # Print scores
    print("\nScores:")

    for i, probability in enumerate(
        probabilities
    ):

        label = model.config.id2label[i]

        print(
            f"{label}: "
            f"{probability.item() * 100:.2f}%"
        )

    # Prediction
    predicted_id = torch.argmax(
        probabilities
    ).item()

    predicted_label = model.config.id2label[
        predicted_id
    ]

    confidence = probabilities[
        predicted_id
    ].item()

    print("\nPrediction:")
    print(predicted_label)

    print(
        "Confidence:",
        f"{confidence * 100:.2f}%"
    )


# ======================================
# FILES TO TEST
# ======================================

test_files = [

    "test.wav",

    "unseen_real_01.wav",
    "unseen_real_02.wav",
    "unseen_real_03.wav",

    "unseen_ai_01.wav",
    "unseen_ai_02.wav",
    "unseen_ai_03.wav"

]


# ======================================
# RUN TEST
# ======================================

print("\n======================================")
print("TESTING AUDIO FILES")
print("======================================")


for filename in test_files:

    filepath = os.path.join(
        AUDIO_DIR,
        filename
    )

    if os.path.exists(filepath):

        predict_audio(
            filepath
        )

    else:

        print(
            "\nFILE NOT FOUND:",
            filepath
        )


# ======================================
# COMPLETE
# ======================================

print("\n======================================")
print("PRETRAINED MODEL TEST COMPLETE")
print("======================================")