#!/usr/bin/env python3
"""Guarded BROM writer for the Echo Plus 2 Lidar Kaeru payload.

This tool writes only the supported expdb range after checking the target GPT,
checking the caller-supplied pre-flash hash, and verifying every block written.
"""
import argparse
import hashlib
import os
import sys
import time

EXPDB_START = 30720
EXPDB_SECTORS = 20480
SECTOR_SIZE = 512


class AutoContinue:
    def __init__(self, *args, **kwargs):
        self.done = False

    def start(self):
        self.done = True


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def read_range(device, start, count):
    result = bytearray()
    for sector in range(count):
        result.extend(device.emmc_read(start + sector))
        if sector % 64 == 0:
            device.kick_watchdog()
    return bytes(result)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--modules", required=True, help="kamakiri-mt8516 modules directory")
    parser.add_argument("--image", required=True, help="Kaeru binary to write")
    parser.add_argument("--expected-stock-sha256", required=True,
                        help="SHA-256 of the current expdb payload before writing")
    parser.add_argument("--yes-write", action="store_true", help="perform the write")
    args = parser.parse_args()
    if not args.yes_write:
        parser.error("refusing to write without --yes-write")

    sys.path.insert(0, os.path.abspath(args.modules))
    import load_payload as payload
    from device import Device
    from functions import parse_gpt, switch_user

    image = open(args.image, "rb").read()
    if not image or len(image) > EXPDB_SECTORS * SECTOR_SIZE:
        raise RuntimeError("Kaeru image has an invalid size")

    payload.UserInputThread = AutoContinue
    print("Waiting for BROM device")
    device = Device().find()
    payload.load_payload(device)
    device.timeout = 5
    time.sleep(1)
    switch_user(device)

    gpt = parse_gpt(device)
    if gpt.get("expdb") != (EXPDB_START, EXPDB_SECTORS):
        raise RuntimeError("unsupported GPT: expdb does not match the Lidar layout")

    sectors = (len(image) + SECTOR_SIZE - 1) // SECTOR_SIZE
    before = read_range(device, EXPDB_START, sectors)
    if sha256(before[:len(image)]).lower() != args.expected_stock_sha256.lower():
        raise RuntimeError("pre-flash expdb hash mismatch; refusing to write")

    padded = image.ljust(sectors * SECTOR_SIZE, b"\0")
    for sector in range(sectors):
        offset = sector * SECTOR_SIZE
        device.emmc_write(EXPDB_START + sector, padded[offset:offset + SECTOR_SIZE])
        if sector % 64 == 0:
            device.kick_watchdog()

    verified = read_range(device, EXPDB_START, sectors)
    if verified != padded:
        raise RuntimeError("readback verification failed; reboot withheld")
    print("Kaeru written and verified:", sha256(image))
    device.reboot()


if __name__ == "__main__":
    main()
