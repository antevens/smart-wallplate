"""Parts, nets and geometry for the sensor flex and the power jumper (docs/DESIGN.md D-27).

Geometry comes from cad/build123d/params.py, so the boards follow the CAD route and shelf.

Sensor flex, single copper layer: a straight strip in the flat. Each 90 degree corner of the
route in the trim is a 45 degree fold, which turns the strip over, so the CN2 plug (facing the
MSR-2), the spring fingers (facing the target) and the SHT45 (facing the vents) all sit on the
copper side. Flat coordinates: X along the strip from the plug centre, Y across it; in the
right channel Y = FLEX_X - room x. The I2S microphone (D-29) sits on a section widened towards
the flange (+Y) on the channel run, its port end towards the fingers.

Power jumper: single-layer flex from the wiring board's J2 (FH12 slide lock) through the
pass-through to a stiffened pad end on the insert shelf, under the spring fingers.
"""
import sys
import uuid
from math import hypot
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "cad" / "build123d"))
from params import (MSR_CN2_X, MSR_Y, FLEX_X, FLEX_W, FLEX_RISE_DY, STIFF_T, FLEX_T, FLEX_HI_Z, SHT_Y, SHT_CHIP,
                    SKIN_Z, SHT_ENTRY, FINGER_X, FINGER_Y, FINGER_PAD, FINGER, FINGER_SEC_IN, FINGER_SEC_OUT,
                    FINGER_SEC_Y, FINGER_LANE_Y, TARGET_Y, FLANGE_OUT, SHELF_OUT, SHELF_TOP_Z, SHELF_UNDER_Z, TARGET_T,
                    JUMPER_W, JUMPER_END, JUMPER_T, JUMPER_SERVICE, jumper_length,
                    AAA_L, BC_CELL_X, BC_CELL_Y0, BC_CELL_Z, BC_TERM_Y, BC_VBAT_X, BC_FLEX_Z, BC_END_T, BC_END_H,
                    BC_FINGERS, BC_STRIP, BC_RUN, BC_JOG, BC_CONTACT_W, BC_COPPER_Y, BC_REG, BC_PCB_W, BC_PCB_CLR, BC_BRIDGE_H, BC_LANE_H,
                    BC_END_CORNER, BC_NA_TONGUE_Y, BC_NA_NECK_W, BC_NA_GROOVE_D, BC_NA_GROOVE_BOT, BC_NA_DOWN,
                    BC_FLOOR_PAD, BC_TONGUE_W, BC_FLOOR_T, BC_RECESS_CLR, SEAT_Z, TARGET_TOP_Z, tongue_walls,
                    BC_PEG_END, BC_PEGS, BC_PEG_HOLE, BC_PAD_STIFF_T,
                    MIC, MIC_Y, MIC_FLEX_Y, MIC_SEC_W, MIC_SEC_Y, MIC_FLEX_HOLE_D, FLEX_PLUG, FLEX_NECK_L)

LIB = "sensor"
REV = "v0.1"
FLEX, JUMPER, COVER = "sensor_flex", "power_jumper", "cover_flex"

# ---- route lengths (3D) -> flat X positions --------------------------------------------
_z_lo = STIFF_T + FLEX_T / 2
_z_hi = FLEX_HI_Z + FLEX_T / 2
_z_sht = SKIN_Z - 0.5 - SHT_CHIP[2] - FLEX_T / 2
S_B = FLEX_X - MSR_CN2_X                                    # plug -> first corner (fold 1)
S_C = S_B + hypot(FLEX_RISE_DY, _z_hi - _z_lo)              # end of the rise
_y_c = MSR_Y - FLEX_RISE_DY
S_D = S_C + (_y_c - SHT_Y)                                  # channel -> bottom corner (fold 2)
S_F = S_D + (FLEX_X - SHT_ENTRY) + hypot(SHT_ENTRY, _z_hi - _z_sht)   # SHT45 at the tail


