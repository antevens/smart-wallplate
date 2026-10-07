"""IKEA BILRESA scroll-wheel remote, visual/clearance model (not a vendor model).

Stadium outline, rounded back edge, wheel disc with its gap ring, three LED dots
and the side parting line. All sizes are MEASURE placeholders in params.py.
build() returns it seated in the pocket (back on SEAT_Z).
"""
from math import cos, sin, pi
from build123d import Axis, Cylinder, Plane, Pos, fillet, loft
from params import *
from common import stadium, slab

N_SECT = 8  # loft sections along the curved back


def back():
    """Flat stadium pad on the back, curving out to the full outline along a
    quarter ellipse (B_BACK_RUN across, B_BACK_RISE up)."""
    secs = []
    for i in range(N_SECT + 1):
        t = (pi / 2) * i / N_SECT
        inset = B_BACK_RUN * (1 - sin(t))
        z = B_BACK_RISE * (1 - cos(t))
        secs.append(Plane.XY.offset(z) * stadium(B_W - 2 * inset, B_H - 2 * inset))
    return loft(secs, ruled=False)


def body():
    b = back() + slab(stadium(B_W, B_H), B_BACK_RISE - 0.01, B_D)
    b = fillet(b.edges().group_by(Axis.Z)[-1], B_FRONT_R)
    return b


def build(lift=0.0):
    b = body()
    # wheel gap ring on the front face
    ring = Pos(0, B_WHEEL_Y, B_D - 0.5) * (Cylinder(B_WHEEL_D / 2 + B_WHEEL_GAP, 1.2)
                                           - Cylinder(B_WHEEL_D / 2, 1.4))
    b -= ring
    for i in (-1, 0, 1):
        b -= Pos(i * B_LED_PITCH, B_LED_Y, B_D) * Cylinder(0.6, 0.8)
    # parting line around the side
    seam_outer = slab(stadium(B_W + 2, B_H + 2), B_SEAM_Z - 0.2, B_SEAM_Z + 0.2)
    seam_inner = slab(stadium(B_W - 0.6, B_H - 0.6), B_SEAM_Z - 0.3, B_SEAM_Z + 0.3)
    b -= seam_outer - seam_inner
    return Pos(0, 0, SEAT_Z + lift) * b


if __name__ == "__main__":
    r = build()
    bb = r.bounding_box()
    print(f"bilresa {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f}, valid={r.is_valid}, vol {r.volume/1000:.1f} cm3")
