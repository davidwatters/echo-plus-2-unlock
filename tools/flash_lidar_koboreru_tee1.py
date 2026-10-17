#!/usr/bin/env python3
"""Write and verify only the preserved Lidar Koboreru TEE1 payload.

This deliberately refuses to touch boot0, expdb, LK, boot slots, GPT, or
misc.  The caller must separately choose any boot-mode flag or reboot action.
"""

import argparse
import hashlib
import sys
from pathlib import Path

SECTOR_SIZE = 512
EXPECTED_PAYLOAD_SHA256 = (
    "95ecb55ce28c9e5e54001e3328770277748f33b015d51297ab8a54e6f1380bf5"
)


def sha256_file(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def require_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise RuntimeError(f"{label} is missing: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Guarded Lidar Koboreru TEE1 payload writer"
    )
    parser.add_argument("--modules", required=True, type=Path)
    parser.add_argument("--stage1", required=True, type=Path)
    parser.add_argument("--stage2", required=True, type=Path)
    parser.add_argument("--payload", required=True, type=Path)
    parser.add_argument(
        "--backup",
        required=True,
        type=Path,
        help="existing full TEE1 readback; must be exactly the target GPT size",
    )
    args = parser.parse_args()

    modules = args.modules.resolve()
    stage1 = args.stage1.resolve()
    stage2 = args.stage2.resolve()
    payload = args.payload.resolve()
    backup = args.backup.resolve()
    for path, label in (
        (modules / "device.py", "device module"),
        (stage1, "stage1"),
        (stage2, "stage2"),
        (payload, "TEE1 payload"),
        (backup, "TEE1 backup"),
    ):
        require_file(path, label)

    if stage1.stat().st_size >= 0xA00:
        raise RuntimeError("stage1 is too large for this loader")
    payload_hash = sha256_file(payload)
    if payload_hash != EXPECTED_PAYLOAD_SHA256:
        raise RuntimeError(
            f"payload SHA-256 mismatch: {payload_hash}; expected {EXPECTED_PAYLOAD_SHA256}"
        )

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
        raise RuntimeError(f"unexpected transport payload requested: {path}")

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
        load_payload.load_payload(device)
        device.timeout = 5
        device.emmc_switch(0)
        device.kick_watchdog()

        gpt = parse_gpt(device)
        tee1 = gpt.get("tee1")
        if not tee1 or len(tee1) != 2:
            raise RuntimeError(f"TEE1 entry missing from GPT: {tee1}")
        start, sectors = tee1
        if (start, sectors) != (8192, 10240):
            raise RuntimeError(f"unexpected Lidar TEE1 GPT entry: {tee1}")
        if backup.stat().st_size != sectors * SECTOR_SIZE:
            raise RuntimeError(
                f"backup size {backup.stat().st_size} does not match TEE1 size {sectors * SECTOR_SIZE}"
            )

        payload_bytes = payload.read_bytes()
        # The original Koboreru flash_binary helper pads only the final
        # partial sector; it does not wipe the rest of TEE1.
        data = payload_bytes + b"\0" * ((-len(payload_bytes)) % SECTOR_SIZE)
        blocks = len(data) // SECTOR_SIZE
        if blocks > sectors:
            raise RuntimeError("payload exceeds TEE1 partition")
        print(f"[TEE1] Backup accepted: {backup.name} ({sha256_file(backup)})")
        print(f"[TEE1] Writing {blocks} sectors at GPT tee1 start {start}...")
        for index in range(blocks):
            offset = index * SECTOR_SIZE
            device.emmc_write(start + index, data[offset:offset + SECTOR_SIZE])
            if index % 16 == 0:
                device.kick_watchdog()
            if index % 256 == 0:
                print(f"\r[TEE1] {index}/{blocks} ({100 * index / blocks:.1f}%)", end="", flush=True)
        print("\r[TEE1] Write complete; verifying...                         ")

        actual = bytearray()
        for index in range(blocks):
            actual.extend(device.emmc_read(start + index))
            if index % 16 == 0:
                device.kick_watchdog()
        if actual[:len(payload_bytes)] != payload_bytes:
            raise RuntimeError("readback does not match the payload bytes")
        padded_hash = hashlib.sha256(actual).hexdigest()
        print("[TEE1] VERIFIED payload SHA-256:", EXPECTED_PAYLOAD_SHA256)
        print("[TEE1] VERIFIED padded-sector SHA-256:", padded_hash)
        print("[TEE1] No reboot or boot-mode flag was changed.")
        return 0
    finally:
        if device is not None:
            try:
                device.close()
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
