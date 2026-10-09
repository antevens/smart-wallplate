"""Print-orientation helpers and mesh export for every printable part.

Run: python export.py -> ../../build/print/<part>.stl (oriented, on the bed, centred)
"""
from pathlib import Path
import trimesh
from build123d import Rot, Pos, export_stl, export_step

OUT = Path(__file__).resolve().parents[2] / "build"

PRINT_ORIENT = {
    "insert": lambda p: p,                          # floor-down: as modelled
    "trim": lambda p: Rot(180, 0, 0) * p,           # face-down
    "coupon_pocket_well": lambda p: p,
    "coupon_msr": lambda p: Rot(180, 0, 0) * p,
    "coupon_rocker": lambda p: p,
    "post": lambda p: Rot(90, 0, 0) * p,            # lying on its flat (flat faces -y -> down)
    "back_cover": lambda p: p,                      # back down: as modelled (D-35)
    "floor_na": lambda p: p,                        # flat, recess up: as modelled (D-41)
    "cap_eu": lambda p: Rot(180, 0, 0) * p,         # face-down (barrier, D-30)
    "trim_eu": lambda p: Rot(180, 0, 0) * p,        # face-down
    "floor_eu": lambda p: p,                        # flat, recess up
}


def on_bed(part):
    bb = part.bounding_box()
    return Pos(-(bb.min.X + bb.max.X) / 2, -(bb.min.Y + bb.max.Y) / 2, -bb.min.Z) * part


def mesh_of(part, tol=0.02):
    import tempfile, os
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "m.stl")
        export_stl(part, f, tolerance=tol, angular_tolerance=0.1)
        m = trimesh.load(f)
    m.merge_vertices()
    return m


def parts():
    import sys
    import insert, trim, coupons, post, backcover, floor_na
    sys.path.insert(0, str(Path(__file__).resolve().parent / "eu"))
    import cap_eu, trim_eu, floor_eu
    ins, tr = insert.build(), trim.build()
    return {"insert": ins, "trim": tr, "post": post.build(),
            "coupon_pocket_well": coupons.pocket_well(ins),
            "coupon_msr": coupons.msr(tr),
            "coupon_rocker": coupons.rocker_ladder(),
            "back_cover": backcover.cover(), "floor_na": floor_na.parts()["floor"],
            "cap_eu": cap_eu.build(), "trim_eu": trim_eu.build(), "floor_eu": floor_eu.parts()["floor"]}


def main():
    pdir = OUT / "print"
    pdir.mkdir(parents=True, exist_ok=True)
    for name, p in parts().items():
        if name in ("insert", "trim"):  # model frame, for the assembly/renders
            export_step(p, str(OUT / f"{name}.step"))
            export_stl(p, str(OUT / f"{name}.stl"), tolerance=0.02, angular_tolerance=0.1)
        q = on_bed(PRINT_ORIENT[name](p))
        export_stl(q, str(pdir / f"{name}.stl"), tolerance=0.02, angular_tolerance=0.1)
        m = trimesh.load(pdir / f"{name}.stl")
        print(f"{name:20s} {m.extents.round(1)} mm  watertight={m.is_watertight}  -> build/print/{name}.stl")
        if not m.is_watertight or max(m.extents[:2]) > 250 or m.extents[2] > 250:
            raise SystemExit(f"{name}: mesh not watertight or larger than the CC2 bed (256 x 256 x 256)")


if __name__ == "__main__":
    main()
