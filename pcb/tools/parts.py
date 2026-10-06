"""Single source for the PSU carrier parts: schematic, PCB and BOM read this.

Board coordinates: origin = board centre, X right, Yup = toward the rocker
(KiCad y = -Yup). Components on F side, which faces INTO the wall box.
Source of truth for connectivity: ../netlist.yaml (kept in sync by hand).
"""
import uuid

NS = uuid.UUID("6d1c1f3e-5a4b-4e0b-9a51-7f3b2f0e2c01")


def uid(*names):
    return str(uuid.uuid5(NS, "/".join(names)))


LIB = "psu_carrier"
IRM_DS = "https://www.meanwell.com/Upload/PDF/IRM-03/IRM-03-SPEC.PDF"

# Layout: PRIMARY (mains) on the right half of the top strip, SECONDARY (5 V) on the
# left half, separated by a routed slot from the top edge to under the module.
# ref: symbol, footprint, value, pin->net, pcb (x, Yup, rot_deg), bom fields
PARTS = {
    "J1": dict(sym="Screw_Terminal_01x02",
               fp="TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal_Pad2.4mm",
               value="MKDS 1,5/2-5,08", nets={"1": "L_IN", "2": "N"},
               pcb=(5.08, 15.0, 180),   # pad1 L' right, pad2 N at (0,15); wire entry faces +Yup
               mfr="Phoenix Contact", mpn="1715721",
               desc="Terminal block 2p 5.08 mm screw, mains in: 1=L' (load side of rocker), 2=N",
               ds="https://www.phoenixcontact.com/en-ca/products/pcb-terminal-block-mkds-15-2-508-1715721"),
    "F1": dict(sym="Fuse", fp="Fuse_Littelfuse_372_D8.50mm", value="T1A 250V",
               nets={"1": "L_IN", "2": "L_F"}, pcb=(14.0, 17.0, 270),  # pad2 at (14,11.92)
               mfr="Littelfuse", mpn="39211000000",
               desc="Fuse TR5 time-lag 1 A 250 VAC, 392 series (IEC 60127-3). RATING = DESIGNER'S CHOICE, Mean Well gives none: human review",
               ds="https://www.littelfuse.com/products/fuses/axial-radial-thru-hole-fuses/te5-fuses/392"),
    "RV1": dict(sym="Varistor", fp="RV_Disc_D7mm_W4.5mm_P5mm", value="S07K275",
                nets={"1": "L_F", "2": "N"}, pcb=(13.5, 4.5, 180),  # pad2 at (8.5,6.6)
                mfr="TDK (EPCOS)", mpn="B72207S0271K101",
                desc="MOV 275 VAC 7 mm disc, 5.0 mm pitch",
                ds="https://www.digikey.com/en/products/detail/epcos-tdk-electronics/B72207S0271K101/593820"),
    "PS1": dict(sym="IRM-03-5", fp="Converter_ACDC_MeanWell_IRM-03-xx_THT", value="IRM-03-5",
                nets={"1": "L_F", "3": "N", "16": "+5V", "14": "GND", "5": "NC5"},
                pcb=None,  # placed by pin 1 position, see gen_pcb.py
                mfr="Mean Well", mpn="IRM-03-5",
                desc="AC-DC module 85-305 VAC in, 5 V 600 mA, 37x24x15 mm, I/P-O/P 4.2 kVAC",
                ds=IRM_DS),
    "C1": dict(sym="C_Polarized", fp="CP_Radial_D5.0mm_P2.00mm", value="47uF 16V",
               nets={"1": "+5V", "2": "GND"}, pcb=(-12.0, 9.0, 180),  # pad2 at (-14,9)
               mfr="Panasonic", mpn="EEU-FC1C470",
               desc="Electrolytic 47 uF 16 V radial 5x11 mm, 2.0 mm pitch, 105 C, FC series (or equivalent)",
               ds="https://www.distrelec.ch/en/radial-electrolytic-capacitor-47uf-52ua-16v-175ma-panasonic-eeufc1c470/p/30013731"),
    "J2": dict(sym="Conn_01x02", fp="JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical", value="5V out",
               nets={"1": "+5V", "2": "GND"}, pcb=(-12.0, 17.0, 180),  # pad2 at (-14.5,17)
               mfr="JST", mpn="B2B-XH-A(LF)(SN)",
               desc="JST XH 2p vertical header, 5 V to MSR-2 (1=+5V, 2=GND)",
               ds="https://www.jst-mfg.com/product/pdf/eng/eXH.pdf"),
}

# PS1 pin 1 (AC/L) target position and the other pins we verify after placement
# orientation 270: AC end on the right (primary side), DC end on the left (secondary).
PS1_ROT = 270
PS1_PINS = {"1": (15.24, -0.61), "3": (10.16, -0.61), "5": (-15.24, -0.61),
            "16": (-10.16, -18.39), "14": (-15.24, -18.39)}

PRIMARY = ["L_IN", "L_F", "N"]
SECONDARY = ["+5V", "GND"]

BOARD = dict(w=42.0, h=44.0, t=1.6, r=1.5,
             slot_x=(-7.5, -5.5), slot_bottom=-8.0,   # notch from the top edge
             rail_keepout=2.0, edge_keepout=1.0)
REV = "v0.2"

# Tracks: net -> list of (layer, width, [(x, Yup), ...]) polylines
TRACKS = {
    "L_IN": [("F.Cu", 1.2, [(5.08, 15.0), (14.0, 17.0)])],
    "L_F": [("F.Cu", 1.2, [(14.0, 11.92), (13.5, 11.4), (13.5, 4.5), (15.24, 2.8), (15.24, -0.61)])],
    "N": [("B.Cu", 1.2, [(0.0, 15.0), (0.0, 9.0), (8.5, 6.6), (8.5, 3.0), (10.16, 1.3), (10.16, -0.61)])],
    "+5V": [("B.Cu", 0.6, [(-10.16, -18.39), (-12.0, -16.5), (-12.0, 9.0), (-12.0, 17.0)])],
    "GND": [("B.Cu", 0.6, [(-15.24, -18.39), (-17.5, -16.0), (-17.5, 6.0), (-14.0, 9.0), (-14.0, 15.0), (-14.5, 17.0)])],
}
