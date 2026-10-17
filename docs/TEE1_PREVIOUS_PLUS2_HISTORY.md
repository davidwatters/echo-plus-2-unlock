# Previous Echo Plus 2 TEE1 history — corrected from HP snapshot

This is the evidence record for the first working Echo Plus 2 (Lidar) setup.
It was corrected after locating the HP's 2026-09-28 working-fastboot snapshot.
It describes preserved artifacts only; it is not a flashing procedure.

## Confirmed facts

| Component | Preserved file / value | What it establishes |
| --- | --- | --- |
| Original stock TEE1 | `tee1-stock-lidar.bin` | Original unit's stock TEE1 partition capture. |
| Stock TEE1 SHA-256 | `d643f0531375da21897abf3841b163f2834815213a223627820eb93001c5a51f` | Reference identity of the stock TEE1 capture. |
| Stock TEE2 SHA-256 | `d643f0531375da21897abf3841b163f2834815213a223627820eb93001c5a51f` | The saved TEE2 capture was byte-identical to saved stock TEE1. |
| Kaeru `expdb` payload | `lidar-kaeru-known-good.bin` | Separate payload stored in `expdb`, SHA-256 `754ab33bc26dc9b359a2e9a187a0ae7810665fc2a7a85b7615b64bcd5f632e82`. |
| Boot0/preloader on working unit | `emmc-boot0-stock.bin` | Working unit's boot0 was preserved as stock; boot0 was not the modified component in this record. |
| 2026-09-28 fastboot snapshot TEE1 | `tee1.bin` from the HP snapshot | SHA-256 `d643f0531375da21897abf3841b163f2834815213a223627820eb93001c5a51f`, exactly matching the stock TEE1 reference. |
| 2026-09-28 fastboot snapshot TEE2 | `tee2.bin` from the HP snapshot | Same stock SHA-256 as TEE1. |

## Important distinction

TEE1 is a user-area partition, separate from eMMC boot0/preloader and separate
from the `expdb` partition. The HP snapshot proves that the working custom
fastboot state retained stock TEE1 and TEE2. The confirmed custom component was
the Kaeru artifact in `expdb`, alongside the matching boot-chain state.

The original working path therefore involved distinct locations:

```text
boot0      stock preloader reference
TEE1       stock, verified against its original capture
expdb      Kaeru payload
```

## Confirmed role of the 1,119,760-byte TEE1 payload

`lidar-koboreru-tee1.img` is 1,119,760 bytes, whereas the actual TEE1
partition is 5,242,880 bytes. It is deliberately a compact payload—not a full
TEE1 clone. The preserved Koboreru installer source writes its corresponding
`tee-cupcake-payload.bin` to the beginning of `tee1`, padding only its final
512-byte sector. It then uses that loader to transfer into Kaeru from `expdb`.

This was independently confirmed on the second Lidar unit by UART output:
`Jumping to kaeru stage 2`, followed by the Kaeru banner and a working
`fastboot oem kaeru-version` response. The payload must therefore be kept
paired with the intended preloader and Kaeru artifact; it is not a generic TEE
image for other product generations.

## What the HP working-fastboot snapshot actually records

The HP contains a dated `lidar-fastboot-unlocked-20260928` snapshot. Its
manifest records a confirmed fastboot state (`unlock_status: true`) while its
full TEE1 and TEE2 dumps still match the stock hash above.

The active Kaeru artifact recorded by that later snapshot was:

```text
lidar-kaeru-fastboot-rammap-fixed.bin
SHA-256: 1ab8c5c02b1a0db732ad220243d9d20eca3540632784d815d5363e793aadbd73
```

The same snapshot records a guarded BROM-side writer named
`lidar-kaeru-callback-fix-flash.py` and source snapshots `board-lidar.c` and
`lidar_defconfig`. Its notes describe a Lidar-specific correction for LK's
loaded-payload address map and stock fastboot initialization. In other words,
the evidence points to a later Kaeru `expdb`/LK-in-memory route. That snapshot
retained stock TEE1, so it must not be used to erase the separately verified
Koboreru TEE1-loader sequence above.

The prior public repository contains the older baseline Kaeru artifact
(`754ab33b...`), not this recorded working-fastboot artifact. Treat those as
different artifacts; do not substitute them based on filename similarity.

Do not infer that an unknown auxiliary artifact establishes compatibility with
a different unit or firmware revision. First preserve and independently verify
that unit's own TEE1 dump.

## New-device comparison workflow

1. Take two read-only TEE1 dumps with `tools/dump_tee1.py`.
2. Confirm both dump hashes match each other.
3. Record the target dump size and SHA-256 alongside this document.
4. Compare the target identity to the stock TEE1 reference above.

This comparison can establish whether a target matches the saved stock
reference; it cannot establish that an unknown image is safe to install.
