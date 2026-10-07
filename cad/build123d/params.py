"""Single source of truth for wall-plate geometry (mm).

Coordinates: X = width, Y = height (up), Z = out of the wall.
z = 0 is the wall surface, plate face at z = PT, z < 0 is inside the box (MAINS SIDE).

Tags:
  MEASURE   placeholder - replace with a caliper reading recorded in
            docs/MEASUREMENTS.md before printing anything final.
  DATASHEET value that must come from a cited datasheet (see docs/BOM.md).
  derived   computed below - do not edit, change the inputs instead.

Two printed parts (DESIGN D-12..D-17) and the wiring board (D-24..D-26):
  insert  (insert.py)  all barrier geometry: remote pocket, switch well and rocker
                       panel, collar flange. UL94 V-0 filament, printed floor-down.
  trim    (trim.py)    face, MSR-2 / SHT45 bays, vents. Any filament, face-down.
  board   (pcb/)       KiCad project; positions mirrored below and compared by checks.py.
"""
from math import sqrt, hypot

# ---- trim plate ----
PW, PH, PT, PR = 82.0, 150.0, 13.0, 6.0   # width, height, proud of wall, corner radius
SKIN = 2.0                                # face/side wall of the hollow trim
FACE_CHAMFER = 1.2

# ---- NA single-gang device box ----
BOX_W, BOX_H = 50.8, 76.2                 # 2" x 3" opening
BOX_D = 63.5                              # MEASURE (2.5" assumed), per room
SCREW_PITCH = 83.3                        # #6-32 device ears, 3-9/32"
SCREW_D, SCREW_HEAD_D = 3.8, 8.0

# ---- IKEA BILRESA scroll wheel remote (kept intact, batteries in) ----
# B_W/B_H: IKEA UK product size 45 x 70 mm, matched by a third-party mount pocket
# (45.4 x 70.4). Reference values, confirm with calipers (docs/MEASUREMENTS.md).
B_W, B_H, B_D = 45.0, 70.0, 20.0          # MEASURE stadium outline + depth (B_D placeholder)
B_BACK_RUN = 8.5                          # MEASURE flat back inset from the outline (each side); ~R8.5 round-over per the third-party pocket
B_BACK_RISE = 8.5                         # MEASURE height where the curved back meets the straight side
B_FRONT_R = 1.0                           # MEASURE front edge round-over
B_WHEEL_D = 36.0                          # MEASURE scroll wheel diameter
B_WHEEL_Y = 14.0                          # MEASURE wheel centre above the remote centre
B_WHEEL_GAP = 0.6                         # MEASURE gap ring around the wheel
B_LED_Y = -10.0                           # MEASURE three LED dots, y of the row
B_LED_PITCH = 4.5                         # MEASURE
B_SEAM_Z = 7.0                            # MEASURE parting line height above the back
B_PROUD = 2.0
CLR = 0.5                                 # remote to pocket wall; 0.6 no longer fits the box with B_W = 45
POCKET_WALL = 1.6                         # pocket shell = mains barrier
SEAT_T = 2.5                              # minimum material under the remote seat
# The remote has a steel plate inside; it ships with an adhesive magnet for walls.
# That magnet is glued into a recess in the pocket floor. The recess is deeper than
# the magnet by MAGNET_SETBACK: the air gap weakens the pull (shim it up to strengthen).
MAGNET = (20.5, 12.5, 1.5)                # MEASURE supplied adhesive magnet (w, h, t incl. tape)
MAGNET_Y = -3.0                           # MEASURE centre of the remote's internal plate (from remote centre); -3 clears the 1802 well
MAGNET_SETBACK = 0.5                      # magnet face below the seat
MAGNET_CLR = 0.3                          # recess clearance around the magnet
MAGNET_END_R = MAGNET[0] / 2              # MEASURE corner radius of the magnet's ends (placeholder: full round end)
MAGNET_SLOT_BOT = -(B_H / 2 - B_BACK_RUN) + MAGNET_CLR  # derived: recess runs down to the lower end of the flat back

