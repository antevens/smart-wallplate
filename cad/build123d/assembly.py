"""Reference assembly: insert + trim + models of every bought-in part.

Envelopes are simple boxes/stadiums sized from params.py - they are for
clearance checks only, NOT vendor models. The wiring board uses the KiCad STEP
(build/wiring_board.step, from pcb/wiring_board) when present. Its F side faces the
plate, so KiCad +x = room +x and no flip is needed.

Run: python assembly.py  -> ../../build/assembly.step
"""
from pathlib import Path
from build123d import Box, Compound, Color, Pos, export_step, import_step
from params import *
from common import stadium, slab
import insert
import trim
import bilresa
import post
import sensor_flex
import jumper

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "build"
WB_STEP = OUT / "wiring_board.step"


def env(part, name, rgb):
    part.label, part.color = name, Color(*rgb)
    return part


def wiring_board():
    """Wiring board: KiCad STEP when built (`make pcb`), else parameter envelopes."""
    if WB_STEP.exists():
        board = import_step(str(WB_STEP))
        # KiCad exports in sheet coordinates: recentre on the board slab, back face at WB_BACK_Z
        slab = max(board.solids(), key=lambda q: q.bounding_box().size.X * q.bounding_box().size.Y).bounding_box()
        cx, cy = (slab.min.X + slab.max.X) / 2, (slab.min.Y + slab.max.Y) / 2
        return env(Pos(-cx, WB_Y - cy, WB_BACK_Z - slab.min.Z) * board, "wiring_board", (0.12, 0.42, 0.23))
    parts = [Pos(0, WB_Y, WB_FRONT_Z - WB[2] / 2) * Box(*WB),
             Pos(IRM_C[0], WB_Y + IRM_C[1], WB_BACK_Z - IRM[2] / 2) * Box(*IRM),
             Pos(WAGO_X, WB_Y + WAGO_Y, WB_BACK_Z - WAGO6[2] / 2) * Box(*WAGO6),
             Pos(J2_POS[0], WB_Y + J2_POS[1], WB_FRONT_Z + 3) * Box(10, 8, 6)]
    return env(Compound(parts), "wiring_board_envelope", (0.12, 0.42, 0.23))


def build_assembly():
    ins = env(insert.build(), "insert_V0", (0.85, 0.3, 0.25))
    tr = env(trim.build(), "trim", (0.95, 0.95, 0.95))
    remote = env(bilresa.build(), "bilresa_model", (0.98, 0.98, 0.96))
    sw_top = Pos(0, SW_Y, WELL_FLOOR_Z + SW_ROCKER_H / 2) * Box(SW_BEZEL[0], SW_BEZEL[1], SW_ROCKER_H)
    sw_body = Pos(0, SW_Y, WELL_FLOOR_Z - SW_BODY[2] / 2) * Box(*SW_BODY)
    switch = env(Compound([sw_top, sw_body]), "marquardt_1802_envelope", (0.7, 0.13, 0.13))
    msr = env(Pos(0, MSR_Y, PT - RADAR_WALL - MSR[2] / 2) * Box(*MSR), "msr2_envelope", (0.2, 0.2, 0.2))
    fp = sensor_flex.parts()
    sht = env(fp["sht45"], "sht45_on_flex", (0.48, 0.12, 0.64))
    flex = env(fp["flex"], "sensor_flex", (0.85, 0.6, 0.1))
    plug = env(fp["plug"] + fp["fingers"] + fp["target"], "cn2_plug_fingers_jumper_pad_end", (0.8, 0.7, 0.3))
    lead5 = env(jumper.build()["jumper"], "flex_jumper_5v", (0.85, 0.6, 0.1))
    box = Pos(0, 0, -BOX_D / 2) * (Box(BOX_W + 3, BOX_H + 3, BOX_D) - Pos(0, 0, 1.5) * Box(BOX_W, BOX_H, BOX_D))
    box = env(box, "device_box_ref", (0.55, 0.6, 0.65))
    posts = env(post.placed(), "board_posts", (0.85, 0.5, 0.17))
    rest = [] if WB_STEP.exists() else [switch]          # the board STEP carries the rocker model
    return Compound(label="wallplate_assembly", children=[ins, tr, remote, *rest, posts, wiring_board(), msr, sht,
                                                           flex, plug, lead5, box])


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    export_step(build_assembly(), str(OUT / "assembly.step"))
    print("wrote assembly.step", "(KiCad wiring board STEP)" if WB_STEP.exists() else "(wiring board envelope)")
