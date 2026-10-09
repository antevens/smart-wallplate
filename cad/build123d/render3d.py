"""Shaded 3D renders for the docs: xvfb-run python render3d.py -> docs/renders/v0.3_*.png"""
import tempfile
from pathlib import Path
import pyvista as pv
from build123d import Box, Pos, export_stl
from params import *
import assembly
import bilresa
import insert
import post
import sensor_flex
import jumper
import trim

R = Path(__file__).resolve().parents[2] / "docs" / "renders"
COL = {"trim": "#f2f1ee", "insert": "#8d949b", "remote": "#fbfaf6", "rocker": "#b23a32",
       "board": "#1f6b3a", "posts": "#d9822b", "flex": "#c98a1c", "plug": "#222222", "sht45": "#5b2a86",
       "fingers": "#e3c565", "target": "#2f7a46", "jumper": "#d99a2b", "irm": "#2b2b2b", "wago": "#c9ccd1", "small": "#c8a03a",
       "msr": "#3a3a3a", "mic": "#2c5d8f", "floor": "#7d8a96", "floor_flex": "#d99a2b", "floor_pads": "#e3c565",
       "cover": "#e9e6df", "stiffener": "#2f7a46", "pads": "#e3c565", "contacts": "#c9a227", "regulator": "#2b2b2b",
       "steel": "#6d7075", "cflex": "#d99a2b", "front_half": "#fbfaf6", "pad_stiffener": "#2f7a46"}
BOARD_KEYS = ("board", "rocker", "irm", "wago", "small")


def board_parts():
    """Split the wiring board into coloured groups. From the KiCad STEP when present (it includes
    the rocker model), else the parameter envelopes."""
    from build123d import Compound
    b = assembly.wiring_board()
    if not assembly.WB_STEP.exists():
        sw = Compound([Pos(0, SW_Y, WELL_FLOOR_Z + SW_ROCKER_H / 2) * Box(SW_BEZEL[0], SW_BEZEL[1], SW_ROCKER_H),
                       Pos(0, SW_Y, WELL_FLOOR_Z - SW_BODY[2] / 2) * Box(*SW_BODY)])
        return {"board": b, "rocker": sw}
    groups = {k: [] for k in ("board", "rocker", "irm", "wago", "small")}
    for sol in b.solids():                                  # by where each solid sits (vendor models are many solids)
        bb = sol.bounding_box()
        c = bb.center()
        if bb.size.Z < 2.0 and bb.size.X > WB[0] - 1:
            groups["board"].append(sol)
        elif c.Z > WB_FRONT_Z and abs(c.X) < SW_BEZEL[0] / 2 + 1 and abs(c.Y - SW_Y) < SW_BEZEL[1] / 2 + 1:
            groups["rocker"].append(sol)
        elif c.Z < WB_BACK_Z and abs(c.X - IRM_C[0]) < IRM[0] / 2 + 1 and abs(c.Y - WB_Y - IRM_C[1]) < IRM[1] / 2 + 1:
            groups["irm"].append(sol)
        elif c.Z < WB_BACK_Z and abs(c.X - WAGO_X) < WAGO6[0] / 2 + 1 and abs(c.Y - WB_Y - WAGO_Y) < 12:
            groups["wago"].append(sol)
        else:
            groups["small"].append(sol)
    return {k: Compound(v) for k, v in groups.items() if v}


def mesh(part, d, name):
    f = Path(d) / f"{name}.stl"
    export_stl(part, str(f), tolerance=0.02, angular_tolerance=0.1)
    return pv.read(str(f))


def parts(lift=0.0, cut=False):
    a = assembly
    ps = {"trim": trim.build(), "insert": insert.build(), "remote": bilresa.build(lift),
          "msr": Pos(0, MSR_Y, PT - RADAR_WALL - MSR[2] / 2) * Box(*MSR), "posts": post.placed(),
          **sensor_flex.parts(), **jumper.build()}
    ps.update(board_parts())
    if cut:  # keep x <= 0 for a half-section (board parts are clipped as meshes in shot())
        keep = Pos(-100, 0, 0) * Box(200, 400, 400)
        ps = {k: (v if k in BOARD_KEYS else v & keep) for k, v in ps.items()}
        ps = {k: v for k, v in ps.items() if k in BOARD_KEYS or (v is not None and v.volume > 1e-6)}
    return ps, cut


def battery_free(lift_cover=0.0, lift_remote=0.0):
    """NA battery-free remote (D-41): jumper with its tongue, floor insert, replacement back cover and the
    remote's front half on it (lifted for exploded views)."""
    import backcover
    import floor_na
    seat = SEAT_Z + BC_FLOOR_T
    ps = {"jumper": jumper.build(battery_free=True)["jumper"], **floor_na.parts()}
    cov = backcover.cover_parts()
    ps.update({("cflex" if k == "flex" else k): Pos(0, 0, seat + lift_cover) * v for k, v in cov.items()})
    ps["front_half"] = Pos(0, 0, seat + lift_remote) * backcover.remote_front()
    return ps