def s_channel(y):
    """Flat X of a point in the right channel at room y."""
    return S_C + (_y_c - y)


def y_channel(x):
    """Flat Y of a point in the right channel at room x."""
    return FLEX_X - x


# ---- flex outline (flat): plug pad, strip, finger section, tail ----------------------------
HALF = FLEX_W / 2
PLUG_HALF, PLUG_LEN = FLEX_PLUG[1] / 2, FLEX_PLUG[0] / 2   # plug end: room for the fan-out
FIN_X0, FIN_X1 = s_channel(FINGER_SEC_Y[1]), s_channel(FINGER_SEC_Y[0])      # flange side, over the pads
LANE_X0, LANE_X1 = s_channel(FINGER_LANE_Y[1]), s_channel(FINGER_LANE_Y[0])   # wall side, track lanes
FIN_Y_IN, FIN_Y_OUT = y_channel(FINGER_SEC_IN), y_channel(FINGER_SEC_OUT)   # + towards the flange
MIC_X0, MIC_X1 = s_channel(MIC_SEC_Y[1]), s_channel(MIC_SEC_Y[0])          # widened microphone section
MIC_XC = s_channel(MIC_Y)                                   # mic body centre (flat), port end towards +X
TAIL_X = S_F + 3.6
NECK_X = PLUG_LEN + FLEX_NECK_L                             # gentle taper from the plug end to the strip
FLEX_OUTLINE = [(-PLUG_LEN, -PLUG_HALF), (PLUG_LEN, -PLUG_HALF), (NECK_X, -HALF), (LANE_X0, -HALF),
                (LANE_X0, FIN_Y_OUT), (LANE_X1, FIN_Y_OUT), (LANE_X1, -HALF), (TAIL_X, -HALF), (TAIL_X, HALF),
                (FIN_X1, HALF), (FIN_X1, FIN_Y_IN), (FIN_X0, FIN_Y_IN), (FIN_X0, HALF),
                (MIC_X1, HALF), (MIC_X1, MIC_SEC_W), (MIC_X0, MIC_SEC_W), (MIC_X0, HALF), (NECK_X, HALF),
                (PLUG_LEN, PLUG_HALF), (-PLUG_LEN, PLUG_HALF)]
FOLDS = (S_B, S_D)                                          # 45 deg folds (fab drawing)
_mic_stiff = ((MIC_XC - MIC[1] / 2 - 0.5, MIC_FLEX_Y - MIC[0] / 2 - 0.5),
              (MIC_XC + MIC[1] / 2 + 0.5, MIC_FLEX_Y + MIC[0] / 2 + 0.5))
STIFFENERS = [((-PLUG_LEN, -PLUG_HALF), (PLUG_LEN, PLUG_HALF)),            # behind the CN2 plug
              ((FIN_X0, FIN_Y_OUT), (FIN_X1, FIN_Y_IN)),                   # behind the fingers
              _mic_stiff]                                                  # behind the microphone

# ---- CN2 mate: placeholder until the part and contact map are confirmed (MEASURE) ----------
CN2_CONFIRMED = False
CN2_PINS, CN2_PITCH, CN2_ROW = 30, 0.4, 1.2                 # 2 x 15, rows at Y +-CN2_ROW
# Placeholder map: lane -> contact, chosen only so the single-layer fan-out keeps the lane order the
# microphone, the fingers and the SHT45 need. NOT the MSR-2's pinout. The microphone has its own
# GND and 3.3 V contacts (nets MIC_GND, MIC_3V3), joined to GND / +3V3 on the MSR-2, so its lanes
# need not cross the others on the single copper layer.
CN2_MAP = {"I2S_WS": "19", "I2S_SCK": "21", "I2S_SD": "23", "MIC_GND": "25", "MIC_3V3": "27", "+5V": "29",
           "+3V3": "24", "SCL": "26", "SDA": "28", "GND": "30"}
I2S_GPIO = {"I2S_SCK": "IO4", "I2S_WS": "IO6", "I2S_SD": "IO7"}   # MSR-2 GPIOs (D-29), free on CN2


