# Al–Ti phase diagram files — sources & attribution

- `ti-al-full-phase-diagram.png` — full Ti–Al binary phase diagram, reproduced from
  T.-C. Dzogbewu, "Additive manufacturing of TiAl-based alloys," *Manufacturing Review* 7 (2020) 35
  (open access, CC BY 4.0), as hosted by the [Aalto University Solid State Chemistry wiki](https://wiki.aalto.fi/spaces/SSC/pages/296557334/Ti-Al+phase+diagram) (CC BY-SA 4.0).
  Axes: atomic percent Al (bottom) / weight percent Al (top); Ti on the left, Al on the right.
- `al-ti-liquidus-annotated.png` — Al-rich liquidus redrawn for issue #161 by
  `al_ti_liquidus_plot.py` from anchor points after Schuster & Palm,
  *J. Phase Equilib. Diffus.* 27 (2006) 255–277 and Murray's Ti–Al assessment.
  Approximate: mid-range liquidus values carry ±20–30 °C of experimental scatter.
  Annotates the ~1500 °C atomizer ceiling and the planned ≤2 wt% Ti alloy range.

## Update, 2026-09-03 — the annotated liquidus is superseded

`al-ti-liquidus-annotated.png` was redrawn from approximate anchor points and reads **20–55 °C low**
between 0.2 and 3 wt% Ti (e.g. 825 °C vs. 868 °C at 1 wt% Ti). Use
[`al-ti-melt-window.md`](al-ti-melt-window.md) and `al-ti-melt-window.png` instead — that liquidus is
computed with pycalphad + COST507 and validated against in-situ LIBS liquidus measurements and the
Al₃Ti melting point. The full binary diagram (`ti-al-full-phase-diagram.png`) is unaffected.
