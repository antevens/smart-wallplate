"""Parts, nets and geometry for the EU boards (docs/DESIGN.md D-30, D-36).

Two boards in the round EU box, both hanging from bosses under the cap. Geometry comes from
cad/build123d/eu/params_eu.py. Coordinates: room x, y (front view, the F side faces the plate);
origin = box centre.

Mains board (MB_*): round, at the rocker's PCB seat. The rocker (Marquardt 1802.2504, DPST) breaks
line and neutral of the load: L_IN -> L_SW and N_IN -> N_SW, between two WAGO 2604-3102 push-in
blocks on the back (wires from the back of the box). L copper (pours) on F.Cu, N on B.Cu. F1 fuses
the PSU feed from L_SW, RV1 clamps it; the PSU (Traco TMPS 03-105) on the back straddles a routed
relief slot: inputs above it, outputs on the 5 V island below it, with a 2-pin header (J3).

5 V board (WB_*): D-shaped, just under the cap, below the switch cup. A pin socket on its back (J1)
takes +5V / GND from the header; two spring pins (P1, P2) on its front reach through the cap onto
the sensor flex's pads (R9, R10). No mains on it.
"""
import sys
import uuid
from math import acos, atan2, cos, degrees, hypot, radians, sin, sqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "cad" / "build123d" / "eu"))
from params_eu import (WB_R, WB_CUT_Y, WB_T, PSU, WAGO_EU, WAGO_PITCH, WAGO_ROW, WAGO_ROW_OFF, MB_T, MB_PSU_C,  # noqa: E402
                       MB_WAGO_C, MB_SLOT, MB_HDR, MB_BOSS, MB_BOSS_D, MB_BOSS_CLR, SW_Y,
                       WB_MOUNT, DOMES, DOME_NOTCH_R, PINS, PIN_PAD_D, PIN_HOLE_D)

LIB = "eu"
MAINS, LV = "eu_mains_board", "eu_5v_board"
REV = "v0.2"
NS = uuid.UUID("8d2f4a8e-0b3c-4e7a-9f1d-6c5b2a1e3d40")


def uid(*names):
    return str(uuid.uuid5(NS, "/".join(names)))


TMPS_DS = "https://www.tracopower.com/sites/default/files/products/datasheets/tmps03_datasheet.pdf"
WAGO_DS = "https://www.wago.com/global/pcb-terminal-blocks-and-pluggable-connectors/pcb-terminal-block/p/2604-3102"
UMT_DS = "https://us.schurter.com/bundles/snceschurter/epim/_ProdPool_/newDS/en/typ_UMT_250.pdf"
CU_DS = "https://www.farnell.com/datasheets/2921094.pdf"

FP_PSU = "Converter_ACDC_TRACO_TMPS03_THT"
FP_WAGO = "WAGO_2604-3102_1x02_P5.00mm_Vertical"
FP_FUSE = "Fuse_Schurter_UMT250"
FP_MOV = "Varistor_TDK_CU4032"
FP_C1 = "C_1206_3216Metric"
FP_MH = "MountingHole_2.2mm_M2"
FP_ROCKER = "Marquardt_1802.2504_DPST_PCB"
FP_HDR = "PinHeader_1x02_P2.54mm_Vertical_SMD_Pin1Left"   # KiCad stock, Samtec TSM -SV pad layout
FP_SOCKET = "PinSocket_1x02_P2.54mm_Vertical"
ROCKER_DS = "Marquardt drawing 1802.2504 rev g, 2003-09-16 (K-drawing 18022504.03)"
FP_PIN = "Harwin_P70-2200045"             # SMT spring pin with peg: pad 2.2, hole 1.2 (drawing P70-2200045)
PIN_DS = ("https://content.harwin.com/asset/7e702b12-8f84-42b5-9282-d7e22f3466f3/"
          "DRG-02624-Technical-Drawing-Datasheet-P70-220-pdf.pdf")
WAGO_PAD = (2.2, 2.2)                     # J1 / J2 pad, round, as the NA 2604 footprint; drill 1.3 (+0.1) DATASHEET
WAGO_DRILL = 1.3
PSU_PAD, PSU_DRILL = 1.5, 0.9             # TMPS pins Ø0.6 +-0.1 (DATASHEET): 0.9 hole, 0.3 annular ring
# TMPS 03 pins, top view, body centre origin, KiCad y down (datasheet bottom view mirrored):
# 1 AC(N), 2 AC(L) on one edge; 3 NC, 4 -Vout, 5 +Vout on the opposite edge (rows 20.32 apart)
PSU_PINS = {"1": (10.16, -10.16), "2": (5.08, -10.16), "3": (-10.16, 10.16), "4": (0.0, 10.16),
            "5": (10.16, 10.16)}

PSU_PIN_NAMES = {"3": "NC"}

EDGE_MAINS = 1.0                          # mains copper to the board edge (rule in the .kicad_dru)


