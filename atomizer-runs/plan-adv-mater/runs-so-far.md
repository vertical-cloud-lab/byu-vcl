# Runs so far, and what each one gives the article

Status on 2026-10-10. None of these runs is part of the repeatability set. All three
since training ran into trouble at the plate: on Oct 2 the melt shot past it, on Oct 6
it landed on the upper sonotrode, and on Oct 8 it dripped onto a frozen lump on the
plate's tip. That is why landing-point checks come first in the plan
([README](README.md#runs-and-what-each-is-meant-to-show)).

| Run (bag ID) | Charge | Plate, booster, amplitude | Pour | O₂ | What happened | Role in the article |
| --- | --- | --- | --- | --- | --- | --- |
| [Oct 2](https://github.com/vertical-cloud-lab/byu-vcl/issues/249#issuecomment-5963148619) (u23y78) | Own-atomized 4047 powder in one as-made 6063 cup with a plug. About 18.6 wt% powder if the cup was full. Charge mass not recorded. | Pure Mo, 1.5:1, 90 | 830 °C, 0.17 bar, 2 min | Low 20s ppm after one wash at 500 °C | The meeting estimate was about 40 % atomized. The melt shot past the plate, which was too far from the nozzle, but the powder core melted. The AlSi10Mg core on Sep 30 had not. | **Pilot for Block B.** It shows the cup route works with a 4047 core. Use it as the EDS mixing test in [caliber#13](https://github.com/vertical-cloud-lab/caliber/pull/13#issuecomment-6032146879). It isn't a spread point: the charge was about 5× smaller and the pour was different. |
| [Oct 6](https://github.com/vertical-cloud-lab/byu-vcl/issues/261) (4yghtr) | 180 g of 6063 rod (logged as "6067") | Small CF, 1:1, 50 (not set on purpose) | 840 °C, 0.2 bar, 2 min | 19 ppm at the start, 121–140 after the pour | The stream landed on the upper sonotrode. Vibration was started late. [Gage's notes](https://github.com/vertical-cloud-lab/byu-vcl/issues/261#issuecomment-6025960787) | **Shakedown, excluded.** It gave a small jar of powder for SEM and a bag of splats. It's the reason for two gates: check the landing point, and start the vibration before the sealing rod. |
| [Oct 8](https://github.com/vertical-cloud-lab/byu-vcl/issues/261#issuecomment-6088484430) (kj0461) | 3 rods about 5 in long, not weighed | CF, 1.5:1, 92 then 100 (HMI "amplitude real") | Setpoint 850 °C, 0.19 bar | 3 washes at 500 °C: 60–70, then ~45, then 25–26 ppm | Slow, steady drips that hit a lump on the plate's tip or fell past it. Hardly any atomization, a puddle in the cup, fine powder on the cone. Bartosz says CF with the 1.5:1 booster doesn't atomize. Globs of metal at the nozzle exit afterwards. [Video record (PR #268)](https://github.com/vertical-cloud-lab/byu-vcl/blob/f74c654/atomizer-runs/2026-10-08/README.md) | **Shakedown, excluded.** It rules out CF at 1.5:1 (on Bartosz's word) and shows the slow drip the trainer recommends. It added the nozzle check to the gate. The fines are worth one SEM look. |

## Earlier, for context

From the [training SOP's run table](https://github.com/vertical-cloud-lab/byu-vcl/blob/88eeace/atomizer-training/sop.md#known-runs-so-far):

- **Sep 29**, three runs of AMAZEMET's 4047 rod. On CF with the amplifying 1:1.5 booster it made *"large, uniform, spherical powder"*. On Mo with the 1:1 the plate cracked. None of these bags has an ID.
- **Sep 30**, nzyjn0 / [8rthq2](https://github.com/vertical-cloud-lab/byu-vcl/issues/249#issuecomment-5939860479): AlSi10Mg powder in a 6063 cup, on Mo with the 1.5:1. The flow was too fast for the low amplitude, and the core didn't melt. #264 leaves AlSi10Mg cores until other powders have been tried.
- [jz31op](https://github.com/vertical-cloud-lab/byu-vcl/issues/249#issuecomment-5939830474): un-atomized metal from the training runs. **Keep it out of Blocks A and B.** Re-melted metal carries extra oxide and has lost some Mg, so it would add a variable to the baseline.

## What's missing from these records

The run-record template fills each of these gaps ([`run-record-template.yaml`](run-record-template.yaml)):

- **Charge mass:** Oct 2 and Oct 8 weren't weighed, and Oct 6 gives a total only.
- **Masses out:** no run weighed its powder, splats, puddle and crucible residue. The "about 40 %" for Oct 2 is an estimate, so no run yet has a yield.
- **O₂ when the sealing rod opened:** not recorded for Oct 2 or Oct 8.
- **Landing point:** none of the three runs checked it before heating.
- **Video of the pour from start to end:** no run has one. Oct 8's video starts mid-pour.
