"""3D models for the footprints of all boards (<project>/kicad/3d/<name>.step).

A vendor STEP placed in scratch/3d/ (git-ignored: vendor terms) is used when present, moved into
footprint coordinates by its entry's transform; otherwise a datasheet envelope is built.
Footprints reference ${KIPRJMOD}/3d/<name>.step with no transform of their own.

Run with the CAD venv: .venv/bin/python pcb/tools/gen_3d.py
Model coordinates: origin = footprint origin, X as the footprint, Y up (= -footprint y),
+Z away from the board on the mounting side.
"""
import sys
from pathlib import Path
from build123d import Box, Cylinder, Pos, Rot, export_step, import_step

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "cad" / "build123d"))
from params import FINGER, FINGER_FREE, MIC                    # noqa: E402

VENDOR = ROOT / "scratch" / "3d"
PROJECTS = {"na": ROOT / "pcb" / "kicad" / "3d", "eu": ROOT / "pcb" / "eu" / "kicad" / "3d",
            "sensor": ROOT / "pcb" / "sensor" / "kicad" / "3d"}


def rocker():
    """Marquardt 1802.2504 (drawing rev g): body 18.6 x 22 from the PCB seat to the panel face (16.2),
    flange 21 x 24 x 2 on the panel face, rocker 5.3 above it; turned 90 deg (long side along x)."""
    r = Pos(0, 0, 16.2 / 2) * Box(22, 18.6, 16.2)
    r += Pos(0, 0, 16.2 + 1) * Box(24, 21, 2)
    return r + Pos(0, 0, 18.2 + 1.65) * Box(19, 16, 3.3)


def rocker_1802_2504(housing):
    """Marquardt 1802.1108 housing (flange, rocker, body; same 1802 frame) above its body bottom, on the
    1802.2504 underside (drawing rev g): body to 11.7 below the panel face, a 2.8 mm stem round each pin to
    the PCB seat (16.2), pins 0.8 mm, 4.3 below the seat. Panel face at Z 16.2, origin = body centre."""
    seat, body_bot, own_bot, pin_l = 16.2, 11.7, 10.5, 4.3
    r = housing & Pos(0, 0, 50 + seat - own_bot) * Box(100, 100, 100)
    r += Pos(0, 0, seat - (own_bot + body_bot) / 2) * Box(22, 18.6, body_bot - own_bot)
    for x in (-5.1, 5.1):
        for y in (0.0, 7.0):
            r += Pos(x, y, (seat - body_bot) / 2) * Box(2.8, 2.8, seat - body_bot)
            r += Pos(x, y, (seat - body_bot - pin_l) / 2) * Box(0.8, 0.8, seat - body_bot + pin_l)
    return r


def wago6():
    """WAGO 2604-1106 (datasheet, WAGO 3D model): 32.4 wide, 16.1 deep at the board from 5.0 before the
    first pin row (entry face) to 11.1 behind it, 16.7 high."""
    return Pos(0, -(11.1 - 5.0) / 2, 16.7 / 2) * Box(32.4, 16.1, 16.7)


def wago2_vertical():
    """WAGO 2604-3102 (datasheet, WAGO 3D model): 12.4 x 16.7, 21.3 above the board; body centred on the
    footprint origin, 0.1 towards pole 1."""
    return Pos(-0.1, 0, 21.3 / 2) * Box(12.4, 16.7, 21.3)


def fuse_umt250():
    """Schurter UMT 250 (datasheet): body 10.1 x 3.1 x 3.3, along x between the pads."""
    return Pos(0, 0, 3.3 / 2) * Box(10.1, 3.1, 3.3)


def mov_cu4032():
    """TDK SIOV CU4032 (datasheet): body 10.2 x 8.0 x 4.5, along x between the pads."""
    return Pos(0, 0, 4.5 / 2) * Box(10.2, 8.0, 4.5)


def tmps03():
    """Traco TMPS 03 (datasheet rev. 2026-07-01): 25.4 x 25.4 x 16.3 body, pins 0.6 x 5.08."""
    b = Pos(0, 0, 16.3 / 2) * Box(25.4, 25.4, 16.3)
    for x, y in ((10.16, 10.16), (5.08, 10.16), (-10.16, -10.16), (0.0, -10.16), (10.16, -10.16)):
        b += Pos(x, y, -5.08 / 2) * Cylinder(0.3, 5.08)
    return b


