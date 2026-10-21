# Sampling a layered powder jar: DEM animations

These animations go with the coring discussion on
[PR #284](https://github.com/vertical-cloud-lab/byu-vcl/pull/284), which is about Step 2 of the
draft [SEM powder prep SOP](../atomized-powder-sem-prep-sop.md): taking top, middle and bottom
samples from the collection jar. The question is about **composition, not particle size**. Figure
3b of the runs plan compares per-particle Si at the top, middle and bottom of the jar. That only
shows a drift during the pour if each sample really comes from its own layer.

Every particle is coloured by **when it was made**. Powder made first lies at the bottom, and powder
made last lies at the top. A sampling method is good if each sample keeps its own colour.

| Colour | Meaning |
| --- | --- |
| blue `#2a78d6` | made first: the bottom third of the run |
| yellow `#eda100` | the middle third |
| red `#e34948` | made last: the top third |
| violet `#6250d6` | sweepings brushed in from the plate, cone and bowl at the end (made at any time) |

## What was simulated

* **Model.** A soft-sphere discrete element method (DEM), written for this in [`dem.py`](dem.py)
  (numba). The normal force is a linear spring and dashpot (restitution 0.3). Tangential friction is a
  Cundall-Strack spring capped by Coulomb friction (particle-particle 0.5, particle-tool 0.3 to 0.5).
  There is rolling resistance (0.08) and a pull-off force of one particle weight for touching
  particles (Bond number 1, so the powder is slightly cohesive). Stiffness is 50 N/m and the time
  step is 25 µs. Tools are rigid bodies that follow set paths.
* **Particles.** 6,600 spheres 0.85 to 1.15 mm across, AlSi10Mg density. They are deliberately
  nearly all one size, so that size segregation doesn't drive the result.
* **Jar.** 24 mm inside diameter, 26 mm tall, filled through a 7 mm stream on the axis (the cone
  outlet) at 5,000 particles/s, with the last 10 % as sweepings from a wider (14 mm) stream. The bed is
  15.5 mm deep on the axis and 12.3 mm at the wall: the powder forms a cone, so the layers slope
  down toward the wall.
* **Methods** ([`scenarios.py`](scenarios.py)), each starting from the same filled jar:
  * **Open glass tube:** 7 mm bore and 0.7 mm wall, pushed to the floor at 30 mm/s, closed at the
    bottom (as if a thumb's suction held the core), lifted out. The core is then pushed out while the
    tube moves along a grounded tray, and the line is split into thirds. A thumb can't let the core
    out a third at a time, so pushing it out is the best case.
  * **Piston corer:** the same tube with a piston. The piston stops at the powder surface and stays
    there while the tube goes down around it. Air trapped between piston and core holds the core up:
    the pressure drop is modelled from how far the core sinks below the piston, P₀·gap/(gap + air in
    the core's pores). It's then laid out the same way.
  * **Three-port thief:** a 5 mm rod with a cone nose, pushed in closed. Three 2.6 mm ports open
    for 0.45 s, set at even heights between the nose and the surface. Whatever is in each port
    when it closes is the sample.
  * **Spoonula:** a 9 × 5 mm spoon with 0.9 mm lips. It digs in at 40°, 52° and 62° (steeper for the
    deeper layers, to stay inside the jar), levels off, and lifts out. Each scoop is aimed at the
    middle of one third of the depth on the axis, one after another in the same spot.
  * **Scrape off whole layers (idealised):** everything above a level that moves down at 12 mm/s is
    removed, pausing at the middle of each third (on the axis) to swab the top layer of particles
    within 3 mm of the axis.
  * **Pour along a line:** the jar tilts over its rim to 150° over 2.6 s while moving along a tray at
    20 mm/s, with the rim 10 mm above it. The line is then split into thirds, and also into nine bins.
* **Scoring** ([`summary.py`](summary.py)): each sample's share of particles from each third, and
  **drift kept** = (mean making time of the top sample − that of the bottom sample) ÷ (the same for
  the true top and bottom thirds). 100 % means a steady Si drift during the run would be measured in
  full, and 0 % means the samples are all the same mixture.

## Results

![summary](media/summary.png)

Animations: [`media/`](media/) has a GIF for each method, and [`all-methods.mp4`](media/all-methods.mp4) runs them
all in a row at full resolution (`render.py` also writes an MP4 per method; those aren't committed). The numbers are in [`results/`](results/) ([`summary.md`](results/summary.md) is the
table version of the chart).

| Method | Top sample from the top third | Middle | Bottom | Drift kept |
| --- | ---: | ---: | ---: | ---: |
| Scrape off whole layers, swab the centre (idealised) | 100 % | 100 % | 100 % | 115 %* |
| Piston corer, core sliced in the tube | 77 % | 68 % | 89 % | 87 % |
| Open tube, core sliced in the tube | 71 % | 64 % | 89 % | 86 % |
| Piston corer, core laid out on a tray | 67 % | 47 % | 70 % | 70 % |
| Open tube, core laid out on a tray | 56 % | 41 % | 57 % | 48 % |
| Pour along a line, split in thirds | 34 % | 32 % | 46 % | 23 % |
| Spoonula, one spoonful per depth in the same spot | 45 % (n = 11) | 7 % | 11 % | 1 % |
| Three-port thief | 0 % (n = 1) | 0 % (n = 12) | 0 % (n = 27) | −13 % |

\* Over 100 % because each swab is a thin slice from near the middle of its third, so the swabs are
further apart in time than the thirds' averages are.

What happened in each:

* **Tubes.** Pushed to the floor of this shallow bed (15 mm deep, about two bore diameters), the open
  tube's core came out 3 % short and the piston corer's not at all. Short cores are a problem in deep
  beds: Susana (2012, via Edison) measured 60 % recovery for a 15 mm tube pushed 150 mm into lactose.
  Inside the tube both cores were still layered. Most of the mixing happened when the core was pushed
  out onto a moving tray, where later powder rolled over earlier powder. Slicing the core into thirds
  while it is still in the tube kept 86-87 % of the drift, against 48-70 % for laying it out.
* **Thief.** The rod dragged powder down along its sides, so the bottom port filled with middle-third
  powder and the middle port with top-third powder. The ports took in 27, 12 and 1 particles. This is
  the failure the layered-bed experiments report for side-port thieves (Muzzio et al. 1997).
* **Spoonula, one spoonful per depth.** The first scoop, near the surface, held only 11 particles. Each
  deeper scoop went in through the layers above and lifted them out with it, and the hole filled from
  the sides in between. The middle scoop was 66 % top third and 28 % sweepings.
* **Scraping off whole layers** (idealised: the scraped powder just disappears, and the swab takes the
  top layer of particles within 3 mm of the axis). Every swab came entirely from its intended third.
  The swab has to be at the centre: the layers slope down toward the wall, so a horizontal surface
  near the wall is younger powder than at the centre.
* **Pour along a line.** The jar tilted at a steady rate, but the powder came out in a few avalanches
  within about a second, so the line piled up into a heap, and later powder buried earlier powder. The
  first ninth of the line was 53 % top third and 11 % sweepings. After that the mean making time fell
  slowly along the line, from 0.52 to 0.34 (the true range is 0 to 1), and rose again in the last ninth.
* **Sweepings.** In the filled jar, a swab of the untouched surface at the centre (the top layer of
  particles within 3 mm of the axis) would be 16 of 18 particles sweepings, not the end of the run.

## What it can and can't tell us

* **The particles are about 30 times too big.** Real powder is 15 to 63 µm. Simulating it at true
  size would take billions of particles. Mixing at a boundary spreads over a few particle diameters,
  so here a boundary smears over a few millimetres, where in real powder it would be a fraction of a
  millimetre. **Movements set by the tool's size are what carry over**: a core coming out short, drag
  past the rod, walls slumping into a hole, the order of a pour. How much one layer spreads into the
  next does not carry over.
* **The tube bore is 7 particles across**, against about 200 for a 6 mm tube in real powder, so
  wall effects and jamming are exaggerated.
* **No air**, apart from the piston corer's simple suction model. Fine powder in air settles
  slowly and doesn't bounce. Here particles fall freely, so the pour scatters more than it would.
* **Real 15 to 45 µm powder is more cohesive** (Bond number of order 10 to 100, against 1 here). It
  holds steeper walls, so a hole slumps less, and it pours in clumps rather than grain by grain.
* So read these as **a ranking of the methods, and a picture of what goes wrong**, not as
  percentages to expect at the SEM.

## Re-running

```
pip install numba numpy scipy matplotlib pillow imageio imageio-ffmpeg
python scenarios.py fill                                  # ~2 min on 4 cores
python scenarios.py open_tube    # also piston, thief, spoon, peel, pour (each 5-30 min)
python core_slices.py open_tube piston                    # score the tube cores as if sliced in the tube
python render.py fill open_tube piston thief spoon peel pour  # media/<name>.gif and .mp4
python render.py --combined                               # media/all-methods.mp4
python summary.py                                         # media/summary.png, results/summary.md
```

Raw trajectories go to `$DEM_OUT` (default `/tmp/dem-out`) and aren't committed.