FP_B2B = "B2B_0.4mm_2x15_PLACEHOLDER"
FP_FINGER = "Harwin_S7081-42R"
FP_SHT = "Sensirion_DFN-4_1.5x1.5mm_P0.8mm_SHT4x_NoCentralPad"
FP_C = "C_0402_1005Metric"
FP_SOT = "SOT-23-5"
TLV_DS = "https://www.ti.com/lit/ds/symlink/tlv755p.pdf"
FP_TP_CONTACT = "Contact_Pad_2.2x4.5mm"
FP_FPC = "FPC_6P_P0.50mm_Contacts"
HARWIN_DS = ("https://content.harwin.com/asset/8cd5d0a8-d578-46b3-8278-7289045a1613/"
             "DRG-02322-Technical-Drawing-Datasheet-S7081R-pdf.pdf")
SHT_DS = "https://sensirion.com/media/documents/33FD6951/624C4357/Datasheet_SHT4x.pdf"
FP_MIC = "PUI_DMM-4026-B-I2S_4x3mm"
FP_R = "R_0402_1005Metric"
MIC_DS = "https://api.puiaudio.com/filename/DMM-4026-B-I2S-R.pdf"
# DMM-4026-B-I2S-R land pattern (datasheet rev A), body frame with +y towards the port: pad columns
# 2.15 apart, rows 0.65 apart, the port 1.28 below the nearest row; pads 0.60 x 0.40; GND ring
# 1.05 / 1.65. Top view: LR, CONFIG, VDD on one column, SD, SCK, WS on the other, far end first.
MIC_PAD, MIC_COL, MIC_ROW, MIC_PORT_ROW = (0.60, 0.40), 2.15 / 2, 0.65, 1.28
MIC_RING = (1.05, 1.65)

# ref: symbol, footprint, value, pin -> net, flat (x, y, rot), bom
FLEX_PARTS = {
    "J1": dict(sym="Conn_02x15_Odd_Even", fp=FP_B2B, value="CN2 mate (TBD)", label="CN2 mate (TBD)",
               nets={pin: lane for lane, pin in CN2_MAP.items()}, pos=(0.0, 0.0, 0), mfr="TBD", mpn="TBD",
               desc="Board-to-board plug mating the MSR-2's rear connector CN2, 0.4 mm, 2 rows (part and "
                    "contact map unconfirmed)", ds=""),
    "J2": dict(sym="Conn_01x01", fp=FP_FINGER, value="S7081-42R +5V", nets={"1": "+5V"}, label="Harwin S7081-42R +5V",
               pos=(s_channel(FINGER_Y[1]), y_channel(FINGER_X), 0), mfr="Harwin", mpn="S7081-42R",
               desc="SMT spring finger, gold, 4 A, working height 2.0 mm: +5 V from the target board", ds=HARWIN_DS),
    "J3": dict(sym="Conn_01x01", fp=FP_FINGER, value="S7081-42R GND", nets={"1": "GND"}, label="Harwin S7081-42R GND",
               pos=(s_channel(FINGER_Y[0]), y_channel(FINGER_X), 0), mfr="Harwin", mpn="S7081-42R",
               desc="SMT spring finger, gold, 4 A, working height 2.0 mm: GND from the target board", ds=HARWIN_DS),
    "U1": dict(label="Sensirion SHT45", sym="SHT4x", fp=FP_SHT, value="SHT45", nets={"1": "SDA", "2": "SCL", "3": "+3V3", "4": "GND"},
               pos=(S_F, 0.0, 0), mfr="Sensirion", mpn="SHT45-AD1B-R2",
               desc="Humidity and temperature sensor, I2C 0x44", ds=SHT_DS),
    "C1": dict(label="100nF", sym="C", fp=FP_C, value="100nF", nets={"1": "+3V3", "2": "GND"},
               pos=(S_F + 2.6, 0.0, 90), mfr="any", mpn="0402 X7R 100 nF 16 V",
               desc="SHT45 decoupling", ds=""),
    "MK1": dict(sym="DMM-4026-B-I2S", fp=FP_MIC, value="DMM-4026-B-I2S-R",
                nets={"1": "MIC_GND", "2": "MIC_GND", "3": "MIC_3V3", "4": "MIC_GND", "5": "I2S_WS", "6": "I2S_SCK",
                      "7": "I2S_SD"},
                pos=(MIC_XC, MIC_FLEX_Y, 90), mfr="PUI Audio", mpn="DMM-4026-B-I2S-R",
                desc="I2S MEMS microphone, bottom port, 1.62-3.63 V; LR low = left channel", ds=MIC_DS),
    "C2": dict(label="100nF", sym="C", fp=FP_C, value="100nF", nets={"1": "MIC_3V3", "2": "MIC_GND"},
               pos=(MIC_XC + 2.8, 1.0, 90), mfr="any", mpn="0402 X7R 100 nF 16 V",
               desc="Microphone decoupling", ds=""),
    "R1": dict(label="100k", sym="R", fp=FP_R, value="100k", nets={"1": "I2S_SD", "2": "MIC_GND"},
               pos=(MIC_XC - 2.9, 2.0, 270), mfr="any", mpn="0402 1% 100 kOhm",
               desc="I2S SD pull-down (microphone datasheet)", ds=""),
}

