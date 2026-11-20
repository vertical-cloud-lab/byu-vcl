# Safety assets: Class D extinguishers at every powder station and on every MiR250 (#303, PR #318)

Sterling, on PR #318 (2026-11-20): "create a new PR focused on assets for safety. Class D fire extinguishers at each
station, etc. Focused primarily on faithful reconstruction / asset creation. Noting that we might even want to have a
class D fire extinguisher mounted at all times to the MiR250 and available for use, in addition to having these next to
each station that deals with powder."

Work in progress; this file is filled in as the pieces land.

## Sources

- **The lab's own unit.** DAL issue #126: an Amerex **B570** (Grainger 8C249, $958.01, shipping weight 56.8 lb),
  bought 2026-01-28 and photographed in its box and beside BYU's CO2 unit. The box label reads "B570 30 LB SALT, BR VLV
  W/ WALL BKT, MARINE BRACKET NOT INCLUDED", P/N 16882.
- **Amerex's Class D datasheet** (`class-d-extinguishers.pdf`, amerex-fire.com): B570 P/N 16882, 30 lb Super D
  (sodium-chloride-based), 35 in H x 13 in W x 8 in D, 53 lb shipping, 195 psig, 3-6 ft range, 24 s, chrome-plated
  brass valve, "soft flow" extension applicator, large-loop stainless pull pin, Class D yellow finish, wall bracket
  included. "There is data showing that zirconium, uranium, titanium, and powdered aluminum fires can be controlled and
  extinguished with this unique extinguisher." C571 (P/N 27576) is the copper unit for lithium: 34 x 11 x 7 in.
- **Amerex's bracket reference** (`fire-extinguisher-bracket-reference.pdf`): the 811 heavy-duty box-type vehicle
  bracket (black; 811G galvanized red). Distributors (Fire Supply Depot, Dival Safety) list the 811 for 20-30 lb units
  with 7.75-8 in cylinders, B570 among them: 9.75 W x 8.125 D x 17.5 H in, 7/16 in holes.
- **Amerex's wheeled catalog** (`wheeled-extinguisher-catalog-english.pdf`, p. 11): the 680R (P/N 10897), 150 lb Super D
  on 36 x 2.5 in steel wheels with non-sparking rubber treads, argon-pressurized and regulated to 125 psi, 25 ft x
  0.75 in hose, extension wand, 52 H x 28 W x 45 D in, 444 lb shipping, 80 s, 4-8 ft.
- **The lab's vacuum SOP** (byu-vcl PR 80, `vacuum-operating-sop.md`, gate 0.2): "Class D extinguisher (Met-L-X /
  Lith-X / NaCl-based) staged at the station: <= 75 ft travel distance per OSHA 1910.157, ideally <= 25 ft. Never
  water, CO2, or ABC on this powder."
- **DAL's mounting study** (DAL branch `claude/issue-126-20261119-2136`, `lab-safety/class-d-extinguisher/`): the
  B570's hook, the NFPA 10 heights (gross weight over 40 lb: top at most 42 in, bottom at least 4 in), the flag-sign
  bracket.
- **NFPA 10 / OSHA 29 CFR 1910.157(d)(5):** Class D agent within 75 ft (23 m) of travel of the hazard.
- **MiR250 spec sheet:** payload 250 kg; "top-module mounting dimensions are equal to robot footprint ... contact MiR
  if a bigger top module is required."
