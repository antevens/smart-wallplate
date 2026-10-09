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
FH12_DS = "https://www.hirose.com/product/en/products/FH12/FH12-6S-0.5SH(55)/"
ROCKER_DS = "Marquardt drawing 1802.2504 rev g, 2003-09-16 (K-drawing 18022504.03)"

# Footprint names in the project library
FP_ROCKER = "Marquardt_1802.2504_DPST_PCB"
FP_WAGO = "WAGO_2604-1106_1x06_P5.00mm_Horizontal"
FP_IRM = "Converter_ACDC_MeanWell_IRM-03-xx_THT"
FP_FUSE = "Fuse_Schurter_UMT250"
FP_MOV = "Varistor_TDK_CU4032"
FP_J2 = "Hirose_FH12-6S-0.5SH_1x06-1MP_P0.50mm_Horizontal"
FP_C1 = "C_1206_3216Metric"
FP_ANT = "Ant_Logo_8mm_SilkScreen"
FP_KICAD = "KiCad-Logo2_5mm_SilkScreen"
FP_MH = "MountingHole_2.6mm_NPTH"

# ref: symbol, footprint, value, pin -> net, placement (x, Y, rot_deg, side), bom
PARTS = {
    # turned 90 degrees: poles are columns (line left at X -5.1, neutral right at X 5.1),
    # in-pins on the body's centre line (Y 19.5), switched pins above (Y 26.5), away from J1
    "S1": dict(sym="SW_DPST_Marquardt", fp=FP_ROCKER, value="1802.2504",
               nets={"1": "L_IN", "1a": "L_SW", "2": "N_IN", "2a": "N_SW"},
               pcb=(0.0, 19.5, 0, "F"), mfr="Marquardt", mpn="1802.2504",
               desc="Rocker switch DPST, ENEC 12(4) A 250 V~, UL/CSA 15 A 125-250 VAC, PCB pins, "
                    "emergency off (line and neutral)",
               ds=ROCKER_DS),
    "J1": dict(sym="Screw_Terminal_01x06", fp=FP_WAGO, value="2604-1106",
               # pads 1..6 run right to left in front view (block is on the back):
               # seen from the back, left to right: PE, N_SW, N_IN, L_SW, L_IN, PE
               nets={"1": "PE", "2": "N_SW", "3": "N_IN", "4": "L_SW", "5": "L_IN", "6": "PE"},
               pcb=(3.0, 8.1, 0, "B"), mfr="WAGO", mpn="2604-1106",
               desc="PCB terminal block, push-in, lever, 6-pole, 5 mm pitch, 4 mm2 / 12 AWG, entry parallel to PCB",
               ds=WAGO_DS),
    "PS1": dict(sym="IRM-03-5", fp=FP_IRM, value="IRM-03-5",
                nets={"1": "L_F", "3": "N_SW", "16": "+5V", "14": "GND", "5": "NC5"},
                pcb=None, mfr="Mean Well", mpn="IRM-03-5",
                desc="AC-DC module 85-305 VAC in, 5 V 600 mA, 37x24x15 mm", ds=IRM_DS),
    "F1": dict(label="Schurter UMT250 T1A", sym="Fuse", fp=FP_FUSE, value="T1A 250V", nets={"1": "L_SW", "2": "L_F"},
               pcb=(-14.6, -23.0, 90, "F"), mfr="Schurter", mpn="3404.2416.22",
               desc="SMD fuse UMT 250, time-lag 1 A 250 VAC. Rating is a designer's choice: human review",
               ds=UMT_DS),
    "RV1": dict(label="TDK CU4032K275G2", sym="Varistor", fp=FP_MOV, value="CU4032K275G2", nets={"1": "L_F", "2": "N_SW"},
                pcb=(-5.5, -22.0, 90, "F"), mfr="TDK", mpn="B72660M0271K093",
                desc="SMD varistor SIOV-CU4032K275G2K1, 275 VAC", ds=CU_DS),
    "C1": dict(label="22uF 10V X5R 1206", sym="C", fp=FP_C1, value="22uF 10V X5R", nets={"1": "+5V", "2": "GND"},
               pcb=(13.0, -26.0, 0, "F"), mfr="Murata", mpn="GRM31CR61A226KE19L",
               desc="Ceramic 22 uF 10 V X5R 1206 (or equivalent)", ds="https://www.murata.com"),
    # turned 180: the flex jumper enters from the top (towards the pass-through); pads 1-3 GND, 4-6 +5V
    "J2": dict(label="Hirose FH12-6S", sym="Conn_01x06", fp=FP_J2, value="5V out (flex jumper)",
               nets={"1": "GND", "2": "GND", "3": "GND", "4": "+5V", "5": "+5V", "6": "+5V"},
               pcb=(13.0, -19.5, 180, "F"), mfr="Hirose", mpn="FH12-6S-0.5SH(55)",
               desc="FPC connector 0.5 mm, 6 contacts, slide lock: 5 V to the flex jumper (D-27, R9)", ds=FH12_DS),
}

