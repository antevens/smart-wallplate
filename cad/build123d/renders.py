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
    # microphone (D-29): sound hole, gasket, stiffener, flex and mic body, zoomed
    import sensor_flex
    from params import MIC_X, MIC_PORT
    fp = sensor_flex.parts()
    export_stl(fp["flex"], str(B / "flex_placed.stl"), tolerance=0.01)
    export_stl(fp["mic"], str(B / "mic_placed.stl"), tolerance=0.01)
    x, y = MIC_X, MIC_PORT[1]
    subprocess.run(tool + [str(R / "v0.3_mic_section.png"), f"{B/'insert.stl'}:tab:red", f"{B/'trim.stl'}:tab:blue",
                           f"{B/'flex_placed.stl'}:tab:orange", f"{B/'mic_placed.stl'}:tab:purple",
                           "--title", "microphone (D-29): trim skin + sound hole (blue), gasket + mic (purple), "
                           "flex + stiffener (orange), insert (red)",
                           "--cut", f"y={y:.2f}@{x - 7:.1f},{x + 7:.1f},7,14",
                           "--cut", f"x={x:.2f}@{y - 5:.1f},{y + 9:.1f},7,14", "--dpi", "110"], check=True)
    print("wrote", R / "v0.3_mic_section.png")


if __name__ == "__main__":
    main()
