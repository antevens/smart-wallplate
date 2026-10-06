"""Single source of truth for wall-plate geometry (mm).

Coordinates: X = width, Y = height (up), Z = out of the wall.
z = 0 is the wall surface, plate face at z = PT, z < 0 is inside the box (MAINS SIDE).

Every value tagged MEASURE is a placeholder - replace it with a caliper
reading recorded in docs/MEASUREMENTS.md before printing anything final.
"""

# ---- plate ----
PW, PH, PT, PR = 82.0, 150.0, 13.0, 6.0   # width, height, proud of wall, corner radius
SKIN = 2.0                                # face/side wall of hollow plate
FACE_CHAMFER = 1.2

# ---- NA single-gang device box ----
BOX_W, BOX_H = 50.8, 76.2                 # 2" x 3" opening
BOX_D = 63.5                              # MEASURE (2.5" assumed)
SCREW_PITCH = 83.3                        # #6-32 device ears, 3-9/32"
SCREW_D, SCREW_HEAD_D = 3.8, 8.0

# ---- IKEA BILRESA scroll wheel remote (kept intact, batteries in) ----
B_W, B_H, B_D = 42.0, 70.0, 20.0          # MEASURE stadium outline + depth
B_PROUD = 2.0
CLR = 0.6
POCKET_WALL = 1.6                         # pocket shell = mains barrier
SEAT_T = 2.5
STEEL = (20.5, 12.5, 0.8)                 # MEASURE steel magnet target recess (w, h, depth)
STEEL_Y = -18.0

# ---- emergency rocker: Bulgin/Arcolectric C1300AABBEN602A ----
SW_CUT = (27.3, 12.3)                     # datasheet panel cutout
SW_PANEL_T = 1.5                          # MEASURE/datasheet snap-in panel range
SW_BEZEL = (31.0, 16.0)                   # MEASURE
SW_ROCKER_H = 10.0                        # MEASURE bezel + rocker height above panel
SW_BODY = (26.0, 11.5, 24.0)              # MEASURE body incl. 6.3 mm tabs
SW_Y = 18.0

# ---- PSU carrier PCB (KiCad project in pcb/) ----
PCB = (40.0, 36.0, 1.6)
PCB_Y = -14.0
PCB_STANDOFF = 4.0
IRM = (37.0, 24.0, 15.0)                  # Mean Well IRM-03-5 body

# ---- Apollo MSR-2 (bare board, out of its case) ----
MSR = (40.0, 24.0, 10.0)                  # MEASURE envelope
MSR_Y = 57.0
RADAR_WALL = 1.2
LUX_POS = (12.0, 0.0)                     # MEASURE light sensor offset from bay centre

# ---- SHT45 breakout tab ----
SHT = (12.0, 8.0, 4.0)
SHT_Y = -62.0

# ---- derived ----
SEAT_Z = PT + B_PROUD - B_D               # remote's back rests here
FLOOR_Z = SEAT_Z - SEAT_T
POCKET_IN = (B_W + 2 * CLR, B_H + 2 * CLR)
POCKET_OUT = (POCKET_IN[0] + 2 * POCKET_WALL, POCKET_IN[1] + 2 * POCKET_WALL)
WELL_FLOOR_Z = SEAT_Z - SW_ROCKER_H       # top face of the switch panel
