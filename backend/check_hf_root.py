import requests

REPO = "garystafford/deepfake-audio-detection"

url = f"https://huggingface.co/api/datasets/{REPO}/tree/main"

params = {
    "recursive": "false",
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

print("\n======================================")
print("HUGGING FACE ROOT")
print("======================================")

for item in data:

    print(
        item.get("type"),
        "|",
        item.get("path")
    )

print("\n======================================")