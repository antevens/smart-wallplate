"""EU sensor flex (D-30, D-41): parts and flat layout for gen_sensor.py.

Same topology as the NA flex (sensor_parts.py): plug end under the MSR-2 on CN2, 45 deg fold 1 into
the right channel, rise to just under the face skin, microphone on its outer side, dip to just above
the cap where the 5 V board's spring pins press on two pads on its underside, rise, 45 deg fold 2 and
the SHT45 on the tail. Battery-free tongue (D-41) off the pad section's inner edge between the pin
pads, under the pocket wall, 45 deg fold on the pocket floor, floor pads under the back cover's
fingers. Single copper layer. Flat coordinates, seen from the copper side: X along the strip
(developed length through the dip), Y = FLEX_X - room x (+Y inwards); the tongue is unfolded about
its fold into the same plane.
"""
import sys
from math import hypot
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "cad" / "build123d" / "eu"))
sys.path.insert(0, str(ROOT / "cad" / "build123d"))
import params_eu as E                                         # noqa: E402
import sensor_parts as sp                                     # noqa: E402

NAME = "eu_sensor_flex"
CN2_CONFIRMED = sp.CN2_CONFIRMED
T = E.FLEX_T
Z_LO, Z_HI, Z_PIN = E.FLEX_LO_Z + T / 2, E.FLEX_HI_Z + T / 2, E.FLEX_PIN_Z + T / 2
Z_SHT = E.SKIN_Z - 0.5 - E.SHT_CHIP[2] - T / 2
PIN_Y = (min(y for _, y in E.PINS) - E.FLEX_PAD_D / 2 - 1.0, max(y for _, y in E.PINS) + E.FLEX_PAD_D / 2 + 1.0)
DIP_IN = (PIN_Y[1] + E.FLEX_DIP, PIN_Y[1])
DIP_OUT = (PIN_Y[0], PIN_Y[0] - E.FLEX_DIP)
L_DIP = hypot(E.FLEX_DIP, Z_HI - Z_PIN)
S_B = E.FLEX_X - E.MSR_CN2_X                                  # plug -> fold 1
_y_c = E.MSR_Y - E.FLEX_RISE_DY
S_C = S_B + hypot(E.FLEX_RISE_DY, Z_HI - Z_LO)                # end of the rise
_S1 = S_C + (_y_c - DIP_IN[0]) + L_DIP                        # pad section starts
_S2 = _S1 + (DIP_IN[1] - DIP_OUT[0])
_S3 = _S2 + L_DIP


def s(y):
    """Flat X of a point in the right channel at room y (through the dip)."""
    if y >= DIP_IN[0]:
        return S_C + (_y_c - y)
    if y >= DIP_IN[1]:
        return S_C + (_y_c - DIP_IN[0]) + (DIP_IN[0] - y) / E.FLEX_DIP * L_DIP
    if y >= DIP_OUT[0]:
        return _S1 + (DIP_IN[1] - y)
    if y >= DIP_OUT[1]:
        return _S2 + (DIP_OUT[0] - y) / E.FLEX_DIP * L_DIP
    return _S3 + (DIP_OUT[1] - y)


def fy(room_x):
    return E.FLEX_X - room_x


S_D = s(E.SHT_Y)                                              # fold 2
S_F = S_D + (E.FLEX_X - E.SHT_ENTRY) + hypot(E.SHT_ENTRY, Z_HI - Z_SHT)
TAIL_X = S_F + 3.6
HALF = E.FLEX_W / 2
PLUG_HALF, PLUG_LEN = E.FLEX_PLUG[1] / 2, E.FLEX_PLUG[0] / 2
NECK_X = PLUG_LEN + E.FLEX_NECK_L
MIC_XC = s(E.MIC_Y)
MIC_Y_FLAT = fy(E.MIC_X)
MX0, MX1 = s(E.MIC_Y + E.EU_MIC_SEC[1] / 2), s(E.MIC_Y - E.EU_MIC_SEC[1] / 2)
MIC_W = E.EU_MIC_SEC[0]
PX0, PX1 = s(PIN_Y[1]), s(PIN_Y[0])
PAD_Y = (fy(E.FLEX_PAD_SEC[1]), fy(E.FLEX_PAD_SEC[0]))        # pad section across (outer, inner)