# 5 V flex jumper (R9, no wires): wiring board J2 (Hirose FH12-6S, slide lock) -> pass-through -> pad
# end on the insert shelf, under the sensor flex's spring fingers. Single copper layer. Flat
# coordinates: X along the strip from the connector-end tip, Y across it; on the pad end (copper up)
# Y = room x - the pad end's centre line, and room y = TARGET_Y[1] - (X - PE_X0).
PE_W = FLANGE_OUT[0] / 2 + SHELF_OUT + (SHELF_TOP_Z - SHELF_UNDER_Z) - 0.15 - (FLANGE_OUT[0] / 2 + 0.15)
PE_CX = FLANGE_OUT[0] / 2 + 0.15 + PE_W / 2                  # pad end centre line (room x)
PE_LEN = TARGET_Y[1] - TARGET_Y[0]
END_W, END_L, END_T = JUMPER_END                              # connector end: width, stiffened length, thickness
PE_X0 = END_L + jumper_length() - 0.5                         # the jumper's path ends 0.5 mm into the pad end
JUMPER_LEN = PE_X0 + PE_LEN
FPC_PITCH, FPC_PAD = 0.5, (3.0, 0.3)                          # MEASURE contact pads (length x, width y), FH12 FPC spec
CONTACT_PAD = (4.5, 1.8)                                      # gold pad under a spring finger (x along the strip, y)
TRACK_W = 0.5                                                 # +5V / GND (MSR-2 < 0.2 A)
GND_Y, P5_Y = -1.05, 0.75                                     # run lanes; GND passes the +5V pad on the -Y side
PE_HALF, RUN_HALF = PE_W / 2, JUMPER_W / 2


def pe_x(room_y):
    """Flat X of a point on the pad end at room y."""
    return PE_X0 + (TARGET_Y[1] - room_y)


CONTACT_Y = (FINGER_X - PE_CX)                                # finger contact line across the pad end
# Battery-free tongue (D-41) off the pad end's inner edge, between the contact pads: through the flange tunnel,
# down the pocket-wall groove and the wall (two 90 deg bends, copper stays up), then on the floor: run, down
# strip, pad strip (floor_na.tongue_path). Flat: X = pe_x(room y) throughout; Y below the pad end follows the
# path length, on the floor Y = tongue_y(room x).
_x_pe = FLANGE_OUT[0] / 2 + 0.15
_out_x, _in_x = tongue_walls()
_xg = _out_x + BC_NA_GROOVE_D - JUMPER_T / 2 - 0.05
_xw = _in_x - JUMPER_T / 2 - 0.05
_zt = TARGET_TOP_Z - JUMPER_T / 2
_zf = SEAT_Z + BC_FLOOR_T - JUMPER_T / 2 - BC_RECESS_CLR
TONGUE_L = (_x_pe - _xg) + (_zt - BC_NA_GROOVE_BOT - 1.2) + hypot(_xg - _xw, 1.2) + (BC_NA_GROOVE_BOT - _zf)


