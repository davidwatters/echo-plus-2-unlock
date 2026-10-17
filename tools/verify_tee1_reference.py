#!/usr/bin/env python3
"""Read-only TEE1 identity check for a user-owned extracted partition image."""
import argparse
import hashlib
from pathlib import Path

# Reference observed on the original single-device Lidar research unit.
REFERENCE_SHA256 = "95ecb55ce28c9e5e54001e3328770277748f33b015d51297ab8a54e6f1380bf5"


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare a TEE1 image extracted from your own backup to the research reference."
    )
    parser.add_argument("tee1_image", type=Path)
    args = parser.parse_args()

    actual = digest(args.tee1_image)
    print(f"TEE1 SHA-256: {actual}")
    print(f"Reference:    {REFERENCE_SHA256}")
    if actual == REFERENCE_SHA256:
        print("MATCH: target image matches the single-device research reference.")
        return 0
    print("NO MATCH: this does not prove incompatibility, but it is not the saved reference.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
