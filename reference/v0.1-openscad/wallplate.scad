// =====================================================================
//  Smart wall plate – FIRST PASS (v0.1)
//  Recessed IKEA BILRESA (scroll wheel) + hidden emergency rocker +
//  Mean Well IRM-03-5 PSU carrier slot + Apollo MSR-2 bay + SHT45 bay
//  North American single-gang device box (2" x 3" opening)
//
//  Coordinates: X = width, Y = height (up), Z = out of wall.
//  z = 0 is the wall surface. Plate face is at z = PT.
//  Everything with z < 0 is inside the box (MAINS SIDE).
//
//  !! All values marked MEASURE are placeholders - caliper them !!
// =====================================================================

$fn = 64;
part = "plate";
show_wall = false;
explode = 0;           // lift the remote out of its pocket (mm)
use_stl = false;       // previews: use pre-rendered plate.stl
sec = "";              // 2D section export of one part

// ---------------- plate ----------------
PW  = 82;     // plate width
PH  = 150;    // plate height (taller than std to fit MSR-2 + SHT45)
PT  = 13;     // plate proud of wall (set by MSR-2 bay depth)
PR  = 6;      // corner radius
SKIN = 2.0;   // face / side wall thickness of hollow plate

// ---------------- box ----------------
BOX_W = 50.8; BOX_H = 76.2;   // 2" x 3" opening
BOX_D = 63.5;                 // 2.5" deep box (MEASURE yours)
SCREW_PITCH = 83.3;           // 3-9/32" device-ear spacing, #6-32

// ---------------- BILRESA ----------------
B_W = 42;   B_H = 70;   B_D = 20;   // MEASURE (stadium outline)
B_PROUD = 2;                        // remote face sits 2 mm proud
CLR = 0.6;                          // fit clearance
POCKET_WALL = 1.6;                  // pocket shell = mains barrier
SEAT_T = 2.5;                       // pocket floor thickness

// ---------------- emergency switch (Bulgin C1300) ----------------
SW_CUT = [27.3, 12.3];      // panel cutout from datasheet
SW_PANEL_T = 1.5;           // snap-in panel thickness - CHECK datasheet range
SW_BEZEL = [31, 16];        // bezel footprint  - MEASURE
SW_ROCKER_H = 10;           // bezel+rocker height above panel - MEASURE
SW_BODY = [26, 11.5, 24];   // body + 6.3mm tabs behind panel - MEASURE
SW_Y = 18;                  // well centre (upper part of pocket)

// ---------------- PSU carrier PCB ----------------
PCB = [40, 36, 1.6];
PCB_Y = -14;                // centre, lower part of pocket
PCB_STANDOFF = 4;
IRM = [37, 24, 15];         // Mean Well IRM-03-5

// ---------------- MSR-2 ----------------
MSR = [40, 24, 10];         // bare board envelope - MEASURE
MSR_Y = 57;
RADAR_WALL = 1.2;           // thin front skin over the radar
LUX_POS = [12, 0];          // light sensor offset from bay centre - MEASURE

// ---------------- SHT45 tab ----------------
SHT = [12, 8, 4];
SHT_Y = -62;

// ---------------- derived ----------------
seat_z  = PT + B_PROUD - B_D;               // remote back rests here
floor_z = seat_z - SEAT_T;                  // back of pocket floor
pin_w = B_W + 2*CLR;  pin_h = B_H + 2*CLR;  // pocket inner
pout_w = pin_w + 2*POCKET_WALL; pout_h = pin_h + 2*POCKET_WALL;
well_floor = seat_z - SW_ROCKER_H;          // top of switch panel

module rrect(w, h, r) {
    offset(r) square([w-2*r, h-2*r], center=true);
}
module stadium(w, h) {          // rounded-end oval like the BILRESA
    r = w/2;
    hull() { translate([0,  h/2-r]) circle(r); translate([0, -(h/2-r)]) circle(r); }
}

