# Safety rules (humans and agents)

This device puts home-built parts in a mains wall box. Nothing in this repo is
certified, and nothing here makes it code-compliant. Treat every rule below as a
hard requirement.

## Electrical
1. Breaker off and verified dead (non-contact tester + meter) before opening any box.
2. The lighting load (up to 15 A) is switched by the certified rocker and wire nuts
   only. It never passes through the carrier PCB.
3. Mains-side parts must carry recognised marks: rocker (CSA/cUL; ENEC for EU/UK),
   IRM-03-5 (cURus/CB/TÜV), terminal block, fuse, MOV, wire nuts.
4. The 5 V lead runs from inside the box to the plate: use wire insulated for at
   least the mains voltage (e.g. 300 V-rated), through the single collar hole.
5. Bond grounds per local code. The printed plate is non-conductive and is not grounded.
6. Box fill must be calculated with the rocker body, PSU carrier and wire nuts counted.
7. The rocker is single-pole: it breaks the hot only. Use the breaker for work on fixtures.

## Mechanical / material
8. Barrier geometry (pocket shell, switch well, collar; the v0.2 box insert) is
   printed in a UL94 V-0 filament with its datasheet on file. PLA/PETG are for
   test fits only.
9. No holes may be added to the barrier other than the 5 V pass-through.

## Regulatory (BC, Canada)
10. Work under a homeowner electrical permit; ask the inspector about the concealed
    emergency switch and the uncertified assembly before installing more than one.
11. Expect questions from your insurer about non-approved equipment.
12. EU/UK: local rules differ (e.g. England Part P). Check before building there.

## For AI agents
- Don't claim compliance, safety, or code approval. Report what was checked.
- Don't relax constraints 2, 8, 9 or the PCB creepage targets to make something fit;
  stop and ask.
