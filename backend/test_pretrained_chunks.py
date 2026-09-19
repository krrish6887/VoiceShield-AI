import os
import numpy as np
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

CHUNK_SECONDS = 8

NUMBER_OF_CHUNKS = 10


# ======================================
# LOAD MODEL
# ======================================

print("\n======================================")
print("VoiceShield-AI")
print("CHUNK-BASED PRETRAINED DETECTOR")
print("======================================")

print("\nLoading model...")

feature_extractor = AutoFeatureExtractor.from_pretrained(
    MODEL_NAME
)

model = AutoModelForAudioClassification.from_pretrained(
    MODEL_NAME
)

model.eval()

print("Model loaded.")

print("\nLabels:")

for key, value in model.config.id2label.items():
    print(key, "=", value)


# ======================================
# PREDICT CHUNK
# ======================================

def predict_chunk(audio_chunk):

    inputs = feature_extractor(
        audio_chunk,
        sampling_rate=16000,
        return_tensors="pt",
        padding=True
    )

    with torch.no_grad():

        outputs = model(**inputs)

        probabilities = torch.softmax(
            outputs.logits,
            dim=-1
        )[0]

    # Class 1 = fake
    fake_score = probabilities[1].item()

    return fake_score


# ======================================
# ANALYZE ONE FILE
# ======================================

def analyze_file(filepath):

    print("\n======================================")
    print(
        "FILE:",
        os.path.basename(filepath)
    )
    print("======================================")

    audio, sr = librosa.load(
        filepath,
        sr=16000,
        mono=True
    )

    duration = len(audio) / sr

    print(
        "Duration:",
        f"{duration:.2f} seconds"
    )

    chunk_length = CHUNK_SECONDS * sr

    # ----------------------------------
    # Generate evenly distributed starts
    # ----------------------------------

    max_start = max(
        0,
        len(audio) - chunk_length
    )

    if max_start == 0:

        starts = [0]

    else:

        starts = np.linspace(
            0,
            max_start,
            min(
                NUMBER_OF_CHUNKS,
                max(
                    1,
                    int(
                        len(audio) / chunk_length
                    )
                )
            ),
            dtype=int
        )

    scores = []

    print(
        "\nTesting",
        len(starts),
        "chunks..."
    )

    # ----------------------------------
    # Process chunks
    # ----------------------------------

    for i, start in enumerate(starts):

        end = start + chunk_length

        chunk = audio[start:end]

        fake_score = predict_chunk(
            chunk
        )

        scores.append(
            fake_score
        )

        print(
            f"Chunk {i + 1:02d}"
            f" | {start / sr:7.1f}s"
            f" - {end / sr:7.1f}s"
            f" | Fake: {fake_score * 100:6.2f}%"
        )

    # ----------------------------------
    # Aggregate
    # ----------------------------------

    scores = np.array(
        scores,
        dtype=np.float32
    )

    mean_score = float(
        np.mean(scores)
    )

    median_score = float(
        np.median(scores)
    )

    fake_chunks = int(
        np.sum(scores >= 0.50)
    )

    fake_percentage = (
        fake_chunks / len(scores)
    ) * 100

    print("\n--------------------------------------")
    print("AGGREGATED RESULT")
    print("--------------------------------------")

    print(
        "Mean fake score:",
        f"{mean_score * 100:.2f}%"
    )

    print(
        "Median fake score:",
        f"{median_score * 100:.2f}%"
    )

    print(
        "Fake chunks:",
        f"{fake_chunks}/{len(scores)}"
    )

    print(
        "Fake chunk percentage:",
        f"{fake_percentage:.1f}%"
    )

    if mean_score >= 0.50:

        print(
            "\nOverall:",
            "LIKELY SYNTHETIC"
        )

    else:

        print(
            "\nOverall:",
            "LIKELY REAL"
        )


# ======================================
# TEST ONLY AI_01 FIRST
# ======================================

test_files = [
    "unseen_real_01.wav",
    "unseen_real_02.wav",
    "unseen_real_03.wav",
    "unseen_ai_01.wav",
    "unseen_ai_02.wav",
    "unseen_ai_03.wav"
]

for filename in test_files:
    filepath = os.path.join(AUDIO_DIR, filename)

    if os.path.exists(filepath):
        analyze_file(filepath)
    else:
        print("File not found:", filepath)
        
print("\n======================================")
print("CHUNK TEST COMPLETE")
print("======================================")