def tongue_y(room_x):
    """Flat Y of a point on the pocket floor at room x (tongue)."""
    return -PE_HALF - TONGUE_L - (_xw - room_x)


_xd, _wd, _y_pad = BC_NA_DOWN
_ps = (BC_FINGERS[0][0] - BC_TONGUE_W / 2, BC_FINGERS[0][0] + BC_TONGUE_W / 2)
_y_bot = min(y for _, y in BC_FINGERS) - BC_FLOOR_PAD[1] / 2 - 1.0
_ta, _tb = pe_x(BC_NA_TONGUE_Y + BC_NA_NECK_W / 2), pe_x(BC_NA_TONGUE_Y - BC_NA_NECK_W / 2)
_d1, _p1 = pe_x(_y_pad), pe_x(_y_bot)
TONGUE_PTS = [(_ta, -PE_HALF), (_ta, tongue_y(_xd - _wd / 2)), (_d1, tongue_y(_xd - _wd / 2)), (_d1, tongue_y(_ps[0])),
              (_p1, tongue_y(_ps[0])), (_p1, tongue_y(_ps[1])), (_d1, tongue_y(_ps[1])), (_d1, tongue_y(_xd + _wd / 2)),
              (_tb, tongue_y(_xd + _wd / 2)), (_tb, -PE_HALF)]
TONGUE_PTS = [q for i, q in enumerate(TONGUE_PTS)                  # drop repeated corners (strip edges that line up)
              if i == 0 or abs(q[0] - TONGUE_PTS[i - 1][0]) + abs(q[1] - TONGUE_PTS[i - 1][1]) > 1e-6]
TONGUE_LANES = (pe_x(BC_NA_TONGUE_Y + 0.55), pe_x(BC_NA_TONGUE_Y - 0.55))   # GND (F), +5V (B) down the tongue
TONGUE_TURN = (16.2, 14.6, 9.0)             # floor: GND / +5V turn at these room x, their vias at room y 9.0
FP_FLOOR_CONTACT = "Contact_Pad_7x4mm"
JUMPER_OUTLINE = [(0.0, -END_W / 2), (END_L, -END_W / 2), (END_L + 2.0, -RUN_HALF), (PE_X0 - 2.0, -RUN_HALF),
                  (PE_X0, -PE_HALF)] + TONGUE_PTS + [(JUMPER_LEN, -PE_HALF), (JUMPER_LEN, PE_HALF), (PE_X0, PE_HALF),
                  (PE_X0 - 2.0, RUN_HALF), (END_L + 2.0, RUN_HALF), (END_L, END_W / 2), (0.0, END_W / 2)]
JUMPER_STIFFENERS = [((0.0, -END_W / 2), (END_L, END_W / 2)),             # connector end: to FPC thickness
                     ((PE_X0, -PE_HALF), (JUMPER_LEN, PE_HALF))]          # pad end: to the old target's 0.6 mm
# FPC contacts 1-3 GND (Y < 0), 4-6 +5V (Y > 0), matching J2's pins (check the contact side on a sample)
JUMPER_PARTS = {"J1": dict(sym="Conn_01x06", fp=FP_FPC, value="FPC 6P 0.5 mm", label="to FH12-6S: 1-3 GND 4-6 +5V",
                           nets={str(n): "GND" if n <= 3 else "+5V" for n in range(1, 7)},
                           pos=(0.2 + FPC_PAD[0] / 2, 0.0, 0), in_bom=False,
                           desc="Flex contacts into J2 of the wiring board (Hirose FH12-6S, slide lock)")}
