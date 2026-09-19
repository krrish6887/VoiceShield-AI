import os
import glob
import hashlib

REAL_DIR = "../datasets/hf_real"
SYNTHETIC_DIR = "../datasets/hf_synthetic"


def file_hash(filepath):
    sha256 = hashlib.sha256()

    with open(filepath, "rb") as f:
        while True:
            data = f.read(1024 * 1024)

            if not data:
                break

            sha256.update(data)

    return sha256.hexdigest()


print("\n======================================")
print("CHECKING DATASET DUPLICATES")
print("======================================")

real_files = sorted(glob.glob(os.path.join(REAL_DIR, "*.flac")))
synthetic_files = sorted(glob.glob(os.path.join(SYNTHETIC_DIR, "*.flac")))

print("REAL files:", len(real_files))
print("SYNTHETIC files:", len(synthetic_files))

print("\nCalculating hashes...")

real_hashes = {}

for filepath in real_files:
    real_hashes[file_hash(filepath)] = os.path.basename(filepath)

duplicate_count = 0

for filepath in synthetic_files:
    h = file_hash(filepath)

    if h in real_hashes:
        duplicate_count += 1

        if duplicate_count <= 10:
            print("\nDUPLICATE FOUND:")
            print("REAL:      ", real_hashes[h])
            print("SYNTHETIC: ", os.path.basename(filepath))


print("\n======================================")
print("RESULT")
print("======================================")

print("Duplicate files:", duplicate_count)

if duplicate_count == 0:
    print("GOOD: No cross-folder duplicates found.")
else:
    print("PROBLEM: REAL and SYNTHETIC contain duplicate audio files.")

print("======================================")