// ---------------------------------------------------------------------
module plate_body() {
    difference() {
        union() {
            // hollow plate shell (open to the wall)
            difference() {
                hull() {
                    linear_extrude(PT-1.2) rrect(PW, PH, PR);
                    linear_extrude(PT) rrect(PW-2.4, PH-2.4, PR-1.2);
                }
                translate([0,0,-0.01]) linear_extrude(PT-SKIN+0.01)
                    rrect(PW-2*SKIN, PH-2*SKIN, PR-SKIN);
            }
            // collar around the box opening: separates the mains-side
            // box from the low-voltage hollow of the plate
            linear_extrude(PT) difference() {
                square([BOX_W+2+3.2, BOX_H+2+3.2], center=true);
                square([BOX_W+2,     BOX_H+2],     center=true);
            }
            // screw bosses
            for (s=[-1,1]) translate([0, s*SCREW_PITCH/2, 0])
                cylinder(r=5.5, h=PT);
            // pocket shell (continuous barrier)
            translate([0,0,floor_z]) linear_extrude(PT-floor_z)
                stadium(pout_w, pout_h);
            // switch well shell
            translate([0, SW_Y, well_floor-SW_PANEL_T])
                linear_extrude(seat_z-well_floor+SW_PANEL_T)
                    rrect(SW_BEZEL[0]+2*CLR+2*POCKET_WALL,
                          SW_BEZEL[1]+2*CLR+2*POCKET_WALL, 2);
            // PSU slot: two rails hanging off the pocket floor
            psu_rails();
            // MSR-2 bay frame
            translate([0, MSR_Y, 0]) linear_extrude(PT)
                difference() { rrect(MSR[0]+2*CLR+3.2, MSR[1]+2*CLR+3.2, 2);
                               rrect(MSR[0]+2*CLR,     MSR[1]+2*CLR,     1); }
            // SHT45 bay frame (isolated from everything else)
            translate([0, SHT_Y, 0]) linear_extrude(PT)
                difference() { rrect(SHT[0]+4, SHT[1]+4, 1.5);
                               rrect(SHT[0]+0.8, SHT[1]+0.8, 0.5); }
        }
        // ---- cuts ----
        // pocket cavity
        translate([0,0,seat_z]) linear_extrude(PT+5) stadium(pin_w, pin_h);
        // switch well cavity
        translate([0, SW_Y, well_floor]) linear_extrude(seat_z-well_floor+0.1)
            rrect(SW_BEZEL[0]+2*CLR, SW_BEZEL[1]+2*CLR, 1);
        // snap-in cutout
        translate([0, SW_Y, well_floor-SW_PANEL_T-1])
            linear_extrude(SW_PANEL_T+2) square(SW_CUT, center=true);
        // steel target recess for the remote's magnet (lower seat)
        translate([0, -18, seat_z-0.8]) linear_extrude(1) square([20.5,12.5], center=true);
        // finger scoops either side of the remote
        for (s=[-1,1]) translate([s*(pin_w/2+1), 0, PT+2.5])
            scale([0.8, 1.8, 1]) sphere(r=7);
        // screw holes, countersunk #6
        for (s=[-1,1]) translate([0, s*SCREW_PITCH/2, 0]) {
            translate([0,0,-1]) cylinder(d=3.8, h=PT+2);
            translate([0,0,PT-3.8]) cylinder(d1=3.8, d2=8, h=3.81);
        }
        // MSR-2 cavity (thin radar skin left at the front)
        translate([0, MSR_Y, -0.01]) linear_extrude(PT-RADAR_WALL)
            rrect(MSR[0]+2*CLR, MSR[1]+2*CLR, 1);
        // light-sensor window
        translate([LUX_POS[0], MSR_Y+LUX_POS[1], PT-3]) cylinder(d=3, h=5);
        // MSR-2 heat vents in top edge
        for (i=[-2:2]) translate([i*7, PH/2-SKIN-1, 3]) cube([3, 6, 6], center=false);
        // SHT45 cavity + vents (face and bottom edge)
        translate([0, SHT_Y, -0.01]) linear_extrude(PT-SKIN)
            rrect(SHT[0]+0.8, SHT[1]+0.8, 0.5);
        for (i=[-1:1]) translate([i*4-1, SHT_Y-3, PT-3]) cube([2, 6, 4]);
        for (i=[-1:1]) translate([i*4-1, -PH/2-1, 2]) cube([2, 10, 6]);
        // 5 V lead pass-through in the collar (SELV, double-insulated lead)
        translate([BOX_W/2+1, 30, 4]) rotate([0,90,0]) cylinder(d=3.5, h=5);
    }
}

module psu_rails() {
    // U-shaped slot: PCB slides in from the top, edge grooves hold it
    rail_len = PCB[1] + 2;
    z_top = floor_z - PCB_STANDOFF;          // component-free face of PCB
    for (s=[-1,1]) difference() {
        hull() {
            translate([s*(PCB[0]/2+1), PCB_Y, (floor_z + z_top-PCB[2]-3)/2])
                cube([4, rail_len, floor_z-(z_top-PCB[2]-3)], center=true);
        }
        translate([s*(PCB[0]/2+0.25), PCB_Y+1, z_top-PCB[2]/2])
            cube([2.5, rail_len+2, PCB[2]+0.4], center=true);
    }
    // bottom end stop
    translate([0, PCB_Y-PCB[1]/2-1.6, (floor_z + z_top)/2])
        cube([PCB[0]+6, 1.6, PCB_STANDOFF+0.01], center=true);
}