# ---- emergency rocker: Marquardt 1802.2504, DPST, PCB pins (D-26) ----
# DATASHEET: Marquardt drawing 1802.2504 rev g (2003-09-16). Mounted turned 90 deg: the
# drawing's 21 x 24 flange is 24 (x) x 21 (y) here; poles are the left/right pin columns.
SW_CUT = (21.9, 19.4)                     # DATASHEET cutout for a 1.25-2 mm panel (19.4 x 21.9)
SW_PANEL_T = 1.5                          # DATASHEET snap-in range 0.75-3 mm (cutout length depends on it)
SW_BEZEL = (24.0, 21.0)                   # DATASHEET flange 21 x 24
SW_ROCKER_H = 5.3                         # DATASHEET rocker top above the panel face (5.3 +- 0.5)
SW_ROCKER_TOL = 0.5                       # DATASHEET tolerance on SW_ROCKER_H
SW_ROCKER_CLR = 0.5                       # rocker top to the remote's back at maximum tolerance
SW_BODY = (22.0, 18.6, 16.2)              # DATASHEET body 18.6 x 22; depth = PCB seat below the panel's FRONT face
SW_PIN_GRID = (10.2, 7.0)                 # DATASHEET hole grid: poles 10.2 apart (x), in/switched 7 (y)
SW_Y = 18.0

# ---- wiring board (single board, D-24/D-25; KiCad project in pcb/) ----
WB = (47.0, 72.0, 1.6)                    # front face (F) towards the plate, back (B) into the box
WB_Y = 0.0                                # board centre
IRM = (37.0, 24.0, 15.0)                  # DATASHEET Mean Well IRM-03-5 body (IRM-03-SPEC 2025-08-08), on B
IRM_C = (0.0, -21.39)                     # PSU body centre on the board (front-view x, y; from pcb/)
WAGO6 = (32.4, 19.2, 20.7)                # DATASHEET WAGO 2604-1106: width, depth along the board, height (on B)
WAGO_X, WAGO_Y = 3.0, 3.5                 # terminal block centre (front-view x, y; from pcb/)
WAGO_ENTRY = (0, 1)                       # direction the wire entries face (front-view x, y): away from the PSU
WAGO_PSU_GAP = 1.0                        # minimum gap from the block's closed back to the PSU body
J2_POS = (13.0, -19.0)                    # SMD 5 V connector on F (front-view x, y; from pcb/), right of the slot
WIRE_SPACE_MIN = 10.0                     # free depth wanted behind the terminal block

# ---- board mounting: screw-in snap posts (D-28) ----
# Four PC-FR posts screw into bosses on the insert's underside and snap through holes in the
# board. Threads are cut after printing, M4 x 0.7: the bosses' holes are printed at the tap-drill
# size and tapped, the posts' studs at the major diameter and cut with a die.
MOUNT_HOLES = ((-21.0, 33.5), (-21.0, -33.5), (21.0, 24.77), (21.0, -33.5))  # board holes (front-view x, y; from pcb/)
MOUNT_HOLE_D = 2.6                        # board hole (pcb MOUNT_D)
MOUNT_BOSS_D = 7.0                        # boss on the insert, stands on the print-bed plane Z_BOT
# boss tops: 1 mm into the corner taper; top right rises into the pocket corner under the remote's
# back round-over, just enough to keep BARRIER_MIN over the hole's cone tip
MOUNT_BOSS_TOP = (-1.6, -1.6, -2.55, -1.6)
MOUNT_THREAD_D, MOUNT_TAP_D = 4.0, 3.3    # M4 x 0.7: stud before the die, tap-drill hole
MOUNT_THREAD_L = 7.0                      # tapped depth (the hole ends in a 45 deg cone)
MOUNT_THREAD_MIN = 6.0                    # minimum engagement, 1.5 x M4
MOUNT_PASS_GAP = 1.0                      # boss to the 5 V pass-through channel
POST_SHAFT_D = 2.3                        # through the board hole
POST_SHOULDER_D = 4.5                     # carries the board's front face
POST_HEAD_D, POST_HEAD_H = 3.2, 1.8       # split cone head over the board's back face
POST_SPLIT_W, POST_SPLIT_L = 0.6, 4.5     # slot through head and shaft, length above the head
POST_HEX_AF, POST_HEX_H = 6.0, 2.0        # hex collar against the boss, across flats
POST_FLAT = 0.1                           # flat on the stud side so the post prints lying down

