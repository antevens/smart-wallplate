"""Write pcb/fab/psu_carrier_v0.2_bom.csv in PCBWay's assembly BOM layout."""
import csv
from pathlib import Path
from parts import PARTS, REV

OUT = Path(__file__).resolve().parents[1] / "fab"
OUT.mkdir(exist_ok=True)
notes = {
    "F1": "Rating T1A is the designer's choice (Mean Well gives none) - confirm before ordering",
    "PS1": "Safety-critical, do not substitute. Sit flush on the board",
    "J1": "Mains in. Wire entry must face the board's top edge (Yup+), see assembly PDF",
    "RV1": "Safety-critical, do not substitute without review",
    "C1": "Polarised: + to pad 1 (square)",
    "J2": "",
}
path = OUT / f"psu_carrier_{REV}_bom.csv"
with path.open("w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Item", "Designator", "Qty", "Manufacturer", "Manufacturer Part Number",
                "Description/Value", "Package/Footprint", "Type", "Datasheet", "Notes"])
    for i, (ref, p) in enumerate(PARTS.items(), 1):
        w.writerow([i, ref, 1, p["mfr"], p["mpn"], f'{p["value"]} - {p["desc"]}', p["fp"], "THT",
                    p["ds"], notes.get(ref, "")])
print("wrote", path)
