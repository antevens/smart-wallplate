VENV ?= .venv
PY ?= $(abspath $(VENV))/bin/python
CAD = cad/build123d

# OrcaSlicer: pinned Linux AppImage, fetched + verified by `make slicer`.
# Override with SLICER=/path/to/OrcaSlicer.AppImage (or squashfs-root/AppRun).
ORCA_VERSION ?= 2.4.2
ORCA_SHA256 ?= d12fb8c8eac1aecd2dfb6377acd48f994f8fa439ed5292fa532dd82880f029fd
ORCA_URL = https://github.com/OrcaSlicer/OrcaSlicer/releases/download/v$(ORCA_VERSION)/OrcaSlicer_Linux_AppImage_Ubuntu2404_V$(ORCA_VERSION).AppImage
ORCA_APPIMAGE = .tools/OrcaSlicer_$(ORCA_VERSION).AppImage
SLICER ?= $(abspath $(ORCA_APPIMAGE))

.PHONY: setup system-deps slicer cad check print pcb renders eu all clean
system-deps:    ## apt packages: KiCad 9, python venv, headless libs for OrcaSlicer (Ubuntu 24.04, sudo)
	tools/install-system-deps.sh

setup: slicer   ## python venv + requirements, OrcaSlicer AppImage
	python3 -m venv $(VENV) && $(VENV)/bin/pip install -r $(CAD)/requirements.txt

slicer: $(ORCA_APPIMAGE)

$(ORCA_APPIMAGE):
	mkdir -p $(dir $@)
	curl -fL --retry 3 -o $@.part $(ORCA_URL)
	echo "$(ORCA_SHA256)  $@.part" | sha256sum -c -
	chmod +x $@.part && mv $@.part $@

cad:            ## STEP/STL of insert + trim, print-oriented STLs (build/print), assembly, replacement back cover
	cd $(CAD) && $(PY) export.py && $(PY) assembly.py && $(PY) backcover.py

check:          ## geometry, barrier, wiring-board fit and printability checks - must pass
	cd $(CAD) && $(PY) checks.py

print: $(if $(filter $(abspath $(ORCA_APPIMAGE)),$(SLICER)),$(ORCA_APPIMAGE))  ## OrcaSlicer projects (print/*.3mf) + G-code (build/print/gcode)
	SLICER="$(SLICER)" $(PY) print/slice.py

pcb:            ## KiCad: wiring board (pcb/), sensor flex + target board (pcb/sensor/), EU PSU board (pcb/eu/): ERC + DRC, fab packs
	pcb/tools/build.sh
	pcb/sensor/tools/build.sh
	pcb/eu/tools/build.sh

WB_PCB = pcb/kicad/wiring_board.kicad_pcb
EU_MB = pcb/eu/kicad/eu_mains_board.kicad_pcb
EU_LV = pcb/eu/kicad/eu_5v_board.kicad_pcb
RENDER_PCB = kicad-cli pcb render --quality high --width 1600 --height 1200

renders:        ## docs/renders/*.png: section sheet, shaded 3D views, wiring board (3D needs xvfb-run headless)
	cd $(CAD) && $(PY) renders.py
	cd $(CAD) && $(if $(DISPLAY),,xvfb-run -a) $(PY) render3d.py
	cd $(CAD) && $(if $(DISPLAY),,xvfb-run -a) $(PY) render_backcover.py
	$(RENDER_PCB) --side top -o docs/renders/wiring_board_front.png $(WB_PCB)
	$(RENDER_PCB) --side bottom -o docs/renders/wiring_board_back.png $(WB_PCB)
	$(RENDER_PCB) --side top --rotate "-40,0,30" -o docs/renders/wiring_board_iso_front.png $(WB_PCB)
	$(RENDER_PCB) --side bottom --rotate "40,0,-30" -o docs/renders/wiring_board_iso_back.png $(WB_PCB)
	python3 pcb/tools/render_bare.py $(WB_PCB)
	python3 pcb/tools/render_bare.py pcb/sensor/kicad/sensor_flex.kicad_pcb sensor_flex --copper-only
	python3 pcb/tools/render_bare.py pcb/sensor/kicad/power_jumper.kicad_pcb power_jumper --copper-only
	python3 pcb/tools/render_bare.py pcb/sensor/kicad/cover_flex.kicad_pcb cover_flex --copper-only
	python3 pcb/tools/render_bare.py pcb/sensor/kicad/eu_sensor_flex.kicad_pcb eu_sensor_flex --copper-only
	$(RENDER_PCB) --side top -o docs/renders/eu_mains_board_front.png $(EU_MB)
	$(RENDER_PCB) --side bottom -o docs/renders/eu_mains_board_back.png $(EU_MB)
	python3 pcb/tools/render_bare.py $(EU_MB) eu_mains_board --copper-only
	$(RENDER_PCB) --side top -o docs/renders/eu_5v_board_front.png $(EU_LV)
	$(RENDER_PCB) --side bottom -o docs/renders/eu_5v_board_back.png $(EU_LV)
	python3 pcb/tools/render_bare.py $(EU_LV) eu_5v_board --copper-only

eu:             ## EU variant (D-30, cad/build123d/eu/): STEP/STL to build/eu, checks, renders (docs/renders/eu_*.png)
	cd $(CAD)/eu && $(PY) cap_eu.py && $(PY) trim_eu.py && $(PY) checks_eu.py
	cd $(CAD)/eu && $(if $(DISPLAY),,xvfb-run -a) $(PY) render_eu.py

all: pcb cad check print renders

clean:
	rm -rf build
