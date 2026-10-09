"""EU variant (D-30): geometry for a round EU flush box (DIN 49073, 68 mm hole saw, Ø60 inside).

A design of its own (shares only the BILRESA, the MSR-2, the SHT45 and the microphone with the NA
plate). Coordinates as in params.py, origin = box centre = remote centre: X width, Y up, Z out of
the wall, z = 0 the wall surface, z < 0 inside the box (MAINS SIDE).

- The BILRESA cannot go below the wall in a Ø60 box (its flat back alone spans ~Ø60), so it sits
  on a 1.6 mm V-0 floor over the box, its top flush with the face: the plate stands out by the
  floor plus the remote.
- The barrier is one flat V-0 cap over the box and the seal band: the floor under the remote, a
  cup down to the panel of the emergency rocker (Marquardt 1802.2504, DPST, PCB pins) under the
  remote's upper half, two holes for the 5 V board's spring pins. Two countersunk screws into the
  box's top and bottom domes, in the pocket floor under the remote.
- The supplied magnet is glued to the floor's underside (box side), under the back cover's steel plate.
- Two boards (D-36). The mains board, at the rocker's PCB seat, carries the rocker, two WAGO
  2604-3102 push-in blocks (L in / switched, N in / switched; wires enter from the back of the box),
  fuse, MOV and the PSU (Traco TMPS 03-105) over a routed relief slot; the PSU's outputs land on a
  5 V island cut off by the slot, with a pin header. The 5 V board, just under the cap, takes 5 V
  from that header through a pin socket and carries the two spring pins that reach through the cap
  onto gold pads on the sensor flex (R9, R10). Both hang from bosses under the cap.
- The trim (PETG) carries everything visible: face, remote pocket walls, finger scoops, MSR-2 and
  SHT45 bays. Two M2 screws through tabs at the bottom of the pocket wall (under the remote's
  rounded back edge) hold it to bosses under the cap.
"""
import sys
from math import sqrt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from params import (B_W, B_H, B_D, B_BACK_RUN, B_BACK_RISE, CLR, POCKET_WALL, MAGNET, MAGNET_Y, MAGNET_END_R,  # noqa: E402,F401
                    MSR, RADAR_WALL, MSR_HOOK, LUX_POS, SHT, SKIN, FACE_CHAMFER, PR, SPLIT_CLR, BARRIER_MIN, V0_RATED_T,
                    PASS_D, MSR_BOARD, MSR_CN2_IN, B2B, B2B_STACK, FLEX_W, FLEX_T, STIFF_T, FLEX_SKIN_GAP,
                    FLEX_PLUG, FLEX_NECK_L, flex_half_width, SHT_CHIP, MIC, MIC_PORT_IN, MIC_FLEX_Y, MIC_FLEX_HOLE_D,
                    MIC_GASKET_D, MIC_SKIN_HOLE_D, BC_FLOOR_T, BC_FLOOR_CLR, BC_TONGUE_W, BC_TONGUE_Y,
                    BC_FINGERS, BC_FLOOR_PAD, BC_DOME_DY, BC_STEEL_FLOOR, BC_STEEL_Y, BC_STEEL, BC_RECESS_CLR,
                    SW_CUT, SW_PANEL_T, SW_BEZEL, SW_ROCKER_H, SW_ROCKER_TOL, SW_ROCKER_CLR, SW_BODY, SW_PIN_GRID, PAD_BODY_GAP)

VARIANT = "eu"

# ---- EU flush box: DIN 49073, Ø68 hole saw ----
# Catalogue values (DIN 49073 box listings, e.g. Kaiser 1555-04; docs/MEASUREMENTS.md), not measured.
BOX_DIA = 60.0                            # MEASURE inside diameter = device opening
BOX_HOLE = 68.0                           # MEASURE hole in the wall (box rim outer diameter)
BOX_D = 47.0                              # MEASURE standard depth
DOME_PITCH = 60.0                         # MEASURE device screw domes: 4 per box at 90 deg, on the box wall
DOME_D = 7.0                              # MEASURE screw dome diameter, full box depth, top at the wall plane
DOME_CLR = 0.75                           # board / parts to a dome
SCREW_D, SCREW_HEAD_D = 3.2, 6.0          # MEASURE device screws 3.2 mm, countersunk head
PLUG_CLR = 0.75                           # cap cup / board to the box wall
COLLAR_LIP = 1.25                         # flat seal band on the wall beyond the box hole
WIRE_SPACE_MIN = 10.0                     # free depth wanted behind the deepest part (reported, not enforced: human
                                          # decision 2026-10-08, depth to be tested in a box)

