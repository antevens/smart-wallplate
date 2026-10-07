"""Single source for the wiring board: parts, nets and geometry (front view, mm).

Front view: X right, Y up towards the rocker, origin = board centre; KiCad y = -Y.
F (front) faces the plate, B (back) faces the box. Decisions: docs/DESIGN.md D-24, D-25.
"""
import uuid

NS = uuid.UUID("2b7f0c1e-4c1d-4f55-9b0e-3a8d6c2f1e07")
LIB = "wiring_board"
PROJECT = "wiring_board"
REV = "v0.3"


def uid(*names):
    return str(uuid.uuid5(NS, "/".join(names)))


IRM_DS = "https://www.meanwell.com/Upload/PDF/IRM-03/IRM-03-SPEC.PDF"
WAGO_DS = "https://www.wago.com/global/pcb-terminal-blocks-and-pluggable-connectors/pcb-terminal-block/p/2604-1106"
UMT_DS = "https://us.schurter.com/bundles/snceschurter/epim/_ProdPool_/newDS/en/typ_UMT_250.pdf"
CU_DS = "https://www.farnell.com/datasheets/2921094.pdf"
JST_DS = "https://www.jst-mfg.com/product/pdf/eng/ePH.pdf"
ROCKER_DS = "Marquardt drawing 1802.2504 rev g, 2003-09-16 (K-drawing 18022504.03)"

# Footprint names in the project library
FP_ROCKER = "Marquardt_1802.2504_DPST_PCB"
FP_WAGO = "WAGO_2604-1106_1x06_P5.00mm_Horizontal"
FP_IRM = "Converter_ACDC_MeanWell_IRM-03-xx_THT"
FP_FUSE = "Fuse_Schurter_UMT250"
FP_MOV = "Varistor_TDK_CU4032"
FP_J2 = "JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal"
FP_C1 = "C_1206_3216Metric"
FP_ANT = "Ant_Logo_8mm_SilkScreen"
FP_KICAD = "KiCad-Logo2_5mm_SilkScreen"
FP_MH_PE = "MountingHole_2.6mm_Pad_PE"
FP_MH = "MountingHole_2.6mm_NPTH"

# ref: symbol, footprint, value, pin -> net, placement (x, Y, rot_deg, side), bom
PARTS = {
    # turned 90 degrees: poles are columns (line left at X -5.1, neutral right at X 5.1),
    # in-pins on the row nearer J1 (Y 14.5), switched pins above (Y 21.5)
    "S1": dict(sym="SW_DPST_Marquardt", fp=FP_ROCKER, value="1802.2504",
               nets={"1": "L_IN", "1a": "L_SW", "2": "N_IN", "2a": "N_SW"},
               pcb=(0.0, 18.0, 0, "F"), mfr="Marquardt", mpn="1802.2504",
               desc="Rocker switch DPST, ENEC 12(4) A 250 V~, UL/CSA 15 A 125-250 VAC, PCB pins, "
                    "emergency off (line and neutral)",
               ds=ROCKER_DS),
    "J1": dict(sym="Screw_Terminal_01x06", fp=FP_WAGO, value="2604-1106",
               # pads 1..6 run right to left in front view (block is on the back):
               # seen from the back, left to right: PE, N_SW, N_IN, L_SW, L_IN, PE
               nets={"1": "PE", "2": "N_SW", "3": "N_IN", "4": "L_SW", "5": "L_IN", "6": "PE"},
               pcb=(3.0, 0.93, 0, "B"), mfr="WAGO", mpn="2604-1106",
               desc="PCB terminal block, push-in, lever, 6-pole, 5 mm pitch, 4 mm2 / 12 AWG, entry parallel to PCB",
               ds=WAGO_DS),
    "PS1": dict(sym="IRM-03-5", fp=FP_IRM, value="IRM-03-5",
                nets={"1": "L_F", "3": "N_SW", "16": "+5V", "14": "GND", "5": "NC5"},
                pcb=None, mfr="Mean Well", mpn="IRM-03-5",
                desc="AC-DC module 85-305 VAC in, 5 V 600 mA, 37x24x15 mm", ds=IRM_DS),
    "F1": dict(sym="Fuse", fp=FP_FUSE, value="T1A 250V", nets={"1": "L_SW", "2": "L_F"},
               pcb=(-14.6, -23.0, 90, "F"), mfr="Schurter", mpn="3404.2416.22",
               desc="SMD fuse UMT 250, time-lag 1 A 250 VAC. Rating is a designer's choice: human review",
               ds=UMT_DS),
    "RV1": dict(sym="Varistor", fp=FP_MOV, value="CU4032K275G2", nets={"1": "L_F", "2": "N_SW"},
                pcb=(-5.5, -22.0, 90, "F"), mfr="TDK", mpn="B72660M0271K093",
                desc="SMD varistor SIOV-CU4032K275G2K1, 275 VAC", ds=CU_DS),
    "C1": dict(sym="C", fp=FP_C1, value="22uF 10V X5R", nets={"1": "+5V", "2": "GND"},
               pcb=(13.0, -26.0, 0, "F"), mfr="Murata", mpn="GRM31CR61A226KE19L",
               desc="Ceramic 22 uF 10 V X5R 1206 (or equivalent)", ds="https://www.murata.com"),
    "J2": dict(sym="Conn_01x02", fp=FP_J2, value="5V out", nets={"1": "+5V", "2": "GND"},
               pcb=(13.0, -19.0, 0, "F"), mfr="JST", mpn="S2B-PH-SM4-TB(LF)(SN)",
               desc="JST PH 2-pin SMD side entry, 5 V to MSR-2 (1=+5V, 2=GND)", ds=JST_DS),
}

