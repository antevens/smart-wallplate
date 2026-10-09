"""NA pocket-floor insert (D-35, D-41): printed floor on the insert's pocket floor for the battery-free
remote (replacement back cover). Opening over the switch well; the sensor-flex tongue comes down the
pocket wall from the right channel and lies in the floor's top recess, its two gold pads flush under
the back cover's spring fingers. Raises the remote by BC_FLOOR_T. Geometry in backcover.py.
"""
from build123d import Pos
from params import *
import backcover


def cutouts():
    """Switch well, and the board-post bosses that rise into the pocket's corners."""
    out = [(0.0, SW_Y, WELL_IN[0], WELL_IN[1])]
    for (x, y), top in zip(MOUNT_HOLES, MOUNT_BOSS_TOP):
        if top > SEAT_Z and abs(x) < POCKET_IN[0] / 2 and abs(y) < POCKET_IN[1] / 2:
            out.append((x, y, MOUNT_BOSS_D, MOUNT_BOSS_D))
    return out


def tongue_path():
    """The tongue on the floor, copper up (no fold): in along BC_NA_TONGUE_Y from the wall, down a narrow
    strip clear of the switch well's opening, then the pad strip under the fingers."""
    wall_x = tongue_walls()[1] - JUMPER_T
    w = BC_NA_NECK_W
    xd, wd, y_pad = BC_NA_DOWN
    xf = BC_FINGERS[0][0]
    y_bot = min(y for _, y in BC_FINGERS) - BC_FLOOR_PAD[1] / 2 - 1.0
    run = (xd - wd / 2, wall_x, BC_NA_TONGUE_Y - w / 2, BC_NA_TONGUE_Y + w / 2, 1)
    down = (xd - wd / 2, xd + wd / 2, y_pad, BC_NA_TONGUE_Y - w / 2, 1)
    pads = (xf - BC_TONGUE_W / 2, xf + BC_TONGUE_W / 2, y_bot, y_pad, 1)
    return [run, down, pads]


def parts():
    p = backcover.floor_insert(POCKET_IN, tongue_walls()[1] - JUMPER_T, cutouts(), tongue_path())
    return {k: Pos(0, 0, SEAT_Z) * v for k, v in p.items()}
