from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

import os
import uuid
import subprocess

import numpy as np
import torch
import librosa
import soundfile as sf


from transformers import (
    AutoFeatureExtractor,
    AutoModelForAudioClassification
)

from risk_engine import calculate_risk


# ==========================================
# VoiceShield-AI Backend
# ==========================================

app = FastAPI(
    title="VoiceShield-AI",
    description="AI-powered real-time voice impersonation detection API",
    version="1.0"
)


# ==========================================
# CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# Configuration
# ==========================================

MODEL_NAME = "garystafford/wav2vec2-deepfake-voice-detector"

CHUNK_SECONDS = 8

UPLOAD_DIR = "uploads"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


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

    # Label 1 = fake / AI-generated
    fake_score = probabilities[1].item()

    return fake_score


# ==========================================
# Analyze Complete Audio
# ==========================================

def analyze_audio(
    filepath,
    transaction_sensitivity="LOW",
    caller_verified=False,
):

    # --------------------------------------
    # Load audio
    # --------------------------------------

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
        fake_chunks / total_chunks
    ) * 100


    # --------------------------------------
    # Voice classification
    # --------------------------------------

    if mean_score >= 0.80:

        prediction = "AI-GENERATED"
        detector_risk = "HIGH"

    elif mean_score >= 0.50:

        prediction = "SUSPICIOUS"
        detector_risk = "MEDIUM"

    else:

        prediction = "REAL"
        detector_risk = "LOW"


    # --------------------------------------
    # Security Risk Engine
    # --------------------------------------

    risk_result = calculate_risk(
        ai_score=mean_score * 100,
        fake_chunk_percentage=fake_percentage,
        transaction_sensitivity=transaction_sensitivity,
        caller_verified=caller_verified,
    )


    # --------------------------------------
    # Return analysis result
    # --------------------------------------

    return {

        "prediction": prediction,

        "detector_risk_level": detector_risk,

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
            float(
                round(
                    float(score) * 100,
                    2
                )
            )
            for score in scores
        ],

        "duration_seconds": round(
            duration,
            2
        ),

        # ----------------------------------
        # Security Risk Engine
        # ----------------------------------

        "risk_score": risk_result[
            "risk_score"
        ],

        "risk_level": risk_result[
            "risk_level"
        ],

        "recommended_action": risk_result[
            "recommended_action"
        ],

        "security_actions": risk_result[
            "security_actions"
        ],
    }


# ==========================================
# API HOME
# ==========================================

@app.get("/")
def home():

    return {

        "project": "VoiceShield-AI",

        "status": "running",

        "message": "AI Voice Detection Backend is Working!"

    }


# ==========================================
# ANALYZE AUDIO API
# ==========================================

