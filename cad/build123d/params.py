"""Single source of truth for wall-plate geometry (mm).

Coordinates: X = width, Y = height (up), Z = out of the wall.
z = 0 is the wall surface, plate face at z = PT, z < 0 is inside the box (MAINS SIDE).

Tags:
  MEASURE   placeholder - replace with a caliper reading recorded in
            docs/MEASUREMENTS.md before printing anything final.
  ESTIMATE  taken from photos / drawings (source in docs/MEASUREMENTS.md, human request
            2026-10-08); replace with a caliper reading before printing anything final.
  REF       reference value from a published source (cited); confirm with calipers.
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
B_W, B_H, B_D = 45.0, 70.0, 20.0          # REF outline (label drawing 1:1: 45.1 x 70.1) + depth (IKEA UK: 20 mm)
B_BACK_RUN = 9.1                          # ESTIMATE flat back inset from the outline (label drawing: flat 51.8 x 26.7)
B_BACK_RISE = 9.0                         # ESTIMATE height where the curved back meets the straight side
B_FRONT_R = 0.8                           # ESTIMATE front edge round-over (FCC external photo)
B_WHEEL_D = 41.5                          # ESTIMATE scroll wheel diameter (FCC photos)
B_WHEEL_Y = 12.5                          # ESTIMATE wheel centre above the remote centre (concentric with the end arc)
B_WHEEL_GAP = 0.3                         # ESTIMATE gap ring around the wheel
B_LED_Y = -12.0                           # ESTIMATE three LED dots, y of the row (terminal end)
B_LED_PITCH = 3.9                         # ESTIMATE
B_SEAM_Z = 9.8                            # MEASURED back cover depth, rim to back (human, 2026-10-09)
B_PROUD = 2.0
CLR = 0.5                                 # remote to pocket wall; 0.6 no longer fits the box with B_W = 45
POCKET_WALL = 1.6                         # pocket shell = mains barrier
SEAT_T = 2.5                              # minimum material under the remote seat
# The remote has a steel plate inside; it ships with an adhesive magnet for walls.
# That magnet is glued into a recess in the pocket floor. The recess is deeper than
# the magnet by MAGNET_SETBACK: the air gap weakens the pull (shim it up to strengthen).
# The supplied magnet (ESTIMATE ~47.4 x 17.5, full round ends R8.75) is cut once across by the user: the piece
# keeps one round end (down, in the recess's round end) and has a straight cut edge up.
MAGNET_FULL = (17.5, 47.4)                # ESTIMATE supplied magnet before the cut (w, length; label drawing ring)
MAGNET = (17.5, 18.5, 2.0)                # cut piece (w, length from the round end to the cut, t ESTIMATE incl. tape)
MAGNET_Y = 0.0                            # ESTIMATE centre of the remote's internal plate (FCC photo: centred in its cover)
MAGNET_REC_Y = -3.75                      # cut piece centre: over the remote's plate and the back cover's steel, the
                                          # cut edge SEAT_T clear of the switch well
MAGNET_SETBACK = 0.5                      # magnet face below the seat
MAGNET_CLR = 0.3                          # recess clearance around the magnet
MAGNET_END_R = MAGNET[0] / 2              # ESTIMATE the magnet's round end (full round, label drawing R8.76)
MAGNET_SLOT_BOT = MAGNET_REC_Y - MAGNET[1] / 2 - MAGNET_CLR   # derived: recess bottom, at the round end

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
SW_PIN_GRID = (10.2, 7.0)                 # DATASHEET hole grid: poles 10.2 apart (x); pins 1 / 2 on the body's centre
                                          # line, 1a / 2a 7 off it (y)
SW_SW_DIR = 1                             # switched pins (1a / 2a) above (+1) or below (-1) the in pins (1 / 2)
SW_Y = 19.5                               # rocker centre (front-view y; from pcb/)
PAD_BODY_GAP = 1.0                        # through-hole pad edge to a part body on the other side of the board
                                          # (pin tail, solder fillet, iron)

# ---- wiring board (single board, D-24/D-25; KiCad project in pcb/) ----
WB = (47.0, 72.0, 1.6)                    # front face (F) towards the plate, back (B) into the box
WB_Y = 0.0                                # board centre
IRM = (37.0, 24.0, 15.0)                  # DATASHEET Mean Well IRM-03-5 body (IRM-03-SPEC 2025-08-08), on B
IRM_C = (0.0, -21.39)                     # PSU body centre on the board (front-view x, y; from pcb/)
WAGO6 = (32.4, 16.1, 20.7)                # DATASHEET WAGO 2604-1106 (3D model): width, depth at the board (entry face to
                                          # closed back; the levers overhang the entry side up top), height incl. pins (on B)
WAGO_X, WAGO_Y = 3.0, 5.05                # terminal block centre at the board (front-view x, y; from pcb/)
WAGO_ENTRY = (0, 1)                       # direction the wire entries face (front-view x, y): away from the PSU
WAGO_PSU_GAP = 1.0                        # minimum gap from the block's closed back to the PSU body
J2_POS = (13.0, -19.5)                    # SMD 5 V connector on F (front-view x, y; from pcb/), right of the slot
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
PASS_D = 4.5                              # 5 V flex jumper pass-through (the only barrier opening): takes the
                                          # jumper's stiffened connector end when it is threaded through
PASS_X, PASS_Y = 21.5, 31.6               # vertical leg position (room frame, same side as J2)
BARRIER_MIN = 1.6                         # thinnest barrier wall allowed
V0_RATED_T = 1.5                          # DATASHEET thickness at which the chosen filament is UL94 V-0

# ---- Apollo MSR-2 (bare board, out of its case) ----
MSR = (40.0, 24.0, 10.0)                  # MEASURE envelope
RADAR_WALL = 1.2
LUX_POS = (12.0, 0.0)                     # MEASURE light sensor offset from bay centre

# ---- SHT45 breakout tab ----
SHT = (12.0, 8.0, 4.0)                    # SHT45 bay (the sensor sits on the flex tail, D-27)
SHT_Y = -62.0

# ---- 5 V flex jumper: wiring board J2 -> pass-through -> pad end on the shelf (D-27, R9, no wires) ----
# J2 is a Hirose FH12-6S-0.5SH slide-lock FPC connector (3 contacts per net); the jumper's pad end
# lies on the insert shelf where the face plate's spring fingers press it. Its connector end is
# threaded through the pass-through from the shelf side and plugged into J2 with the board held
# beside the insert (latch in view); the spare length folds into the gap between board and insert.
FH12 = (6.1, 5.6, 2.0)                    # REF FH12-6S body (x, y, height): KiCad footprint / Hirose FH12 series
JUMPER_W = 3.0                            # flex run width
JUMPER_END = (3.5, 4.0, 0.3)              # MEASURE connector end: width (6 contacts at 0.5), stiffened length, thickness
JUMPER_T = 0.2                            # 2-layer polyimide flex (design value; confirm with the PCBWay stack-up)
JUMPER_X = 15.0                           # run between the rocker body (x <= 11.3) and the right-hand bosses
JUMPER_SERVICE = 40.0                     # spare length folded between board and insert (plug in with the board beside it)

# ---- sensor flex (D-27): MSR-2 CN2 -> spring fingers over the 5 V jumper's pad end -> SHT45 ----
# Single-layer flex in the trim: plug end under the MSR-2, up the top-right corner to just under
# the face skin, down the right channel (spring-finger section over a shelf on the insert), along
# the bottom to the SHT45 bay.
MSR_BOARD = (38.0, 21.5)                  # REF bare MSR-2 board, from Apollo's case cavity 38.08 x 21.67 (Printables 932026)
MSR_HOOK = 0.5                            # snap hooks at the board's short ends: lip over its back face (D-45)
MSR_CN2_IN = 6.4                          # MEASURE REF CN2 centre from the board's end (Apollo wiki photo); CN2 at the right end here
B2B = (7.6, 3.0)                          # MEASURE REF CN2 housing (photo); 0.4 mm pitch, 2 rows, ~26-30 contacts (D-27)
B2B_STACK = 1.5                           # MEASURE mated height of CN2 + plug (1.5 if P4S-like)
FLEX_W, FLEX_T, STIFF_T = 4.0, 0.12, 0.15  # flex width, polyimide flex, FR4 stiffener under the plug / pins
FLEX_PLUG = (12.0, 8.0)                   # plug end of the flex (along x, across): CN2 mate and fan-out
FLEX_NECK_L = 10.0                        # taper from the plug end to FLEX_W
FLEX_X = 36.8                             # flex centre line in the right channel
FLEX_SKIN_GAP = 0.15                      # flex + stiffener top below the trim's face skin
FLEX_LEAD_GAP = 1.0                       # free strip along the flange's right face for the 5 V jumper
FLEX_RISE_DY = 12.0                       # run along y over which the flex rises from the wall to under the skin
FINGER_SEC_OUT = 39.7                     # finger section's outer edge: lanes for 4 tracks beside the finger pads
FINGER_LANE_MARGIN = 6.0                  # wall-side lanes extend beyond the pads: room for the tracks to step in
TRIM_WALL_RECESS = 1.0                    # trim side wall thinned on the inside over the finger section
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
SHELF_STOP = (0.8, 0.4)                   # stop at the shelf's lower end (D-45): length along y, height above the shelf
TARGET_T = 0.6                            # jumper pad end thickness, flex + stiffener (pads under the fingers)
TARGET_Y = (11.3, 29.0)                   # jumper pad end extent along y (the run joins at the top)

# ---- microphone (D-29): I2S MEMS mic on the sensor flex, push-to-talk ----
# PUI Audio DMM-4026-B-I2S-R, bottom port, on the flex's underside in the right channel (above the
# finger section, where the flange corner rounds away). Its port faces the face skin through a hole
# in flex + stiffener, sealed to the skin by an adhesive gasket, and a sound hole through the skin.
MIC = (3.00, 4.00, 1.00)                  # DATASHEET body w x l x h (DMM-4026-B-I2S-R rev A)
MIC_PORT_IN = 1.00                        # DATASHEET port centre from the body's port end
MIC_Y = 40.75                             # body centre along the channel (room y), port end down
MIC_FLEX_Y = 2.0                          # body centre from the flex centre line, towards the flange
MIC_SEC_W = 4.4                           # widened flex section: edge from the centre line, towards the flange
MIC_SEC_Y = (38.0, 46.0)                  # widened section's extent along the channel (room y)
MIC_FLEX_HOLE_D = 0.5                     # port hole through flex + stiffener
MIC_GASKET_D = 2.6                        # adhesive gasket ring OD (ID = MIC_SKIN_HOLE_D), FLEX_SKIN_GAP thick
MIC_SKIN_HOLE_D = 1.0                     # sound hole through the face skin
MIC_CLR = 0.5                             # flex section and mic body to the insert flange

# ---- replacement back cover (D-35): the BILRESA E2490 without cells, powered from the plate ----
# Remote coordinates: origin = remote centre, x / y as the front view, z = 0 the back's outer face.
AAA_D, AAA_L = 10.5, 44.5                 # DATASHEET IEC 60086-2 LR03 / IEC 61951-2 HR03 maximum diameter, height
BC_CELL_X = 11.2                          # ESTIMATE cell axes at +-x (label drawing bays +-10.95, contacts +-11.4)
BC_CELL_Y0 = 0.0                          # REF compartment centre along y (FCC photos: centred; MEASURE)
BC_CELL_Z = 6.8                           # ESTIMATE cell axis above the back's outer face (wall + clearance + r)
BC_TERM_Y = -1                            # REF terminal end (VBAT / GND contacts) at -y, the LED end (FCC photos)
BC_VBAT_X = -1                            # REF VBAT contact on the -x cell, GND on the +x cell (FCC photos; check on a unit)
BC_WALL = 1.6                             # MEASURED cover shell thickness (human, 2026-10-09)
BC_PRY = (6.0, 1.2)                       # MEASURE screwdriver notch in the rim at the bottom end (-y): width, depth
# snap clips: one at each end (x = 0), free-standing inside the end wall, below the rim; the housing's edge comes
# down into the cover and the clip's hook catches its wall
BC_LATCH_W = 3.5                          # ESTIMATE ear width (human photos IMG_5088-5090)
BC_LATCH_T = 1.2                          # ESTIMATE ear thickness (radial; photos)
BC_LATCH_IN = 3.0                         # ESTIMATE slot centre in from the outline at the ends
BC_LATCH_TOPS = (4.7, 6.5)                # MEASURED clip tops above the inside floor: bottom end (-y), top end (+y)
BC_LATCH_HOOK = 0.5                       # MEASURE hook at the clip's tip, inwards (catches the housing's wall)
BC_SIDE_TAB = (6.0, 1.5, 3.8)             # side ribs at mid-length (y 0), free-standing on the shell's curved floor,
                                          # against flex: length along y, thickness (ESTIMATE, photos), top above the
                                          # inside floor (MEASURED, human 2026-10-09)
BC_SIDE_TAB_GAP = 36.1                    # MEASURED inside spacing between the side ribs (human, 2026-10-09)
BC_STEEL = (12.0, 20.0, 2.0)              # MEASURED the remote's plate (a magnet), x, y, t (human, 2026-10-09); moved
                                          # from its own cover
BC_STEEL_FLOOR = 0.4                      # cover wall left under the steel plate
# cover flex retention (D-45): FR4 stiffener on the pad / regulator section, printed pegs heat-staked through it;
# the end section drops into a slot (a lip in front of each contact block) and snaps under a hook on the block's top
BC_PAD_STIFF_T = 0.3                      # FR4 stiffener on the pad section (non-copper side, up)
BC_PEG_END = 2.5                          # flex beyond the upper finger's body, room for the top peg
BC_PEGS = ((14.4, -0.5), (14.4, 8.6))     # peg centres: between the fingers (rib between the windows), above the +5V one
BC_PEG_D, BC_PEG_HOLE, BC_PEG_STAKE = 1.2, 1.4, 1.0   # peg, hole in flex + stiffener, length above it to melt over
BC_END_LIP = (0.8, 1.0, 0.1)              # lip in front of each block's foot: thickness, height above the ledge, gap
BC_END_HOOK = 0.5                         # hook on each block's top over the end section's top edge
BC_STEEL_CLIP = (4.0, 0.8, 0.5, 0.4)      # clips at both ends of the steel pocket: width, tab thickness, hook over the
                                          # plate's edge, gap behind the tab (to flex)
BC_STEEL_Y = -5.5                         # steel plate centre in the cover (the EU magnet sits under it, clear of the switch cup)
BC_FLEX_Z = FINGER_WH                     # flex underside above the back face: fingers at working height on flush pads
BC_FINGERS = ((14.4, 4.0), (14.4, -5.0))  # +5V, GND spring fingers (S7081-42R) on the cover's back (x, y), long axis y
BC_DOME_DY = 0.0                          # DATASHEET contact dome 3.15 +-0.25 from the bend end of the 6.25 body (~centred)
BC_WIN_CLR = 0.3                          # finger window round the finger body
BC_STRIP = (11.3, 16.5)                   # flex pad section across x (finger windows + the +3V3 lane past the GND finger)
BC_RUN = (10.7, 13.3)                     # flex run across x to the terminal end (clear of the curved wall; slot roof <= 3 mm)
BC_JOG = 6.0                              # y length of the regulator section between the pad section and the run
# 3.3 V regulator on the cover flex (D-41), copper down in a recess in the cover: TI TLV75533PDBVR + 1 uF in / out
BC_REG = {"U1": (13.1, -11.8), "C3": (14.6, -9.2), "C4": (12.5, -14.6)}   # part centres (remote x, y)
BC_REG_BODY = (3.0, 3.0, 1.45)            # DATASHEET TLV755P DBV (SOT-23-5): body + leads <= 3.0 x 3.0, 1.45 max high
BC_CAP0402 = (1.0, 0.5, 0.55)             # DATASHEET 0402 capacitor (GRM155R61A105KE15): 1.0 x 0.5, 0.55 max high
BC_REG_RECESS = (11.4, 16.4, -15.0, -8.8) # recess under the regulator section (x0, x1, y0, y1), down to BC_STEEL_FLOOR
BC_END_T = 0.4                            # FR4 stiffener behind the flex's end section
BC_END_H = 8.8                            # flex end section height above the flex plane: the contact pads plus 0.5, its
                                          # top hook (D-45) under the cell top (BC_CELL_Z + AAA radius)
BC_CONTACT_W = FINGER_PAD[1] + 1.0        # end section width round each contact finger (long axis across x)
BC_TERM_SETBACK = 0.0                     # MEASURE fixed (+) contact plate's face behind the cell's end plane (0 = on it)
BC_END_CORNER = 1.5                       # 45 deg cut at the end section's lower outer corners (cover's curved back)
BC_PCB_W = 11.6                           # ESTIMATE the plastic divider between the cells (drawing; the PCB is 11.1)
BC_PCB_CLR = 0.5                          # flex end section to the PCB strip
BC_BRIDGE_H = 2.0                         # MEASURE flex band passing under the PCB strip (below its back-side parts)
BC_LANE_H = 0.6                           # +3V3 lane across the band, above the bend line (below the contact fingers)
BC_BLOCK_T = 4.0                          # contact block depth behind the end section (along the cell axis)
BC_BLOCK_W = BC_CONTACT_W + 1.0           # contact block width across
# pocket-floor insert (face plate side): printed floor, sensor-flex tongue with flush pads under the fingers
BC_FLOOR_T = 0.6                          # floor insert under the remote (raises it by this)
BC_FLOOR_CLR = 0.3                        # floor insert to the pocket wall
BC_FLOOR_PAD = (4.0, 7.0)                 # flush gold pads on the tongue under the fingers (finger 6.25 long)
BC_TONGUE_W = 5.0                         # sensor-flex tongue width
BC_TONGUE_Y = -12.0                       # tongue run from the right channel into the pocket (y), below the pads
BC_RECESS_CLR = 0.02                      # tongue recess depth over the flex thickness
# NA: the tongue leaves the 5 V jumper's pad end (on the insert shelf) at its inner edge, runs inwards in a
# tunnel through the insert flange above the wall plane, down a groove in the pocket wall, free down the wall
# into the floor insert's recess (copper up after the two bends), then L-turns to the pads under the fingers
BC_NA_TONGUE_Y = 18.65                    # tongue centre (room y): between the pad end's GND and +5V contact pads
BC_NA_NECK_W = 2.4                        # tongue width from the pad end to the pad strip on the floor
BC_NA_SLOT = (2.8, 0.1, 0.35)             # tunnel width (roof bridge <= 3.0), floor below / roof above the flex
BC_NA_DOWN = (15.5, 3.0, 7.8)             # floor: x centre and width of the strip down to the pads, pad strip top y
BC_NA_GROOVE_D = 0.4                      # groove depth in the pocket wall
BC_NA_GROOVE_BOT = 0.5                    # groove lower end (above the wall plane; the remote's round-over clears below)

# ================= derived =================
BC_CELL_END_Y = BC_CELL_Y0 + BC_TERM_Y * AAA_L / 2                    # a full-length cell's terminal end
BC_COPPER_Y = BC_CELL_END_Y + BC_TERM_Y * (BC_TERM_SETBACK - FINGER_WH)  # end section copper: contact fingers
                                                                       # at working height on the fixed plate
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
SHT_ENTRY = SHT[0] / 2 + 0.4 + 1.6 + 1.0  # flex tail enters the SHT45 bay frame from the right
FINGER_SEC_IN = FINGER_X - FINGER_PAD[0] / 2 - 0.3                    # finger section's inner (flange-side) edge
FINGER_SEC_Y = (FINGER_Y[0] - FINGER_PAD[1] / 2 - 0.5, FINGER_Y[1] + FINGER_PAD[1] / 2 + 0.5)    # flange side
FINGER_LANE_Y = (FINGER_Y[0] - FINGER_PAD[1] / 2 - FINGER_LANE_MARGIN,
                 FINGER_Y[1] + FINGER_PAD[1] / 2 + FINGER_LANE_MARGIN)                       # wall side
MIC_X = FLEX_X - MIC_FLEX_Y                                           # mic body centre (room x)
MIC_PORT = (MIC_X, MIC_Y - (MIC[1] / 2 - MIC_PORT_IN))                # port / sound hole axis (room x, y)
MIC_SEC_IN = FLEX_X - MIC_SEC_W                                       # widened section's inner (flange-side) edge


def pocket_wall_x(y):
    """x of the remote pocket's right wall at room y (stadium: straight sides, semicircular ends)."""
    a = POCKET_IN[0] / 2
    over = abs(y) - (POCKET_IN[1] / 2 - a)
    return a if over <= 0 else sqrt(a * a - over * over)


