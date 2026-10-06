#!/usr/bin/env bash
# Regenerate the KiCad project, verify it, and write PCBWay fab outputs + STEP.
# Usage: pcb/tools/export_fab.sh   (from the repo root; needs KiCad 9 + .venv for the 3D envelope)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
T="$ROOT/pcb/tools"; K="$ROOT/pcb/kicad"; F="$ROOT/pcb/fab"
PY3D="${PY3D:-$ROOT/.venv/bin/python}"
REV=v0.2

# gen_pcb.py needs KiCad's own Python (the one that can `import pcbnew`), which an
# active virtualenv hides. KICAD_PYTHON overrides the search.
KIPY=""
for p in "${KICAD_PYTHON:-}" /usr/bin/python3 /usr/local/bin/python3 python3 \
         /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3; do
  [ -n "$p" ] && command -v "$p" >/dev/null 2>&1 && "$p" -c "import pcbnew" >/dev/null 2>&1 && { KIPY="$p"; break; }
done
[ -n "$KIPY" ] || { echo "no Python with KiCad's pcbnew module found; set KICAD_PYTHON" >&2; exit 1; }
PY=python3; command -v "$PY" >/dev/null || PY="$KIPY"

cd "$T"
"$PY3D" gen_3d.py
"$PY" gen_libs.py
"$PY" gen_project.py
"$PY" gen_schematic.py
"$KIPY" gen_pcb.py

cd "$K"
kicad-cli sch erc --severity-all --exit-code-violations -o "$F/erc.rpt" psu_carrier.kicad_sch
kicad-cli pcb drc --severity-all --schematic-parity --exit-code-violations -o "$F/drc.rpt" psu_carrier.kicad_pcb

rm -rf "$F/gerbers"; mkdir -p "$F/gerbers"
kicad-cli pcb export gerbers -o "$F/gerbers/" \
  --layers F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,Edge.Cuts \
  --subtract-soldermask --no-x2 psu_carrier.kicad_pcb
kicad-cli pcb export drill -o "$F/gerbers/" --format excellon --excellon-units mm \
  --excellon-separate-th --generate-map --map-format gerberx2 psu_carrier.kicad_pcb
rm -f "$F/psu_carrier_${REV}_gerbers.zip"
(cd "$F/gerbers" && zip -q -j "$F/psu_carrier_${REV}_gerbers.zip" ./*)

kicad-cli pcb export pos -o "$F/psu_carrier_${REV}_centroid.csv" --format csv --units mm \
  --side front --use-drill-file-origin psu_carrier.kicad_pcb
"$PY" "$T/gen_bom.py"

kicad-cli pcb export pdf -o "$F/psu_carrier_${REV}_assembly.pdf" --mode-single \
  --layers F.Fab,F.Silkscreen,F.Courtyard,Edge.Cuts --include-border-title psu_carrier.kicad_pcb
kicad-cli pcb export pdf -o "$F/psu_carrier_${REV}_back_silk.pdf" --mode-single --mirror \
  --layers B.Silkscreen,B.Cu,Edge.Cuts --include-border-title psu_carrier.kicad_pcb
kicad-cli sch export pdf -o "$F/psu_carrier_${REV}_schematic.pdf" psu_carrier.kicad_sch

kicad-cli pcb export step -o "$ROOT/cad/vendor/psu_carrier.step" --drill-origin --subst-models \
  --force psu_carrier.kicad_pcb
kicad-cli pcb render -o "$F/psu_carrier_3d_top.png" --side top --width 1600 --height 1200 \
  --quality high psu_carrier.kicad_pcb
kicad-cli pcb render -o "$F/psu_carrier_3d_bottom.png" --side bottom --width 1600 --height 1200 \
  --quality high psu_carrier.kicad_pcb
kicad-cli pcb render -o "$F/psu_carrier_3d.png" --side top --rotate "-45,0,45" --width 1600 \
  --height 1200 --quality high psu_carrier.kicad_pcb
echo "fab outputs in $F"
