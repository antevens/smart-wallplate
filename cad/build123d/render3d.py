"""Shaded 3D renders for the docs: xvfb-run python render3d.py -> docs/renders/v0.2_*.png"""
import tempfile
from pathlib import Path
import pyvista as pv
from build123d import Box, Pos, export_stl
from params import *
import assembly
import bilresa
import insert
import trim

R = Path(__file__).resolve().parents[2] / "docs" / "renders"
COL = {"trim": "#f2f1ee", "insert": "#8d949b", "remote": "#fbfaf6", "rocker": "#b23a32",
       "psu": "#1f6b3a", "msr": "#3a3a3a"}


def mesh(part, d, name):
    f = Path(d) / f"{name}.stl"
    export_stl(part, str(f), tolerance=0.02, angular_tolerance=0.1)
    return pv.read(str(f))


def parts(lift=0.0, cut=False):
    a = assembly
    sw = a.Compound([Pos(0, SW_Y, WELL_FLOOR_Z + SW_ROCKER_H / 2) * Box(SW_BEZEL[0], SW_BEZEL[1], SW_ROCKER_H),
                     Pos(0, SW_Y, PANEL_BOT_Z - SW_BODY[2] / 2) * Box(*SW_BODY)])
    ps = {"trim": trim.build(), "insert": insert.build(), "remote": bilresa.build(lift),
          "rocker": sw, "psu": a.psu(),
          "msr": Pos(0, MSR_Y, PT - RADAR_WALL - MSR[2] / 2) * Box(*MSR)}
    if cut:  # keep x <= 0 for a half-section (the imported board is clipped as a mesh in shot())
        keep = Pos(-100, 0, 0) * Box(200, 400, 400)
        ps = {k: (v if k == "psu" else v & keep) for k, v in ps.items()}
    return ps, cut


def shot(name, ps, cam, size=(1400, 1100), hide=(), head=0.55):
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
            if cut and k == "psu":
                m = m.clip(normal="x", origin=(0, 0, 0))
            p.add_mesh(m, color=COL[k], smooth_shading=True, split_sharp_edges=True,
                       specular=0.25, specular_power=20)
        p.camera_position = cam
        p.enable_anti_aliasing("ssaa")
        p.screenshot(str(R / f"{name}.png"))
        p.close()
    print("wrote", R / f"{name}.png")


def main():
    R.mkdir(parents=True, exist_ok=True)
    shot("v0.2_front", parts(), [(150, -170, 260), (0, 0, 0), (0, 1, 0)], hide=("psu", "rocker"))
    shot("v0.2_remote_out", parts(lift=45), [(210, -200, 330), (0, 0, 15), (0, 1, 0)], hide=("psu",))
    shot("v0.2_section", parts(cut=True), [(290, 70, 150), (0, 0, -5), (0, 1, 0)])
    shot("v0.2_back", parts(), [(130, -120, -230), (0, -5, -10), (0, 1, 0)], hide=("trim", "msr"), head=1.0)
    shot("bilresa_model", {"remote": bilresa.build()}, [(70, -90, 120), (0, 0, 0), (0, 1, 0)], size=(900, 900))
    shot("bilresa_back", {"remote": bilresa.build()}, [(95, -60, -110), (0, 0, SEAT_Z + B_D / 2), (0, 1, 0)], size=(900, 900), head=1.0)


if __name__ == "__main__":
    main()