def tongue_walls():
    """NA tongue (D-41) across its width: (outermost wall x, innermost wall x) of the pocket wall."""
    xs = [pocket_wall_x(BC_NA_TONGUE_Y + d * BC_NA_SLOT[0] / 2) for d in (-1, 0, 1)]
    return max(xs), min(xs)


def flex_half_width(x):
    """Sensor flex half width at flat X (from the CN2 plug centre): plug end, neck taper, strip."""
    p, w = FLEX_PLUG[0] / 2, FLEX_PLUG[1] / 2
    if x <= p:
        return w
    if x >= p + FLEX_NECK_L:
        return FLEX_W / 2
    return w - (w - FLEX_W / 2) * (x - p) / FLEX_NECK_L


def jumper_path():
    """5 V flex jumper centre line (room x, y, z): J2 -> service loop (Z-fold in the gap between board
    and insert) -> pass-through (along the bottom of its 45 deg leg) -> pad end on the shelf."""
    zk = -1.0                                            # bend of the pass-through (insert.pass_through)
    face = FLANGE_OUT[0] / 2
    r = PASS_D / 2
    chord = r - sqrt(r * r - (JUMPER_W / 2) ** 2)        # the strip lies across the bottom of the round leg
    o = (r - chord - JUMPER_T) / sqrt(2)                 # strip centre below the leg's axis (x and z parts)
    t = face - PASS_X
    pad_x = (FLANGE_OUT[0] / 2 + 0.15 + FLANGE_OUT[0] / 2 + SHELF_OUT + (SHELF_TOP_Z - SHELF_UNDER_Z) - 0.15) / 2
    e = (J2_POS[0], WB_Y + J2_POS[1] + FH12[1] / 2 + 0.3, WB_FRONT_Z + FH12[2] / 2)
    lo, mid, hi = WB_FRONT_Z + FH12[2] + 1.5, (WB_FRONT_Z + Z_BOT) / 2, Z_BOT - 2.5
    y0 = WB_Y + J2_POS[1] + 9.0
    fold = JUMPER_SERVICE / 2                            # two runs of the Z-fold add the spare length
    return [e, (JUMPER_X, y0, lo), (JUMPER_X, y0 + fold, lo), (JUMPER_X, y0 + fold, mid),
            (JUMPER_X, y0, mid), (JUMPER_X, y0, hi), (JUMPER_X, PASS_Y - 4.0, hi),
            (PASS_X + o, PASS_Y, Z_BOT - 1.7), (PASS_X + o, PASS_Y, zk - o),
            (face + o, PASS_Y, zk + t - o),                                  # leaves the flange face
            (pad_x, TARGET_Y[1] - 0.5, SHELF_TOP_Z + TARGET_T + JUMPER_T / 2)]


def jumper_length():
    pts = jumper_path()
    return sum(hypot(*(b[i] - a[i] for i in range(3))) for a, b in zip(pts, pts[1:]))
