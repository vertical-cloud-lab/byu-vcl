"""Questions for edison_corrosion_cu.py: the CubXL corrosion plan in this
folder's parent, carried over to copper alloys for naval use made by
single-stream blown-powder DED (PR #278, asked 2026-10-18).

They follow on from the 53 Cu/DED queries of digital-alloy-lab PR #117
(edison-trajectories/cu-ded-2026-10/), which covered the alloys, powder
making, DED, film mechanisms, short-vs-long tests and corrosion metrology in
general. These ask what changes when the test is the CubXL's: a 3-4 mm
O-ring well of ~150 uL on a polished cross-section, a low-cost potentiostat,
and ICP of the used liquid. ALREADY_KNOWN lists what PR #117 settled, so the
answers build on it instead of repeating it."""

CONTEXT = """\
CONTEXT (do not summarize this back): Brigham Young University's Vertical
Cloud Lab (EXCLUDE publications by Sterling G. Baird) is planning automated
small-area corrosion tests on a Cartesian gantry robot with a pipetting head
and a potentiostat (the "CubXL"). The plan, written first for the lab's
aluminum alloys, is: polished metallographic cross-sections with a bare metal
back for electrical contact; a 3D-printed clamp holding 2-4 fluoroelastomer
(FKM) O-ring wells per piece (3-4 mm inner diameter, 0.07-0.13 cm2, about
150 uL of electrolyte each, open to air); a leak-free Ag/AgCl mini-reference
and a Pt-wire counter carried by the gantry head. The robot fills each well
from stock solutions, runs open-circuit potential (30 min), linear
polarization resistance (+/-10 mV), then a cyclic polarization reversed at a
current threshold; it photographs each spot before and after, and pipettes
the used electrolyte into a tube for offline ICP-OES/ICP-MS (element-resolved
dissolution). Candidate potentiostats are low-cost (IO Rodeo Rodeostat,
MYSTAT, PalmSens EmStat Pico). We now want to do the same for COPPER ALLOYS
FOR NAVAL USE (seawater piping, heat exchangers and condensers, propellers,
valves and fittings, and repair of cast nickel-aluminum bronze (NAB) and
wrought Cu-Ni), deposited by single-stream blown-powder laser directed energy
deposition (DED: one pre-alloyed powder feed, not in-situ blending), likely on
a 300-500 W infrared fiber-laser DED unit. Alloys: Cu-Ni 90-10 (C70600) and
70-30 (C71500) with Fe, Mn and Cr; NAB (C95800, C63000/C63020) and Mn-Al
bronze; reference coupons of wrought C71500 and cast C95800. Specimens:
deposits built on themselves; deposits on cast NAB and wrought Cu-Ni plates
(repair coupons with deposit, fusion zone, heat-affected zone and substrate);
single tracks and thin walls; and byproducts (splats, crucible skull) of
in-house ultrasonic atomization of the powders.
"""

ALREADY_KNOWN = """\
ALREADY ESTABLISHED (do not re-derive; build on it): Cu-Ni corrosion product
films take weeks to months to mature, so one-hour tests rank fresh surfaces;
Tafel fits on an oxygen-diffusion-limited cathodic branch and an assumed
Stern-Geary B are unreliable for these alloys; natural seawater can reverse
rankings obtained in 3.5% NaCl or ASTM D1141; DeCost et al. 2022 (JOM,
autonomous scanning droplet cell) optimized Al-Ni-Ti coatings only in
simulation on an existing dataset; MAP-E (Persaud et al. 2026, npj Mater.
Degrad.) automated O-ring flat-cell pitting tests on 304 stainless steel;
blown-powder laser DED of NAB and of Cu-30Ni has been published (Li et al.
2021; Bhattacharya et al. 2011).
"""

