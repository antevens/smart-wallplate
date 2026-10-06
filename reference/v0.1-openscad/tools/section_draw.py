import re, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch

def load(fn):
    s=open(fn).read()
    d=" ".join(re.findall(r'd="([^"]*)"',s,re.S))
    verts=[];codes=[]
    for tok in re.findall(r'([MLZ])([^MLZ]*)',d):
        c,args=tok
        if c=='Z':
            if verts: verts.append(verts[-1]); codes.append(Path.CLOSEPOLY)
            continue
        x,y=map(float,args.replace(',',' ').split()[:2])
        verts.append((x,-y)); codes.append(Path.MOVETO if c=='M' else Path.LINETO)
    return Path(verts,codes)

parts=[("wall","#d9d4c7","Drywall"),("box","#8a96a3","Device box (2.5\" deep)"),
       ("plate","#f2f2f2","Printed plate"),("remote","#f3e6c8","BILRESA (intact)"),
       ("switch","#b22222","Emergency rocker"),("psu","#2e7d32","IRM-03-5 carrier PCB"),
       ("msr","#333333","MSR-2"),("sht","#7b1fa2","SHT45")]
fig,ax=plt.subplots(figsize=(9,12),dpi=150)
for p,col,lab in parts:
    pa=load(f"sec_{p}.svg")
    ax.add_patch(PathPatch(pa,facecolor=col,edgecolor="#222",lw=0.6,label=lab,fill=True))
from matplotlib.patches import Rectangle
ax.add_patch(Rectangle((-63.5,-39.6),63.5,79.2,color="#ffd6d6",alpha=0.45,zorder=0))
ax.text(-60,36,"MAINS SIDE\n(inside box)",color="#a00",fontsize=10,va="top")
ax.text(16,72,"ROOM",color="#555",fontsize=10,va="top")
ax.axvline(0,color="#999",ls="--",lw=0.8); ax.text(0.5,-80,"wall surface z=0",fontsize=7,color="#666")
def note(xy,txt,xyt):
    ax.annotate(txt,xy=xy,xytext=xyt,fontsize=8,arrowprops=dict(arrowstyle="-",lw=0.6,color="#444"),
                bbox=dict(boxstyle="round,pad=0.25",fc="white",ec="#bbb",lw=0.5))
note((10,57),"MSR-2 bay\n1.2 mm radar skin",(22,60))
note((-12,18),"Rocker well + snap-in\ncutout 27.3×12.3",(-58,34))
note((-25,-10),"PSU slot rails\n(PCB slides in)",(-62,-6))
note((10,-62),"SHT45 bay, vented\nface + bottom edge",(22,-58))
note((6,-30),"Pocket shell = barrier\n(flame-rated filament)",(20,-30))
note((-10,41.6),"#6-32 to box ears\n83.3 mm pitch",(22,38))
ax.set_xlim(-70,45); ax.set_ylim(-85,80); ax.set_aspect("equal")
ax.set_xlabel("depth from wall (mm)  —  negative = into box"); ax.set_ylabel("height (mm)")
ax.set_title("Section through centreline (x = 0) — first pass v0.1\nplaceholder dims: measure BILRESA, switch body, MSR-2",fontsize=10)
ax.legend(loc="lower left",fontsize=7,framealpha=0.95)
ax.grid(alpha=0.2)
plt.tight_layout(); plt.savefig("03_section.png")
