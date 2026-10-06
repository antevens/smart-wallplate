import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle, Polygon

fig = plt.figure(figsize=(14, 8), dpi=150)
ax = fig.add_axes([0.03, 0.08, 0.46, 0.84])
ax2 = fig.add_axes([0.52, 0.08, 0.46, 0.84])

# ---------------- board layout (component side) ----------------
BW, BH = 40, 36
ax.add_patch(FancyBboxPatch((0, 0), BW, BH, boxstyle="round,pad=0,rounding_size=1.5",
             fc="#1f6b3a", ec="#0d3", lw=1.2))
# isolation slot under module (primary | secondary)
slot_x = 27.0
ax.add_patch(Rectangle((slot_x-0.75, -0.01), 1.5, 26, fc="white", ec="#0d3", lw=0.8))
ax.annotate("routed isolation slot\n(target ≥6 mm creepage)", xy=(slot_x, 1.0), xytext=(slot_x+6, -5.2), fontsize=6.5, ha="center", arrowprops=dict(arrowstyle="-", lw=0.6))

# IRM-03-5 outline (long axis horizontal), pins
mx, my = 1.5, 11
ax.add_patch(Rectangle((mx, my), 37, 24, fc="#202020", ec="#bbb", lw=0.8, alpha=0.88))
ax.text(mx+18.5, my+16, "Mean Well IRM-03-5\n5 V / 600 mA", ha="center", va="center",
        color="white", fontsize=8.5, weight="bold")
pins = [(mx+3.5, my+4, "AC/N"), (mx+3.5, my+20, "AC/L"),
        (mx+33.5, my+4, "−Vo"), (mx+33.5, my+20, "+Vo")]
for x, y, l in pins:
    ax.add_patch(Circle((x, y), 1.0, fc="#d4a017", ec="k", lw=0.4))
    ax.text(x+(2.0 if x < 20 else -2.0), y, l, color="#ffd54f", fontsize=6.5,
            ha="left" if x < 20 else "right", va="center")
ax.text(mx+18.5, my+5, "pin positions approximate – use Mean Well footprint", ha="center",
        color="#ccc", fontsize=5.5, style="italic")

# primary-side parts in the bottom strip
def part(x, y, w, h, fc, lab, sub=""):
    ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec="k", lw=0.6))
    ax.text(x+w/2, y+h/2, lab, ha="center", va="center", fontsize=7, weight="bold",
            color="white" if fc not in ("#e8e0c8", "#f5f5f5") else "k")
    if sub: ax.text(x+w/2, y-0.9, sub, ha="center", va="top", fontsize=5.6, color="white")
part(1.0, 2.0, 10.2, 7.5, "#2e8b57", "J1", "L' / N in")
part(12.5, 3.0, 8.5, 5.0, "#e8e0c8", "F1", "slow-blow")
part(21.5, 2.5, 4.5, 6.0, "#1565c0", "RV1", "MOV")
part(30.0, 2.5, 7.5, 5.8, "#f5f5f5", "J2", "5 V out")

