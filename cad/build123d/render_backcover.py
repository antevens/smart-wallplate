"""Replacement back cover renders (D-35): xvfb-run python render_backcover.py -> docs/renders/bc_*.png"""
import sys
from pathlib import Path
from build123d import Pos
import render3d as r3
import backcover as bc

sys.path.insert(0, str(Path(__file__).resolve().parent / "eu"))
import params_eu as eu                                      # noqa: E402

r3.COL.update({"cover": "#e9e6df", "flex": "#d99a2b", "stiffener": "#2f7a46", "pads": "#e3c565",
               "fingers": "#c9a227", "contacts": "#c9a227", "regulator": "#2b2b2b", "pad_stiffener": "#2f7a46", "steel": "#6d7075", "floor": "#7d8a96", "floor_pads": "#e3c565",
               "floor_flex": "#d99a2b", "cap": "#8d949b", "front_half": "#fbfaf6"})


def placed(parts, z):
    return {k: Pos(0, 0, z) * v for k, v in parts.items()}


def eu_context():
    import cap_eu
    import trim_eu
    return {"cap": cap_eu.build(), "trim": trim_eu.build()}


def main():
    cov = bc.cover_parts(free=True)
    r3.shot("bc_inside", cov, [(70, -120, 140), (0, -6, 4), (0, 0, 1)], size=(1300, 1100), head=0.9)
    r3.shot("bc_back", cov, [(60, -90, -140), (4, -4, 0), (0, 0, 1)], size=(1300, 1100), head=0.9)
    # in the EU plate: floor insert on the cap in the pocket, cover and remote lifted above it
    flo = placed(bc.floor_insert(eu.POCKET_IN, eu.POCKET_IN[0] / 2 + eu.POCKET_WALL), eu.CAP_T)
    ctx = eu_context()
    r3.shot("bc_floor", {**ctx, **flo}, [(90, -130, 170), (8, -2, 0), (0, 1, 0)], size=(1300, 1100),
            hide=("trim",), head=0.9)
    lift = eu.SEAT_Z
    ex = {**ctx, **flo, **placed(bc.cover_parts(), lift + 25), "front_half": Pos(0, 0, lift + 50) * bc.remote_front()}
    r3.shot("bc_exploded", ex, [(230, -200, 130), (0, 0, 25), (0, 0, 1)], size=(1400, 1300), head=0.85,
            alpha={"trim": 0.2})


def finger_section():
    """2D sections through the +3V3 finger (x and y cuts): floor insert and its pad, finger at working
    height through its window, ledge, flex."""
    import subprocess
    from build123d import export_stl
    root = Path(__file__).resolve().parents[2]
    out = root / "build" / "backcover"
    out.mkdir(parents=True, exist_ok=True)
    fl = bc.floor_insert(eu.POCKET_IN, eu.POCKET_IN[0] / 2 + eu.POCKET_WALL, ())
    stl = {"cover": bc.cover(), "fingers": bc.fingers(), "flex": bc.flex(),
           "floor": Pos(0, 0, -bc.BC_FLOOR_T) * fl["floor"], "pad": Pos(0, 0, -bc.BC_FLOOR_T) * fl["floor_flex"]}
    cols = {"cover": "tab:blue", "fingers": "goldenrod", "flex": "tab:orange", "floor": "tab:gray", "pad": "tab:orange"}
    args = []
    for k, part in stl.items():
        export_stl(part, str(out / f"{k}.stl"), tolerance=0.01)
        args.append(f"{out / (k + '.stl')}:{cols[k]}")
    x, y = bc.BC_FINGERS[0]
    tool = [sys.executable, str(root / "cad" / "tools" / "sections.py"), str(r3.R / "bc_finger_section.png")]
    subprocess.run(tool + args + ["--title", "Back cover finger (D-35): cover (blue), S7081-42R at working height (gold), "
                                  "flex + floor tongue (orange), floor insert (grey)",
                                  "--cut", f"x={x}@{y - 6},{y + 6},-1.5,4", "--cut", f"y={y}@{x - 5},{x + 6},-1.5,4",
                                  "--dpi", "120"], check=True)
    print("wrote", r3.R / "bc_finger_section.png")
    # VBAT end finger: cover, contact block, stiffener, flex, S7081 at working height; the plate plane dashed
    end = {"cover": bc.cover(), "contacts": bc.end_fingers(), "flex": bc.flex(), "stiffener": bc.stiffener()}
    ecol = {"cover": "tab:blue", "contacts": "goldenrod", "flex": "tab:orange", "stiffener": "tab:green"}
    args = []
    for k, part in end.items():
        export_stl(part, str(out / f"end_{k}.stl"), tolerance=0.01)
        args.append(f"{out / ('end_' + k + '.stl')}:{ecol[k]}")
    xv, yc = bc.BC_VBAT_X * bc.BC_CELL_X, bc.copper_y()
    subprocess.run([sys.executable, str(root / "cad" / "tools" / "sections.py"), str(r3.R / "bc_contact_section.png")]
                   + args + ["--title", "Back cover VBAT contact (D-40): S7081-42R (gold) at working height, its dome on "
                             f"the plate plane y {bc.BC_CELL_END_Y:.2f}; flex (orange), stiffener (green), cover (blue)",
                             "--cut", f"x={xv}@{yc - 5},{yc + 7},-0.5,14",
                             "--cut", f"z={bc.BC_CELL_Z}@{xv - 7},{xv + 7},{yc - 5},{yc + 7}", "--dpi", "120"],
                   check=True)
    print("wrote", r3.R / "bc_contact_section.png")


if __name__ == "__main__":
    main()
    finger_section()
