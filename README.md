# Echo Plus 2 Lidar — Kaeru fastboot unlock kit

This repository contains the minimal, device-family-specific materials used to
bring up Kaeru fastboot on the Amazon Echo Plus (2nd generation, Lidar / MT8516).
It deliberately does **not** contain a system image, audio stack, Wi-Fi data,
SSH keys, account data, or backups from any individual unit.

## Supported target

Only use this with an Echo Plus 2 / Lidar on the exact stock layout documented
by the preflight step.  Do not treat the included binary as a universal Android
boot image or flash it to a different Echo generation.

The writer checks the target GPT entry before it writes and always reads the
written blocks back for verification.  It does not reboot if that verification
fails.

## Contents

- `artifacts/lidar-kaeru-known-good.bin` — known-good Kaeru payload for the
  supported Lidar layout.
- `source/lidar-board-kaeru-baseline.c` — matching target-board source patch.
- `brom-payload/` — source for the BROM handoff payload.
- `tools/flash_kaeru.py` — explicit, guarded expdb writer.
- `tools/sha256sums.txt` — artifact integrity hashes.

## Before writing

1. Make an independent full partition backup of the target.
2. Clone the matching BROM host tooling and use its `modules/` directory:

   ```text
   git clone https://github.com/R0rt1z2/kamakiri.git
   cd kamakiri
   git checkout 77122812f02562ca19cfba78ba32ef64ce324b69
   ```

   This kit deliberately does not bundle that separate upstream project.
3. Put the device into BROM mode.
4. Run the writer with the real paths and **your own verified expected stock
   fingerprint**. The command refuses a mismatched GPT or partition hash.

```text
python tools/flash_kaeru.py \
  --modules /path/to/kamakiri/modules \
  --image artifacts/lidar-kaeru-known-good.bin \
  --expected-stock-sha256 YOUR_PRE_FLASH_EXPDB_SHA256 \
  --yes-write
```

`YOUR_PRE_FLASH_EXPDB_SHA256` must be calculated from the target before its
first write.  A target with a different hash must be investigated, not forced.

## Recovery

Keep the backup made in step 1.  Recovery must restore the exact expdb blocks
from that backup using the same BROM tooling.  This repository intentionally
does not ship somebody else's stock partitions.

## Status

This is a focused research/recovery kit for the supported Echo Plus 2 hardware.
Use at your own risk and only on hardware you own or are authorized to service.
