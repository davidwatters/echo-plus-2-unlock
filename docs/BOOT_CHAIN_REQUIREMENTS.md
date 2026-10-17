# Boot-chain requirements and reproducibility status

This document corrects an earlier overstatement in the project README.

## What this repository provides

The repository provides three distinct pieces:

1. A pinned BROM transport which loads its stage-1 and stage-2 payloads for a
   temporary maintenance session.
2. A guarded writer for the Kaeru payload stored in the `expdb` range.
3. The corresponding opaque Kaeru `expdb` binary used on the original research
   unit, with an integrity hash.

The BROM stages are used by `tools/flash_kaeru.py` through the pinned
`third_party/kamakiri/modules/load_payload.py`; they are not expected to print
their banners during a normal power-on boot.

## What this repository does not provide

The original working-device fastboot snapshot shows stock TEE1 and stock TEE2,
each with this SHA-256:

```text
d643f0531375da21897abf3841b163f2834815213a223627820eb93001c5a51f
```

The baseline `expdb` Kaeru payload alone is still not evidence that another
device has the matching boot-chain state or will reproduce the same fastboot
behavior. A user can compare a TEE1 image extracted from their own backup with
the included read-only helper:

```text
python tools/verify_tee1_reference.py path/to/their/tee1.bin
```

### Historical working-fastboot evidence

A dated private snapshot of the original research unit records a later,
different Kaeru artifact in the `expdb` role:

```text
lidar-kaeru-fastboot-rammap-fixed.bin
SHA-256: 1ab8c5c02b1a0db732ad220243d9d20eca3540632784d815d5363e793aadbd73
```

That snapshot also records stock TEE1/TEE2. This public repository contains
the earlier baseline artifact, not that later working-fastboot artifact. The
historical hash is recorded for provenance only; it is not a compatibility
guarantee or a substitute for reproducible source and target validation.

Likewise, this project does not include a complete persistent operating-system
installation. Any device-specific configuration—such as Wi-Fi credentials,
player identity, paired Zigbee network state, and SSH host identity—must be
created independently on each target.

## Preflight requirement

Before asserting that a target matches the research unit, preserve the target's
own complete backup and compare its boot-chain components against known-good
references from the same firmware family. A normal verified boot after writing
`expdb` indicates only that the stock boot chain still owns the boot; it does
not prove that the Kaeru component is active.

Do not infer incompatibility solely from an MTK model string such as `MT8167B`
versus a board/platform label used in older project notes. Establish compatibility
from the partition layout, firmware revision, and observed behavior instead.

## Status

The public project is a research component, not a complete one-click unlock.
It remains validated on one device only.
