"""Section renders of the v0.2 assembly for the docs: python renders.py -> docs/renders/*.png"""
import subprocess, sys
from pathlib import Path
from build123d import export_stl
import assembly

ROOT = Path(__file__).resolve().parents[2]
B = ROOT / "build"
R = ROOT / "docs" / "renders"


def main():
    R.mkdir(parents=True, exist_ok=True)
    export_stl(assembly.psu(), str(B / "psu_placed.stl"), tolerance=0.05)
    tool = [sys.executable, str(ROOT / "cad" / "tools" / "sections.py")]
    parts = [f"{B/'insert.stl'}:tab:red", f"{B/'trim.stl'}:tab:blue", f"{B/'psu_placed.stl'}:tab:green"]
    from params import PCB_Y, SW_Y, PASS_Y, MSR_Y
    subprocess.run(tool + [str(R / "v0.2_sections.png")] + parts +
                   ["--title", "v0.2: insert (red, UL94 V-0), trim (blue), PSU carrier (green); dashed = wall surface",
                    "--cut", "x=0", "--cut", f"y={PCB_Y}", "--cut", f"y={SW_Y}",
                    "--cut", f"y={PASS_Y}", "--cut", "z=12", "--cut", "z=-19"], check=True)
    print("wrote", R / "v0.2_sections.png")


if __name__ == "__main__":
    main()