# Silkscreen logos (board-only footprints) and the project URL, as on the author's other
# boards. ANT_LOGO_H = height the ant logo is scaled to (source: pcb/art/Ant_Logo_SilkScreen.kicad_mod).
ANT_LOGO_H = 8.0
# ref: footprint, (x, Y), side, rotation (deg): ant upper left, KiCad logo upper right (turned to
# fit between the rocker and the right PE ring)
LOGOS = {"LOGO1": (FP_ANT, (-15.5, 27.0), "F", 0), "LOGO2": (FP_KICAD, (15.6, 27.0), "F", 90)}
URL = "github.com/antevens/smart-wallplate"
URL_POS = (0.0, 18.0, "B")

# Mounting holes for the insert's snap posts (D-28), front view; mirrored in cad params
# (MOUNT_HOLES, checked by `make check`). Plated holes carry PE so the ring stays continuous
# round them; the bottom-right one sits outside the ring and is unplated. Top right is lowered
# so the insert boss clears the 5 V pass-through.
MOUNT_D, MOUNT_PAD = 2.6, 3.6
POST_SHOULDER_D, POST_HEAD_D = 4.5, 3.2     # post shoulder on the front, snap head on the back
MOUNT = {"MH1": ((-21.0, 33.5), "PE"), "MH2": ((-21.0, -33.5), "PE"),
         "MH3": ((21.0, 24.77), "PE"), "MH4": ((21.0, -33.5), None)}

# PS1 on the back: target pad positions (front view). AC end left, DC end right.
PS1_PINS = {"1": (-15.24, -12.5), "3": (-10.16, -12.5), "5": (15.24, -12.5),
            "16": (10.16, -30.28), "14": (15.24, -30.28)}

NETCLASS = {"Mains_L": ["L_IN", "L_SW", "L_F"], "Mains_N": ["N_IN", "N_SW"], "PE": ["PE"],
            "SELV": ["+5V", "GND"]}

BOARD = dict(w=47.0, h=72.0, t=1.6, r=1.5, slot=(3.0, 5.0, -10.9))