# primary traces (thick, wide spacing)
tr = dict(color="#c9a227", lw=3.2, solid_capstyle="round", alpha=0.85)
ax.plot([8.7, 8.7, 12.5], [9.5, 9.5, 5.5], **tr)                # J1 L' -> F1
ax.plot([21, 22.5, 22.5, mx+3.5], [5.5, 5.5, 10.4, my+20], **tr)  # F1 -> AC/L (under module)
ax.plot([22.5, 23.75], [8.5, 8.5], **tr)                        # RV1 top on fused L
ax.plot([23.75, 23.75, 0.9, 0.9, 3.6, mx+3.5], [2.5, 1.0, 1.0, 10.2, 10.2, my+4], **tr)  # RV1 -> N, J1 N -> AC/N
ax.plot([3.6, 3.6], [9.5, 10.2], **tr)
# secondary traces
ts = dict(color="#c9a227", lw=1.8, solid_capstyle="round", alpha=0.85)
ax.plot([mx+33.5, 35.5, 35.5], [my+20, my+20, 8.3], **ts)
ax.plot([mx+33.5, 32, 32], [my+4, my+4, 8.3], **ts)
# mounting: board edges ride in the plate's rails
for x in (0, BW): ax.add_patch(Rectangle((x-1.3, 0), 1.3 if x == 0 else 1.3, BH, fc="#9e9e9e", alpha=0.35))
ax.text(-1.8, BH/2, "rail", rotation=90, va="center", fontsize=6.5, color="#555")
ax.text(BW+0.6, BH/2, "rail", rotation=90, va="center", fontsize=6.5, color="#555")
ax.annotate("", xy=(0, -2.6), xytext=(BW, -2.6), arrowprops=dict(arrowstyle="<->", lw=0.7))
ax.text(BW/2-8, -4.2, "40 mm", ha="center", fontsize=7.5)
ax.annotate("", xy=(-3.6, 0), xytext=(-3.6, BH), arrowprops=dict(arrowstyle="<->", lw=0.7))
ax.text(-5.0, BH/2, "36 mm", rotation=90, va="center", fontsize=7.5)
ax.text(8, BH+1.2, "PRIMARY (mains)", fontsize=8, color="#c62828", weight="bold")
ax.text(29.5, BH+1.2, "SECONDARY (SELV)", fontsize=8, color="#1565c0", weight="bold")
ax.set_xlim(-7, 45); ax.set_ylim(-6, 40); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("PSU carrier PCB v0.1 – 2-layer, 1.6 mm FR-4 (component side)", fontsize=10)

# ---------------- wiring / schematic ----------------
ax2.axis("off"); ax2.set_xlim(0, 100); ax2.set_ylim(0, 100)
ax2.set_title("Box wiring – 15 A lighting path stays OFF the PCB", fontsize=10)
def box(x, y, w, h, t, fc="#f4f4f4", ec="#333"):
    ax2.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4", fc=fc, ec=ec, lw=1))
    ax2.text(x+w/2, y+h/2, t, ha="center", va="center", fontsize=8)
box(2, 78, 14, 8, "LINE\n(supply)", "#ffe0e0")
box(2, 14, 14, 8, "NEUTRAL", "#e0e0ff")
box(33, 76, 20, 12, "Emergency rocker\nBulgin C1300\n(cULus/CSA)", "#ffcdd2")
box(78, 78, 18, 8, "LOAD\n→ smart bulbs", "#fff3cd")
box(42, 40, 26, 18, "Carrier PCB\nJ1 → F1 → RV1\n→ IRM-03-5", "#c8e6c9")
box(78, 40, 18, 18, "MSR-2\n(+ SHT45\non I²C)", "#e0e0e0")
L = dict(lw=2.2, color="#c62828"); N = dict(lw=2.2, color="#1e40af"); S = dict(lw=1.4, color="#555")
ax2.plot([16, 33], [82, 82], **L)
ax2.plot([53, 78], [82, 82], **L)
ax2.add_patch(Circle((64, 82), 1.4, fc="#c62828"))
ax2.text(64, 85.5, "wire nut\n(load side)", ha="center", fontsize=6.5)
ax2.plot([64, 64, 50], [82, 66, 58.4], **L)
ax2.text(65.5, 69, "pigtail 18 AWG\nL' → J1", fontsize=6.5)
ax2.plot([16, 87], [18, 18], **N)
ax2.add_patch(Circle((50, 18), 1.4, fc="#1e40af"))
ax2.plot([50, 50], [18, 39.6], **N)
ax2.text(51.5, 26, "N → J1", fontsize=6.5)
ax2.plot([87, 87], [18, 77.6], **N); ax2.text(88, 30, "N → bulbs", fontsize=6.5)
ax2.plot([68.4, 77.6], [49, 49], **S)
ax2.text(73, 51.5, "5 V, double-\ninsulated lead\nthrough collar", ha="center", fontsize=6)
ax2.text(2, 6,
 "• Switch OFF kills bulbs AND the MSR-2 (PSU fed from load side).\n"
 "• Ground: bond to box / device per local code (printed plate needs no ground).\n"
 "• F1, RV1 values: size for 85–305 VAC per the IRM-03 datasheet; MOV ≈275 VAC covers 120 V & 230 V.\n"
 "• Wire sizes shown are typical NA; follow local code and box-fill rules.",
 fontsize=7, va="bottom")
plt.savefig("06_psu_pcb_and_wiring.png", facecolor="white")
