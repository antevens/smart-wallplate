#!/bin/bash
#
# Regenerate the wiring board: 3D envelopes, libraries, project, schematic and
# board, then run ERC and DRC and export the STEP model and the PCBWay fab pack.
#
# Usage: pcb/tools/build.sh
# Environment: CAD_PYTHON (python with build123d, default .venv/bin/python),
#              KICAD_PYTHON (python with pcbnew, default python3).

set -euo pipefail

TOOLS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly TOOLS
BOARD_DIR="$(dirname "${TOOLS}")"
readonly BOARD_DIR
REPO="$(cd "${BOARD_DIR}/.." && pwd)"
readonly REPO
readonly PRJ="${BOARD_DIR}/kicad"
readonly FAB="${BOARD_DIR}/fab"
readonly OUT="${REPO}/build"

function err() {
  echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $*" >&2
}

function generate() {
  local cad_python="${CAD_PYTHON:-${REPO}/.venv/bin/python}"
  local kicad_python="${KICAD_PYTHON:-python3}"
  local script

  "${cad_python}" "${TOOLS}/gen_3d.py"
  for script in gen_libs gen_project gen_schematic gen_pcb; do
    "${kicad_python}" "${TOOLS}/${script}.py"
  done
}

function check() {
  local status=0

  mkdir -p "${OUT}"
  # creepage geometry asserts flood stderr; the reports carry the results
  kicad-cli sch erc --severity-all --exit-code-violations \
    -o "${OUT}/wiring_board_erc.rpt" "${PRJ}/wiring_board.kicad_sch" 2>/dev/null || status=1
  kicad-cli pcb drc --severity-all --schematic-parity --exit-code-violations \
    -o "${OUT}/wiring_board_drc.rpt" "${PRJ}/wiring_board.kicad_pcb" 2>/dev/null || status=1
  grep -h "^ \?\*\* \(Found\|ERC messages\)" "${OUT}/wiring_board_erc.rpt" "${OUT}/wiring_board_drc.rpt" || true
  return "${status}"
}

function export_step() {
  mkdir -p "${OUT}"
  kicad-cli pcb export step --subst-models -f -o "${OUT}/wiring_board.step" \
    "${PRJ}/wiring_board.kicad_pcb" >/dev/null 2>&1
}

function export_fab() {
  local kicad_python="${KICAD_PYTHON:-python3}"
  local pcb="${PRJ}/wiring_board.kicad_pcb"
  local rev

  rev="$("${kicad_python}" -c "import sys; sys.path.insert(0, '${TOOLS}'); from parts import REV; print(REV)")"
  rm -rf "${FAB}/gerbers"
  mkdir -p "${FAB}/gerbers"
  # board-centre (aux) origin for Gerbers, drill and centroid alike
  kicad-cli pcb export gerbers -o "${FAB}/gerbers/" --use-drill-file-origin \
    --layers F.Cu,B.Cu,F.Mask,B.Mask,F.Paste,F.Silkscreen,B.Silkscreen,Edge.Cuts \
    --subtract-soldermask --no-x2 "${pcb}" >/dev/null
  kicad-cli pcb export drill -o "${FAB}/gerbers/" --format excellon --drill-origin plot \
    --excellon-units mm --excellon-separate-th --generate-map --map-format gerberx2 \
    "${pcb}" >/dev/null
  rm -f "${FAB}"/wiring_board_*_gerbers.zip
  (cd "${FAB}/gerbers" && zip -q -j "${FAB}/wiring_board_${rev}_gerbers.zip" ./*)
  kicad-cli pcb export pos -o "${OUT}/wiring_board_pos.csv" --format csv --units mm \
    --side both --use-drill-file-origin "${pcb}" >/dev/null
  "${kicad_python}" "${TOOLS}/gen_fab.py" "${OUT}/wiring_board_pos.csv"
  kicad-cli pcb export pdf -o "${FAB}/wiring_board_${rev}_assembly_front.pdf" --mode-single \
    --layers F.Fab,F.Silkscreen,F.Courtyard,Edge.Cuts --include-border-title "${pcb}" >/dev/null
  kicad-cli pcb export pdf -o "${FAB}/wiring_board_${rev}_assembly_back.pdf" --mode-single \
    --mirror --layers B.Fab,B.Silkscreen,B.Courtyard,Edge.Cuts --include-border-title \
    "${pcb}" >/dev/null
  kicad-cli sch export pdf -o "${FAB}/wiring_board_${rev}_schematic.pdf" \
    "${PRJ}/wiring_board.kicad_sch" >/dev/null
  cp "${OUT}/wiring_board_erc.rpt" "${FAB}/erc.rpt"
  cp "${OUT}/wiring_board_drc.rpt" "${FAB}/drc.rpt"
  echo "fab pack in ${FAB}"
}

function main() {
  generate
  if ! check; then
    err "ERC or DRC reported violations; see ${OUT}/wiring_board_*.rpt"
    exit 1
  fi
  export_step
  export_fab
}

main "$@"