# ---- insert (box side, V-0) ----
PLUG_CLR = 0.75                           # insert body to box wall, each side
PLUG_R = 3.0
COLLAR_LIP = 1.25                         # flat seal band on the wall beyond the box edge
FLANGE = 3.0                              # flange beyond the island, clamped by the trim
ISLAND_RIM = 1.2                          # visible insert rim around pocket + scoops
ISLAND_R = 6.0
BOSS_R = 4.0                              # screw boss on the insert
KEY_D, KEY_H, KEY_CLR = 3.0, 1.0, 0.15    # locating pins insert -> trim (asymmetric = keyed)
KEY_POS = ((25.0, 30.0), (-25.0, -22.0))
SPLIT_CLR = 0.25                          # trim to insert clearance
SCOOP = (6.0, 16.0, 9.0)                  # finger scoop ellipsoid radii (x, y, z)
SCOOP_ZC = PT + 2.5                       # scoop centre height
PASS_D = 3.5                              # 5 V lead pass-through (the only barrier opening)
PASS_X, PASS_Y = 21.5, 31.0               # vertical leg position (room frame, same side as J2)
BARRIER_MIN = 1.6                         # thinnest barrier wall allowed
V0_RATED_T = 1.5                          # DATASHEET thickness at which the chosen filament is UL94 V-0

# ---- Apollo MSR-2 (bare board, out of its case) ----
MSR = (40.0, 24.0, 10.0)                  # MEASURE envelope
RADAR_WALL = 1.2
LUX_POS = (12.0, 0.0)                     # MEASURE light sensor offset from bay centre

# ---- SHT45 breakout tab ----
SHT = (12.0, 8.0, 4.0)                    # SHT45 bay (the sensor sits on the flex tail, D-27)
SHT_Y = -62.0

# ---- sensor flex (D-27): MSR-2 CN2 -> spring fingers over the insert's target board -> SHT45 ----
# Single-layer flex in the trim: plug end under the MSR-2, up the top-right corner to just under
# the face skin, down the right channel (spring-finger section over a shelf on the insert), along
# the bottom to the SHT45 bay.
MSR_BOARD = (38.0, 21.5)                  # REF bare MSR-2 board, from Apollo's case cavity 38.08 x 21.67 (Printables 932026)
MSR_CN2_IN = 6.4                          # MEASURE REF CN2 centre from the board's end (Apollo wiki photo); CN2 at the right end here
B2B = (7.6, 3.0)                          # MEASURE REF CN2 housing (photo); 0.4 mm pitch, 2 rows, ~26-30 contacts (D-27)
B2B_STACK = 1.5                           # MEASURE mated height of CN2 + plug (1.5 if P4S-like)
FLEX_W, FLEX_T, STIFF_T = 4.0, 0.12, 0.15  # flex width, polyimide flex, FR4 stiffener under the plug / pins
FLEX_X = 36.8                             # flex centre line in the right channel
FLEX_SKIN_GAP = 0.15                      # flex + stiffener top below the trim's face skin
FLEX_LEAD_GAP = 1.0                       # free strip along the flange's right face for the 5 V lead
SHT_CHIP = (1.5, 1.5, 0.5)                # DATASHEET Sensirion SHT45 DFN-4 body, on the flex tail
# power contact: two Harwin S7081-42R SMT spring fingers (+5 V, GND) on the flex underside
FINGER = (3.18, 6.25)                     # DATASHEET S7081-42R body w x l (drawing S7081-42R iss. 7)
FINGER_PAD = (3.60, 6.65)                 # DATASHEET recommended pad layout
FINGER_FREE, FINGER_WH_MIN = 2.30, 1.70   # DATASHEET free height, recommended minimum working height
FINGER_WH = 2.0                           # design working height (datasheet recommends 2.10)
FINGER_TOL = 0.2                          # z stack tolerance (prints + flex) the working height must absorb
FINGER_Y = (15.0, 22.3)                   # finger centres along the channel, long axis along y
FINGER_X = 35.95                          # finger centre line: flex edge clears the flange, dome over the target
SHELF_UNDER_Z = 7.0                       # shelf underside: the flange is solid to its outer face from z 6.8
SHELF_OUT = 2.8                           # flat underside beyond the flange face (<= 3.0 printable), then 45 deg up
TARGET_T = 0.6                            # target board thickness (pads under the fingers, lead pads at the top)
TARGET_Y = (11.3, 29.0)                   # target board extent along y (lead pads at the top end)