OUTPUT = """\
OUTPUT FORMAT: For each relevant item give the full citation with DOI; the
material and how it was made (wrought, cast, weld, laser clad or laser
surface melted, blown-powder DED, WAAM, LPBF); the composition in wt%; the
cell (bulk flat cell, droplet or capillary cell, O-ring area) and electrolyte
volume; the electrolyte and duration; and the key numbers (Ecorr against a
stated reference, Rp, icorr, breakdown or protection potentials, current
ranges, dissolution rates by element, depth of attack). Tag each item: [CITE]
worth citing; [NUMBERS] gives a quantitative benchmark; [NAVY] Navy/DoD-funded
or a Navy application; [CUBXL] changes how the small-cell robot test should be
built or run (say how); [NOVELTY-RISK] overlaps the planned work (say how);
[GAP] shows something not yet done. If the literature does not answer part
of the question, say so plainly instead of padding with loosely related work.
End with a ranked "Top 5 changes to the small-cell plan for copper alloys".
"""


def q(body: str) -> str:
    return (CONTEXT + "\n" + ALREADY_KNOWN + "\n" + body.strip() + "\n\n"
            + OUTPUT)


BATCHES = {}

# Batch 1: what the aluminum plan's cell, sequence, chemistry link, specimens
# and electrolyte become for copper alloys in naval service. Two
# LITERATURE_HIGH (small-cell artifacts; element-resolved dissolution, the
# chemistry link) and one PRECEDENT (has anyone automated this for copper).
BATCHES[1] = {
    "c1-01-small-cell-artifacts-cu": {
        "job": "LITERATURE_HIGH",
        "query": q("""
QUESTION: What goes wrong, physically and chemically, when Cu-Ni and NAB (or
copper and brasses, if nothing closer exists) are tested in a small-volume
cell (a 1-5 mm O-ring flat cell, droplet cell or capillary microcell holding
roughly 10-200 uL, open to air) instead of a conventional bulk cell (>100
mL)? Cover: (a) accumulation of dissolved copper (CuCl2-, Cu2+) in the small
volume and its redeposition on the specimen or on the Pt counter, and how it
shifts Ecorr, Rp and the cathodic current; (b) oxygen supply: the oxygen
reduction limiting current density in an unstirred well against a stirred
bulk cell, and whether a 30-60 min test depletes dissolved oxygen; (c)
evaporation and the resulting chloride rise over 1-2 h, and mitigations
(humidified lid, oil overlayer, gelled electrolyte); (d) pH change from the
counter electrode; (e) crevice attack under the gasket for copper alloys:
whether attack concentrates inside the crevice or just outside its mouth,
whether NAB shows selective phase attack under the O-ring, and which gasket
materials (FKM, PTFE, silicone) or cell designs minimize it; (f) published
measurements of how Ecorr, Rp or breakdown potentials of copper alloys change
with exposed area or electrolyte volume. Give the area and electrolyte
volume of each study, and say which artifacts are large enough to change the
ranking of alloys.
"""),
    },
    "c1-02-dc-sequence-for-cu": {
        "job": "LITERATURE",
        "query": q("""
QUESTION: The aluminum plan runs OCP (30 min), LPR (+/-10 mV at 0.167 mV/s),
then an ASTM G61-style cyclic polarization reversed at 1 mA/cm2 to obtain
pitting and repassivation potentials. Copper alloys in seawater mostly
corrode actively under a Cu2O-based film rather than pitting from a passive
state. Which sequences of DC measurements (and EIS, where used) have
characterized Cu-Ni and NAB in chloride or seawater within about 2 hours, and
what does each step return? Is cyclic polarization meaningful for these
alloys: are there published breakdown, pitting or protection potentials for
Cu-Ni (including in sulfide-polluted water) and for NAB selective phase
corrosion, and which reversal criteria were used? Should potentiostatic holds
be added at service-relevant potentials, such as the mixed potential of a
galvanic couple with steel or titanium, or the cathodic protection potentials
applied to NAB propellers (including potentials reported to suppress
selective phase corrosion), and what current densities do such holds draw?
Report measured ranges for wrought, cast and additively manufactured Cu-Ni
and NAB: Ecorr (vs SCE or Ag/AgCl), Rp (ohm cm2), icorr (uA/cm2),
oxygen-reduction limiting current density, anodic current density up to
+300 mV above Ecorr, and the potential window used, so that a potentiostat's
current ranges and compliance can be sized for 0.07-0.13 cm2 spots.
"""),
    },
    "c1-03-element-resolved-dissolution-cu": {
        "job": "LITERATURE_HIGH",
        "query": q("""
QUESTION: What has element-resolved dissolution analysis shown for Cu-Ni
(90-10, 70-30) and aluminum bronzes/NAB in chloride or seawater? Cover atomic
emission spectroelectrochemistry (AESEC; Ogle and co-workers), scanning flow
cell ICP-MS, and offline ICP-OES/ICP-MS or AAS of test solutions or immersion
water. Report dissolution rates by element (Cu, Ni, Fe, Mn, Al) in
ug/cm2/day or an equivalent unit; whether dissolution is congruent or
selective (for example Ni and Fe retained in the film, or dealuminification
of NAB's kappa/alpha phases); and whether the electrolyte's Al/Cu or Ni/Cu
ratio tracks selective phase corrosion depth. How well does dissolved metal
agree with the passed charge (faradaic balance), given that copper
redeposits and corrosion products stay on the surface? Practical points for
a 150 uL sample in 3.5% NaCl or substitute ocean water: dilution and sodium
matrix effects on ICP-OES vs ICP-MS, acidification, loss to polypropylene
tubes, detection limits. For naval relevance, include copper release rates of
Cu-Ni and NAB in seawater, their link to antifouling performance (any
release-rate threshold), how the release rate falls as the film matures,
regulatory or Navy limits on copper discharge from ships and seawater
systems, and any standard method for metal release rates (e.g. ASTM D6442,
ISO 15181 for antifouling coatings) that could be adapted to bare alloys.
"""),
    },
    "c1-04-zone-resolved-repair-electrochem": {
        "job": "LITERATURE",
        "query": q("""
QUESTION: How do the deposit, fusion boundary, heat-affected zone and
substrate of welded, laser-clad, friction-stir-processed or additively
repaired NAB and Cu-Ni differ electrochemically in chloride or seawater, as
measured by spatially resolved methods (microcapillary cell, scanning droplet
cell, SVET, SECM, SKPFM/Volta potential, local EIS) or by masked
macro-specimens? Report the potential and current differences between zones,
the microstructural features responsible (kappa phases, retained beta or
martensite, interdendritic Ni depletion, interlayer bands, dilution from the
substrate), and the size of each feature compared with a 3-4 mm measurement
spot and with a DED track (about 1 mm wide, 0.2-0.5 mm layers). Report
galvanic coupling between a deposit and its substrate (ZRA, mixed-potential
or area-ratio studies): galvanic current densities and which member is
anodic. Recommend how to place wells on a polished cross-section of a repair
coupon, and say whether a 3-4 mm well averages over features that matter.
"""),
    },
    "c1-05-specimen-prep-surface-state-cu": {
        "job": "LITERATURE",
        "query": q("""
QUESTION: How does surface preparation change the short-term electrochemistry
and early film formation of Cu-Ni and NAB in seawater, and how should a
robot-tested specimen of an additively manufactured copper alloy be prepared?
Cover the final polish (SiC grit vs 1 um diamond vs colloidal silica or
alumina), the deformed surface layer and smearing of kappa phases in NAB,
cleaning (ethanol, ultrasonic, water rinse), and the time and humidity
between polishing and immersion (air-formed Cu2O). Cover AM-specific issues:
as-deposited rough surfaces with adhered powder vs machined vs polished
faces; build-plane orientation (top vs side, XY vs XZ) in DED, WAAM or LPBF
copper alloys; and porosity: how pores intersecting a small spot act as
crevices, how pore fraction correlates with corrosion of printed copper
alloys, and how to detect or exclude pore-affected spots (imaging before the
test, X-ray CT). Include mounting effects (crevice at the resin interface,
conductive mounts). Give numbers where available, such as Ecorr or Rp shifts
with finish and density thresholds.
"""),
    },
    "c1-06-electrolyte-series-naval": {
        "job": "LITERATURE",
        "query": q("""
QUESTION: For an automated screen that mixes each test solution from stocks,
which electrolyte series would give each copper alloy a slope rather than a
single point (as a log[chloride] series does for aluminum pitting) while
staying relevant to naval seawater service? Candidates: chloride
concentration; sulfide additions (polluted harbor water, e.g. 0.01-10 mg/L),
including the order of sulfide and clean-seawater exposure; dissolved
oxygen; pH; ammonia; ferrous ion dosing (ferrous sulfate pre-filming of naval
condensers); temperature. For each, report how Cu-Ni (90-10, 70-30) and NAB
respond (Ecorr, icorr, film composition, localized attack) with numbers,
which variables have reversed the ranking of alloys, and how to make and keep
these solutions stable in small open wells (sulfide oxidation and loss as
H2S, precipitation in ASTM D1141, oxygen equilibration). Say which 2-3
variables give the most naval-relevant information per test.
"""),
    },
    "c1-07-mini-jet-flow-cell-cu": {
        "job": "LITERATURE",
        "query": q("""
QUESTION: Can erosion-corrosion of Cu-Ni and NAB be screened on millimetre
spots with a small pumped flow: a submerged micro-jet, wall-jet,
channel-flow or impinging-jet cell fed by a syringe or peristaltic pump?
Report small-scale flow cells used on copper alloys (nozzle diameter,
standoff, flow rate, wall shear stress, duration); the wall shear stresses or
velocities at which Cu-Ni and NAB films break down, and how they relate to
the critical pipe velocities of about 3-4 m/s for 90-10 and higher for 70-30;
how electrochemical signals (current transients, Rp, OCP) were recorded
during flow; and whether such tests ranked alloys the same way as pipe-loop,
jet-impingement rig or rotating-cylinder tests. Include welded or
additively manufactured copper alloys if any exist. If the literature allows,
estimate the flow rate needed to reach those shear stresses in a 3-4 mm cell.
"""),
    },
    "c1-08-precedent-automated-cu-corrosion": {
        "job": "PRECEDENT",
        "query": """\
Has anyone used an automated, robotic or gantry-based electrochemical
platform (scanning droplet cell, O-ring flat-cell array, or a multi-electrode
array with automated liquid handling) to test the corrosion of copper alloys
(Cu-Ni, nickel-aluminum bronze, aluminum bronze, brass), in particular
additively manufactured (blown-powder DED, wire-arc, laser powder bed fusion)
or weld-repaired copper alloys, or combined such tests with element-resolved
analysis (ICP or AESEC) of the test electrolyte? Give the closest examples
published up to October 2026 with DOIs, and for each say what it did and did
not do: alloy, manufacturing route, cell, electrolyte, number of specimens,
and any machine learning or closed-loop selection. Exclude publications by
Sterling G. Baird.
""",
    },
    "c1-09-rapid-solidification-proxies-cu": {
        "job": "LITERATURE",
        "query": q("""
QUESTION: Which cheap, rapidly solidified forms of a copper alloy predict the
corrosion of its blown-powder DED deposit? Cover laser surface melting (LSM)
of NAB and Cu-Ni, single laser tracks, splat-quenched or melt-spun ribbons,
arc-melted buttons, and atomized powder consolidated by other routes. For
each, report the cooling rate, the resulting phases (retained beta or
martensite, suppressed kappa, Ni and Fe in solution), and corrosion in
chloride against the cast or wrought alloy, with numbers. Has any study
compared LSM or single-track corrosion with a multi-layer deposit of the
same alloy, showing whether reheating by later layers changes it? Which proxy
would rank compositions the same way as multi-layer DED, and which would
mislead?
"""),
    },
    "c1-10-coulometric-oxide-reduction-cu": {
        "job": "LITERATURE",
        "query": q("""
QUESTION: Can coulometric (cathodic) reduction, such as sequential
electrochemical reduction analysis (SERA) or galvanostatic or linear-sweep
reduction in borate buffer or KCl, quantify oxides and corrosion products on
copper alloys with the same low-cost potentiostat? Cover (a) films formed on
Cu-Ni and NAB in seawater (Cu2O, CuO, Cu2(OH)3Cl, Ni- and Fe-rich layers):
reduction potentials, charge-to-thickness conversion, precision, and
agreement with XPS or other methods; (b) the native oxide on copper alloy
powders or polished surfaces, and whether reduction of a powder (for example
in a cavity microelectrode or a packed-powder electrode) has been used to
estimate the oxide thickness or oxygen content of metal powders, compared
with inert-gas-fusion oxygen analysis; (c) interference from Ni, Fe, Al and
Mn oxides that do not reduce in the same potential window. Report the
electrolyte, current density and detection limit (nm or mC/cm2).
"""),
    },
}