# ---- emergency rocker: Marquardt 1802.2504, DPST, PCB pins (as the NA plate, D-26; values in params.py) ----
SW_Y = 12.5                               # rocker centre: cup clear of the top screw dome and of the magnet
SW_SW_DIR = -1                            # switched pins (1a / 2a) 7 mm below the in pins (1 / 2, on SW_Y)

# ---- remote and plate ----
B_PROUD = 0.0                             # remote top flush with the face
CAP_T = BARRIER_MIN                       # cap floor = barrier (V-0)
CAP_MARGIN = 0.5                          # cap beyond the seal band and the pocket walls
TRIM_TAB = (3.0, 8.0, 1.0)                # pocket-wall tab into the pocket (x depth, y length, thickness)
TRIM_SCREW_Y = 9.0                        # trim screws at (+-x, y): clear of the cup and the PSU
TRIM_SCREW_D, TRIM_HEAD_D = 2.0, 3.8      # M2 thread-forming screw, countersunk flush in the tab
TRIM_BOSS_D, TRIM_BOSS_L = 6.0, 5.0       # boss under the cap floor (box side), clear of the 5 V board
MSR_GAP = 1.0                             # pocket walls / cap to the MSR-2 and SHT45 bay frames

# ---- sensor flex (D-27 / D-29 topology): MSR-2 CN2 -> right channel -> SHT45 ----
FLEX_X = 27.5                             # flex centre line in the right channel (pocket wall 24.6 .. skin 37.85),
                                          # over the spring pins
FLEX_RISE_DY = 12.0                       # run along y over which the flex rises from the plug level to under the skin
MIC_Y = 28.0                              # mic body centre along the channel
# power contact (R9, no wires): two spring pins on the 5 V board's front reach up through two holes in
# the cap and press on gold pads on the flex, which dips to just above the cap there; a rib from the
# trim's face skin backs the flex over the pins.
# Harwin P70-2200045, SMT with peg (drawing P70-2200045 iss. 2, 2021-06-04): heights above the board
PIN_FREE, PIN_WH, PIN_WH_MAX, PIN_WH_MIN = 8.20, 7.10, 7.20, 6.40   # DATASHEET free, normal, max, min working
PIN_DESIGN_WH, PIN_TOL = 6.8, 0.3         # design working height (mid-range) and the stack tolerance it absorbs
PIN_FLANGE = (2.00, 1.00)                 # DATASHEET flange diameter, height
PIN_BARREL_D, PIN_PLUNGER_D = 1.54, 0.90  # DATASHEET barrel, plunger tip
PIN_PAD_D, PIN_HOLE_D = 2.20, 1.20        # DATASHEET recommended solder pad, through hole for the peg
PINS = ((25.9, -4.6), (25.9, -9.0))       # GND, +5 V (room x, y): on the 5 V board, clear of the right dome;
                                          # GND first so the tongue's lanes need no crossing after its fold (D-41)
PIN_CAP_HOLE_D = 1.9                      # cap hole round each pin (barrel 1.54)
PIN_FLEX_GAP = 0.3                        # flex underside above the cap top at the pins
FLEX_PAD_D = 2.4                          # gold pad on the flex under each pin (plunger tip 0.9)
FLEX_DIP = 12.0                           # run along y over which the flex drops to / rises from the pins
FLEX_PAD_SEC = (24.3, 30.2)               # flex widened over the pins (room x), into a recess in the pocket wall's foot
# battery-free tongue (D-41): leaves the pad section's inner edge between the pins (+5V from the +5V pin pad, GND
# from the GND pin pad, on one copper layer), under the pocket wall (trim notch), along the floor insert, 45 deg
# fold beside the floor pads (copper up), then the pad strip clear of the switch cup's opening
EU_TONGUE_Y = (PINS[0][1] + PINS[1][1]) / 2   # tongue centre (room y)
EU_TONGUE_W = 1.6                         # tongue width from the pad section to the fold
EU_FOLD_X = 17.6                          # 45 deg fold square centre (room x), beside the pads
EU_STRIP_X0 = 13.2                        # pad strip's inner edge: clear of the switch cup's opening
EU_PAD_X = (13.5, 16.3)                   # floor pads (room x) under the fingers at x 14, clear of the cup opening
WALL_RECESS = 0.6                         # trim pocket wall thinned at its foot over the pad section

