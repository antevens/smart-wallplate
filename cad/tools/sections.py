"""Section renders of STL parts for review: python sections.py out.png part.stl[:color] ... --cut AXIS=VALUE ...

Each --cut makes one panel; all parts are sliced on that plane and filled.
"""
import sys
import numpy as np
import trimesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
from matplotlib.path import Path as MPath
from shapely.geometry import Polygon

AX = {"x": (0, (1, 2), ("y", "z")), "y": (1, (0, 2), ("x", "z")), "z": (2, (0, 1), ("x", "y"))}


def main(argv):
    out = argv[0]
    parts, cuts, title = [], [], ""
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == "--cut":
            cuts.append(argv[i + 1]); i += 2; continue
        if a == "--title":
            title = argv[i + 1]; i += 2; continue
        path, _, col = a.partition(":")
        parts.append((trimesh.load(path), col or "tab:blue"))
        i += 1
    n = len(cuts)
    cols = min(n, 3)
    rows = (n + cols - 1) // cols
    fig, axs = plt.subplots(rows, cols, figsize=(6.5 * cols, 6.5 * rows), squeeze=False)
    for k, c in enumerate(cuts):
        ax = axs[k // cols][k % cols]
        axis, val = c.split("=")
        ai, (u, v), (lu, lv) = AX[axis]
        normal = np.zeros(3); normal[ai] = 1
        origin = np.zeros(3); origin[ai] = float(val)
        for mesh, col in parts:
            sec = mesh.section(plane_origin=origin, plane_normal=normal)
            if sec is None:
                continue
            region = None
            for loop in sec.discrete:
                if len(loop) < 4:
                    continue
                ring = Polygon(loop[:, [u, v]]).buffer(0)
                region = ring if region is None else region.symmetric_difference(ring)
            if region is None or region.is_empty:
                continue
            for poly in getattr(region, "geoms", [region]):
                if poly.geom_type != "Polygon":
                    continue
                verts, codes = [], []
                for r in [poly.exterior] + list(poly.interiors):
                    xy = np.asarray(r.coords)
                    verts += xy.tolist(); codes += [MPath.MOVETO] + [MPath.LINETO] * (len(xy) - 2) + [MPath.CLOSEPOLY]
                ax.add_patch(PathPatch(MPath(verts, codes), fc=col, ec="k", lw=0.4, alpha=0.75))
        ax.set_title(f"{axis} = {val}")
        ax.set_xlabel(lu); ax.set_ylabel(lv)
        ax.set_aspect("equal"); ax.autoscale_view(); ax.grid(alpha=0.3)
        if axis != "z":
            ax.axhline(0, color="r", lw=0.8, ls="--")  # wall surface
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(out, dpi=80)


if __name__ == "__main__":
    main(sys.argv[1:])
