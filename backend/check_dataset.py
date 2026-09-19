import os
import glob
import numpy as np
import librosa


REAL_DIR = "../datasets/hf_real"
FAKE_DIR = "../datasets/hf_synthetic"


def inspect_folder(folder, name, count=5):

    files = sorted(
        glob.glob(os.path.join(folder, "*.flac"))
    )

    print("\n======================================")
    print(name)
    print("======================================")

    print("Files found:", len(files))

    print("\nFirst few files:")

    for filepath in files[:count]:

        try:

            audio, sr = librosa.load(
                filepath,
                sr=16000,
                mono=True
            )

            duration = len(audio) / sr

            rms = np.sqrt(
                np.mean(audio ** 2)
            )

            print(
                os.path.basename(filepath),
                "|",
                f"duration={duration:.2f}s",
                "|",
                f"RMS={rms:.6f}"
            )

        except Exception as e:

            print(
                "ERROR:",
                os.path.basename(filepath),
                e
            )


inspect_folder(
    REAL_DIR,
    "HF REAL"
)

inspect_folder(
    FAKE_DIR,
    "HF SYNTHETIC"
)


print("\n======================================")
print("DATASET FOLDER CHECK COMPLETE")
print("======================================")