"""Reference assembly: insert + trim + models of every bought-in part.

Envelopes are simple boxes/stadiums sized from params.py - they are for
clearance checks only, NOT vendor models. The PSU carrier uses the KiCad STEP
(cad/vendor/psu_carrier.step) when present. Its F side (components) faces into
the box, so it is turned 180 deg about Y: KiCad +x -> room -x.

Run: python assembly.py  -> ../../build/assembly.step, ../../build/pcb_outline.dxf
"""
from pathlib import Path
from build123d import (Box, Compound, Color, Pos, Rot, Rectangle, Polyline, Line,
                       ThreePointArc, export_step, import_step, ExportDXF, Unit, extrude)
from params import *
from common import stadium, slab
import insert
import trim
import bilresa

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "build"
PCB_STEP = ROOT / "cad" / "vendor" / "psu_carrier.step"


def env(part, name, rgb):
    part.label, part.color = name, Color(*rgb)
    return part


def psu():
    if PCB_STEP.exists():
        board = import_step(str(PCB_STEP))
        return env(Pos(0, PCB_Y, PCB_BACK_Z) * Rot(0, 180, 0) * board, "psu_carrier", (0.12, 0.42, 0.23))
    pcb = Pos(0, PCB_Y, PCB_BACK_Z - PCB[2] / 2) * Box(*PCB)
    irm = Pos(0, PCB_Y - PCB[1] / 2 + IRM[1] / 2 + 0.5, PCB_FRONT_Z - IRM[2] / 2) * Box(*IRM)
    return env(Compound([pcb, irm]), "psu_carrier_envelope", (0.12, 0.42, 0.23))


def build_assembly():
    ins = env(insert.build(), "insert_V0", (0.85, 0.3, 0.25))
    tr = env(trim.build(), "trim", (0.95, 0.95, 0.95))
    remote = env(bilresa.build(), "bilresa_model", (0.98, 0.98, 0.96))
    sw_top = Pos(0, SW_Y, WELL_FLOOR_Z + SW_ROCKER_H / 2) * Box(SW_BEZEL[0], SW_BEZEL[1], SW_ROCKER_H)
    sw_body = Pos(0, SW_Y, PANEL_BOT_Z - SW_BODY[2] / 2) * Box(*SW_BODY)
    switch = env(Compound([sw_top, sw_body]), "c1300_envelope", (0.7, 0.13, 0.13))
    msr = env(Pos(0, MSR_Y, PT - RADAR_WALL - MSR[2] / 2) * Box(*MSR), "msr2_envelope", (0.2, 0.2, 0.2))
    sht = env(Pos(0, SHT_Y, PT - SKIN - 0.8) * Box(SHT[0], SHT[1], 1.6), "sht45_tab", (0.48, 0.12, 0.64))
    box = Pos(0, 0, -BOX_D / 2) * (Box(BOX_W + 3, BOX_H + 3, BOX_D) - Pos(0, 0, 1.5) * Box(BOX_W, BOX_H, BOX_D))
    box = env(box, "device_box_ref", (0.55, 0.6, 0.65))
    return Compound(label="wallplate_assembly", children=[ins, tr, remote, switch, psu(), msr, sht, box])


def pcb_outline_dxf():
    """Edge.Cuts reference for the PSU carrier, KiCad front view, origin = board centre.
    Includes the isolation slot notch from the top edge."""
    w, h, r = PCB[0] / 2, PCB[1] / 2, 1.5
    x0, x1 = PCB_SLOT_X
    sr = (x1 - x0) / 2
    pts = [(x1, h), (w - r, h)]
    edges = [Line((x1, h), (w - r, h)),
             ThreePointArc((w - r, h), (w - r * 0.2929, h - r * 0.2929), (w, h - r)),
             Line((w, h - r), (w, -h + r)),
             ThreePointArc((w, -h + r), (w - r * 0.2929, -h + r * 0.2929), (w - r, -h)),
             Line((w - r, -h), (-w + r, -h)),
             ThreePointArc((-w + r, -h), (-w + r * 0.2929, -h + r * 0.2929), (-w, -h + r)),
             Line((-w, -h + r), (-w, h - r)),
             ThreePointArc((-w, h - r), (-w + r * 0.2929, h - r * 0.2929), (-w + r, h)),
             Line((-w + r, h), (x0, h)),
             Line((x0, h), (x0, PCB_SLOT_YEND + sr)),
             ThreePointArc((x0, PCB_SLOT_YEND + sr), ((x0 + x1) / 2, PCB_SLOT_YEND), (x1, PCB_SLOT_YEND + sr)),
             Line((x1, PCB_SLOT_YEND + sr), (x1, h))]
    dxf = ExportDXF(unit=Unit.MM)
    dxf.add_layer("Edge.Cuts")
    for e in edges:
        dxf.add_shape(e, layer="Edge.Cuts")
    dxf.write(str(OUT / "pcb_outline.dxf"))


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    export_step(build_assembly(), str(OUT / "assembly.step"))
    pcb_outline_dxf()
    print("wrote assembly.step and pcb_outline.dxf", "(KiCad board STEP)" if PCB_STEP.exists() else "(PSU envelope)")