# ---- 5 V board (D-shaped, just under the cap, below the switch cup) ----
WB_T = 1.6
WB_CUT_CLR = 1.0                          # board's straight edge below the switch cup
WB_MOUNT = ((-12.0, -22.0), (16.0, -21.0))  # board holes (M2, from pcb/eu), screwed to bosses under the cap
WB_MOUNT_D, WB_BOSS_D = 2.2, 5.0          # board hole; cap boss (tap-drilled for an M2 thread-forming screw)
FRONT_PARTS = {"C1": (3.2, 1.6, 1.8)}      # 1206 capacitor on the 5 V board's front

# ---- mains board (round, at the rocker's PCB seat) ----
MB_T = 1.6
MB_PSU_C = (0.0, -12.5)                   # PSU centre (on the back), inputs on its upper row
PSU = (25.4, 25.4, 16.3)                  # DATASHEET Traco TMPS 03-105 body w, h, height above the board (rev. 2026-07-01)
WAGO_EU = (12.6, 16.7, 21.3)              # DATASHEET WAGO 2604-3102 (3D model): body 12.4 wide, 0.1 off the poles' centre
                                          # (bound +-6.3 about it), depth, height above the board
WAGO_PITCH = 5.0                          # DATASHEET pin spacing (poles)
WAGO_ROW = 8.2                            # DATASHEET (WAGO 3D model 2604-3102): distance of the two solder-pin rows
WAGO_ROW_OFF = 0.65                       # DATASHEET (WAGO 3D model): rows' centre from the body centre, towards the
                                          # entry side (body 3.6 past the first row, 4.9 past the second, lever side)
MB_WAGO_C = ((16.6, 7.5), (-16.6, 7.5))   # L block (right), N block (left), body centres on the back; poles
                                          # along y, upper pole in, lower pole switched (as the rocker's poles);
                                          # levers towards the board centre
MB_SLOT = (-18.0, 18.0, -17.5, 2.0)       # routed relief slot under the PSU: x0, x1, y, width
MB_HDR = (-5.0, -20.5)                    # 2-pin header on the 5 V island (front): pin 1 (+5V) here, pin 2 (GND) 2.54 below
MB_BOSS = ((-17.5, 19.5), (17.5, 19.5), (-20.0, -12.0))  # mains board holes (M2) on long cap bosses: two beside
                                          # the switch cup, one through the 5 V board (the PSU end)
MB_BOSS_D, MB_BOSS_CLR = 6.0, 0.5         # long boss diameter; hole round it in the 5 V board (each side)
MB_FRONT_PARTS = {"RV1": (10.2, 8.0, 4.5),  # DATASHEET TDK CU4032 body (w, h, t)
                  "F1": (10.1, 3.1, 3.3)}  # REF Schurter UMT 250 body
HDR = (2.54, 5.08, 8.38)                  # DATASHEET Samtec TSM-102-01-L-SV (SMT): insulator 2.54 + post 5.84 above the board
HDR_BODY = 2.54                           # DATASHEET TSM insulator height
SOCKET = (2.54, 5.08, 8.5)                # DATASHEET 2.54 mm pin socket 1x2, 8.5 mm (on the 5 V board's back)

