# Feature tree — `dummy pipette` Part Studio

Generated from [`onshape/features.json`](onshape/features.json) with
`python fetch_onshape.py --no-fetch --report`. Regenerate after any refetch
rather than editing by hand.

Coordinates and extents are in millimetres. Sketch "extent" is the bounding box
of that sketch's non-construction geometry *in its own sketch plane*, so it is a
size cue, not a global position.

```
  0  Sketch 1     sketch    13 entities; extent x -22.33..22.33 mm, y -0.04..32.40 mm
  1  Extrude 1    extrude   operationType=NEW, endBound=BLIND, depth=234 mm
  2  Sketch 2     sketch    2 entities; extent x -5.50..5.50 mm, y 10.70..21.70 mm
  3  Extrude 2    extrude   operationType=NEW, endBound=BLIND, depth=75 mm
  4  Sketch 3     sketch    1 entities; extent x -5.14..5.14 mm, y 11.06..21.34 mm
  5  Extrude 3    extrude   operationType=ADD, endBound=BLIND, depth=4 mm
  6  Draft 1      draft     angle=11 deg
  7  Fillet 1     fillet    radius=5 mm
  8  Sketch 4     sketch    1 entities; extent x -3.65..3.65 mm, y 12.55..19.85 mm
  9  Extrude 4    extrude   operationType=ADD, endBound=BLIND, depth=3 mm
 10  Sketch 6     sketch    1 entities; extent (no placed geometry)
 11  Sketch 5     sketch    9 entities; extent x 16.20..19.06 mm, y 316.00..328.27 mm
 12  Revolve 1    revolve   operationType=ADD, fullRevolve=True, angle=30 deg
 13  Sketch 9     sketch    9 entities; extent x -18.50..18.50 mm, y 122.00..215.00 mm
 14  #featureName hole      style=SIMPLE, holeDiameterV3=3 mm, holeDepthV3=12 mm, endStyleV2=BLIND, locationSignatures=(16.5, 0.0, 124.0); (9.0, 0.0, 124.0); (-9.0, 0.0, 124.0); (-16.5, 0.0, 124.0); (9.5, 0.0, 213.0); (-9.5, 0.0, 213.0)
 15  Sketch 7     sketch    5 entities; extent x -27.06..27.06 mm, y 43.00..87.00 mm
 16  Extrude 5    extrude   operationType=REMOVE, endBound=BLIND, depth=5 mm, oppositeDirection=True
 17  Sketch 8     sketch    5 entities; extent x -7.99..7.99 mm, y 52.00..87.00 mm
 18  Extrude 6    extrude   operationType=ADD, endBound=BLIND, depth=3 mm
 19  Fillet 2     fillet    radius=2 mm
 20  Chamfer 1    chamfer   chamferType=OFFSET_ANGLE, width=0.5 mm, angle=45 deg
 21  Sketch 10    sketch    1 entities; extent x -5.95..5.95 mm, y 10.25..22.15 mm
 22  Extrude 7    extrude   operationType=REMOVE, endBound=BLIND, depth=10 mm, oppositeDirection=True
 23  Sketch 11    sketch    5 entities; extent x 7.75..16.20 mm, y 224.00..307.96 mm
 24  Revolve 2    revolve   operationType=REMOVE, fullRevolve=True, angle=30 deg
 25  Sketch 12    sketch    1 entities; extent x -5.88..5.88 mm, y -22.08..-10.31 mm
 26  Extrude 8    extrude   operationType=ADD, endBound=BLIND, depth=9 mm
 27  Sketch 13    sketch    3 entities; extent x 22.08..23.30 mm, y 226.98..229.00 mm
 28  Revolve 3    revolve   operationType=ADD, fullRevolve=True, angle=30 deg
 29  Sketch 14    sketch    7 entities; extent x 12.70..16.20 mm, y 205.67..235.00 mm
 30  Revolve 4    revolve   operationType=REMOVE, fullRevolve=True, angle=30 deg
 31  Sketch 15    sketch    8 entities; extent x 13.20..19.20 mm, y 225.00..235.00 mm
 32  Extrude 9    extrude   operationType=REMOVE, endBound=THROUGH_ALL, depth=25 mm, symmetric=True
 33  Sketch 16    sketch    8 entities; extent x -5.88..333.32 mm, y -22.08..-10.31 mm
 34  Extrude 10   extrude   operationType=REMOVE, endBound=BLIND, depth=10 mm, oppositeDirection=True
 35  Sketch 17    sketch    4 entities; extent x 0.00..32.40 mm, y 0.00..60.00 mm
 36  Extrude 11   extrude   operationType=REMOVE, endBound=THROUGH_ALL, depth=25 mm, oppositeDirection=True, symmetric=True
 37  Sketch 18    sketch    12 entities; extent x -8.90..8.90 mm, y 9.14..23.52 mm
 38  Extrude 12   extrude   operationType=REMOVE, endBound=THROUGH_ALL, depth=25 mm, oppositeDirection=True
 39  Fillet 3     fillet    radius=3 mm
```
