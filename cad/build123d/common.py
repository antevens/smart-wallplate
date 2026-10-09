"""Small geometry helpers shared by the printed parts."""
from build123d import (Matrix, Pos, Rot, RectangleRounded, Sphere, Cylinder, Plane,
                       extrude, loft, Sketch, Vector)


def rr(w, h, r):
    """Rounded rectangle sketch; r is clamped so a stadium (r = w/2) still works."""
    return RectangleRounded(w, h, min(r, min(w, h) / 2 - 0.01))


def stadium(w, h):
    """BILRESA-like rounded-end oval (long axis = Y)."""
    return rr(w, h, w / 2)


def slab(sketch, z0, z1):
    """Extrude a 2D sketch between two absolute z levels."""
    return Pos(0, 0, z0) * extrude(sketch, z1 - z0)


def frame(w, h, wall, r, z0, z1, y=0.0):
    outer = rr(w + 2 * wall, h + 2 * wall, r + wall)
    inner = rr(w, h, max(r, 0.3))
    return Pos(0, y, 0) * (slab(outer, z0, z1) - slab(inner, z0 - 1, z1 + 1))


def taper(w, h, r, z0, z1, grow):
    """Rounded-rect frustum: (w,h,r) at z0, offset outward by `grow` at z1."""
    a = Plane.XY.offset(z0) * rr(w, h, r)
    b = Plane.XY.offset(z1) * rr(w + 2 * grow, h + 2 * grow, r + grow)
    return loft([a, b])


def ellipsoid(rx, ry, rz):
    """Poles on the Y axis so no mesh singularity lands on a cut surface."""
    return (Rot(90, 0, 0) * Sphere(1)).transform_geometry(Matrix([[rx, 0, 0, 0], [0, ry, 0, 0], [0, 0, rz, 0]]))


def rod(p0, p1, d):
    """Cylinder of diameter d from point p0 to p1."""
    p0, p1 = Vector(*p0), Vector(*p1)
    v = p1 - p0
    c = Cylinder(d / 2, v.length)
    pl = Plane(origin=(p0 + p1) * 0.5, z_dir=v)
    return pl * c


def board_hooks(cy, board_x, back_z, front_z, frame_in, hook, t=0.9, w=6.0, clr=0.2, relief=0.6):
    """Snap hooks at both short ends of a board held in a bay: a tab hangs from the face skin (front_z) at
    x = +-(board_x / 2 + clr), its lip `hook` deep catching the board's back face at back_z, a 45 deg lead-in
    below so the board snaps in from behind. Returns (hooks, reliefs): reliefs are cut from the bay frame
    behind each tab (frame_in = the frame's inner half width) so the tab can flex out past the lip."""
    from build123d import Box, Polyline, extrude, make_face
    hooks = reliefs = None
    xi = board_x / 2 + clr                              # tab's inner face
    zb = back_z - hook                                  # tab bottom
    pts = [(xi, front_z + 0.01), (xi + t, front_z + 0.01), (xi + t, zb), (xi - hook, back_z), (xi, back_z),
           (xi, front_z + 0.01)]
    prof = extrude(Plane.XZ * make_face(Polyline(*pts)), w / 2, both=True)   # profile x / z, along y
    for s in (1, -1):
        h = Pos(0, cy, 0) * (prof if s > 0 else prof.mirror(Plane.YZ))
        r = Pos(s * (frame_in + relief / 2 - 0.01), cy, (zb + front_z) / 2 - 0.5) * Box(relief + 0.02, w + 0.6,
                                                                                       front_z - zb - 1.0)
        hooks = h if hooks is None else hooks + h
        reliefs = r if reliefs is None else reliefs + r
    return hooks, reliefs