# Silkscreen logos (board-only footprints) and the project URL, as on the author's other
# boards. ANT_LOGO_H = height the ant logo is scaled to (source: pcb/art/Ant_Logo_SilkScreen.kicad_mod).
ANT_LOGO_H = 8.0
# ref: footprint, (x, Y), side, rotation (deg): ant upper left, KiCad logo upper right (turned to
# fit between the rocker and the right PE ring)
LOGOS = {"LOGO1": (FP_ANT, (-15.5, 27.0), "F", 0), "LOGO2": (FP_KICAD, (15.6, 27.0), "F", 90)}
URL = "github.com/antevens/smart-wallplate"
URL_POS = (0.0, 14.6, "B")

# Mounting holes for the insert's snap posts (D-28), front view; mirrored in cad params
# (MOUNT_HOLES, checked by `make check`). All unplated, with no copper under the posts: a copper
# keep-out round each hole (MOUNT_KO) on both layers, and the PE ring detours round MH1 and MH3
# on the inside (PE_DETOURS), so earth continuity never depends on copper the posts press on, or
# on vias. Top right is lowered so the insert boss clears the 5 V pass-through.
MOUNT_D = 2.6
POST_SHOULDER_D, POST_HEAD_D = 4.5, 3.2     # post shoulder on the front, snap head on the back
MOUNT_KO = max(POST_SHOULDER_D, POST_HEAD_D) / 2 + 0.5   # copper keep-out radius round each hole
MOUNT = {"MH1": (-21.0, 33.5), "MH2": (-21.0, -33.5), "MH3": (21.0, 24.77), "MH4": (21.0, -33.5)}

# PS1 on the back: target pad positions (front view). AC end left, DC end right.
PS1_PINS = {"1": (-15.24, -12.5), "3": (-10.16, -12.5), "5": (15.24, -12.5),
            "16": (10.16, -30.28), "14": (15.24, -30.28)}

NETCLASS = {"Mains_L": ["L_IN", "L_SW", "L_F"], "Mains_N": ["N_IN", "N_SW"], "PE": ["PE"],
            "SELV": ["+5V", "GND"]}

BOARD = dict(w=47.0, h=72.0, t=1.6, r=1.5, slot=(3.0, 5.0, -10.9))

# PE ring round the AC part (both layers): outer outline and hole, front view
RING_OUTER = [(-22.5, -35.0), (2.5, -35.0), (2.5, -10.9), (22.5, -10.9), (22.5, 35.0), (-22.5, 35.0)]
RING_INNER = [(-20.0, -32.5), (0.0, -32.5), (0.0, -8.9), (20.0, -8.9), (20.0, 32.5), (-20.0, 32.5)]
SELV_ZONE = [(7.0, -33.5), (19.5, -33.5), (19.5, -13.0), (7.0, -13.0)]

# Load-path pours (net, layer, outline); the zone filler applies the spacing rules
POURS = [
    # in-pins (both J1 rows) straight up on the front
    ("L_IN", "F.Cu", [(-9.0, -2.0), (-1.5, -2.0), (-1.5, 21.5), (-9.0, 21.5)]),
    ("N_IN", "F.Cu", [(2.0, -2.0), (8.5, -2.0), (8.5, 21.5), (2.0, 21.5)]),
    # switched neutral: right of the N_IN pin, over the top to S1.2a (back)
    ("N_SW", "B.Cu", [(8.5, -2.0), (14.0, -2.0), (14.0, 29.0), (1.0, 29.0), (1.0, 24.5), (8.5, 24.5)]),
    # switched line (back): down from J1.4, under J1, up the left edge to S1.1a; also feeds F1
    ("L_SW", "B.Cu", [(2.0, 8.0), (2.0, -6.0), (-3.0, -6.0), (-3.0, -30.0), (-19.0, -30.0),
                      (-19.0, 29.0), (-1.0, 29.0), (-1.0, 8.0)]),
]

# PE arms: J1.6 / J1.1 (pin pairs at x -9.5 / 15.5) to the PE ring, flush with the outer edges of
# the pin pair's pads; they end square at the pins' centre line, behind the pads, so the pads
# still set the 3.5 mm keep-away from the neighbouring L / N terminals.
PE_PIN_X = (-9.5, 15.5)
PE_ROWS = (-0.1, 8.1)                       # J1's two solder-pin rows (front view y): first row (entry side) above
WAGO_PAD = (2.2, 2.2)                       # J1 pad size (x, y), round, used by the footprint
WAGO_ROW_PITCH = 8.2                        # DATASHEET (WAGO 3D model 2604-1106): second row behind the first
WAGO_BODY = (5.0, 11.1, 8.1)                # DATASHEET (WAGO 3D model): entry face before / closed back behind the
                                            # first row at the board; the levers overhang the entry side up top
