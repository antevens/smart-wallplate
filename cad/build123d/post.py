"""BOARD POST - screws into an insert boss and snaps through a wiring-board hole (D-28).

Modelled at the origin: z = 0 is the boss face (Z_BOT), the stud points up (+z) into the boss,
the board is below. Print: lying on its flat (export.py), so the snap prongs flex along the
layers; PC-FR. Cut the stud's M4 x 0.7 thread with a die after printing.
Run:  python post.py  -> ../../build/post.step / .stl
"""
from build123d import Box, Cone, Cylinder, Pos, RegularPolygon, extrude
from params import *


def build():
    board_front, board_back = WB_FRONT_Z - Z_BOT, WB_BACK_Z - Z_BOT
    stud = Pos(0, 0, MOUNT_THREAD_L / 2 - 0.5) * Cylinder(MOUNT_THREAD_D / 2, MOUNT_THREAD_L - 1.0)
    hexc = Pos(0, 0, -POST_HEX_H) * extrude(RegularPolygon(POST_HEX_AF / 2, 6, major_radius=False), POST_HEX_H)
    shoulder = Pos(0, 0, (board_front - POST_HEX_H) / 2) * Cylinder(POST_SHOULDER_D / 2, -POST_HEX_H - board_front)
    shaft = Pos(0, 0, (board_front + board_back) / 2) * Cylinder(POST_SHAFT_D / 2, WB[2] + 0.01)
    head = Pos(0, 0, board_back - POST_HEAD_H / 2) * Cone(POST_SHAFT_D / 2 - 0.4, POST_HEAD_D / 2, POST_HEAD_H)
    split_len = POST_SPLIT_L + WB[2] + POST_HEAD_H
    split = Pos(0, 0, board_back - POST_HEAD_H + split_len / 2 - 0.01) * Box(POST_SPLIT_W, POST_HEAD_D + 1, split_len)
    p = stud + hexc + shoulder + ((shaft + head) - split)
    # print flat on the -y side at the stud (thread crest only); the split is perpendicular to it,
    # so the prongs flex parallel to the bed
    return p - Pos(0, -MOUNT_THREAD_D / 2 - 50 + POST_FLAT, 0) * Box(100, 100, 100)


def placed():
    """All four posts in assembly position."""
    p = build()
    out = None
    for x, y in MOUNT_HOLES:
        q = Pos(x, y, Z_BOT) * p
        out = q if out is None else out + q
    return out


if __name__ == "__main__":
    from pathlib import Path
    from build123d import export_step, export_stl
    out = Path(__file__).resolve().parents[2] / "build"
    out.mkdir(exist_ok=True)
    p = build()
    export_step(p, str(out / "post.step"))
    export_stl(p, str(out / "post.stl"))
    print("post", p.bounding_box().size)
