# Echo Plus 2 Lidar — Kaeru expdb component

This repository contains the Kaeru `expdb` component and the pinned BROM
transport used during research on one Amazon Echo Plus (2nd generation, Lidar)
unit. It deliberately does **not** contain a system image, audio stack, Wi-Fi
data, SSH keys, account data, or backups from any individual unit.

> [!IMPORTANT]
> This repository alone is **not** a complete persistent-unlock or full-system
> installer. The original working unit also used a matching TEE1 handoff
> artifact and a firmware-specific boot-chain state. Those materials are not
> reproduced or built by this tree. Writing the Kaeru `expdb` payload alone
> must not be represented as sufficient to reproduce the original unit.

See [Boot-chain requirements and reproducibility status](docs/BOOT_CHAIN_REQUIREMENTS.md)
before treating a normal verified boot as a failed or successful Kaeru test.

The approach uses the MTK BootROM/Kamakiri-style chain with a Lidar-specific
Kaeru payload. It is a focused, reproducible port of that approach—not a
universal installer or a repackaged full amonet-koboreru release.

> [!WARNING]
> **Early hardware support — tested on one device only.** This kit has been
> validated on a single Echo Plus 2 / Lidar unit. It may not work on another
> unit, even with the same product name. Use it only on hardware you own or are
> authorized to service, make and verify a complete backup first, and accept
> the risk of device data loss or an unrecoverable boot failure. There is no
> warranty or promise of support for any particular firmware revision.

## Supported target

Only use this with an Echo Plus 2 / Lidar on the exact stock layout documented
by the preflight step.  Do not treat the included binary as a universal Android
boot image or flash it to a different Echo generation.

The writer checks the target GPT entry before it writes and always reads the
written blocks back for verification.  It does not reboot if that verification
fails.

## Contents

- `artifacts/lidar-kaeru-known-good.bin` — known-good Kaeru `expdb` payload
  for the tested layout.
- `source/lidar-board-kaeru-baseline.c` — historical baseline source note;
  it is not a reproducible build recipe for the opaque payload above.
- `brom-payload/` — source for the BROM handoff payload.
- `tools/flash_kaeru.py` — explicit, guarded expdb writer.
- `tools/sha256sums.txt` — artifact integrity hashes.
- `third_party/kamakiri/` — pinned upstream Kamakiri source dependency.

## Clone the repository

Clone it with its pinned dependency included:

```text
git clone --recurse-submodules https://github.com/davidwatters/echo-plus-2-unlock.git
cd echo-plus-2-unlock
```

If you already cloned it without the dependency, run:

```text
git submodule update --init --recursive
```

## Before writing

1. Make an independent full partition backup of the target.
2. Use the included pinned BROM host-tool dependency at
   `third_party/kamakiri/modules/`. Do not substitute an arbitrary newer
   Kamakiri revision while reproducing this result.
3. Put the device into BROM mode.
4. Run the writer with the real paths and **your own verified expected stock
   fingerprint**. The command refuses a mismatched GPT or partition hash.

```text
python tools/flash_kaeru.py \
  --modules third_party/kamakiri/modules \
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

This is a focused research/recovery component for the supported Echo Plus 2
hardware. Use at your own risk and only on hardware you own or are authorized
to service. A complete reproducible port requires the matching handoff source,
exact build inputs, and validation against the target firmware revision.
