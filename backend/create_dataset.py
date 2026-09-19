import os
import csv
import glob

from feature_extraction import extract_features


# ============================================
# VoiceShield-AI V2 Dataset
# ============================================

REAL_DIR = "../datasets/hf_real"
SYNTHETIC_DIR = "../datasets/hf_synthetic"

OUTPUT_FILE = "../datasets/features_v2.csv"


def process_folder(folder, label, label_name):

    print("\n======================================")
    print(f"Processing {label_name} audio")
    print("======================================")

    # Find FLAC and WAV files
    files = []

    files.extend(
        glob.glob(os.path.join(folder, "*.flac"))
    )

    files.extend(
        glob.glob(os.path.join(folder, "*.wav"))
    )

    files.sort()

    print("Folder:", folder)
    print("Found", len(files), "audio files.")

    data = []

    for i, filepath in enumerate(files):

        try:

            features = extract_features(filepath)

            # Add label
            row = list(features) + [label]

            data.append(row)

            print(
                f"[{i + 1}/{len(files)}] "
                f"Processed: {os.path.basename(filepath)}"
            )

        except Exception as e:

            print(
                f"\nERROR processing: "
                f"{os.path.basename(filepath)}"
            )

            print("Error:", e)

    print(
        f"\nCompleted {label_name}: "
        f"{len(data)} samples"
    )

    return data


# ============================================
# Process REAL
# ============================================

real_data = process_folder(
    REAL_DIR,
    0,
    "REAL"
)


# ============================================
# Process SYNTHETIC
# ============================================

synthetic_data = process_folder(
    SYNTHETIC_DIR,
    1,
    "SYNTHETIC"
)


# ============================================
# Combine datasets
# ============================================

all_data = real_data + synthetic_data


if len(all_data) == 0:

    print("\nERROR: No audio files were processed.")
    exit()


# Number of features
feature_count = len(all_data[0]) - 1


# ============================================
# Create CSV header
# ============================================

header = []

for i in range(feature_count):
    header.append(f"feature_{i + 1}")

header.append("label")


# ============================================
# Write CSV
# ============================================

print("\n======================================")
print("Creating V2 CSV dataset...")
print("======================================")


with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

    writer.writerow(header)

    writer.writerows(all_data)


# ============================================
# Final report
# ============================================

print("\n======================================")
print("V2 DATASET CREATION COMPLETE")
print("======================================")

print("Real samples:", len(real_data))
print("Synthetic samples:", len(synthetic_data))
print("Total samples:", len(all_data))

print("Feature count:", feature_count)

print("\nLabel information:")
print("0 = REAL")
print("1 = SYNTHETIC")

print("\nCSV saved at:")
print(OUTPUT_FILE)

print("\n======================================")
print("READY FOR V2 TRAINING")
print("======================================")