PE_ARM_W = abs(PE_ROWS[1] - PE_ROWS[0]) + WAGO_PAD[1]
_arm_y = ((PE_ROWS[0] + PE_ROWS[1]) - PE_ARM_W) / 2, ((PE_ROWS[0] + PE_ROWS[1]) + PE_ARM_W) / 2
_ring_l, _ring_r = RING_INNER[0][0] - 0.5, RING_INNER[3][0] + 0.5    # 0.5 mm into the ring

# PE ring detours round MH1 and MH3 on the inside: annular sectors from MOUNT_KO out to
# MOUNT_KO + PE_DETOUR_W over the inner side (degrees from the hole centre, counter-clockwise),
# overlapping the ring at both ends. MH2 (bottom-left corner, next to F1) interrupts the ring:
# PE runs J1.6 -> left edge -> MH1 -> top -> MH3 -> J1.1, and the ring's lower part stays joined
# to both arms. gen_pcb.py checks that this path holds on F.Cu without vias or hole copper.
PE_DETOUR_W = 2.0
PE_DETOURS = {"MH1": (-100.0, 10.0), "MH3": (80.0, 280.0)}
PE_ARMS = [("F.Cu", [(_ring_l, _arm_y[0]), (PE_PIN_X[0], _arm_y[0]), (PE_PIN_X[0], _arm_y[1]), (_ring_l, _arm_y[1])])]
PE_ARMS += [(lay, [(PE_PIN_X[1], _arm_y[0]), (_ring_r, _arm_y[0]), (_ring_r, _arm_y[1]), (PE_PIN_X[1], _arm_y[1])])
            for lay in ("F.Cu", "B.Cu")]

# Pour priorities: pours closer together than their spacing rule compete for copper, and equal
# priorities make the result depend on fill order. Line pours win over neutral.
POUR_PRIO = {"L_IN": 3, "N_IN": 2, "L_SW": 3, "N_SW": 2}

# Tracks: net -> [(layer, width, [(x, Y), ...])]
VIAS = {"L_SW": [(-12.0, -28.4), (-9.0, -28.4)]}  # (x, y), 1.0 / 0.5 mm

TRACKS = {
    # fused line: F1.2 (top) -> PS1.1, and F1.2 -> RV1.1 (bottom) round the right of F1
    "L_F": [("F.Cu", 0.8, [(-14.6, -18.75), (-15.6, -17.0), (-15.6, -13.5), (-15.24, -12.5)]),
            ("F.Cu", 0.8, [(-14.6, -18.75), (-11.2, -19.5), (-11.2, -26.65), (-5.5, -26.65)])],
    # switched neutral: RV1.2 (top) -> PS1.3
    "N_SW": [("F.Cu", 0.8, [(-5.5, -17.35), (-5.5, -14.0), (-10.16, -12.5)]),
             # J1.2 -> under J1 -> RV1 track
             ("F.Cu", 0.5, [(10.5, -0.1), (10.5, -5.0), (-5.5, -5.0), (-5.5, -14.0)])],
    # PSU feed: F1.1 -> vias to the L_SW pour on the back
    "L_SW": [("F.Cu", 0.8, [(-14.6, -27.25), (-13.0, -28.4), (-9.0, -28.4)])],
    # J1.6 and J1.1 (both pin rows) to the ring
    "+5V": [("F.Cu", 0.8, [(10.16, -30.28), (10.16, -26.0), (11.53, -26.0)]),
            ("F.Cu", 0.8, [(11.53, -26.0), (11.53, -22.6), (12.25, -22.6)]),
            ("F.Cu", 0.3, [(11.75, -22.6), (12.75, -22.6)]),                       # bar under J2.4-6
            ("F.Cu", 0.3, [(11.75, -22.6), (11.75, -20.85)]), ("F.Cu", 0.3, [(12.25, -22.6), (12.25, -20.85)]),
            ("F.Cu", 0.3, [(12.75, -22.6), (12.75, -20.85)])],
    "GND": [("F.Cu", 0.8, [(15.24, -30.28), (15.24, -26.0), (14.47, -26.0)]),
            ("F.Cu", 0.8, [(14.47, -26.0), (14.47, -22.6), (13.75, -22.6)]),
            ("F.Cu", 0.3, [(13.25, -22.6), (14.25, -22.6)]),                       # bar under J2.1-3
            ("F.Cu", 0.3, [(13.25, -22.6), (13.25, -20.85)]), ("F.Cu", 0.3, [(13.75, -22.6), (13.75, -20.85)]),
            ("F.Cu", 0.3, [(14.25, -22.6), (14.25, -20.85)])],
}
