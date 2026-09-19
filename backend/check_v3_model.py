import torch

MODEL_PATH = "../models/voice_detector_v3.pth"

print("\n======================================")
print("CHECKING V3 MODEL")
print("======================================")

checkpoint = torch.load(
    MODEL_PATH,
    map_location="cpu"
)

print("Checkpoint type:")
print(type(checkpoint))

print("\nCheckpoint contents:")

if isinstance(checkpoint, dict):

    for key, value in checkpoint.items():

        if hasattr(value, "shape"):
            print(
                key,
                "->",
                type(value),
                "shape:",
                value.shape
            )
        else:
            print(
                key,
                "->",
                type(value)
            )

else:

    print("Model is stored directly.")

print("\n======================================")
print("V3 MODEL CHECK COMPLETE")
print("======================================")