def notches(cut_y=None):
    """Edge notches (centre, radius) round the box's screw domes that reach into the board."""
    out = []
    for c in DOMES:
        if (cut_y is None or c[1] - DOME_NOTCH_R < cut_y) and hypot(*c) - DOME_NOTCH_R < WB_R:
            out.append((c, DOME_NOTCH_R))
    return out


def outline(cut_y=None, step=4.0):
    """Closed polyline (room x, y): the box circle less clearance, cut straight at cut_y (None: the
    whole circle), with the dome notches. Walks the circle clockwise."""
    if cut_y is None:
        t_start, t_end = 0.0, -360.0
    else:
        xc = sqrt(WB_R ** 2 - cut_y ** 2)
        t_start = degrees(atan2(cut_y, xc))
        t_end = 180.0 - t_start - 360.0

    def norm(t):                                          # angle in the walk's range (t_start .. t_end)
        while t > t_start:
            t -= 360.0
        while t < t_end:
            t += 360.0
        return t

    cuts = []
    for (cx, cy), r in notches(cut_y):
        d = hypot(cx, cy)
        half = degrees(acos((WB_R ** 2 + d ** 2 - r ** 2) / (2 * WB_R * d)))
        tc = norm(degrees(atan2(cy, cx)))
        cuts.append((tc + half, tc - half, (cx, cy), r))
    cuts.sort(key=lambda q: -q[0])

    def arc(cx, cy, r, a0, a1):
        n = max(2, int(abs(a1 - a0) / step))
        return [(cx + r * cos(radians(a0 + (a1 - a0) * k / n)), cy + r * sin(radians(a0 + (a1 - a0) * k / n)))
                for k in range(n + 1)]

    pts = [] if cut_y is None else [(-sqrt(WB_R ** 2 - cut_y ** 2), cut_y)]
    t = t_start
    for t_in, t_out, (cx, cy), r in cuts:
        pts += arc(0, 0, WB_R, t, t_in)[:-1]
        p_in = (WB_R * cos(radians(t_in)), WB_R * sin(radians(t_in)))
        p_out = (WB_R * cos(radians(t_out)), WB_R * sin(radians(t_out)))
        n_in = degrees(atan2(p_in[1] - cy, p_in[0] - cx))
        n_out = degrees(atan2(p_out[1] - cy, p_out[0] - cx))
        # of the two ways round the notch, take the one whose middle lies inside the board circle
        alt = n_out + (360.0 if n_out < n_in else -360.0)
        mid = (n_in + n_out) / 2
        if hypot(cx + r * cos(radians(mid)), cy + r * sin(radians(mid))) > WB_R:
            n_out = alt
        pts += arc(cx, cy, r, n_in, n_out)[:-1]
        t = t_out
    pts += arc(0, 0, WB_R, t, t_end)[:-1]
    return pts


# ref: symbol, footprint, value, nets, pos (x, y, rot), side, bom
MAINS_PARTS = {
    "S1": dict(sym="SW_DPST_Marquardt", fp=FP_ROCKER, value="1802.2504",
               nets={"1": "L_IN", "1a": "L_SW", "2": "N_IN", "2a": "N_SW"}, pos=(0.0, SW_Y, 180), side="F",
               mfr="Marquardt", mpn="1802.2504",
               desc="Rocker switch DPST, ENEC 12(4) A 250 V~, UL/CSA 15 A 125-250 VAC, PCB pins: emergency off "
                    "(line and neutral of the load)", ds=ROCKER_DS),
    # J1 is turned 180 deg from J2 (both levers towards the board centre): its pole 2 is the upper one
    "J1": dict(sym="Screw_Terminal_01x02", fp=FP_WAGO, value="2604-3102", nets={"1": "L_SW", "2": "L_IN"},
               pos=(*MB_WAGO_C[0], 0), side="B", mfr="WAGO", mpn="2604-3102", label="WAGO 2604-3102 L",
               desc="PCB terminal block, push-in, 2-pole, 4 mm2, entry 90 deg to the PCB, 400 V III/2: house line in, "
                    "switched line to the load", ds=WAGO_DS),
    "J2": dict(sym="Screw_Terminal_01x02", fp=FP_WAGO, value="2604-3102", nets={"1": "N_IN", "2": "N_SW"},
               pos=(*MB_WAGO_C[1], 0), side="B", mfr="WAGO", mpn="2604-3102", label="WAGO 2604-3102 N",
               desc="PCB terminal block, push-in, 2-pole, 4 mm2, entry 90 deg to the PCB, 400 V III/2: house neutral in, "
                    "switched neutral to the load", ds=WAGO_DS),
    "F1": dict(label="Schurter UMT250 T1A", sym="Fuse", fp=FP_FUSE, value="T1A 250V", nets={"1": "L_SW", "2": "L_F"},
               pos=(14.0, -3.0, 0), side="F", mfr="Schurter", mpn="3404.2416.22",
               desc="SMD fuse UMT 250, time-lag 1 A 250 VAC (TMPS 03 recommended input fuse T1.0 A / 250 V)",
               ds=UMT_DS),
    "RV1": dict(label="TDK CU4032K275G2", sym="Varistor", fp=FP_MOV, value="CU4032K275G2", nets={"1": "L_F", "2": "N_SW"},
                pos=(-17.0, -3.0, 90), side="F", mfr="TDK", mpn="B72660M0271K093",
                desc="SMD varistor SIOV-CU4032K275G2K1, 275 VAC", ds=CU_DS),
    "PS1": dict(sym="TMPS03-105", fp=FP_PSU, value="TMPS 03-105",
                nets={"1": "N_SW", "2": "L_F", "4": "GND", "5": "+5V"}, pin_names=PSU_PIN_NAMES,
                pos=(*MB_PSU_C, 0), side="B", mfr="Traco Power", mpn="TMPS 03-105",
                desc="AC-DC module 85-264 VAC in, 5 V 600 mA, 25.4x25.4x16.3 mm, IEC/UL 62368-1, IEC 60335-1",
                ds=TMPS_DS),
    # SMT header (no pin tails under the PSU on the back); footprint origin between the posts, pin 1 post on MB_HDR
    "J3": dict(sym="Conn_01x02", fp=FP_HDR, value="TSM-102-01-L-SV", nets={"1": "+5V", "2": "GND"},
               pos=(MB_HDR[0], MB_HDR[1] - 1.27, 0), side="F", mfr="Samtec", mpn="TSM-102-01-L-SV",
               label="Samtec TSM-102-01-L-SV",
               desc="SMT pin header 1x2, 2.54 mm, 5.84 mm post, gold on post: 5 V to the 5 V board's pin socket "
                    "(5 V island)", ds="https://suddendocs.samtec.com/catalog_english/tsm.pdf"),
}
MAINS_PARTS.update({f"MH{i + 1}": dict(sym="MountingHole", fp=FP_MH, value="M2", nets={}, pos=(*xy, 0), side="F",
                                       mfr="-", mpn="-", desc="M2 to the long cap boss", ds="", in_bom=False)
                    for i, xy in enumerate(MB_BOSS)})