@app.post("/analyze")
async def analyze(

    file: UploadFile = File(...),
    transaction_sensitivity: str = Form("LOW"),
    transaction_type: str = Form("None"),
    transaction_amount: float = Form(0),
    caller_verified: bool = Form(False),
    caller_name: str = Form("Unknown Caller"),
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
    # Run Voice Detection + Risk Engine
    # --------------------------------------

    result = analyze_audio(

        filepath,

        transaction_sensitivity=transaction_sensitivity,

        caller_verified=caller_verified,

    )


    # --------------------------------------
    # Add filename
    # --------------------------------------

    result["filename"] = filename


    # --------------------------------------
    # Add transaction context
    # --------------------------------------

    result["transaction_context"] = {

        "caller_name": caller_name,

        "transaction_type": transaction_type,

        "transaction_amount": transaction_amount,

        "transaction_sensitivity":
            transaction_sensitivity,

        "caller_verified":
            caller_verified,

    }


    # --------------------------------------
    # Return final response
    # --------------------------------------

    return result


# ==========================================
# LIVE MICROPHONE CHUNK ANALYSIS API
# ==========================================

@app.post("/analyze-chunk")
async def analyze_chunk(
    file: UploadFile = File(...),
    transaction_sensitivity: str = Form("HIGH"),
    caller_verified: bool = Form(False),
):
    """
    Analyze one live microphone audio chunk.
    """

    # --------------------------------------
    # Create temporary input filename
    # --------------------------------------

    extension = os.path.splitext(
        file.filename or ""
    )[1]

    if not extension:
        extension = ".webm"

    temp_filename = (
        f"live_{uuid.uuid4().hex}{extension}"
    )

    temp_path = os.path.join(
        UPLOAD_DIR,
        temp_filename
    )

    # --------------------------------------
    # Create temporary converted WAV path
    # --------------------------------------

    converted_path = os.path.join(
        UPLOAD_DIR,
        f"converted_{uuid.uuid4().hex}.wav"
    )

    try:

        # ----------------------------------
        # Receive uploaded audio
        # ----------------------------------

        contents = await file.read()

        if not contents:

            return {
                "error": "Empty audio chunk received."
            }


        # ----------------------------------
        # Save uploaded audio temporarily
        # ----------------------------------

        with open(
            temp_path,
            "wb"
        ) as f:

            f.write(contents)


        # ----------------------------------
        # Convert to 16 kHz mono WAV
        # ----------------------------------

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                temp_path,
                "-ac",
                "1",
                "-ar",
                "16000",
                "-sample_fmt",
                "s16",
                converted_path,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            check=True,
        )


        # ----------------------------------
        # Load converted WAV
        # ----------------------------------

        audio, sr = sf.read(
            converted_path,
            dtype="float32"
        )


        # ----------------------------------
        # Convert stereo to mono
        # ----------------------------------

        if audio.ndim > 1:

            audio = np.mean(
                audio,
                axis=1
            )


        # ----------------------------------
        # Calculate duration
        # ----------------------------------

        duration = len(audio) / sr


        if duration < 1.0:

            return {
                "error": "Audio chunk is too short."
            }


        # ----------------------------------
        # Voice authenticity detection
        # ----------------------------------

        fake_score = predict_chunk(
            audio
        )

        ai_score = fake_score * 100


        # ----------------------------------
        # Chunk classification
        # ----------------------------------

        if fake_score >= 0.80:

            chunk_status = "AI"

        elif fake_score >= 0.50:

            chunk_status = "SUSPICIOUS"

        else:

            chunk_status = "REAL"


        # ----------------------------------
        # Calculate security risk
        # ----------------------------------

        fake_percentage = (
            100.0
            if fake_score >= 0.50
            else 0.0
        )


        risk_result = calculate_risk(
            ai_score=ai_score,
            fake_chunk_percentage=fake_percentage,
            transaction_sensitivity=transaction_sensitivity,
            caller_verified=caller_verified,
        )


        # ----------------------------------
        # Return live analysis result
        # ----------------------------------

        return {

            "chunk_score": round(
                ai_score,
                2
            ),

            "chunk_status": chunk_status,

            "duration_seconds": round(
                duration,
                2
            ),

            "risk_score": risk_result[
                "risk_score"
            ],

            "risk_level": risk_result[
                "risk_level"
            ],

            "action": risk_result[
                "recommended_action"
            ],

            "security_actions": risk_result[
                "security_actions"
            ],
        }


    except subprocess.CalledProcessError as e:

        error_message = e.stderr.decode(
            errors="ignore"
        )

        print(
            "FFmpeg conversion error:",
            error_message
        )

        return {
            "error":
                "Audio conversion failed."
        }


    except Exception as e:

        print(
            "Live chunk analysis error:",
            str(e)
        )

        return {
            "error":
                f"Unable to analyze live audio: {str(e)}"
        }


    finally:

        # ----------------------------------
        # Delete original temporary audio
        # ----------------------------------

        if os.path.exists(temp_path):

            try:

                os.remove(temp_path)

            except Exception as cleanup_error:

                print(
                    "Temporary input cleanup error:",
                    cleanup_error
                )


        # ----------------------------------
        # Delete converted WAV
        # ----------------------------------

        if os.path.exists(converted_path):

            try:

                os.remove(converted_path)

            except Exception as cleanup_error:

                print(
                    "Converted audio cleanup error:",
                    cleanup_error
                )