# ================= derived =================
SEAT_Z = PT + B_PROUD - B_D               # remote's back rests here
POCKET_IN = (B_W + 2 * CLR, B_H + 2 * CLR)
POCKET_OUT = (POCKET_IN[0] + 2 * POCKET_WALL, POCKET_IN[1] + 2 * POCKET_WALL)
WELL_FLOOR_Z = SEAT_Z - SW_ROCKER_H - SW_ROCKER_TOL - SW_ROCKER_CLR   # top face of the switch panel
PANEL_BOT_Z = WELL_FLOOR_Z - SW_PANEL_T   # underside of the switch panel
WELL_IN = (SW_BEZEL[0] + 2 * CLR, SW_BEZEL[1] + 2 * CLR)
DECK_Z = PT - SKIN                        # insert flange top = trim face underside

WB_FRONT_Z = WELL_FLOOR_Z - SW_BODY[2]    # board front face = rocker PCB seat (measured from the panel's front face)
WB_BACK_Z = WB_FRONT_Z - WB[2]
Z_BOT = PANEL_BOT_Z                       # lowest point of the insert = print bed (panel underside)

# insert outline
PLUG = (BOX_W - 2 * PLUG_CLR, BOX_H - 2 * PLUG_CLR)
SEAL = (BOX_W + 2 * COLLAR_LIP, BOX_H + 2 * COLLAR_LIP)
_sc_face = SCOOP[0] * sqrt(max(0.0, 1 - ((SCOOP_ZC - PT) / SCOOP[2]) ** 2))
SCOOP_X = POCKET_IN[0] / 2 + 0.6
ISLAND = (2 * (SCOOP_X + _sc_face + ISLAND_RIM), POCKET_OUT[1] + 2 * ISLAND_RIM)
FLANGE_OUT = (ISLAND[0] + 2 * FLANGE, ISLAND[1] + 2 * FLANGE)
# depth of the 45-degree taper that carries the flange underside (plug corner -> pocket shell)
_r = POCKET_OUT[0] / 2
_cx, _cy = PLUG[0] / 2 - PLUG_R * (1 - 0.7071), PLUG[1] / 2 - PLUG_R * (1 - 0.7071)
TAPER_D = round(hypot(_cx, _cy - (POCKET_OUT[1] / 2 - _r)) - _r + 0.6, 1)

# MSR-2 bay sits just above the top screw (boss + countersink), SHT45 bay as before
MSR_Y = SCREW_PITCH / 2 + max(BOSS_R + SPLIT_CLR, SCREW_HEAD_D / 2 + 1.0) + MSR[1] / 2 + CLR
MSR_BACK_Z = PT - RADAR_WALL - MSR[2]     # MSR-2 board back (CN2 side) towards the wall
MSR_CN2_X = MSR_BOARD[0] / 2 - MSR_CN2_IN
SKIN_Z = PT - SKIN                        # underside of the trim's face skin
FLEX_HI_Z = SKIN_Z - FLEX_SKIN_GAP - STIFF_T - FLEX_T   # flex underside in the channel
TARGET_TOP_Z = FLEX_HI_Z - FINGER_WH                    # target pads at the fingers' working height
SHELF_TOP_Z = TARGET_TOP_Z - TARGET_T