LV_PARTS = {
    "J1": dict(sym="Conn_01x02", fp=FP_SOCKET, value="Socket 1x2 2.54", nets={"1": "+5V", "2": "GND"},
               pos=(*MB_HDR, 0), side="B", mfr="Samtec", mpn="SSW-102-01-L-S",
               label="+5V GND socket", desc="5 V from the mains board's header (5 V island)", ds="https://suddendocs.samtec.com/catalog_english/ssw.pdf"),
    "C1": dict(label="22uF 10V X5R 1206", sym="C", fp=FP_C1, value="22uF 10V X5R", nets={"1": "+5V", "2": "GND"},
               pos=(16.0, -6.8, 90), side="F", mfr="Murata", mpn="GRM31CR61A226KE19L",
               desc="Ceramic 22 uF 10 V X5R 1206 (or equivalent)", ds="https://www.murata.com"),
    "P1": dict(label="Harwin P70-2200045 GND", sym="Conn_01x01", fp=FP_PIN, value="P70-2200045 GND", nets={"1": "GND"},
               pos=(*PINS[0], 0), side="F", mfr="Harwin", mpn="P70-2200045",
               desc="Spring pin, 2 A, 7.1 mm working height: GND to the flex pad through the cap", ds=PIN_DS),
    "P2": dict(label="Harwin P70-2200045 +5V", sym="Conn_01x01", fp=FP_PIN, value="P70-2200045 +5V", nets={"1": "+5V"},
               pos=(*PINS[1], 0), side="F", mfr="Harwin", mpn="P70-2200045",
               desc="Spring pin, 2 A, 7.1 mm working height: +5 V to the flex pad through the cap", ds=PIN_DS),
    "MH1": dict(sym="MountingHole", fp=FP_MH, value="M2", nets={}, pos=(*WB_MOUNT[0], 0), side="F",
                mfr="-", mpn="-", desc="M2 to the cap boss", ds="", in_bom=False),
    "MH2": dict(sym="MountingHole", fp=FP_MH, value="M2", nets={}, pos=(*WB_MOUNT[1], 0), side="F",
                mfr="-", mpn="-", desc="M2 to the cap boss", ds="", in_bom=False),
}
LV_BOSS_HOLES = [(xy, MB_BOSS_D / 2 + MB_BOSS_CLR) for xy in MB_BOSS if xy[1] < WB_CUT_Y]   # long bosses passing

NETCLASS = {"Mains_L": ("L_IN", "L_SW", "L_F"), "Mains_N": ("N_IN", "N_SW"), "SELV": ("+5V", "GND")}
TRACK_W = {"Mains_L": 1.0, "Mains_N": 1.0, "SELV": 0.6}
LOAD_NETS = ("L_IN", "L_SW", "N_IN", "N_SW")                 # carry the load current: copper pours
