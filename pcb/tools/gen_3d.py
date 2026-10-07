"""Envelope 3D models for the footprints without a vendor model (kicad/3d/*.step).

Run with the CAD venv: .venv/bin/python pcb/tools/gen_3d.py
Origin = footprint origin, +Z = away from the board on the mounting side.
"""
from pathlib import Path
from build123d import Box, Pos, export_step

OUT = Path(__file__).resolve().parents[1] / "kicad" / "3d"
OUT.mkdir(parents=True, exist_ok=True)

# Marquardt 1802.2504 (drawing 1802.2504 rev g): body 18.6 x 22 from the PCB seat to the
# panel face (16.2), flange 21 x 24 x 2 on the panel face, rocker 5.3 above the panel face.
# Body centred on the footprint origin, turned 90 degrees (long side along x).
rocker = Pos(0, 0, 16.2 / 2) * Box(22, 18.6, 16.2)
rocker += Pos(0, 0, 16.2 + 1) * Box(24, 21, 2)
rocker += Pos(0, 0, 18.2 + 1.65) * Box(19, 16, 3.3)
export_step(rocker, str(OUT / "Marquardt_1802.2504.step"))

# WAGO 2604-1106: 32.4 x 19.2, 16.7 above the board; body centred at y -2.57 in the footprint
wago = Pos(0, 2.57, 16.7 / 2) * Box(32.4, 19.2, 16.7)
export_step(wago, str(OUT / "WAGO_2604-1106.step"))
print("wrote", OUT)
