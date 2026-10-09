"""EU variant renders (D-30): xvfb-run python render_eu.py -> docs/renders/eu_*.png"""
from pathlib import Path
from build123d import Box, Cylinder, Pos
from params_eu import *
import render3d as r3
import cap_eu
import trim_eu
import boards_eu
import sensor_eu
import floor_eu

r3.COL.update({"cap": "#8d949b", "switch": "#b23a32", "magnet": "#4a4a4a", "box": "#d9822b", "pins": "#e3c565",
               "pads": "#e3c565", "floor": "#7d8a96", "floor_flex": "#d99a2b", "floor_pads": "#e3c565", "wago": "#9aa0a6", "psu": "#2b2b2b",
               "front": "#c8a03a", "mains_board": "#2f7a46", "mains_front": "#c8a03a", "header": "#2b2b2b",
               "socket": "#2b2b2b"})


def box_shell():
    """The flush box (Ø60 inside, 1.5 mm wall), for context."""
    outer = Pos(0, 0, -BOX_D / 2 - 0.75) * Cylinder(BOX_R + 1.5, BOX_D + 1.5)
    return outer - Pos(0, 0, -BOX_D / 2 + 0.01) * Cylinder(BOX_R, BOX_D)


def parts(lift=0.0):
    b = boards_eu.parts()
    return {"trim": trim_eu.build(), "cap": cap_eu.build(), "remote": boards_eu.remote(lift),
            "msr": Pos(0, MSR_Y, PT - RADAR_WALL - MSR[2] / 2) * Box(*MSR),
            "switch": boards_eu.switch_model(), "board": b["board"], "psu": b["psu"], "wago": b["wago"], "magnet": b["magnet"], "front": b["front"],
            "mains_board": b["mains_board"], "mains_front": b["mains_front"], "header": b["header"], "socket": b["socket"],
            "box": box_shell(), **sensor_eu.parts(), **floor_eu.parts()}


def main():
    contact_section()
    ps = parts()
    r3.shot("eu_front", ps, [(130, -170, 260), (0, 8, 0), (0, 1, 0)], hide=("box",))
    r3.shot("eu_remote_out", parts(lift=45), [(170, -190, 300), (0, 8, 15), (0, 1, 0)], hide=("box",))
    keep = Pos(-100, 0, 0) * Box(200, 400, 400)          # half left of the x = 0 plane: cup, button, board, PSU
    cut = {k: v & keep for k, v in ps.items()}
    cut = {k: v for k, v in cut.items() if v is not None and v.volume > 1e-6}
    r3.shot("eu_section", cut, [(230, 40, 60), (0, 5, -8), (0, 0, 1)])
    r3.shot("eu_back", ps, [(140, -120, -230), (0, 0, -10), (0, 1, 0)], hide=("trim", "msr", "box"), head=1.0)
    off = {"remote": 70, "trim": 40, "msr": 40, "flex": 40, "plug": 40, "mic": 40, "sht45": 40, "pads": 40,
           "floor": 20, "floor_flex": 20, "floor_pads": 20, "cap": 0, "magnet": -8,
           "board": -18, "front": -18, "pins": -18, "socket": -18, "switch": -30,
           "mains_board": -45, "mains_front": -45, "header": -45, "psu": -45, "wago": -45}
    ex = {k: Pos(0, 0, off[k]) * v for k, v in ps.items() if k in off}
    r3.shot("eu_exploded", ex, [(300, -240, 120), (0, 0, -5), (0, 1, 0)], size=(1400, 1300), head=0.8)
    # sensor flex, mic, SHT45 and the spring pins (trim and remote hidden)
    r3.shot("eu_flex", ps, [(170, -150, 230), (8, 8, 5), (0, 1, 0)], size=(1400, 1300),
            hide=("trim", "remote", "board", "psu", "wago", "front", "switch", "magnet", "box"), head=0.9)
    # face plate lifted off (trim see-through) with everything attached to it; the cap side stays:
    # the 5 V board's spring pins on the flex's pads are the only electrical interface (R9)
    face = ("trim", "msr", "flex", "plug", "sht45", "pads", "mic", "floor", "floor_flex", "floor_pads")
    sep = {k: (Pos(0, 0, 35) * v if k in face else v) for k, v in ps.items()}
    r3.shot("eu_separation", sep, [(220, -150, 100), (12, 0, 5), (0, 0, 1)], size=(1400, 1200),
            hide=("remote", "box"), head=0.9, alpha={"trim": 0.18, "cap": 0.6})
    # power contact, cut through the spring pins' centre line: 5 V board, pins through the cap's holes,
    # the flex's pads on the pins, the trim's rib backing the flex
    keep = ("cap", "flex", "pads", "pins", "board", "front", "trim")
    cut_x = PINS[0][0]
    cutter = Pos(cut_x - 100, 0, 0) * Box(200, 400, 400)
    cps = {k: v & cutter for k, v in ps.items() if k in keep}
    cps = {k: v for k, v in cps.items() if v is not None and v.volume > 1e-6}
    r3.shot("eu_contact", cps, [(cut_x + 55, -6.8, 12), (cut_x - 2, -6.8, -1), (0, 0, 1)], size=(1200, 900),
            head=1.0)
    # into the box from behind: mains board with the WAGO blocks and the PSU, rocker, 5 V board, bosses
    r3.shot("eu_box", ps, [(90, -110, -170), (0, -2, -8), (0, 1, 0)], size=(1300, 1100),
            hide=("trim", "remote", "msr", "flex", "plug", "mic", "sht45", "pads", "box", "floor", "floor_flex",
                  "floor_pads"), head=1.0)


def contact_section():
    """2D section through the spring pins (x = pin centre line) and across them (y = +5 V pin)."""
    import subprocess
    import sys
    from build123d import export_stl
    root = Path(__file__).resolve().parents[3]
    out = root / "build" / "eu"
    out.mkdir(parents=True, exist_ok=True)
    b = boards_eu.parts()
    sens = sensor_eu.parts()
    stl = {"cap": cap_eu.build(), "trim": trim_eu.build(), "board": b["board"] + b["front"], "pins": b["pins"],
           "flex": sens["flex"] + sens["pads"]}
    cols = {"cap": "tab:red", "trim": "tab:blue", "board": "tab:green", "pins": "goldenrod", "flex": "tab:orange"}
    args = []
    for k, part in stl.items():
        export_stl(part, str(out / f"{k}.stl"), tolerance=0.01)
        args.append(f"{out / (k + '.stl')}:{cols[k]}")
    x, y = PINS[0]
    tool = [sys.executable, str(root / "cad" / "tools" / "sections.py"), str(r3.R / "eu_contact_section.png")]
    subprocess.run(tool + args + ["--title", "EU power contact (R9): 5 V board + spring pins (gold), cap (red, V-0), "
                                  "flex + pads (orange), trim rib (blue)",
                                  "--cut", f"x={x}@-14,1,-8,22", "--cut", f"y={y}@20,34,-8,22", "--dpi", "110"],
                   check=True)
    print("wrote", r3.R / "eu_contact_section.png")


if __name__ == "__main__":
    main()