# ================= derived =================
BOX_R = BOX_DIA / 2
SEAL_R = BOX_HOLE / 2 + COLLAR_LIP
POCKET_IN = (B_W + 2 * CLR, B_H + 2 * CLR)
POCKET_OUT = (POCKET_IN[0] + 2 * POCKET_WALL, POCKET_IN[1] + 2 * POCKET_WALL)
SEAT_Z = CAP_T + BC_FLOOR_T                                # remote's back on the pocket-floor insert (D-35)
PT = SEAT_Z + B_D - B_PROUD                                # plate face
DECK_Z = PT - SKIN
CAP_R = max(SEAL_R, POCKET_OUT[1] / 2) + CAP_MARGIN        # cap disc (covers seal band and pocket walls)
# switch cup: from the floor down to the rocker's panel
CUP_IN = (SW_BEZEL[0] + 2 * CLR, SW_BEZEL[1] + 2 * CLR)
CUP_OUT = (CUP_IN[0] + 2 * BARRIER_MIN, CUP_IN[1] + 2 * BARRIER_MIN)
PANEL_TOP_Z = SEAT_Z - SW_ROCKER_CLR - SW_ROCKER_H - SW_ROCKER_TOL   # rocker top under the remote at max tolerance
PANEL_BOT_Z = PANEL_TOP_Z - SW_PANEL_T
SW_BOT_Z = PANEL_TOP_Z - SW_BODY[2]                        # rocker's PCB seat = mains board front
DOMES = ((0.0, DOME_PITCH / 2), (DOME_PITCH / 2, 0.0), (0.0, -DOME_PITCH / 2), (-DOME_PITCH / 2, 0.0))
SCREWS = (DOMES[0], DOMES[2])             # top and bottom domes: countersunk in the pocket floor, under the remote
# magnet glued under the floor at the back cover's steel plate
MAGNET_Z = (-MAGNET[2], 0.0)
EU_MAGNET_Y = min(BC_STEEL_Y, SW_Y - CUP_OUT[1] / 2 - 0.5 - MAGNET[1] / 2)   # under the cover's steel, clear of the cup
# 5 V board: circle less clearance, cut below the cup
WB_R = BOX_R - PLUG_CLR
FLEX_PIN_Z = CAP_T + PIN_FLEX_GAP                          # flex underside over the pins
WB_FRONT = FLEX_PIN_Z - PIN_DESIGN_WH                      # board front: pins at their design working height
WB_BACK = WB_FRONT - WB_T
WB_CUT_Y = SW_Y - CUP_OUT[1] / 2 - WB_CUT_CLR
MB_FRONT = SW_BOT_Z
MB_BACK = MB_FRONT - MB_T
DEEPEST = min(MB_BACK - PSU[2], MB_BACK - WAGO_EU[2])
HDR_GAP = WB_BACK - MB_FRONT                               # mains board front to the 5 V board's back
HDR_ENGAGE = (MB_FRONT + HDR[2]) - (WB_BACK - SOCKET[2])   # header post inside the socket
DOME_NOTCH_R = DOME_D / 2 + DOME_CLR      # board notch round a dome
# trim: finger notch left of the pocket (the right channel carries the flex), 45 deg sides so the
# face-down print needs no support
NOTCH = (6.0, 26.0, 5.0)                  # width (x, at the face), length (y, at the face), depth
NOTCH_X = POCKET_IN[0] / 2 + 0.5           # notch centre line: cuts into the pocket wall
NOTCH_BLOCK = 1.6                          # solid trim around the notch
TRIM_SCREW_X = POCKET_IN[0] / 2 - TRIM_HEAD_D / 2 - 0.2    # head clear of the pocket wall above the tab
MSR_Y = POCKET_OUT[1] / 2 + MSR_GAP + 1.6 + MSR[1] / 2 + CLR
SHT_Y = -(POCKET_OUT[1] / 2 + MSR_GAP + 1.6 + SHT[1] / 2 + 0.4)
PW = 2 * (CAP_R + SPLIT_CLR + SKIN)
PL_Y = (SHT_Y - SHT[1] / 2 - 0.4 - 1.6 - SKIN - 1.0, MSR_Y + MSR[1] / 2 + CLR + 1.6 + SKIN + 1.0)
PH = PL_Y[1] - PL_Y[0]
PC = (0.0, (PL_Y[0] + PL_Y[1]) / 2)                        # plate centre relative to the box centre

# sensor flex, derived
MSR_BACK_Z = PT - RADAR_WALL - MSR[2]
MSR_CN2_X = MSR_BOARD[0] / 2 - MSR_CN2_IN
SKIN_Z = PT - SKIN
FLEX_HI_Z = SKIN_Z - FLEX_SKIN_GAP - STIFF_T - FLEX_T     # flex underside in the channel
FLEX_LO_Z = MSR_BACK_Z - B2B_STACK - FLEX_T               # flex underside at the plug
EU_MIC_FLEX_Y = 2.5                                        # mic centre outwards of the flex centre line (room x)
MIC_X = FLEX_X + EU_MIC_FLEX_Y                             # mic on the outer side of the flex
EU_MIC_SEC = (5.7, MIC[1] + 8.0)                           # flex widened outwards over the mic: width from the
                                                           # centre line, length along the channel
MIC_PORT = (MIC_X, MIC_Y - (MIC[1] / 2 - MIC_PORT_IN))
SHT_ENTRY = SHT[0] / 2 + 0.4 + 1.6 + 1.0
