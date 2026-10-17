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

The original working device also relied on a firmware-specific TEE1 handoff
state. The `expdb` Kaeru payload alone is not evidence that another device has
that state or will reproduce the same fastboot behavior.

The original TEE1 handoff artifact is intentionally not published here because
this repository does not contain a reproducible source build, provenance, or a
device-revision compatibility matrix for it. It must not be replaced with an
opaque binary and described as a universally safe flashing step.

For provenance, the SHA-256 of the TEE1 handoff image observed on the original
single-device research unit is:

```text
95ecb55ce28c9e5e54001e3328770277748f33b015d51297ab8a54e6f1380bf5
```

This is an identifier, not a firmware download or compatibility guarantee. A
user can compare a TEE1 image extracted from their own backup with the included
read-only helper:

```text
python tools/verify_tee1_reference.py path/to/their/tee1.bin
```

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
