PY ?= python3
CAD = cad/build123d

.PHONY: cad check clean
cad:
	cd $(CAD) && $(PY) wallplate.py && $(PY) assembly.py
	cp build/pcb_outline.dxf pcb/mech/pcb_outline.dxf
check:
	cd $(CAD) && $(PY) wallplate.py --check
clean:
	rm -rf build