JUMPER_PARTS.update({
    "TP1": dict(sym="TestPoint", fp=FP_TP_CONTACT, value="+5V contact", nets={"1": "+5V"}, in_bom=False, label="+5V",
                pos=(pe_x(FINGER_Y[1]), CONTACT_Y, 0), desc="Under the +5 V spring finger (sensor flex J2)"),
    "TP2": dict(sym="TestPoint", fp=FP_TP_CONTACT, value="GND contact", nets={"1": "GND"}, in_bom=False, label="GND",
                pos=(pe_x(FINGER_Y[0]), CONTACT_Y, 0), desc="Under the GND spring finger (sensor flex J3)"),
    "TP3": dict(sym="TestPoint", fp=FP_FLOOR_CONTACT, value="+5V floor pad", nets={"1": "+5V"}, in_bom=False,
                label="+5V", pos=(pe_x(BC_FINGERS[0][1]), tongue_y(BC_FINGERS[0][0]), 0),
                desc="Floor pad under the back cover's +5V finger (D-41)"),
    "TP4": dict(sym="TestPoint", fp=FP_FLOOR_CONTACT, value="GND floor pad", nets={"1": "GND"}, in_bom=False,
                label="GND", pos=(pe_x(BC_FINGERS[1][1]), tongue_y(BC_FINGERS[1][0]), 0),
                desc="Floor pad under the back cover's GND finger (D-41)"),
})


# Replacement back cover flex (D-35): two S7081-42R spring fingers on the pad section (on the cover's
# ledge, copper down, fingers through windows onto the plate's floor pads) -> run -> one 90 deg bend at
# the terminal end -> two more S7081-42R on the cell axes against the remote's battery contacts. Single
# copper layer, copper outside the bend. Flat coordinates, seen from the copper side: X = -x (remote),
# Y = y on the ledge; on the end section a point h above the bend line maps to Y = y_copper - h.
COVER_CONFIRMED = False                                     # positions are REF / MEASURE (FCC photos)
COVER_TRACK = 0.3
_y_c = BC_COPPER_Y                                          # end section copper face (room y) = bend line
_yt = max(y for _, y in BC_FINGERS) + FINGER[1] / 2 + BC_PEG_END
_yb = min(y for _, y in BC_FINGERS) - FINGER[1] / 2 - 1.0
_yj = _yb - BC_JOG
_xs0, _xs1 = -BC_STRIP[1], -BC_STRIP[0]                     # pad section in flat X
_xr0, _xr1 = -BC_RUN[1], -BC_RUN[0]                         # run in flat X
_xo = BC_CELL_X + BC_CONTACT_W / 2 + 0.5                    # end section half width
_xi = BC_PCB_W / 2 + BC_PCB_CLR                             # notch round the remote's PCB strip
_c = BC_END_CORNER
COVER_Y_BAND = _y_c - BC_BRIDGE_H                           # band under the PCB strip
COVER_Y_END = _y_c - BC_END_H
COVER_Y_PAD = _y_c - (BC_CELL_Z - BC_FLEX_Z)                # contact fingers on the cell axes
COVER_BEND_Y = _y_c
COVER_OUTLINE = [(_xs0, _yt), (_xs1, _yt), (_xs1, _yb), (_xr1, _yb), (_xr1, _y_c), (_xo - _c, _y_c), (_xo, _y_c - _c),
                 (_xo, COVER_Y_END), (_xi, COVER_Y_END), (_xi, COVER_Y_BAND), (-_xi, COVER_Y_BAND),
                 (-_xi, COVER_Y_END), (-_xo, COVER_Y_END), (-_xo, _y_c - _c), (-_xo + _c, _y_c), (_xr0, _y_c),
                 (_xr0, _yj), (_xs0, _yj)]
COVER_STIFF = [((-_xo, COVER_Y_END), (_xo, _y_c))]          # FR4 BC_END_T behind the end section (non-copper side)
COVER_PAD_STIFF = [((_xs0, _yb), (_xs1, _yt)),                # FR4 BC_PAD_STIFF_T on the pad and regulator sections
                   ((min(_xs0, _xr0), _yj), (max(_xs1, _xr1), _yb))]
