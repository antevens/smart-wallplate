"""Write the PCBWay BOM and centroid files of an EU board into pcb/eu/fab/<board>/ from eu_parts.py.

Usage: python3 gen_fab_eu.py BOARD POS_CSV   (BOARD: eu_mains_board or eu_5v_board; POS_CSV from
`kicad-cli pcb export pos --format csv`). Parts in DNP are left out of the centroid and listed as not
fitted in the BOM; mounting holes (in_bom False) are left out of both.
"""
import csv
import sys
from pathlib import Path
import eu_parts as ep

FAB = Path(__file__).resolve().parents[1] / "fab"
PARTS = {ep.MAINS: ep.MAINS_PARTS, ep.LV: ep.LV_PARTS}
# S1 snaps into the printed cap's cup from the front before it can be soldered (D-36)
DNP = {ep.MAINS: {"S1": "Do not fit. Soldered by hand after the rocker is snapped into the printed cap"}}
NOTES = {
    ep.MAINS: {
        "PS1": "Safety-critical, do not substitute. Back (B) side over the routed relief slot, sit flush",
        "J1": "Safety-critical, do not substitute. Back (B) side, levers towards the board centre",
        "J2": "Safety-critical, do not substitute. Back (B) side, levers towards the board centre",
        "F1": "T1A 250 V per the Traco TMPS 03 datasheet's recommended input fuse - confirm before ordering",
        "RV1": "Safety-critical, do not substitute without review",
        "J3": "SMT header on the 5 V island (no pin tails under the PSU)",
    },
    ep.LV: {
        "P1": "SMT spring pin, front (F), peg into the 1.2 mm hole",
        "P2": "SMT spring pin, front (F), peg into the 1.2 mm hole",
        "J1": "THT socket on the back (B), mates the mains board's J3 (Samtec TSM): confirm 8.51 mm body (SOCKET)",
    },
}
SIDE = {"F": "Top", "B": "Bottom"}


def write_bom(board):
    path = FAB / board / f"{board}_{ep.REV}_bom.csv"
    dnp, notes = DNP.get(board, {}), NOTES.get(board, {})
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Item", "Designator", "Qty", "Manufacturer", "Manufacturer Part Number",
                    "Description/Value", "Package/Footprint", "Layer", "Datasheet", "Notes"])
        rows = [(ref, p) for ref, p in PARTS[board].items() if p.get("in_bom", True)]
        for i, (ref, p) in enumerate(rows, 1):
            w.writerow([i, ref, 0 if ref in dnp else 1, p["mfr"], p["mpn"], f'{p["value"]} - {p["desc"]}',
                        p["fp"], SIDE[p.get("side", "F")], p.get("ds", ""), dnp.get(ref, notes.get(ref, ""))])
    print("wrote", path)


def write_centroid(board, pos_csv):
    path = FAB / board / f"{board}_{ep.REV}_centroid.csv"
    skip = set(DNP.get(board, {})) | {ref for ref, p in PARTS[board].items() if not p.get("in_bom", True)}
    with open(pos_csv, newline="") as src, path.open("w", newline="") as dst:
        rows = csv.reader(src)
        w = csv.writer(dst)
        w.writerow(next(rows))
        for row in rows:
            if row and row[0] not in skip:
                w.writerow(row)
    print("wrote", path)


def main():
    board, pos_csv = sys.argv[1], sys.argv[2]
    (FAB / board).mkdir(parents=True, exist_ok=True)
    write_bom(board)
    write_centroid(board, pos_csv)


if __name__ == "__main__":
    main()
