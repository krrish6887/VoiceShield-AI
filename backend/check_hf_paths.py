import requests

REPO = "garystafford/deepfake-audio-detection"


def check_folder(folder):

    print("\n======================================")
    print("CHECKING:", folder)
    print("======================================")

    url = f"https://huggingface.co/api/datasets/{REPO}/tree/main"

    params = {
        "path": folder,
        "recursive": "true",
        "expand": "false"
    }

    response = requests.get(
        url,
        params=params,
        timeout=60
    )

    print("HTTP status:", response.status_code)

    response.raise_for_status()

    data = response.json()

    files = []

    for item in data:

        if item.get("type") == "file":

            path = item.get("path", "")

            if path.lower().endswith(".flac"):

                files.append(path)

    print("Audio files found:", len(files))

    print("\nFirst 10 paths:")

    for path in files[:10]:
        print(path)

    return files


real_files = check_folder("data/real")
fake_files = check_folder("data/fake")


print("\n======================================")
print("COMPARISON")
print("======================================")

if real_files and fake_files:

    print("\nFirst REAL file:")
    print(real_files[0])

    print("\nFirst FAKE file:")
    print(fake_files[0])

print("\n======================================")
print("EXPECTED")
print("======================================")

print("REAL should contain filenames beginning with:")
print("yt_")

print("\nFAKE should contain filenames beginning with:")
print("el_, hg_, hu_, lv_, po_, or sp_")

print("\n======================================")