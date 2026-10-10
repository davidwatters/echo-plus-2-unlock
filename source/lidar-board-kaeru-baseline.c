// SPDX-License-Identifier: AGPL-3.0-or-later
// Echo Plus 2nd Generation (Lidar): stable Kaeru bootstrap for the full port.

#include <arch/arm.h>
#include <board_ops.h>
#include <lib/common.h>

void board_early_init(void)
{
    /* Verified Lidar permanent-unlock predicate. */
    FORCE_RETURN(0x41E01968, 1);
    printf("Lidar Kaeru baseline: unlocked stock boot flow retained\n");
}

void board_late_init(void)
{
    printf("Lidar Kaeru baseline: ready for common-hook port\n");
}
