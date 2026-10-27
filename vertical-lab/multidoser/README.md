# The multi-doser's own code, verbatim

`params.py`, `parts.py`, `layout.py` and `kinematics.py` are byte-for-byte copies of
[`cad/chain-carousel-v2/`](https://github.com/vertical-cloud-lab/powder-doser/tree/1c135e040a4eec28ddbbf5d121f05b0f592e6e05/cad/chain-carousel-v2)
in powder-doser at `1c135e0`: the head of [PR #185](https://github.com/vertical-cloud-lab/powder-doser/pull/185),
the multi-doser chain carousel v2 of #128. Change them there, not here, and copy them again.
[`../carousel.py`](../carousel.py) runs them for the animation.

`reference/` holds the three STEP files that `layout.py` reads:
- Sam's Oct 13 mounting plate and electronics carriage
- the lab's threaded auger
- its cap

They are fetched from the same commit and SHA-256 checked on first use, and never committed.

| File | SHA-256 |
|---|---|
| `kinematics.py` | `9edab8194bcc38ff8cea3c53f39e96d28a439133509b7f5bc7d0fc7ba3ec75b8` |
| `layout.py` | `45256fd0d755951c12720a526085ec71bbcc755575e02e066644d0a7082332bf` |
| `params.py` | `6e61caf1a86ede1fa44e8be7876395ba85724a9b8c253d70b196fec3e5fe8244` |
| `parts.py` | `8fc22e86a0c7f610c7aca495a015aa2e0c3abf0097efc0df861dfb9f69f090cf` |
