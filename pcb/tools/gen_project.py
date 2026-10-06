"""Write the seed pcb/kicad/psu_carrier.kicad_pro and the custom DRC rules (.kicad_dru)."""
import json
from pathlib import Path
from parts import PRIMARY, SECONDARY

PRJ = Path(__file__).resolve().parents[1] / "kicad"


def netclass(name, track, clearance, color):
    return {"name": name, "bus_width": 12, "clearance": clearance, "diff_pair_gap": 0.25,
            "diff_pair_via_gap": 0.25, "diff_pair_width": 0.2, "line_style": 0, "microvia_diameter": 0.3,
            "microvia_drill": 0.1, "pcb_color": color, "priority": 0 if name != "Default" else 2147483647,
            "schematic_color": color, "track_width": track, "via_diameter": 0.8, "via_drill": 0.4,
            "wire_width": 6}


pro = {
    "board": {
        "design_settings": {
            "defaults": {"board_outline_line_width": 0.05, "copper_text_size_h": 1.5, "copper_text_size_v": 1.5,
                         "silk_line_width": 0.15, "silk_text_size_h": 1.0, "silk_text_size_v": 1.0,
                         "silk_text_thickness": 0.15},
            # PCBWay standard-process minimums (with margin)
            "rules": {"min_clearance": 0.2, "min_copper_edge_clearance": 0.5, "min_hole_clearance": 0.25,
                      "min_hole_to_hole": 0.5, "min_through_hole_diameter": 0.3, "min_track_width": 0.2,
                      "min_via_annular_width": 0.15, "min_via_diameter": 0.6, "min_silk_clearance": 0.0,
                      "min_text_height": 0.8, "min_text_thickness": 0.12, "solder_mask_to_copper_clearance": 0.0},
            "rule_severities": {"lib_footprint_issues": "warning", "lib_footprint_mismatch": "warning"},
        },
    },
    "meta": {"filename": "psu_carrier.kicad_pro", "version": 3},
    "net_settings": {
        "classes": [netclass("Default", 0.3, 0.2, "rgba(0, 0, 0, 0.000)"),
                    netclass("Primary", 1.2, 0.5, "rgb(194, 0, 0)"),
                    netclass("Secondary", 0.6, 0.2, "rgb(0, 132, 0)")],
        "meta": {"version": 4},
        "netclass_assignments": None,
        "netclass_patterns": [{"netclass": "Primary", "pattern": f"/{n}"} for n in PRIMARY]
                             + [{"netclass": "Secondary", "pattern": n} for n in SECONDARY],
    },
    "schematic": {"meta": {"version": 1}},
    "sheets": [["", "Root"]],
}

DRU = """(version 1)
# Isolation design TARGETS for the PSU carrier (pcb/SPEC.md, AGENTS.md hard constraint 3).
# These are NOT a compliance claim. A human must review them against IEC 62368-1
# (reinforced insulation, 250 VAC working, pollution degree 2, OVC II) before fab.

(rule "Board edge clearance"
    (constraint edge_clearance (min 0.5mm)))

(rule "PRI-SEC clearance >= 6.0 mm"
    (condition "A.NetClass == 'Primary' && B.NetClass == 'Secondary'")
    (constraint clearance (min 6.0mm)))

(rule "PRI-SEC creepage >= 6.0 mm"
    (condition "A.NetClass == 'Primary' && B.NetClass == 'Secondary'")
    (constraint creepage (min 6.0mm)))

(rule "L-N clearance >= 2.5 mm"
    (condition "A.NetName == '/N' && (B.NetName == '/L_IN' || B.NetName == '/L_F')")
    (constraint clearance (min 2.5mm)))

(rule "L-N creepage >= 2.5 mm"
    (condition "A.NetName == '/N' && (B.NetName == '/L_IN' || B.NetName == '/L_F')")
    (constraint creepage (min 2.5mm)))

(rule "Primary copper to board edge >= 1.0 mm"
    (condition "A.NetClass == 'Primary'")
    (constraint edge_clearance (min 1.0mm)))

(rule "PS1 body outline may cross the isolation slot"
    # The slot runs under the module by design; only the module's silkscreen body
    # outline is affected. Copper edge clearance is unchanged.
    (layer "F.Silkscreen")
    (condition "A.Parent.Reference == 'PS1' || B.Parent.Reference == 'PS1'")
    (constraint silk_clearance (min -10mm))
    (constraint edge_clearance (min -10mm)))

"""

if __name__ == "__main__":
    # Seed project file (libs/sheets); gen_pcb.py re-saves it with netclasses and
    # board rules set through the pcbnew API (KiCad ignores hand-written netclasses).
    (PRJ / "psu_carrier.kicad_pro").write_text(json.dumps(pro, indent=2) + "\n")
    (PRJ / "psu_carrier.kicad_dru").write_text(DRU)
    print("project seed + rules written")
