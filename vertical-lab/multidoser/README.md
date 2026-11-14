# The multi-doser's own code, verbatim

`chain-carousel-v5/` holds byte-for-byte copies of
[`cad/chain-carousel-v5/`](https://github.com/vertical-cloud-lab/powder-doser/tree/353dae78829ef8fffaa1bd584876a157145a0b76/cad/chain-carousel-v5)
in powder-doser at `353dae7`: the head of [PR #185](https://github.com/vertical-cloud-lab/powder-doser/pull/185) on
2026-11-05, the multi-doser chain carousel v5 of #128 (the A&D HR-202i under the dose point,
[comment](https://github.com/vertical-cloud-lab/powder-doser/pull/185#issuecomment-6638969198)). `vendor/` holds the
vendor helpers v5's `parts.py` imports, from
[`cad/vendor/`](https://github.com/vertical-cloud-lab/powder-doser/tree/353dae78829ef8fffaa1bd584876a157145a0b76/cad/vendor)
at the same commit. Change them there, not here, and copy them again. [`../carousel.py`](../carousel.py) runs them for
the animation, and [`../notes/multidoser.md`](../notes/multidoser.md) says what v5 is and what we added to it.

The folder layout mirrors powder-doser's `cad/`, because the copies find their neighbours by relative path:
`parts.py` puts `../vendor` on `sys.path`, and `layout.py` reads Sam's STEPs from `../chain-carousel-v4/reference/`
(v5 adds none). Those three STEPs (Sam's Oct 13 mounting plate and electronics carriage, the lab's threaded auger, its
cap) are fetched from the same commit by `carousel.py` and SHA-256 checked on first use, and never committed; they are
the same files round 8 used for v2.

The vendors' own STEP files (McMaster screws and nuts, Actuonix's P16, StepperOnline's NEMA 34) are not
redistributable and live in powder-doser's git-ignored `cad/vendor/files/`. They are not fetched here: with no
`manifest_*.json` and no `files/`, `vendor/common.step_or_none` returns `None` and every builder draws its own
parametric stand-in, as powder-doser does on a checkout without them. `layout.shape()` would read v2's committed
per-part STEPs instead if `chain-carousel-v2/step/components/` were on disk; it isn't, so the stand-ins are used.

| File | SHA-256 |
|---|---|
| `chain-carousel-v5/kinematics.py` | `9edab8194bcc38ff8cea3c53f39e96d28a439133509b7f5bc7d0fc7ba3ec75b8` |
| `chain-carousel-v5/layout.py` | `28fc8b43d0b59174d270bba6950e079c94670036176c375f84b84196aef96dec` |
| `chain-carousel-v5/params.py` | `17cdcd8fc3e75e77174cb935d15ffcd25826427fa7996199fcfc9861627464a4` |
| `chain-carousel-v5/parts.py` | `9785573eadc970924766fe384505101fb21aaa411e3baa6c5023c19e5a5ea849` |
| `chain-carousel-v5/parts3.py` | `d57d3e00f1f425b61fcc94f9cf097b49a1db175a1c274205c0b8a814e3e2a46e` |
| `chain-carousel-v5/parts4.py` | `5780c152979e4901f7b5ab4dfb3f0329e8c220034d4fafbf80f0ab97536e52a2` |
| `chain-carousel-v5/parts5.py` | `e3a39e10637210c4c44d1e18aa2797aa6c4b2295b2071baaade482889e432318` |
| `vendor/actuonix.py` | `9c11ce7f512347dfac88e95a62d2adb04e5b622cf7f68e2854d6758cfec435ef` |
| `vendor/common.py` | `307249424f6294c631e68f25779a6c51c40d4db4162ddb2bdb050aee142f2591` |
| `vendor/mcmaster.py` | `078b0eed9fb8459ec43b8acc55efe8b73c6f51eaa70c29f51262076304a20faa` |
| `vendor/vendor_other.py` | `ba7422c64cc6e7f50717f193cb4498faf03e7990ad905253dded802ffafbc48f` |

| Fetched at run time (`chain-carousel-v4/reference/`) | SHA-256 |
|---|---|
| `sam-oct13-mounting-plate-and-carriage.step` | `dae4b71975c2fb5f2442df2ee457c811909d9ae343cb31b6850e905f8256b81a` |
| `auger-threaded-storage.step` | `3008ccbea47bae590934fcef5106a5a904a1ab069ed188480a760ff2e13ce6ff` |
| `auger-cap-threaded.step` | `2a2e8eda516330268003ad40faeb1b4339300c8f2d00e928ec4c8550259e6b82` |

Round 8's copies of v2 (powder-doser `1c135e0`: `params.py`, `parts.py`, `layout.py`, `kinematics.py` at this folder's
top level) were removed in round 9: nothing runs v2 any more. They are in this repo's history at `9a5dc71`.