# tongue: room points after the 45 deg fold map back by the reflection about the fold square's diagonal
_cx, _cy = E.EU_FOLD_X, E.EU_TONGUE_Y
_h = E.EU_TONGUE_W / 2


def unfold(room_x, room_y):
    """Room point on the floor after the fold -> its place on the unfolded strip (room plane)."""
    return _cx - (room_y - _cy), _cy - (room_x - _cx)


def flat_floor(room_x, room_y, folded=True):
    xu, yu = unfold(room_x, room_y) if folded else (room_x, room_y)
    return s(yu), fy(xu)


_y_top = max(y for _, y in E.BC_FINGERS) + E.BC_FLOOR_PAD[1] / 2 + 0.5
_y_bot = min(y for _, y in E.BC_FINGERS) - E.BC_FLOOR_PAD[1] / 2 - 1.0
_f0, _f1 = _cx - _h, _cx + _h
_side_x1 = _f0 - 0.3
# unfolded extents: the strip up (room x EU_STRIP_X0.._f1, y _cy+_h.._y_top), the part beside the fold
_up_x = (s(_cy - (E.EU_STRIP_X0 - _cx)), s(_cy - (_f1 - _cx)))        # flat X (low, high)
_up_y = (fy(_cx - (_cy + _h - _cy)), fy(_cx - (_y_top - _cy)))         # flat Y (low, high)
_side_x = (s(_cy - (E.EU_STRIP_X0 - _cx)), s(_cy - (_side_x1 - _cx)))
_side_y = (fy(_cx - (_y_bot - _cy)), _up_y[0])
_run_x = (s(_cy + _h), s(_cy - _h))
TONGUE_PTS = [(_run_x[1], PAD_Y[1]), (_run_x[1], _up_y[1]), (_up_x[0], _up_y[1]), (_up_x[0], _side_y[0]),
              (_side_x[1], _side_y[0]), (_side_x[1], _side_y[1]), (_run_x[0], _up_y[0]), (_run_x[0], PAD_Y[1])]
FOLD_LINE = ((_run_x[0], fy(_f1)), (_run_x[1], fy(_f0)))      # 45 deg fold across the run (flat)
TONGUE_LANES = (s(_cy + 0.4), s(_cy - 0.4))                   # GND (from the GND pin pad), +5V

FLEX_OUTLINE = [(-PLUG_LEN, -PLUG_HALF), (PLUG_LEN, -PLUG_HALF), (NECK_X, -HALF), (MX0, -HALF), (MX0, -MIC_W),
                (MX1, -MIC_W), (MX1, -HALF), (PX0, -HALF), (PX0, PAD_Y[0]), (PX1, PAD_Y[0]), (PX1, -HALF),
                (TAIL_X, -HALF), (TAIL_X, HALF), (PX1, HALF), (PX1, PAD_Y[1])] + TONGUE_PTS + \
               [(PX0, PAD_Y[1]), (PX0, HALF), (NECK_X, HALF), (PLUG_LEN, PLUG_HALF), (-PLUG_LEN, PLUG_HALF)]
FOLDS = (S_B, S_D)
_mic_stiff = ((MIC_XC - E.MIC[1] / 2 - 0.5, MIC_Y_FLAT - E.MIC[0] / 2 - 0.5),
              (MIC_XC + E.MIC[1] / 2 + 0.5, MIC_Y_FLAT + E.MIC[0] / 2 + 0.5))
STIFFENERS = [((-PLUG_LEN, -PLUG_HALF), (PLUG_LEN, PLUG_HALF)), ((PX0, PAD_Y[0]), (PX1, PAD_Y[1])), _mic_stiff]

# CN2 placeholder map (as sensor_parts: NOT the MSR-2's pinout): the order the single-layer lanes need here;
# GND on two contacts: GND (pin pad, tongue) and GND_SHT (the SHT45's own contact), joined on the MSR-2
CN2_MAP = {"19": "GND", "21": "+5V", "23": "GND_SHT", "25": "SDA", "27": "SCL", "29": "+3V3",
           "20": "MIC_3V3", "22": "MIC_GND", "24": "I2S_SD", "26": "I2S_SCK", "28": "I2S_WS"}
