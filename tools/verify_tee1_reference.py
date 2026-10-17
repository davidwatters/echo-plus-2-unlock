#!/usr/bin/env python3
"""Read-only TEE1 identity check for a user-owned extracted partition image."""
import argparse
import hashlib
from pathlib import Path

# Stock TEE1 observed in the original working custom-fastboot Lidar snapshot.
REFERENCE_SHA256 = "d643f0531375da21897abf3841b163f2834815213a223627820eb93001c5a51f"


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare a TEE1 image extracted from your own backup to the working-unit stock reference."
    )
    parser.add_argument("tee1_image", type=Path)
    args = parser.parse_args()

    actual = digest(args.tee1_image)
    print(f"TEE1 SHA-256: {actual}")
    print(f"Reference:    {REFERENCE_SHA256}")
    if actual == REFERENCE_SHA256:
        print("MATCH: target image matches the working-unit stock TEE1 reference.")
        return 0
    print("NO MATCH: this does not prove incompatibility, but it is not the saved reference.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
