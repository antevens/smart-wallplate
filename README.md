# Smart wall plate

Replacement for a single-gang light switch: recessed IKEA BILRESA remote, hidden
emergency rocker, Apollo MSR-2 mmWave presence + SHT45 climate, powered by a
Mean Well IRM-03-5 on a small carrier PCB.

Start with `AGENTS.md` (for people too), then `docs/SAFETY.md`.

```
pip install -r cad/build123d/requirements.txt
make cad check
```
Outputs land in `build/`. The first-pass renders are in `reference/v0.1-openscad/renders/`.
