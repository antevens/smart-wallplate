"""Reference assembly: plate + envelope models of every bought-in part.

Envelopes are simple boxes/stadiums sized from params.py - they are for
clearance checks only, NOT accurate vendor models. Replace with vendor STEP
files in cad/vendor/ when available (see docs/BOM.md).

Run: python assembly.py  -> ../../build/assembly.step, ../../build/pcb_outline.dxf
"""
from pathlib import Path
from build123d import (Box, Cylinder, RectangleRounded, Rectangle, Compound, Color, Pos,
                       export_step, ExportDXF, Unit, Rot, SlotCenterToCenter, extrude)
from params import *
import wallplate

OUT = Path(__file__).resolve().parents[2] / "build"


def env(part, name, rgb):
    part.label, part.color = name, Color(*rgb)
    return part


def build_assembly():
    plate = env(wallplate.build(), "plate", (0.95, 0.95, 0.95))
    remote = Pos(0, 0, SEAT_Z) * extrude(Rot(0, 0, 90) * SlotCenterToCenter(B_H - B_W, B_W), B_D)
    remote = env(remote, "bilresa_envelope", (0.95, 0.9, 0.78))
    sw_top = Pos(0, SW_Y, WELL_FLOOR_Z + SW_ROCKER_H / 2) * Box(SW_BEZEL[0], SW_BEZEL[1], SW_ROCKER_H)
    sw_body = Pos(0, SW_Y, WELL_FLOOR_Z - SW_PANEL_T - SW_BODY[2] / 2) * Box(*SW_BODY)
    switch = env(Compound([sw_top, sw_body]), "c1300_envelope", (0.7, 0.13, 0.13))
    z_pcb = FLOOR_Z - PCB_STANDOFF
    pcb = env(Pos(0, PCB_Y, z_pcb - PCB[2] / 2) * Box(*PCB), "psu_pcb", (0.12, 0.42, 0.23))
    irm = env(Pos(0, PCB_Y + 5, z_pcb - PCB[2] - IRM[2] / 2) * Box(*IRM), "irm03_envelope", (0.15, 0.15, 0.15))
    msr = env(Pos(0, MSR_Y, PT - RADAR_WALL - MSR[2] / 2) * Box(*MSR), "msr2_envelope", (0.2, 0.2, 0.2))
    sht = env(Pos(0, SHT_Y, PT - SKIN - 0.8) * Box(SHT[0], SHT[1], 1.6), "sht45_tab", (0.48, 0.12, 0.64))
    box = Pos(0, 0, -BOX_D / 2) * (Box(BOX_W + 3, BOX_H + 3, BOX_D) - Pos(0, 0, 1.5) * Box(BOX_W, BOX_H, BOX_D))
    box = env(box, "device_box_ref", (0.55, 0.6, 0.65))
    return Compound(label="wallplate_assembly",
                    children=[plate, remote, switch, pcb, irm, msr, sht, box])


def pcb_outline_dxf():
    """Edge.Cuts for the PSU carrier (origin = board centre). Import into KiCad on Edge.Cuts."""
    dxf = ExportDXF(unit=Unit.MM)
    dxf.add_layer("Edge.Cuts")
    dxf.add_shape(RectangleRounded(PCB[0], PCB[1], 1.5), layer="Edge.Cuts")
    dxf.write(str(OUT / "pcb_outline.dxf"))


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    export_step(build_assembly(), str(OUT / "assembly.step"))
    pcb_outline_dxf()
    print("wrote assembly.step and pcb_outline.dxf")
