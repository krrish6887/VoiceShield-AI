import numpy as np
import librosa


def extract_features(audio_path):

    # --------------------------------
    # 1. Load audio
    # --------------------------------

    audio, sr = librosa.load(
        audio_path,
        sr=16000
    )

    # --------------------------------
    # 2. MFCC
    # --------------------------------

    mfcc = librosa.feature.mfcc(
        y=audio,
        sr=sr,
        n_mfcc=40
    )

    mfcc_mean = np.mean(mfcc, axis=1)
    mfcc_std = np.std(mfcc, axis=1)

    # --------------------------------
    # 3. Spectral Centroid
    # --------------------------------

    spectral_centroid = librosa.feature.spectral_centroid(
        y=audio,
        sr=sr
    )

    centroid_mean = np.mean(spectral_centroid)
    centroid_std = np.std(spectral_centroid)

    # --------------------------------
    # 4. Spectral Rolloff
    # --------------------------------

    spectral_rolloff = librosa.feature.spectral_rolloff(
        y=audio,
        sr=sr
    )

    rolloff_mean = np.mean(spectral_rolloff)
    rolloff_std = np.std(spectral_rolloff)

    # --------------------------------
    # 5. Zero Crossing Rate
    # --------------------------------

    zero_crossing = librosa.feature.zero_crossing_rate(
        audio
    )

    zcr_mean = np.mean(zero_crossing)
    zcr_std = np.std(zero_crossing)

    # --------------------------------
    # 6. RMS Energy
    # --------------------------------

    rms = librosa.feature.rms(
        y=audio
    )

    rms_mean = np.mean(rms)
    rms_std = np.std(rms)

    # --------------------------------
    # 7. Combine features
    # --------------------------------

    features = np.concatenate([
        mfcc_mean,
        mfcc_std,
        [
            centroid_mean,
            centroid_std,
            rolloff_mean,
            rolloff_std,
            zcr_mean,
            zcr_std,
            rms_mean,
            rms_std
        ]
    ])

    return features


# --------------------------------
# Test the feature extractor
# --------------------------------

if __name__ == "__main__":

    audio_file = "audio/test.wav"

    features = extract_features(audio_file)

    print("\nFeature extraction successful!")

    print("Number of features:", len(features))

    print("\nFeature vector:")
    print(features)