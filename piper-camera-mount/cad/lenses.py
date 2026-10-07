"""The two official Raspberry Pi HQ Camera lenses: their specs, and solids to put on the camera.

Specs are Raspberry Pi's: the "HQ Camera C/CS lenses" table in the camera documentation
(https://www.raspberrypi.com/documentation/accessories/camera.html) and the two lens guides,
https://datasheets.raspberrypi.com/hq-camera/cs-mount-lens-guide.pdf and c-mount-lens-guide.pdf.
Masses are the retailers' figures (Raspberry Pi doesn't list them). The ring layout and the two
locking thumbscrews on each lens aren't in any drawing Raspberry Pi publishes: they are measured
off product photos and scaled to the official overall size, so treat them as estimates.

Positions along the lens are `s`, mm forward of the camera's CS seat (the face the lens's
shoulder screws down onto); negative s is inside the camera's mount.
"""
from __future__ import annotations

from dataclasses import dataclass

import cadquery as cq

THREAD_D = 25.4        # 1"-32 UN, C and CS mount alike


@dataclass(frozen=True)
class Lens:
    key: str
    name: str
    f: float                    # focal length, mm
    mount: str                  # "CS", or "C" (on the HQ Camera, through its 5 mm C-CS adapter)
    od: float                   # largest diameter, official
    length: float               # overall, thread included, official
    thread: float               # of that, inside the camera's mount (estimate)
    mass_g: float
    fov_hq_deg: tuple           # official, on the HQ Camera: across, up, diagonal
    f_numbers: tuple            # widest and narrowest aperture
    mod_m: float                # minimum object distance, official
    rated_mp: float
    image_format: str
    price_usd: float            # Raspberry Pi's list price
    profile: tuple              # (s0, s1, diameter) from the seat forward; the last ring's s1 is the front
    screws: tuple               # (s, what it locks): radial locking thumbscrews
    screw_tip_r: float          # how far a thumbscrew reaches from the axis (estimate, from photos)
    screw_d: float = 3.0        # its knurled head
    glass_d: float = 22.0       # the recess in front of the front element
    adapter: float = 0.0        # C-CS adapter, part of the profile; its length

    @property
    def front_s(self) -> float:
        return self.profile[-1][1]

    def d_at(self, s: float) -> float:
        return next(d for s0, s1, d in self.profile if s0 <= s <= s1)


LENSES = {
    # Front to back: a short front barrel and lip, the outer grip, the aperture ring (OPEN/CLOSE,
    # with its thumbscrew), the focus ring (NEAR/FAR, with its thumbscrew), then 4 mm of thread.
    # Focusing turns the outer two rings together (4-5 turns, by Raspberry Pi's guide), so the
    # aperture thumbscrew can end up pointing anywhere round the lens.
    "6mm": Lens(
        key="6mm", name="6 mm wide-angle (CS mount)", f=6.0, mount="CS", od=30.0, length=34.0, thread=4.0,
        mass_g=53.0, fov_hq_deg=(55.0, 45.0, 71.0), f_numbers=(1.2, 16.0), mod_m=0.2, rated_mp=3.0,
        image_format='1/2"', price_usd=25.0,
        profile=((0.0, 12.3, 29.0), (12.3, 21.9, 29.4), (21.9, 27.3, 30.0), (27.3, 28.8, 29.0),
                 (28.8, 30.0, 30.0)),
        screws=((4.0, "focus"), (17.4, "aperture")), screw_tip_r=20.0),
    # Only for comparison: the 5 mm C-CS adapter, then the lens (aperture ring nearest the camera,
    # focus ring, front), 4 mm of its C thread inside the adapter.
    "16mm": Lens(
        key="16mm", name="16 mm telephoto (C mount)", f=16.0, mount="C", od=39.0, length=50.0, thread=4.0,
        mass_g=133.7, fov_hq_deg=(22.2, 16.7, 27.8), f_numbers=(1.4, 16.0), mod_m=0.2, rated_mp=10.0,
        image_format='1"', price_usd=50.0,
        profile=((0.0, 5.0, 31.0), (5.0, 16.0, 36.0), (16.0, 36.0, 38.0), (36.0, 51.0, 39.0)),
        screws=((10.5, "aperture"), (26.0, "focus")), screw_tip_r=24.0, glass_d=30.0, adapter=5.0),
}


def _cyl(d: float, z0: float, z1: float) -> cq.Workplane:
    return cq.Workplane("XY").circle(d / 2).extrude(z1 - z0).translate((0, 0, z0))


def lens_body_local(lens: Lens, seat_z: float) -> cq.Workplane:
    """The lens without its thumbscrews, in the camera's own frame (optical axis -Z, PCB front
    face at z = 0), its shoulder on the CS seat at z = seat_z."""
    body = _cyl(THREAD_D, seat_z, seat_z + lens.thread)
    for s0, s1, d in lens.profile:
        body = body.union(_cyl(d, seat_z - s1, seat_z - s0))
    front = seat_z - lens.front_s
    return body.cut(_cyl(lens.glass_d, front - 1.0, front + 2.5))


def lens_screws_local(lens: Lens, seat_z: float, angles: tuple) -> cq.Workplane:
    """The locking thumbscrews, each pointing `angles[i]` degrees round the axis from local +X."""
    out = None
    for (s, _), a in zip(lens.screws, angles):
        r0 = lens.d_at(s) / 2 - 0.5
        sc = (cq.Workplane("YZ").circle(lens.screw_d / 2).extrude(lens.screw_tip_r - r0)
              .translate((r0, 0, seat_z - s)).rotate((0, 0, 0), (0, 0, 1), a))
        out = sc if out is None else out.union(sc)
    return out


def lens_keepout_local(lens: Lens, seat_z: float, c: float) -> cq.Workplane:
    """What the printed parts must stay out of, grown by c: the lens, plus the circle each
    thumbscrew can sweep (it can point anywhere), all the way back to the camera, since the pod
    goes onto its seat along the lens axis with the lens fitted."""
    k = _cyl(lens.od + 2 * c, seat_z - lens.front_s - c, seat_z)
    s_max = max(s for s, _ in lens.screws) + lens.screw_d / 2 + c
    return k.union(_cyl(2 * (lens.screw_tip_r + c), seat_z - s_max, 0.0))


def screw_sweep_local(lens: Lens, seat_z: float) -> cq.Workplane:
    """Every place a thumbscrew can be once the lens is screwed in: one band per screw."""
    out = None
    for s, _ in lens.screws:
        band = _cyl(2 * lens.screw_tip_r, seat_z - s - lens.screw_d / 2, seat_z - s + lens.screw_d / 2)
        out = band if out is None else out.union(band)
    return out
