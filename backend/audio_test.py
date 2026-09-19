import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt

# -----------------------------------
# 1. Load audio
# -----------------------------------

audio_path = "audio/test.wav"

audio, sample_rate = librosa.load(
    audio_path,
    sr=16000
)

print("Audio loaded successfully!")
print("Sample rate:", sample_rate)
print("Number of samples:", len(audio))
print("Duration:", len(audio) / sample_rate, "seconds")


# -----------------------------------
# 2. Display waveform
# -----------------------------------

plt.figure(figsize=(12, 4))

librosa.display.waveshow(
    audio,
    sr=sample_rate
)

plt.title("Voice Waveform")
plt.xlabel("Time (seconds)")
plt.ylabel("Amplitude")

plt.show()


# -----------------------------------
# 3. Generate Mel Spectrogram
# -----------------------------------

mel_spectrogram = librosa.feature.melspectrogram(
    y=audio,
    sr=sample_rate,
    n_mels=128
)

mel_db = librosa.power_to_db(
    mel_spectrogram,
    ref=np.max
)

plt.figure(figsize=(12, 5))

librosa.display.specshow(
    mel_db,
    sr=sample_rate,
    x_axis="time",
    y_axis="mel"
)

plt.colorbar(format="%+2.0f dB")
plt.title("Mel Spectrogram")

plt.show()


# -----------------------------------
# 4. Extract MFCC
# -----------------------------------

mfcc = librosa.feature.mfcc(
    y=audio,
    sr=sample_rate,
    n_mfcc=40
)

print("MFCC shape:", mfcc.shape)

print("\nMFCC mean:")
print(mfcc.mean(axis=1))

print("\nMFCC standard deviation:")
print(mfcc.std(axis=1))