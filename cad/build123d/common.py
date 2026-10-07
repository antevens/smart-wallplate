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
