"""Envelope 3D model for the TR5 fuse (KiCad ships none for Fuse_Littelfuse_372_D8.50mm).

Littelfuse 392 (TE5/TR5) body: 8.5 mm dia x 8 mm high, leads 5.08 mm pitch.
Origin = pad 1, model sits on the board top (z=0 up). Envelope only.
Run with the CAD venv:  .venv/bin/python pcb/tools/gen_3d.py
"""
from pathlib import Path
from build123d import Cylinder, Pos, Align, export_step

OUT = Path(__file__).resolve().parents[1] / "kicad" / "3d"
OUT.mkdir(parents=True, exist_ok=True)
body = Pos(2.54, 0, 0.5) * Cylinder(4.25, 7.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
leads = [Pos(x, 0, -3.0) * Cylinder(0.3, 3.5, align=(Align.CENTER, Align.CENTER, Align.MIN)) for x in (0, 5.08)]
part = body + leads[0] + leads[1]
part.label = "Fuse_TR5_D8.5mm_H8mm"
export_step(part, str(OUT / "Fuse_TR5_D8.5mm_H8mm.step"))
print("wrote", OUT / "Fuse_TR5_D8.5mm_H8mm.step")