// ---------------------------------------------------------------------
//  ghost components for the assembly view
// ---------------------------------------------------------------------
module ghost_box() {
    color("SlateGray", 0.18) difference() {
        translate([0,0,-BOX_D]) linear_extrude(BOX_D) square([BOX_W+3, BOX_H+3], center=true);
        translate([0,0,-BOX_D+1.5]) linear_extrude(BOX_D) square([BOX_W, BOX_H], center=true);
    }
    if (show_wall) color("Gainsboro", 0.25) translate([0,0,-12.7]) linear_extrude(12.7)
        difference() { square([PW+40, PH+40], center=true); square([BOX_W+3, BOX_H+3], center=true); }
}
module ghost_bilresa() {
    color("OldLace") translate([0,0,seat_z+explode]) {
        linear_extrude(B_D-1) stadium(B_W, B_H);
        translate([0, 6, B_D-1]) cylinder(d=32, h=1.2);          // wheel
        color("Silver") translate([0, 6, B_D-0.6]) cylinder(d=26, h=1);
        translate([0,-25,B_D-1]) for(i=[-1:1]) translate([i*3,0,0]) cylinder(d=1.2,h=0.6);
    }
}
module ghost_switch() {
    translate([0, SW_Y, well_floor]) {
        color("DimGray") linear_extrude(2) square([SW_BEZEL[0], SW_BEZEL[1]], center=true);
        color("Firebrick") translate([0,0,2]) rotate([0,8,0])
            linear_extrude(SW_ROCKER_H-3) square([SW_CUT[0]-2, SW_CUT[1]-2], center=true);
        color("DimGray") translate([0,0,-SW_PANEL_T-SW_BODY[2]])
            linear_extrude(SW_BODY[2]) square([SW_BODY[0], SW_BODY[1]], center=true);
        color("Gold") for (x=[-6,6]) translate([x-0.4,-3.2,-SW_PANEL_T-SW_BODY[2]-8]) cube([0.8,6.3,8]);
    }
}
module ghost_psu() {
    z_pcb = floor_z - PCB_STANDOFF;
    translate([0, PCB_Y, z_pcb]) {
        color("DarkGreen") translate([0,0,-PCB[2]]) linear_extrude(PCB[2])
            square([PCB[0], PCB[1]], center=true);
        // IRM-03-5 hangs off the back of the board (into the box)
        color("#222") translate([0, 5, -PCB[2]-IRM[2]]) linear_extrude(IRM[2])
            square([IRM[0], IRM[1]], center=true);
        color("#2a6") translate([-12, -13, -PCB[2]-8]) cube([10.2, 7.5, 8]);    // J1
        color("Beige") translate([2, -14, -PCB[2]-6]) cube([7, 4, 6]);          // F1
        color("RoyalBlue") translate([13, -14.5, -PCB[2]-10]) cube([4.5, 6, 10]); // RV1
    }
}
module ghost_msr() {
    translate([0, MSR_Y, PT-RADAR_WALL-MSR[2]]) {
        color("#1b1b1b") linear_extrude(1.6) square([MSR[0], MSR[1]], center=true);
        color("Silver") translate([-8,0,1.6]) linear_extrude(2.4) square([16.6,13.2], center=true);
        color("Goldenrod") translate([8,-5,1.6]) linear_extrude(3) square([18,7], center=true);
    }
}
module ghost_sht() {
    color("Purple") translate([0, SHT_Y, PT-SKIN-1.6]) linear_extrude(1.6)
        square([SHT[0], SHT[1]], center=true);
}

module plate_vis() { if (use_stl) import("plate.stl"); else plate_body(); }
module assembly() {
    color("WhiteSmoke") plate_vis();
    ghost_bilresa(); ghost_switch(); ghost_psu(); ghost_msr(); ghost_sht(); ghost_box();
}

if (part == "plate")    plate_body();
if (part == "assembly") assembly();
if (part == "section")  intersection() { assembly(); translate([-400,-200,-200]) cube([400,400,400]); }
if (part == "noremote") { color("WhiteSmoke") plate_vis(); ghost_switch(); ghost_psu(); ghost_msr(); ghost_sht(); }

// 2D section through x = 0 (for the annotated section drawing)
module secpart() {
    if (sec=="plate")   plate_body();
    if (sec=="remote")  ghost_bilresa();
    if (sec=="switch")  ghost_switch();
    if (sec=="psu")     ghost_psu();
    if (sec=="msr")     ghost_msr();
    if (sec=="sht")     ghost_sht();
    if (sec=="box")     difference() {
        translate([0,0,-BOX_D]) linear_extrude(BOX_D) square([BOX_W+3, BOX_H+3], center=true);
        translate([0,0,-BOX_D+1.5]) linear_extrude(BOX_D) square([BOX_W, BOX_H], center=true); }
    if (sec=="wall") translate([0,0,-12.7]) linear_extrude(12.7)
        difference() { square([PW+40, PH+40], center=true); square([BOX_W+3, BOX_H+3], center=true); }
}
if (part == "sec") projection(cut=true) rotate([0,90,0]) secpart();
