# Safety rules (humans and agents)

This device puts home-built parts in a mains wall box. Nothing in this repo is
certified, and nothing here makes it code-compliant. Treat every rule below as a
hard requirement.

## Electrical
1. Breaker off and verified dead (non-contact tester + meter) before opening any box.
2. The lighting load (up to 15 A) is switched by the certified rocker only. Line,
   neutral and ground pass through the wiring PCB via listed push-in terminals
   (D-23). That board is not certified: it is the part an inspector is most likely
   to question.
3. Mains-side parts must carry recognised marks: rocker (CSA/cUL; ENEC for EU/UK),
   IRM-03-5 (cURus/CB/TÜV), terminal block, fuse, MOV.
4. The 5 V lead runs from inside the box to the plate: use wire insulated for at
   least the mains voltage (e.g. 300 V-rated), through the single collar hole.
5. Bond grounds per local code. The printed plate is non-conductive and is not grounded.
6. Box fill must be calculated with the insert, the rocker body and the wiring board
   (terminal block, PSU) counted.
7. The rocker breaks line and neutral of the lighting load; the line feed and ground
   stay connected on the board. Use the breaker for work on fixtures.

## Mechanical / material
8. Barrier geometry (pocket shell, switch well, collar; the box insert) is
   printed in a UL94 V-0 filament with its datasheet on file. PLA/PETG are for
   test fits only.
9. No holes may be added to the barrier other than the 5 V pass-through. The rocker
   panel cutout is closed by the rocker body itself: never energise with the rocker out.
   `make check` runs a barrier-continuity test (mains air must not reach the pocket,
   trim hollow or room); it must pass.

## Regulatory (BC, Canada)
10. Work under a homeowner electrical permit; ask the inspector about the concealed
    emergency switch and the uncertified assembly before installing more than one.
11. Expect questions from your insurer about non-approved equipment.
12. EU/UK: local rules differ (e.g. England Part P). Check before building there.

## For AI agents
- Don't claim compliance, safety, or code approval. Report what was checked.
- Don't relax constraints 2, 8, 9 or the PCB creepage targets to make something fit;
  stop and ask.