# PE ring round the AC part (both layers): outer outline and hole, front view
RING_OUTER = [(-22.5, -35.0), (2.5, -35.0), (2.5, -10.9), (22.5, -10.9), (22.5, 35.0), (-22.5, 35.0)]
RING_INNER = [(-20.0, -32.5), (0.0, -32.5), (0.0, -8.4), (20.0, -8.4), (20.0, 32.5), (-20.0, 32.5)]
SELV_ZONE = [(7.0, -33.5), (19.5, -33.5), (19.5, -13.0), (7.0, -13.0)]

# Load-path pours (net, layer, outline); the zone filler applies the spacing rules
POURS = [
    # in-pins straight up on the front
    ("L_IN", "F.Cu", [(-9.0, 2.0), (-1.5, 2.0), (-1.5, 17.0), (-9.0, 17.0)]),
    ("N_IN", "F.Cu", [(2.0, 2.0), (8.5, 2.0), (8.5, 17.0), (2.0, 17.0)]),
    # switched neutral: right of the N_IN pin, over the top to S1.2a (back)
    ("N_SW", "B.Cu", [(8.5, 2.0), (14.0, 2.0), (14.0, 25.5), (1.0, 25.5), (1.0, 19.0), (8.5, 19.0)]),
    # switched line (back): down from J1.4, under J1, up the left edge to S1.1a; also feeds F1
    ("L_SW", "B.Cu", [(2.0, 8.0), (2.0, -6.0), (-3.0, -6.0), (-3.0, -30.0), (-19.0, -30.0),
                      (-19.0, 27.0), (-1.0, 27.0), (-1.0, 8.0)]),
]

# Tracks: net -> [(layer, width, [(x, Y), ...])]
VIAS = {"L_SW": [(-12.0, -28.4), (-9.0, -28.4)]}  # (x, y), 1.0 / 0.5 mm

TRACKS = {
    # fused line: F1.2 (top) -> PS1.1, and F1.2 -> RV1.1 (bottom) round the right of F1
    "L_F": [("F.Cu", 0.8, [(-14.6, -18.75), (-15.6, -17.0), (-15.6, -13.5), (-15.24, -12.5)]),
            ("F.Cu", 0.8, [(-14.6, -18.75), (-11.2, -19.5), (-11.2, -26.65), (-5.5, -26.65)])],
    # switched neutral: RV1.2 (top) -> PS1.3
    "N_SW": [("F.Cu", 0.8, [(-5.5, -17.35), (-5.5, -14.0), (-10.16, -12.5)]),
             # J1.2 -> under J1 -> RV1 track
             ("F.Cu", 0.8, [(10.5, 0.93), (10.5, -2.6), (8.5, -4.4), (-5.5, -4.4), (-5.5, -14.0)])],
    # PSU feed: F1.1 -> vias to the L_SW pour on the back
    "L_SW": [("F.Cu", 0.8, [(-14.6, -27.25), (-13.0, -28.4), (-9.0, -28.4)])],
    # J1.6 and J1.1 (both pin rows) to the ring
    "PE": [("F.Cu", 1.2, [(-9.5, 0.93), (-9.5, 5.93)]), ("F.Cu", 2.0, [(-10.1, 3.43), (-20.5, 3.43)]),
           ("F.Cu", 1.2, [(15.5, 0.93), (15.5, 5.93)]), ("F.Cu", 2.0, [(16.1, 3.43), (20.5, 3.43)]),
           ("B.Cu", 1.2, [(15.5, 0.93), (15.5, 5.93)]), ("B.Cu", 2.0, [(16.1, 3.43), (20.5, 3.43)])],
    "+5V": [("F.Cu", 0.8, [(10.16, -30.28), (10.16, -26.0), (11.53, -26.0)]),
            ("F.Cu", 0.8, [(11.53, -26.0), (11.53, -18.0), (12.0, -16.15)])],
    "GND": [("F.Cu", 0.8, [(15.24, -30.28), (15.24, -26.0), (14.47, -26.0)]),
            ("F.Cu", 0.8, [(14.47, -26.0), (14.47, -18.0), (14.0, -16.15)])],
}