FP_PIN_PAD = "Contact_Pad_D2.4mm"
FP_FLOOR_PAD = "Contact_Pad_2.9x7mm"
_pad_c = ((E.EU_PAD_X[0] + E.EU_PAD_X[1]) / 2, [y for _, y in E.BC_FINGERS])
PARTS = {
    "J1": dict(sym="Conn_02x15_Odd_Even", fp=sp.FP_B2B, value="CN2 mate (TBD)", label="CN2 mate (TBD)",
               nets=dict(CN2_MAP), pos=(0.0, 0.0, 0), mfr="TBD", mpn="TBD",
               desc="Board-to-board plug mating the MSR-2's rear connector CN2, 0.4 mm, 2 rows (part and "
                    "contact map unconfirmed)", ds=""),
    "TP1": dict(sym="TestPoint", fp=FP_PIN_PAD, value="GND pin pad", nets={"1": "GND"}, in_bom=False, label="GND",
                pos=(s(E.PINS[0][1]), fy(E.PINS[0][0]), 0), desc="Under the 5 V board's GND spring pin (P1)"),
    "TP2": dict(sym="TestPoint", fp=FP_PIN_PAD, value="+5V pin pad", nets={"1": "+5V"}, in_bom=False, label="+5V",
                pos=(s(E.PINS[1][1]), fy(E.PINS[1][0]), 0), desc="Under the 5 V board's +5V spring pin (P2)"),
    "TP3": dict(sym="TestPoint", fp=FP_FLOOR_PAD, value="+5V floor pad", nets={"1": "+5V"}, in_bom=False,
                label="+5V", pos=(*flat_floor(_pad_c[0], _pad_c[1][0]), 0),
                desc="Floor pad under the back cover's +5V finger (D-41)"),
    "TP4": dict(sym="TestPoint", fp=FP_FLOOR_PAD, value="GND floor pad", nets={"1": "GND"}, in_bom=False,
                label="GND", pos=(*flat_floor(_pad_c[0], _pad_c[1][1]), 0),
                desc="Floor pad under the back cover's GND finger (D-41)"),
    "U1": dict(label="Sensirion SHT45", sym="SHT4x", fp=sp.FP_SHT, value="SHT45",
               nets={"1": "SDA", "2": "SCL", "3": "+3V3", "4": "GND_SHT"}, pos=(S_F, 0.0, 0), mfr="Sensirion",
               mpn="SHT45-AD1B-R2", desc="Humidity and temperature sensor, I2C 0x44", ds=sp.SHT_DS),
    "C1": dict(label="100nF", sym="C", fp=sp.FP_C, value="100nF", nets={"1": "+3V3", "2": "GND_SHT"},
               pos=(S_F + 2.6, 0.0, 90), mfr="any", mpn="0402 X7R 100 nF 16 V", desc="SHT45 decoupling", ds=""),
    "MK1": dict(sym="DMM-4026-B-I2S", fp=sp.FP_MIC, value="DMM-4026-B-I2S-R",
                nets={"1": "MIC_GND", "2": "MIC_GND", "3": "MIC_3V3", "4": "MIC_GND", "5": "I2S_WS", "6": "I2S_SCK",
                      "7": "I2S_SD"},
                pos=(MIC_XC, MIC_Y_FLAT, 90), mfr="PUI Audio", mpn="DMM-4026-B-I2S-R",
                desc="I2S MEMS microphone, bottom port, 1.62-3.63 V; LR low = left channel", ds=sp.MIC_DS),
    "C2": dict(label="100nF", sym="C", fp=sp.FP_C, value="100nF", nets={"1": "MIC_3V3", "2": "MIC_GND"},
               pos=(MIC_XC - 3.75, MIC_Y_FLAT - 2.08, 90), mfr="any", mpn="0402 X7R 100 nF 16 V",
               desc="Microphone decoupling", ds=""),
    "R1": dict(label="100k", sym="R", fp=sp.FP_R, value="100k", nets={"1": "MIC_GND", "2": "I2S_SD"},
               pos=(MIC_XC - 2.8, MIC_Y_FLAT - 0.575, 90), mfr="any", mpn="0402 1% 100 kOhm",
               desc="I2S SD pull-down (microphone datasheet)", ds=""),
}