COVER_PEG_HOLES = [(-x, y) for x, y in BC_PEGS]              # heat-stake pegs of the cover through flex + stiffener
COVER_LANES = (_xr1 - 0.75, _xr0 + 0.75)                    # +3V3 (inner), GND (outer) down the run
COVER_PARTS = {
    "J1": dict(sym="Conn_01x01", fp=FP_FINGER, value="S7081-42R +5V", nets={"1": "+5V"}, label="S7081-42R",
               pos=(-BC_FINGERS[0][0], BC_FINGERS[0][1], 90), mfr="Harwin", mpn="S7081-42R",
               desc="SMT spring finger, gold, 4 A, working height 2.0 mm: +5 V from the plate's floor pad", ds=HARWIN_DS),
    "J2": dict(sym="Conn_01x01", fp=FP_FINGER, value="S7081-42R GND", nets={"1": "GND"}, label="S7081-42R",
               pos=(-BC_FINGERS[1][0], BC_FINGERS[1][1], 90), mfr="Harwin", mpn="S7081-42R",
               desc="SMT spring finger, gold, 4 A, working height 2.0 mm: GND from the plate's floor pad", ds=HARWIN_DS),
    "J3": dict(sym="Conn_01x01", fp=FP_FINGER, value="S7081-42R VBAT", nets={"1": "+3V3"}, label="S7081-42R",
               pos=(-BC_VBAT_X * BC_CELL_X, COVER_Y_PAD, 0), mfr="Harwin", mpn="S7081-42R",
               desc="SMT spring finger, gold, 4 A, working height 2.0 mm: on the remote's VBAT (P1) contact plate",
               ds=HARWIN_DS),
    "J4": dict(sym="Conn_01x01", fp=FP_FINGER, value="S7081-42R GND", nets={"1": "GND"}, label="S7081-42R",
               pos=(BC_VBAT_X * BC_CELL_X, COVER_Y_PAD, 0), mfr="Harwin", mpn="S7081-42R",
               desc="SMT spring finger, gold, 4 A: on the remote's GND (P2) leaf spring", ds=HARWIN_DS),
    # 3.3 V for the remote (D-41): copper down in a recess in the cover; pin 1 IN, 2 GND, 3 EN, 4 NC, 5 OUT
    "U1": dict(sym="TLV75533PDBV", fp=FP_SOT, value="TLV75533PDBVR", label="TI TLV75533PDBVR",
               nets={"1": "+5V", "2": "GND", "3": "+5V", "5": "+3V3"}, pin_names={"4": "NC"},
               pos=(-BC_REG["U1"][0], BC_REG["U1"][1], 90),
               mfr="Texas Instruments", mpn="TLV75533PDBVR",
               desc="LDO 3.3 V 500 mA, 1.45-5.5 V in, SOT-23-5: the remote's supply from +5 V", ds=TLV_DS),
    "C3": dict(label="1uF", sym="C", fp=FP_C, value="1uF", nets={"1": "GND", "2": "+5V"},
               pos=(-BC_REG["C3"][0], BC_REG["C3"][1], 0), mfr="Murata", mpn="GRM155R61A105KE15D",
               desc="LDO input capacitor, 1 uF 10 V X5R 0402 (TLV755P: >= 1 uF)", ds=""),
    "C4": dict(label="1uF", sym="C", fp=FP_C, value="1uF", nets={"1": "GND", "2": "+3V3"},
               pos=(-BC_REG["C4"][0], BC_REG["C4"][1], 0), mfr="Murata", mpn="GRM155R61A105KE15D",
               desc="LDO output capacitor, 1 uF 10 V X5R 0402 (TLV755P: >= 1 uF)", ds=""),
}

def uid(*parts):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "smart-wallplate/sensor/" + "/".join(parts)))
