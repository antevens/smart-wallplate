"""Section renders of the assembly for the docs: python renders.py -> docs/renders/*.png"""
import subprocess, sys
from pathlib import Path
from build123d import export_stl
import assembly

ROOT = Path(__file__).resolve().parents[2]
B = ROOT / "build"
R = ROOT / "docs" / "renders"


def main():
    R.mkdir(parents=True, exist_ok=True)
    import bilresa
    export_stl(assembly.wiring_board(), str(B / "wiring_board_placed.stl"), tolerance=0.05)
    export_stl(bilresa.build(), str(B / "bilresa_placed.stl"), tolerance=0.05)
    import post
    export_stl(post.placed(), str(B / "posts_placed.stl"), tolerance=0.02)
    tool = [sys.executable, str(ROOT / "cad" / "tools" / "sections.py")]
    parts = [f"{B/'insert.stl'}:tab:red", f"{B/'trim.stl'}:tab:blue", f"{B/'wiring_board_placed.stl'}:tab:green",
             f"{B/'bilresa_placed.stl'}:tab:gray", f"{B/'posts_placed.stl'}:tab:orange"]
    from params import WB_Y, WAGO_Y, WB_FRONT_Z, WB, SW_Y, PASS_Y, MSR_Y, MOUNT_HOLES
    subprocess.run(tool + [str(R / "v0.3_sections.png")] + parts +
                   ["--title", "v0.3: insert (red, UL94 V-0), trim (blue), wiring board (green), board posts (orange), "
                    "BILRESA (grey); dashed = wall",
                    "--cut", "x=0", "--cut", f"x={MOUNT_HOLES[0][0]}", "--cut", f"y={WB_Y + WAGO_Y}", "--cut", f"y={SW_Y}",
                    "--cut", f"y={PASS_Y}", "--cut", "z=12", "--cut", f"z={WB_FRONT_Z - WB[2] / 2}"], check=True)
    print("wrote", R / "v0.3_sections.png")


if __name__ == "__main__":
    main()
