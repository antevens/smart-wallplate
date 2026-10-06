VENV ?= .venv
PY ?= $(abspath $(VENV))/bin/python
CAD = cad/build123d

.PHONY: setup cad check print pcb renders all clean
setup:
	python3 -m venv $(VENV) && $(VENV)/bin/pip install -r $(CAD)/requirements.txt

cad:            ## STEP/STL of insert + trim, print-oriented STLs (build/print), assembly, PCB outline DXF
	cd $(CAD) && $(PY) export.py && $(PY) assembly.py
	cp build/pcb_outline.dxf pcb/mech/pcb_outline.dxf

check:          ## geometry, barrier, PSU fit and printability checks - must pass
	cd $(CAD) && $(PY) checks.py

print:          ## ElegooSlicer projects (print/*.3mf) + G-code (build/print/gcode); needs ELEGOO_SLICER
	$(PY) print/slice.py

pcb:            ## KiCad project, ERC + DRC, PCBWay fab pack, cad/vendor/psu_carrier.step
	pcb/tools/export_fab.sh

renders:        ## docs/renders/v0.2_sections.png
	cd $(CAD) && $(PY) renders.py

all: pcb cad check print renders

clean:
	rm -rf build
