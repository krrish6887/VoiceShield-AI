import os
import numpy as np
import torch
import librosa

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from transformers import (
    AutoFeatureExtractor,
    AutoModelForAudioClassification
)

# ==========================================
# VoiceShield-AI Backend
# ==========================================

app = FastAPI(
    title="VoiceShield-AI",
    description="AI-generated voice detection API",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_NAME = "garystafford/wav2vec2-deepfake-voice-detector"

CHUNK_SECONDS = 8


# ==========================================
# Load AI Voice Detection Model
# ==========================================

print("Loading VoiceShield-AI model...")

feature_extractor = AutoFeatureExtractor.from_pretrained(
    MODEL_NAME
)

model = AutoModelForAudioClassification.from_pretrained(
    MODEL_NAME
)

model.eval()

print("Model loaded successfully!")


# ==========================================
# Temporary upload directory
# ==========================================

UPLOAD_DIR = "uploads"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


# ==========================================
# Predict One Audio Chunk
# ==========================================

def predict_chunk(audio_chunk):

    inputs = feature_extractor(
        audio_chunk,
        sampling_rate=16000,
        return_tensors="pt",
        padding=True
    )

    with torch.no_grad():

        outputs = model(
            **inputs
        )

        probabilities = torch.softmax(
            outputs.logits,
            dim=-1
        )[0]

    fake_score = probabilities[1].item()

    return fake_score


# ==========================================
# Analyze Complete Audio
# ==========================================

def analyze_audio(filepath):

    audio, sr = librosa.load(
        filepath,
        sr=16000,
        mono=True
    )

    duration = len(audio) / sr

    chunk_length = CHUNK_SECONDS * sr

    scores = []

    # --------------------------------------
    # Create 8-second chunks
    # --------------------------------------

    for start in range(
        0,
        len(audio),
        chunk_length
    ):

        end = min(
            start + chunk_length,
            len(audio)
        )

        chunk = audio[start:end]

        # Ignore extremely short final chunk
        if len(chunk) < sr * 2:
            continue

        score = predict_chunk(
            chunk
        )

        scores.append(score)

    # --------------------------------------
    # Safety check
    # --------------------------------------

    if not scores:

        return {
            "error": "Audio is too short for analysis."
        }

    scores = np.array(
        scores,
        dtype=np.float32
    )

    # --------------------------------------
    # Aggregate results
    # --------------------------------------

    mean_score = float(
        np.mean(scores)
    )

    median_score = float(
        np.median(scores)
    )

    fake_chunks = int(
        np.sum(scores >= 0.50)
    )

    total_chunks = len(scores)

    fake_percentage = (
        fake_chunks /
        total_chunks
    ) * 100

    # --------------------------------------
    # Classification
    # --------------------------------------

    if mean_score >= 0.80:

        prediction = "AI-GENERATED"
        risk = "HIGH"

    elif mean_score >= 0.50:

        prediction = "SUSPICIOUS"
        risk = "MEDIUM"

    else:

        prediction = "REAL"
        risk = "LOW"

    # --------------------------------------
    # Return result
    # --------------------------------------

    return {

        "prediction": prediction,

        "risk_level": risk,

        "ai_score": round(
            mean_score * 100,
            2
        ),

        "median_ai_score": round(
            median_score * 100,
            2
        ),

        "fake_chunks": fake_chunks,

        "total_chunks": total_chunks,

        "fake_chunk_percentage": round(
            fake_percentage,
            2
        ),

       "chunk_scores": [
    float(round(float(score) * 100, 2))
    for score in scores
],

        "duration_seconds": round(
            duration,
            2
        )

    }


# ==========================================
# API HOME
# ==========================================

@app.get("/")
def home():

    return {

        "project": "VoiceShield-AI",

        "status": "running",

        "message":
        "AI Voice Detection Backend is Working!"

    }


# ==========================================
# ANALYZE AUDIO API
# ==========================================

@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...)
):

    # --------------------------------------
    # Create safe filename
    # --------------------------------------

    filename = os.path.basename(
        file.filename
    )

    filepath = os.path.join(
        UPLOAD_DIR,
        filename
    )

    # --------------------------------------
    # Save uploaded file
    # --------------------------------------

    contents = await file.read()

    with open(
        filepath,
        "wb"
    ) as f:

        f.write(contents)

    print(
        "\nAnalyzing:",
        filename
    )

    # --------------------------------------
    # Run detector
    # --------------------------------------

    result = analyze_audio(
        filepath
    )

    # --------------------------------------
    # Add filename
    # --------------------------------------

    result["filename"] = filename

    return result