def shot(name, ps, cam, size=(1400, 1100), hide=(), head=0.55, alpha=None):
    ps, cut = ps if isinstance(ps, tuple) else (ps, False)
    with tempfile.TemporaryDirectory() as d:
        p = pv.Plotter(off_screen=True, window_size=size, lighting="none")
        p.set_background("white")
        p.add_light(pv.Light(light_type="headlight", intensity=head))
        p.add_light(pv.Light(position=(200, 300, 400), focal_point=(0, 0, 0), intensity=0.6, light_type="scene light"))
        p.add_light(pv.Light(position=(-300, -100, 200), focal_point=(0, 0, 0), intensity=0.25, light_type="scene light"))
        for k, v in ps.items():
            if k in hide or v is None:
                continue
            m = mesh(v, d, k)
            if cut and k in BOARD_KEYS:
                m = m.clip(normal="x", origin=(0, 0, 0))
            p.add_mesh(m, color=COL[k], smooth_shading=True, split_sharp_edges=True,
                       specular=0.25, specular_power=20, opacity=(alpha or {}).get(k, 1.0))
        p.camera_position = cam
        p.enable_anti_aliasing("ssaa")
        p.screenshot(str(R / f"{name}.png"))
        p.close()
    print("wrote", R / f"{name}.png")


def main():
    R.mkdir(parents=True, exist_ok=True)
    shot("v0.3_front", parts(), [(150, -170, 260), (0, 0, 0), (0, 1, 0)], hide=BOARD_KEYS)
    shot("v0.3_remote_out", parts(lift=45), [(210, -200, 330), (0, 0, 15), (0, 1, 0)], hide=BOARD_KEYS)
    shot("v0.3_section", parts(cut=True), [(290, 70, 150), (0, 0, -5), (0, 1, 0)])
    shot("v0.3_back", parts(), [(130, -120, -230), (0, -5, -10), (0, 1, 0)], hide=("trim", "msr"), head=1.0)
    # exploded: remote, trim, insert (with rocker), wiring board pulled apart along z
    ps, _ = parts()
    off = {"remote": 95, "trim": 55, "msr": 55, "flex": 55, "plug": 55, "sht45": 55, "fingers": 55, "mic": 55,
           "target": 0,
           "jumper": 0,
           "insert": 0, "posts": -25,
           **{k: -55 for k in BOARD_KEYS}}
    exploded = {k: Pos(0, 0, off[k]) * v for k, v in ps.items() if k in off}
    shot("v0.3_exploded", exploded, [(330, -260, 120), (0, 0, 15), (0, 1, 0)], size=(1400, 1300), head=0.8)
    # face plate lifted off (trim see-through) with everything attached to it; the insert side
    # stays: the spring fingers on the target board are the only electrical interface (R9)
    face = ("trim", "msr", "flex", "plug", "sht45", "fingers", "mic")
    sep = {k: (Pos(0, 0, 35) * v if k in face else v) for k, v in ps.items()}
    shot("v0.3_separation", sep, [(230, -150, 110), (15, 5, 5), (0, 0, 1)], size=(1400, 1200),
         hide=("remote", "posts"), head=0.9, alpha={"trim": 0.18, "insert": 0.55})
    # sensor flex route (trim and remote hidden): MSR-2 end, right channel, SHT45 tail
    shot("v0.3_flex", parts(), [(170, -150, 230), (8, 0, 5), (0, 1, 0)], size=(1400, 1300),
         hide=("trim", "remote", "posts") + BOARD_KEYS, head=0.9)
    # power contact: spring fingers on the flex over the target board on the insert shelf
    keep = ("insert", "flex", "fingers", "target", "plug")
    shot("v0.3_contact", parts(), [(75, -10, 45), (35.5, 20, 8), (0, 0, 1)], size=(1200, 900),
         hide=tuple(k for k in list(COL) if k not in keep), head=1.0)
    # 5 V power path: insert and trim cut at the pass-through axis, seen from the right
    ps, _ = parts()
    keep = Pos(PASS_X - 150, 0, 0) * Box(300, 400, 400)
    ps = {k: (v & keep if k in ("insert", "trim") else v) for k, v in ps.items()}
    shot("v0.3_power", ps, [(230, -40, 30), (22, 5, -8), (0, 1, 0)], size=(1400, 1100),
         hide=("remote", "trim", "posts", "msr"), head=1.0)
    # battery-free remote (D-41): floor insert, tongue from the jumper's pad end, cover and remote lifted off
    ps, _ = parts()
    ps.pop("remote")
    ps["jumper"] = None
    bf = battery_free(lift_cover=30, lift_remote=55)
    ps = {k: v for k, v in ps.items() if v is not None}
    shot("v0.3_battery_free", {**ps, **bf}, [(260, -230, 210), (5, 0, 10), (0, 1, 0)], size=(1400, 1300),
         hide=("trim", "msr", "posts") + BOARD_KEYS, head=0.85)
    # tongue path: insert, floor, cover and remote cut on the tongue's plane, seen from +y
    ps, _ = parts()
    ps.pop("remote")
    ps.pop("jumper")
    bf = battery_free()
    keep = Pos(0, BC_NA_TONGUE_Y - 100, 0) * Box(300, 200, 300)
    cutp = {k: (v & keep) for k, v in {**ps, **bf}.items() if k not in BOARD_KEYS and k != "jumper"}
    cutp = {k: v for k, v in cutp.items() if v is not None and v.volume > 1e-6}
    cutp["jumper"] = jumper.tongue()
    shot("v0.3_tongue", cutp, [(30, 200, 40), (24, BC_NA_TONGUE_Y, 3), (0, 0, 1)], size=(1400, 1000),
         hide=("msr", "posts"), head=1.0, alpha={"trim": 0.35})
    shot("bilresa_model", {"remote": bilresa.build()}, [(70, -90, 120), (0, 0, 0), (0, 1, 0)], size=(900, 900))
    shot("bilresa_back", {"remote": bilresa.build()}, [(95, -60, -110), (0, 0, SEAT_Z + B_D / 2), (0, 1, 0)], size=(900, 900), head=1.0)


if __name__ == "__main__":
    main()
