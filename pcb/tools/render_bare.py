"""Render a board without components, so traces and pours are visible.

Writes to docs/renders/ (NAME defaults to the board file's stem):
  NAME_bare_front.png, NAME_bare_back.png, NAME_bare_iso.png
      3D renders of a copy of the board with every 3D model removed.
  NAME_copper_front.png, NAME_copper_back.png
      Flat plots of each copper layer with the outline (back seen from behind).

Run with the Python that ships pcbnew:
  python3 pcb/tools/render_bare.py [BOARD.kicad_pcb] [NAME] [--copper-only]
--copper-only skips the 3D renders; boards without copper on B.Cu get no back plot.
Needs kicad-cli and pdftoppm (poppler-utils) on PATH.
"""
import shutil
import sys
import subprocess
import tempfile
from pathlib import Path

import pcbnew

ROOT = Path(__file__).resolve().parents[2]
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
COPPER_ONLY = "--copper-only" in sys.argv
BOARD = Path(ARGS[0]).resolve() if ARGS else ROOT / "pcb" / "kicad" / "wiring_board.kicad_pcb"
NAME = ARGS[1] if len(ARGS) > 1 else BOARD.stem
OUT = ROOT / "docs" / "renders"
RENDER = ["kicad-cli", "pcb", "render", "--quality", "high", "--width", "1600", "--height", "1200"]
VIEWS = {"front": ["--side", "top"], "back": ["--side", "bottom"],
         "iso": ["--side", "top", "--rotate", "-40,0,30"]}
PLOTS = {"front": ("F.Cu", []), "back": ("B.Cu", ["--mirror"])}


def bare_copy(tmp):
    """Copy the board with all 3D models removed; returns the copy's path."""
    board = pcbnew.LoadBoard(str(BOARD))
    for fp in board.GetFootprints():
        fp.Models().clear()
    dst = tmp / BOARD.name
    pcbnew.SaveBoard(str(dst), board)
    pro = BOARD.with_suffix(".kicad_pro")
    if pro.exists():
        shutil.copy(pro, tmp / pro.name)
    return dst


def has_back_copper(board):
    """True if any track, pad or zone is on B.Cu (KiCad keeps two copper layers even when one is empty)."""
    b = pcbnew.B_Cu
    return (any(t.IsOnLayer(b) for t in board.GetTracks())
            or any(p.IsOnLayer(b) for fp in board.GetFootprints() for p in fp.Pads())
            or any(z.IsOnLayer(b) for z in board.Zones()))


def crop(png, pad=40):
    """Trim the plotted page down to the board."""
    from PIL import Image, ImageChops
    im = Image.open(png).convert("RGB")
    bbox = ImageChops.difference(im, Image.new("RGB", im.size, "white")).getbbox()
    if bbox:
        im.crop((max(bbox[0] - pad, 0), max(bbox[1] - pad, 0),
                 min(bbox[2] + pad, im.width), min(bbox[3] + pad, im.height))).save(png)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        bare = bare_copy(tmp)
        back = has_back_copper(pcbnew.LoadBoard(str(BOARD)))
        for name, args in ({} if COPPER_ONLY else VIEWS).items():
            out = OUT / f"{NAME}_bare_{name}.png"
            subprocess.run(RENDER + args + ["-o", str(out), str(bare)], check=True,
                           stdout=subprocess.DEVNULL)
            print("wrote", out)
        for name, (layer, extra) in PLOTS.items():
            if layer == "B.Cu" and not back:
                continue
            pdf = tmp / f"{name}.pdf"
            subprocess.run(["kicad-cli", "pcb", "export", "pdf", "--mode-single", "--layers",
                            f"{layer},Edge.Cuts", *extra, "-o", str(pdf), str(BOARD)],
                           check=True, stdout=subprocess.DEVNULL)
            stem = OUT / f"{NAME}_copper_{name}"
            subprocess.run(["pdftoppm", "-r", "300", "-png", "-singlefile", "-cropbox", str(pdf), str(stem)],
                           check=True)
            crop(stem.with_suffix(".png"))
            print("wrote", stem.with_suffix(".png"))


if __name__ == "__main__":
    main()
