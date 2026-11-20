# The OT-2 as the CubXL's liquid station (`ot2_corrosion.py`)

Asked on PR #318 (2026-11-04): "What's the point of showing the OT-2 workflow? This doesn't seem to be tied to anything
alloy related." The clip gives the OT-2 on tray A the job digital-wetlab
[PR #83](https://github.com/vertical-cloud-lab/digital-wetlab/pull/83) names for it as direction 5, "solution and
sample prep for the lab's corrosion work (CubXL, ONR YIP)": it "can make the electrolyte matrix ... make the
matrix-matched ICP-OES dilutions" ([`grants/ot2-new-directions/README.md` §5 at
`aff0623`](https://github.com/vertical-cloud-lab/digital-wetlab/blob/aff0623/grants/ot2-new-directions/README.md)).
So the two machines on tray A read as one corrosion station: the OT-2 makes a stock the CubXL draws from, the CubXL runs
the night's wells, and the OT-2 turns the CubXL's tubes into ICP-MS samples.

`xvfb-run --server-num=82 python3 ot2_corrosion.py` writes [`out/mp4/instruments/ot2_corrosion_prep.mp4`](../out/mp4/instruments/ot2_corrosion_prep.mp4)
and `out/instruments/ot2_corrosion_prep.{gif,png,json}` (59 s, 13 steps). `PREVIEW=1` gives the end of each step.

## What it does, and the volumes

Every volume is one a real pipette moves, every liquid is drawn at the height its volume gives in its own vessel, and a
panel at the top right reads the volumes out as they change. The two pipettes are the ones in Opentrons' STEP: a
**P300 single** (30-300 µL, 300 µL tips) on the right mount and a **P20 single** (1-20 µL, 20 µL tips) on the left.

| Step | Pipette | Volumes | Source |
|---|---|---|---|
| Before a night: the CubXL's 0.1 mg/L S stock from its 10 mg/L stock, 1:100, sulfide last | P300, then P20 | 1980 µL of seawater (ASTM D1141, no heavy metals) from reservoir trough 2 into deep well H6, as 6 × 300 + 180 µL, from above the liquid; then 20 µL of the 10 mg/L stock below the surface: 2.0 mL at 0.1 mg/L S | DAL `protocol.md` §3: "make the 0.1 mg/L stock from the 10 mg/L one, not from solid", "ASW first and sulfide last" |
| After the night: the CubXL's nine tubes | | 0.5 mL PP tubes, 320 µL each: a well's 150 µL, a 150 µL DI rinse, 20 µL of 1 M trace-metal HNO₃; eight wells and the stock blank | DAL `protocol.md` §4 steps 11-12, and "9 tubes with the stock blank" |
| Diluent | P300 | 900 µL of 2 % HNO₃ into deep well H1 as 3 × 300 µL, dispensed from above, so the tip touches only acid | DAL `protocol.md` §6: "ICP-MS with a collision cell, after a 10× dilution in dilute HNO₃" |
| Sample | P300, fresh tip | 100 µL of tube 1 into H1: 1.0 mL at 10×; 220 µL stay in the tube for a re-run. Mixed 3 × 250 µL | as above |
| A matrix-matched standard | P20 | 10 µL of a 1 mg/L Cu, Ni, Fe, Mn, Al standard into 990 µL of blank matrix in H12: 10 µg/L | **our example**; DAL names no standards. PR #83 direction 5 asks for matrix-matched dilutions |

DAL = digital-alloy-lab [`alloy-corrosion/copper/protocol.md`](https://github.com/vertical-cloud-lab/digital-alloy-lab/blob/aeda51a/alloy-corrosion/copper/protocol.md)
at `aeda51a`, the head of DAL PR #180.

## The deck

Opentrons' slot positions (`ot2_standard.json`, as PR #320 places them): slot 1, 300 µL tips (A1, B1 and C1 used, in
Opentrons' pick order); slot 4, 20 µL tips (A1, B1); slot 2, a printed tube block on an SBS footprint holding the night's
tubes on DAL's 2 × 8 rack pitch (12 × 18 mm), cut through its front row so tube 1 shows, plus two open 1.5 mL tubes,
the 10 mg/L sulfide stock and the standard; slot 3, a NEST 2 mL 96 deep-well plate, cut through row H; slot 5, a NEST
12-well 15 mL reservoir (2 % HNO₃, seawater, blank matrix); slot 12, the fixed trash. The tube block, the reservoir's
contents and the standard are ours: DAL's deck is the CubXL's, not the OT-2's.

## Assumed, or open

- **The sulfide stock is made in the open.** DAL keeps both sulfide stocks deaerated, "with as little headspace as
  possible". An open deep well doesn't, and 2 mL in the CubXL's 20 mL deck vial is mostly headspace. A smaller deck
  vial, or a 20 mL batch (66 P300 transfers: a job for a P1000), would fix it. Who carries the 2 mL to the CubXL (a
  person, or the arm) isn't shown.
- **Acid and sulfide are kept to separate runs.** The sulfide stock fades out as the acid trough appears, after
  DAL's rule that the acid tip never touches a sulfide liquid (§9). On the real deck they would be two protocols.
- The 2 % HNO₃, the blank matrix's make-up and the 1 mg/L standard are our choices. The ICP-MS is the campus Agilent 8900
  DAL names; nothing here was run.
- The OT-2 is Opentrons' reference STEP, split into its moving pieces exactly as PR #320 (`instruments_round2.py` at
  `5a39245`) does it. That code is copied here because #320 isn't merged into this branch; once it is, this module
  should import it instead.
