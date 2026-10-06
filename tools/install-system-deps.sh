#!/usr/bin/env bash
# System packages for the whole toolchain on Ubuntu 24.04 (the dev container base).
#   python3-venv            CAD venv (make setup)
#   kicad 9 (PPA)           PCB generation, ERC/DRC, fab outputs (make pcb)
#   xvfb, webkit2gtk, GL    run the OrcaSlicer AppImage headless (make print)
# OrcaSlicer itself is downloaded and checksum-verified by `make slicer`.
set -euo pipefail
SUDO=$([ "$(id -u)" = 0 ] && echo "" || echo sudo)
$SUDO apt-get update -qq
$SUDO apt-get install -y -qq software-properties-common python3-venv python3-pip curl
$SUDO add-apt-repository -y ppa:kicad/kicad-9.0-releases
$SUDO apt-get update -qq
$SUDO apt-get install -y -qq --no-install-recommends kicad kicad-footprints kicad-symbols kicad-packages3d
$SUDO apt-get install -y -qq xvfb libwebkit2gtk-4.1-0 libgtk-3-0 libgl1 libegl1 libglu1-mesa
