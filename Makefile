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

.PHONY: setup system-deps slicer cad check print pcb renders all clean
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

cad:            ## STEP/STL of insert + trim, print-oriented STLs (build/print), assembly, PCB outline DXF
	cd $(CAD) && $(PY) export.py && $(PY) assembly.py
	cp build/pcb_outline.dxf pcb/mech/pcb_outline.dxf

check:          ## geometry, barrier, PSU fit and printability checks - must pass
	cd $(CAD) && $(PY) checks.py

print: $(if $(filter $(abspath $(ORCA_APPIMAGE)),$(SLICER)),$(ORCA_APPIMAGE))  ## OrcaSlicer projects (print/*.3mf) + G-code (build/print/gcode)
	SLICER="$(SLICER)" $(PY) print/slice.py

pcb:            ## KiCad project, ERC + DRC, PCBWay fab pack, cad/vendor/psu_carrier.step
	pcb/tools/export_fab.sh

renders:        ## docs/renders/*.png: section sheet + shaded 3D views (3D needs xvfb-run headless)
	cd $(CAD) && $(PY) renders.py
	cd $(CAD) && $(if $(DISPLAY),,xvfb-run -a) $(PY) render3d.py

all: pcb cad check print renders

clean:
	rm -rf build
