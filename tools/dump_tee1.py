#!/usr/bin/env python3
"""Read-only TEE1 dumper for an Echo Plus 2 Lidar.

This tool only reads the target's GPT and TEE1 partition.  It refuses to
overwrite a backup and never calls an eMMC write, erase, or reboot function.
"""

import argparse
import hashlib
import os
import sys
from pathlib import Path

SECTOR_SIZE = 512


def require(path: Path) -> None:
    if not path.is_file():
        raise RuntimeError(f"Required file missing: {path}")


def hash_file(path: Path) -> str:
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Read and verify TEE1 only")
    parser.add_argument("--modules", required=True, type=Path)
    parser.add_argument("--stage1", required=True, type=Path)
    parser.add_argument("--stage2", required=True, type=Path)
    parser.add_argument("--output", default="lidar_current_tee1.bin", type=Path)
    args = parser.parse_args()

    modules = args.modules.resolve()
    stage1 = args.stage1.resolve()
    stage2 = args.stage2.resolve()
    output = args.output.resolve()
    partial = output.with_name(output.name + ".partial")

    for path in (modules / "device.py", stage1, stage2):
        require(path)
    if stage1.stat().st_size >= 0xA00:
        raise RuntimeError("Stage1 is too large for this loader")
    if output.exists() or partial.exists():
        raise RuntimeError(f"Refusing to overwrite existing backup: {output}")

    sys.path.insert(0, str(modules))
    from device import Device
    import load_payload
    from functions import parse_gpt

    original_loader = load_payload.load_payload_file

    def local_loader(path):
        name = Path(path).name
        if name == "stage1.bin":
            return original_loader(str(stage1))
        if name == "stage2.bin":
            return original_loader(str(stage2))
        raise RuntimeError(f"Unexpected payload requested: {path}")

    load_payload.load_payload_file = local_loader

    class AutoContinue:
        def __init__(self, *args, **kwargs):
            self.done = True

        def start(self):
            self.done = True

    load_payload.UserInputThread = AutoContinue
    device = None
    try:
        print("[TEE1] Waiting for BootROM device...")
        device = Device().find()
        print("[TEE1] Loading read-only transport stages...")
        load_payload.load_payload(device)
        device.timeout = 5
        device.emmc_switch(0)
        device.kick_watchdog()

        gpt = parse_gpt(device)
        tee1 = gpt.get("tee1")
        if not tee1 or len(tee1) != 2:
            raise RuntimeError(f"TEE1 entry missing from GPT: {tee1}")
        start, sectors = tee1
        if not isinstance(start, int) or not isinstance(sectors, int) or sectors <= 0:
            raise RuntimeError(f"Invalid TEE1 GPT entry: {tee1}")
        expected_size = sectors * SECTOR_SIZE
        print(f"[TEE1] GPT entry: start={start}, sectors={sectors}, bytes={expected_size}")

        digest = hashlib.sha256()
        with partial.open("xb") as target:
            for index in range(sectors):
                block = device.emmc_read(start + index)
                if len(block) != SECTOR_SIZE:
                    raise RuntimeError(f"Sector {index}: got {len(block)} bytes")
                target.write(block)
                digest.update(block)
                if index % 16 == 0:
                    device.kick_watchdog()
                if index % 256 == 0:
                    print(f"\r[TEE1] {index}/{sectors} ({100 * index / sectors:.1f}%)", end="", flush=True)
            target.flush()
            os.fsync(target.fileno())
        print("\r[TEE1] 100.0% COMPLETE                     ")

        if partial.stat().st_size != expected_size:
            raise RuntimeError("Output size does not match GPT")
        streamed = digest.hexdigest()
        saved = hash_file(partial)
        if streamed != saved:
            raise RuntimeError("Saved file hash does not match read stream")
        os.replace(partial, output)
        print("[TEE1] COMPLETE")
        print("[TEE1] File:", output)
        print("[TEE1] SHA256:", saved)
        return 0
    finally:
        if device is not None:
            try:
                device.close()
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