def p70():
    """Harwin P70-2200045 (drawing DRG-02624): flange 2.0 x 1.0, barrel 1.54, plunger 0.9, free 8.2."""
    p = Pos(0, 0, 0.5) * Cylinder(1.0, 1.0)
    p += Pos(0, 0, 1.0 + (6.7 - 1.0) / 2) * Cylinder(1.54 / 2, 6.7 - 1.0)
    return p + Pos(0, 0, 6.7 + 1.5 / 2) * Cylinder(0.45, 1.5)


def s7081():
    """Harwin S7081-42R (drawing iss. 7) at its free height: foot, arm, contact dome; long axis x."""
    import backcover
    return Rot(0, 0, 90) * Rot(180, 0, 0) * backcover.finger(FINGER_FREE)


def dmm4026():
    """PUI DMM-4026-B-I2S-R (datasheet rev A): body 3 x 4 x 1 (port on the board side)."""
    return Pos(0, 0, MIC[2] / 2) * Box(MIC[0], MIC[1], MIC[2])


def sht4x():
    """Sensirion SHT4x DFN-4 (datasheet): 1.5 x 1.5 x 0.5."""
    return Pos(0, 0, 0.25) * Box(1.5, 1.5, 0.5)


# name: (projects, envelope, vendor file in scratch/3d or None, vendor transform: Rot x/y/z, then Pos
#        [, finish: function applied to the moved vendor shape])
MODELS = {
    # Marquardt LIB_1802.1108 (1802.1108.stp): panel face at z 0, rocker +z, poles along y (+-5.1), terminal
    # rows at x 0 (1 / 2, on the body centre) and -7.05 (1a / 2a): x -> -Y, y -> X, z + 16.2 -> Z; underside
    # replaced by the 1802.2504's
    "Marquardt_1802.2504": (("na", "eu"), rocker, "marquardt_1802.1108/1802.1108/3D/1802.1108.stp",
                            ((0, 0, -90), (0, 0, 16.2)), rocker_1802_2504),
    # WAGO 2604-1106.stp (wago.com, CADENAS download): poles along z (2.3 + 5k), first pin row at x 0, second
    # at x -8.2, entries at +x, board at y 0, body +y: z -> X (centred), x -> Y, y -> Z
    "WAGO_2604-1106": (("na",), wago6, "wago/2604-1106.stp", ((90, 0, 90), (-14.8, 0, 0))),
    "Fuse_Schurter_UMT250": (("na", "eu"), fuse_umt250, None, None),
    "Varistor_TDK_CU4032": (("na", "eu"), mov_cu4032, None, None),
    # Traco tmps03_3d_drawing.stp (tracopower.com/overview/tmps03, 3D drawings): body z 0..16 with the
    # pins up, inputs along y at x -10.16: flip, turn the inputs onto the footprint's pin 1 / 2 row
    "Converter_ACDC_TRACO_TMPS03_THT": (("eu",), tmps03, "tmps03_3d_drawing.stp", ((180, 0, -90), (0, 0, 16.0))),
    # WAGO 2604-3102.stp (wago.com, CADENAS download): poles along z (2.3, 7.3), first pin row at x 0, second
    # at x -8.2 (lever side), board at y 0, body +y: z -> X (poles' centre), x -> Y (body centre), y -> Z
    "WAGO_2604-3102_1x02_P5.00mm_Vertical": (("eu",), wago2_vertical, "wago/2604-3102.stp",
                                              ((90, 0, 90), (-4.8, 4.75, 0))),
    "Harwin_P70-2200045": (("eu",), p70, None, None),
    "Harwin_S7081-42R": (("sensor",), s7081, None, None),
    "PUI_DMM-4026-B-I2S_4x3mm": (("sensor",), dmm4026, None, None),
    "Sensirion_DFN-4_1.5x1.5mm_P0.8mm_SHT4x_NoCentralPad": (("sensor",), sht4x, None, None),
}


def build(name):
    projects, envelope, vendor, tf, *finish = MODELS[name]
    if vendor and (VENDOR / vendor).exists():
        (rx, ry, rz), off = tf
        shape = Pos(*off) * Rot(0, 0, rz) * Rot(0, ry, 0) * Rot(rx, 0, 0) * import_step(str(VENDOR / vendor))
        for f in finish:
            shape = f(shape)
        return shape, f"vendor {vendor}"
    return envelope(), "datasheet envelope"


def main():
    for name, (projects, *_rest) in MODELS.items():
        shape, src = build(name)
        for p in projects:
            PROJECTS[p].mkdir(parents=True, exist_ok=True)
            export_step(shape, str(PROJECTS[p] / f"{name}.step"))
        print(f"{name}: {src} -> {', '.join(projects)}")


if __name__ == "__main__":
    main()
