import os
import requests
import time

REPO = "garystafford/deepfake-audio-detection"

REAL_DIR = "../datasets/hf_real"
SYNTHETIC_DIR = "../datasets/hf_synthetic"

MAX_FILES = 500

os.makedirs(REAL_DIR, exist_ok=True)
os.makedirs(SYNTHETIC_DIR, exist_ok=True)


# ======================================
# GET FILE LIST
# ======================================

def get_files(folder):

    url = (
        f"https://huggingface.co/api/datasets/"
        f"{REPO}/tree/main/{folder}"
    )

    params = {
        "recursive": "true",
        "expand": "false"
    }

    response = requests.get(
        url,
        params=params,
        timeout=60
    )

    response.raise_for_status()

    data = response.json()

    files = []

    for item in data:

        if item.get("type") == "file":

            path = item.get("path", "")

            if path.lower().endswith(".flac"):
                files.append(path)

    return files


# ======================================
# DOWNLOAD ONE FILE
# ======================================

def download_file(repo_path, output_path):

    url = (
        "https://huggingface.co/datasets/"
        + REPO
        + "/resolve/main/"
        + repo_path
        + "?download=true"
    )

    temp_path = output_path + ".part"

    for attempt in range(5):

        try:

            response = requests.get(
                url,
                stream=True,
                timeout=120
            )

            response.raise_for_status()

            with open(temp_path, "wb") as f:

                for chunk in response.iter_content(
                    chunk_size=1024 * 1024
                ):

                    if chunk:
                        f.write(chunk)

            os.replace(temp_path, output_path)

            return True

        except Exception as e:

            print(
                f"\nDownload failed "
                f"(attempt {attempt + 1}/5): {e}"
            )

            if os.path.exists(temp_path):
                os.remove(temp_path)

            time.sleep(2)

    return False


# ======================================
# DOWNLOAD FOLDER
# ======================================

def download_folder(folder, output_dir, label):

    print("\n======================================")
    print(f"DOWNLOADING {label}")
    print("======================================")

    print("Repository folder:", folder)

    files = get_files(folder)

    print("Audio files found:", len(files))

    if len(files) == 0:

        print("ERROR: No FLAC files found!")

        return

    files = sorted(files)[:MAX_FILES]

    print("Files selected:", len(files))

    successful = 0

    for i, repo_path in enumerate(files):

        original_name = os.path.basename(repo_path)

        # Safety check
        if label == "REAL":

            if not original_name.startswith("yt_"):

                print(
                    "\nWARNING: Unexpected REAL file:"
                )

                print(original_name)

        if label == "SYNTHETIC":

            valid_prefixes = (
                "el_",
                "hg_",
                "hu_",
                "lv_",
                "po_",
                "sp_"
            )

            if not original_name.startswith(valid_prefixes):

                print(
                    "\nWARNING: Unexpected SYNTHETIC file:"
                )

                print(original_name)

        output_name = (
            f"{label.lower()}_hf_{i:04d}.flac"
        )

        output_path = os.path.join(
            output_dir,
            output_name
        )

        print(
            f"[{i + 1}/{len(files)}] "
            f"{original_name}"
        )

        if download_file(
            repo_path,
            output_path
        ):

            successful += 1

    print(
        f"\nCompleted {label}: "
        f"{successful}/{len(files)}"
    )


# ======================================
# MAIN
# ======================================

print("\n======================================")
print("VoiceShield-AI")
print("HUGGING FACE DATASET DOWNLOAD")
print("======================================")

print("\nDataset:")
print(REPO)

print("\nIMPORTANT:")
print("REAL      -> top-level real/")
print("SYNTHETIC -> top-level fake/")

# REAL
download_folder(
    "real",
    REAL_DIR,
    "REAL"
)

# SYNTHETIC
download_folder(
    "fake",
    SYNTHETIC_DIR,
    "SYNTHETIC"
)

print("\n======================================")
print("DOWNLOAD COMPLETE")
print("======================================")

print("Target:")
print("500 REAL")
print("500 SYNTHETIC")

print("\n======================================")