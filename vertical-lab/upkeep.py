"""Upkeep (#303, round 10): what every station needs over the years, and the lab's year with it booked.

    python3 upkeep.py              # the model -> out/upkeep_model.json, out/upkeep_year.png, out/upkeep_week.png
    python3 upkeep.py model        # the JSON only
    python3 timelapse.py model     # the finale's own model, which now books all of this too

Sterling, on PR #318 (2026-11-07): "Something that's been on my mind is maintenance over long-term and how that gets
handled in workflows." The finale's schedule (timelapse.simulate) had no maintenance beyond Friday afternoons and two
failure rates. This module is the task table as data (TASKS, FAILS: the interval, who does it, the downtime, the
spares, a source or "assumed"), and the hooks that book it into that same schedule:

* **calendar PM** (every so many days, at a time of day or in the Friday-afternoon window);
* **usage-driven consumables** (every so many hours of a machine's work, or so many of its steps);
* **robot-run reference checks** (booked like a step: a unit carries the reference to the station, the tray comes to
  the opening, the result goes on a control chart);
* **random failures** (seeded; per operating hour for a machine, per calendar hour for the Shuttles, the units and
  the services), each repaired by a person on the next shift, or by a vendor after a wait for parts.

A person's task is booked into the one day-shift person's free time, around the atomizer's crucible hours (which
keep priority: the atomizer is the bottleneck). Which person, where, is ``who``:

    arm        the arm, inside the workflow                 (no people's time)
    opening    a person at the opening                      (the tray presented, the MiR driven off: the Shuttle can
                                                             present no other tray meanwhile)
    extracted  a person with the tray pulled out on Kardex's full tray extraction (notes/maintenance.md)
    floor      a person at a machine on the floor (or at a unit on its charger)
    vendor     a vendor's service visit (the person hosts it for an hour)
    auto       the machine itself (a purifier regeneration, a UPS self-test)

Everything here is a model. Every interval with no maker's figure or standard behind it says "assumed".
"""
from __future__ import annotations

import bisect
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

import timelapse as TL

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
NAME = "upkeep"
SEED = 303

WHO = {
    "arm": "the arm, inside the workflow",
    "opening": "a person at the opening",
    "extracted": "a person, the tray pulled out",
    "floor": "a person at a floor machine or unit",
    "vendor": "a vendor's visit",
    "auto": "the machine itself",
    "desk": "a person at a desk or PC (software, data, paperwork)",
}
KINDS = {
    "crucible": "the atomizer's crucible, every run",
    "pm": "preventive maintenance",
    "consumables": "consumables and restocking",
    "repair": "repairs",
    "vendor": "hosting vendor visits",
    "review": "control charts and planning",
    "it": "software, IT and data",
    "compliance": "safety and compliance",
}
PEOPLE = {"opening", "extracted", "floor", "desk"}

# The route's stations and the trays they ride on (timelapse.STEPS); the floor machines have none.
TRAY_OF = {st: tr for _, st, _, _, tr, _, _ in TL.STEPS if tr}
ROUTE = list(TL.STATION_NAMES)
TRAYS = "ABCDEFGHIJKLMNO"
SPARES_TRAY = "a spares tray (proposed: Shuttle 1's free 390 mm at the top of the rear column takes a 350 mm tray "\
              "without a UPS or cameras; notes/tray_plan.md)"

PARAMS = {
    "seed": dict(value=SEED, source="the failures' random draws; any seed gives a year like this one"),
    "staff": dict(value=1, unit="people on the weekday day shift (08:00-16:00)",
                  source="round 8's one person for the crucible (timelapse PARAMS shift); maintenance fills their time "
                         "between the crucible hours"),
    "crucible_first": dict(value=True, source="assumed policy: the atomizer is the bottleneck, so a person's "
                                              "maintenance never takes a crucible hour (a run slot's first hour)"),
    "after_hours": dict(value="a fault that needs a person waits for the next shift (no one on call)",
                        source="assumed policy: the lab runs lights out; notes/upkeep.md shows what an on-call "
                               "person or a remote reset would buy"),
    "vendor_start_h": dict(value=8.0, unit="h of day", source="assumed: a vendor arrives at 08:00 on a weekday"),
    "vendor_host_h": dict(value=1.0, unit="h a visit", source="assumed: a person lets the vendor in, shows the "
                                                              "machine, signs off"),
    "presentations_per_step": dict(value=2, source="timelapse: a tray step presents its tray to load it and again "
                                                   "to unload it"),
    "mates_per_presentation": dict(value=2, source="the tray's plate leaves its slot's dock, mates the bay's, leaves "
                                                   "it and mates its slot's again (services.py hookups)"),
    "transit_s": dict(value=6.0, unit="s on the UPS per transit",
                      source="notes/services.md: about 6 s from R2 to the opening"),
    "grips_per_step": dict(value=4, source="assumed: a step's load and unload, each a pick and a place, as in "
                                           "chapters 1-7"),
}


def T(key, asset, what, every, who, down, *, person=None, kind="pm", spares="", source="assumed", at=None,
      route=True, unit=None):
    """One upkeep task. every: ("days", n) calendar; ("h", n) hours of the asset's work; ("n", n[, step]) its steps
    (or one step's); ("mates", n) the tray coupling's mating cycles; ("years", n) beyond the first year (not booked,
    only counted). down: hours the asset is out of use. person: people's hours (default: down for a person's task,
    0 for the arm and the machine, PARAMS vendor_host_h for a vendor)."""
    if person is None:
        person = down if who in PEOPLE else (PARAMS["vendor_host_h"]["value"] if who == "vendor" else 0.0)
    if at is None:
        at = {"arm": "night", "auto": "night", "vendor": "vendor"}.get(who, "day")
    if who == "vendor" and kind == "pm":
        kind = "vendor"
    return dict(key=key, asset=asset, what=what, every=every, who=who, down=down, person=person, kind=kind,
                spares=spares, source=source, at=at, route=route, unit=unit)


# ================================================================================================ the task table
# asset: a route station (timelapse STEPS), "vlm1"/"vlm2" (a Shuttle: its opening), "unit" (each MiR250 + UR10e),
# "tray:X" (a tray's own parts: coupling, UPS, cameras; "tray:*" each of the fifteen), or a service ("n2", "chiller",
# "fumehood", "glovebox", "depowder", "storage", ...). Sources: makers' manuals, datasheets and standards, as cited;
# "assumed" otherwise. notes/upkeep.md has the same table with the links.
# Sources, cited by key in each task's source (notes/upkeep.md has them as links):
SRC = {
    "kardex": "Kardex Remstar knowledge base, 'How often should preventive maintenance be performed': 'every 6 months, "
              "or twice a year for standard machines'; quarterly if heavily used",
    "combitac": "Stäubli CombiTac overview CT-Overview-11014010: power, data and fluid inserts 'Mating cycles 100,000'; "
                "CT-align docking frame 100,000 (search snippet)",
    "eaton": "Eaton 5PX manual 614-07977-00: automatic battery test 'Every week' by default; 3-5 years float life at "
             "25 °C (Eaton, search snippet); 9PX Li-ion (LFP) 8-10 years (eps-dc)",
    "picam": "ac-training-lab picam docs: systemd Restart=always, RestartSec=10; cron reboot at 05, 13 and 21 h",
    "mir": "MiR250 user guide, periodic tasks (mirsupport): weekly scanners and lights, monthly wheels and charging "
           "pads, quarterly stop tests, half-yearly battery connector and braking test, yearly casters and drive "
           "wheels replaced",
    "ur": "Universal Robots inspection and maintenance plan: safety functions 'tested monthly'; control box air "
          "filters; service check 'at least bi-annually'",
    "robotiq": "Robotiq 2F-85 manual pp. 88-91: cleaning weekly, inspection monthly, fingertips '1 Million cycles or "
               "when wear is visible', overhaul at 2 million cycles",
    "realsense": "RealSense on-chip calibration white paper: 'may indeed never be required'; recalibrate when "
                 "|health| > 0.25",
    "parker": "Parker UHPN2 '12 Month's Service - Filter Kit' MKUHPN2-FK; catalyst module about 3 years (search "
              "snippets; parker.com refused the runner)",
    "thermoflex": "ThermoFlex manual: PM timer 3,000 h for a laboratory (condenser filter, fluid bag; changed while "
                  "running); 'changing the fluid every six months'",
    "purelab": "Inert PureLab manual (NIST copy): gloves and O-rings by inspection, box filters yearly, catalyst every "
               "3 years; EPFL glovebox guidelines: regeneration every 3-6 months, sensors every 1-2 years; Cornell: "
               "pump oil twice a year, a regeneration up to 12 h",
    "hood": "OSHA 1910.1450 App. A: hoods 'routinely tested'; annual face-velocity checks are general practice",
    "retsch": "Retsch sieve info sheet: below 500 um only an ultrasonic bath, no brushing, dry at 80 °C max; Gilson "
              "on ASTM E2427: check each sieve periodically with a reference material",
    "eos_filter": "Yasin et al. 2024 (NSF PAR 10600321): an EOS M290 circulation filter's life is 2,500 build hours; "
                  "GE US12172115B2: wet the condensate with water before the housing is opened (Al and Ti give off "
                  "gas when wetted)",
    "edm": "generic wire-EDM practice: FANUC America 'weekly cleaning taking less than an hour'; MMS 'power contacts "
           "indexed every 50 to 100 hours of cutting'; Langenhorst (MoldMaking) 300 h conductivity sensor and "
           "auto-threader, 500 h lower arm, 1,000 h tank; FANUC EU PM 'every 2,000 operating hours or 1x per year'; "
           "a 15.9 kg spool is '60 hours of wire'",
    "edm_al": "MMS: 'cutting aluminum raises the conductivity of the dielectric fluid quickly', so the resin goes "
              "sooner",
    "e4": "ZwickRoell on ISO 7500-1 / ASTM E4: 'an interval of no more than 12 months'; ISO 9513 extensometers about "
          "12 months, at most 18 (snippet); Instron 6800 manual p. 101: 'an annual service check'",
    "ams2750": "AMS2750 (Heat Treat Today, Thermal Processing): SAT quarterly, TUS quarterly for a Class 5 furnace; "
               "test thermocouples type K 5 uses or 3 months",
    "leco": "LECO PX series: automatic bowl wash, gear drive with no belt; MX series: 6-7 min for a 1.5 in mount; "
            "about 20 g of phenolic a mount (UMich SOP, snippet)",
    "rigaku": "Rigaku MiniFlex Office Hour 4: check 'monthly or bi-weekly using a standard like NIST SP 640'; FBI "
              "IOSS-773-03 daily; chiller water every 3-6 months",
    "hitachi": "Hitachi TM3000/TM3030 manuals (the TM4000's own not found): 30 min cool-down for a filament change, "
               "anode cleaned every 5-6 filaments, TMP 3-5 years; a tungsten filament about 100 h (Thermo Fisher)",
    "malvern": "Malvern QAS3002 sheet: Dv50 within 2.5 %; a clean cycle and background check after every "
               "measurement (UWM SOP)",
    "keysight": "Keysight G200 note 5991-1453EN: area function and frame stiffness on fused silica in about 15 min",
    "plastometrex": "PLX-Benchtop procedure (MaintainX): profilometer calibration at start-up and every 3 h",
    "mitutoyo": "Mitutoyo 63ETB591: the reference-block check 'immediately before the daily start of the test "
                "schedule'; indirect verification 12 months, at most 18 (ASTM E92, via Metkon)",
    "and": "A&D HR-i manual: no internal mass, 'Calibration using a weight that you have'; USP <41>: 10 weighings, "
           "2s/m at most 0.10 %",
    "gamry": "Gamry: a reference electrode within 5 mV of a master; calibrate the potentiostat 'at least once per "
             "year'",
    "iso8655": "Sartorius on ISO 8655: a gravimetric check at least yearly, every 3-6 months by risk",
}

TASKS = [
    # ---- the Shuttles (each)
    T("vlm_service", "vlm*", "Kardex service visit: drives, belts, extractor, light curtain, safety checks", ("days", 182),
      "vendor", 8.0, spares="as the technician finds", source=SRC["kardex"] + "; the 8 h visit is assumed"),
    T("vlm_clean", "vlm*", "the opening's light curtain and sensors cleaned; shutter and tray stops checked",
      ("days", 28), "opening", 0.5, source="assumed"),
    T("bay_dock", "vlm*", "the bay's CombiTac dock: contacts wiped, pins, O-rings and coupling faces checked (it "
      "mates with every tray the Shuttle presents)", ("days", 91), "opening", 0.5, spares="O-rings, contact cleaner",
      source="assumed: quarterly; " + SRC["combitac"]),
    # ---- each tray's coupling, UPS and cameras (each of the fifteen trays)
    T("dock_inspect", "tray:*", "CombiTac plate and bay dock: contacts wiped, pins, O-rings and coupling faces checked",
      ("mates", 10000), "opening", 0.5, spares="O-rings, contact cleaner",
      source="assumed: every 10,000 mating cycles, a tenth of the rating (" + SRC["combitac"] + ")"),
    T("ups_test", "tray:*", "UPS battery self-test (the load stays on)", ("days", 7), "auto", 0.0, source=SRC["eaton"]),
    T("cams_wipe", "tray:*", "stream cameras' lenses wiped, focus and aim checked", ("days", 91), "opening", 0.25,
      source="assumed; the cameras restart themselves (" + SRC["picam"] + ")"),
    # ---- the units (each MiR250 + UR10e + 2F-85 + D405)
    T("mir_weekly", "unit", "MiR250 scanners and lights cleaned and checked; 2F-85 wiped", ("days", 7), "floor", 0.25,
      source=SRC["mir"] + "; " + SRC["robotiq"]),
    T("mir_monthly", "unit", "MiR250 casters and drive wheels cleaned, bolts checked, charging pads cleaned; 2F-85 "
      "inspected", ("days", 28), "floor", 0.5, source=SRC["mir"] + "; " + SRC["robotiq"]),
    T("ur_monthly", "unit", "UR10e safety functions tested (stops, freedrive, brake release); MiR stops quarterly",
      ("days", 28), "floor", 0.25, source=SRC["ur"] + "; " + SRC["mir"]),
    T("unit_halfyear", "unit", "MiR battery connector, braking distance, wheel diameters; UR10e bolts, cables, flat "
      "rings, control box filter", ("days", 182), "floor", 1.5, spares="controller filter kit",
      source=SRC["mir"] + "; " + SRC["ur"]),
    T("mir_wheels", "unit", "MiR250 casters and drive wheels replaced, IMU calibrated", ("days", 365), "floor", 2.0,
      kind="consumables", spares="4 casters, 2 drive wheels", source=SRC["mir"]),
    T("unit_service", "unit", "UR and MiR service visit", ("days", 365), "vendor", 8.0,
      source=SRC["ur"] + "; the visit's length is assumed"),
    T("gripper_tips", "unit", "2F-85 fingertips replaced", ("n", 1_000_000), "floor", 0.5, kind="consumables",
      spares="2F-85 fingertips", source=SRC["robotiq"]),
    T("d405_cal", "unit", "D405 on-chip health check on a flat target, recalibrated if over 0.25", ("days", 28),
      "arm", 0.1, source=SRC["realsense"] + "; monthly is assumed"),
    # ---- services
    T("n2_filters", "n2", "N2 generator: 12-month filter kit", ("days", 365), "floor", 0.5, kind="consumables",
      spares="MKUHPN2-FK filter kit", source=SRC["parker"]),
    T("chiller_filter", "chiller", "chiller: condenser filter and fluid bag (changed while it runs)", ("days", 125),
      "floor", 0.25, kind="consumables", spares="fluid filter bag, condenser filter",
      source=SRC["thermoflex"] + "; 3,000 h of a 24 h day is 125 days"),
    T("chiller_fluid", "chiller", "chiller: fluid changed (the XRD's tube stops)", ("days", 182), "floor", 1.0,
      kind="consumables", spares="distilled water or glycol mix", source=SRC["thermoflex"]),
    T("hood_cert", "fumehood", "fume hood: face-velocity certification", ("days", 365), "vendor", 2.0,
      source=SRC["hood"]),
    T("gb_regen", "glovebox", "glovebox purifier regenerated (forming gas, up to 12 h)", ("days", 120), "auto", 12.0,
      person=0.5, spares="5 % H2 forming gas: one 50 L cylinder for 5-6 regenerations", source=SRC["purelab"]),
    T("gb_weekly", "glovebox", "gloveboxes (floor and tray K): gloves and antechamber O-rings inspected", ("days", 7),
      "floor", 0.25, source=SRC["purelab"]),
    T("gb_halfyear", "glovebox", "gloves replaced; vacuum pump oil changed; box filters", ("days", 182), "floor", 1.5,
      kind="consumables", spares="butyl gloves, O-rings, pump oil, 0.3 um filters", source=SRC["purelab"]),
    # ---- the atomizer: AMAZEMET publishes none of this ("low maintenance costs"); the crucible is in every run
    T("rp_clean", "repowder", "rePowder: chamber, cyclone and powder catch cleaned; seals checked", ("days", 7),
      "floor", 1.5, at="fri", source="assumed (Friday afternoon, when no run starts)"),
    T("rp_crucible_stock", "repowder", "new graphite crucible and nozzle holder into the rotation",
      ("n", 15, "atomize"), "floor", 0.5, kind="consumables", spares="graphite crucible, nozzle holder",
      source="assumed: 15 runs a crucible"),
    T("rp_thermocouple", "repowder", "Type N thermocouple and its sheath replaced", ("n", 40, "atomize"), "floor", 0.5,
      kind="consumables", spares="Type N thermocouple, ceramic sheath",
      source="assumed; its sheath 'cracks normally' (notes/crucible_automation.md)"),
    T("rp_insulation", "repowder", "insulation set (bottom, side tube, top cone) replaced", ("n", 60, "atomize"),
      "floor", 1.0, kind="consumables", spares="alumina-silica insulation set", source="assumed"),
    T("rp_pump_oil", "repowder", "vacuum pump oil changed", ("days", 91), "floor", 0.5, kind="consumables",
      spares="pump oil", source="assumed"),
    T("rp_service", "repowder", "AMAZEMET service visit", ("days", 365), "vendor", 8.0, source="assumed"),
    # ---- the sieving cell (the ultrasonic clean after every use is in the sieve step)
    T("sv_ipa", "sieve_cell", "sieving cell: the ultrasonic bath's IPA changed, the wash module's filter", ("days", 7),
      "floor", 0.5, kind="consumables", spares="IPA", source="assumed"),
    T("sv_check", "sieve_cell", "the arm images each sieve's cloth against a backlight; open area trended",
      ("n", 20, "sieve"), "arm", 0.25, source="assumed (" + SRC["retsch"] + ")"),
    T("sv_verify", "sieve_cell", "reference material sieved (ASTM E2427); each sieve's result trended", ("days", 28),
      "arm", 0.75, spares="certified glass beads", source=SRC["retsch"] + "; monthly is assumed"),
    T("sv_replace", "sieve_cell", "the finest sieves (45 and 63 um) replaced when the check drifts",
      ("n", 300, "sieve"), "floor", 0.5, kind="consumables", spares="200 mm test sieves, 45 and 63 um",
      source="assumed: every 300 runs"),
    T("sv_shaker", "sieve_cell", "the shaker's amplitude calibrated", ("days", 365), "vendor", 1.0,
      source="Retsch: the AS 200 control is calibratable; yearly from one customer's review"),
    # ---- the Aconity MIDI and the depowdering box
    T("ac_filter", "aconity", "MIDI: circulation filter changed; the old one wetted (passivated) first", ("h", 1000),
      "floor", 3.0, kind="consumables", spares="filter cartridge, water for passivation",
      source="assumed: 1,000 build hours, against EOS's 2,500 for an M290, since Al condensate is heavier ("
             + SRC["eos_filter"] + ")"),
    T("ac_weekly", "aconity", "MIDI: chamber cleaned, laser window wiped, recoater blade checked", ("days", 7), "floor",
      1.0, source="assumed"),
    T("ac_blade", "aconity", "recoater blade replaced", ("n", 40, "print"), "floor", 0.5, kind="consumables",
      spares="recoater blades", source="assumed"),
    T("ac_laser", "aconity", "laser power and focus measured", ("days", 91), "floor", 1.5, source="assumed"),
    T("ac_service", "aconity", "Aconity service visit", ("days", 365), "vendor", 8.0,
      source="assumed; an EOS M290 tender quotes 8 h of labour a visit (snippet)"),
    T("dp_filter", "depowder", "depowdering box: filter changed", ("days", 28), "floor", 0.5, kind="consumables",
      spares="filter", source="assumed"),
    # ---- the wire EDM: hours of its work (about half of it cutting, assumed)
    T("edm_wire", "wire_edm", "wire spool changed; the scrap wire bin emptied", ("h", 120), "floor", 0.25,
      kind="consumables", spares="0.25 mm brass wire, 15.9 kg spools", source=SRC["edm"]),
    T("edm_contacts", "wire_edm", "power-feed contacts indexed and cleaned", ("h", 150), "floor", 0.25,
      kind="consumables", spares="power feeders", source=SRC["edm"]),
    T("edm_300", "wire_edm", "conductivity sensor and auto-threader cleaned; filters changed", ("h", 600), "floor",
      1.0, kind="consumables", spares="2 paper filter cartridges", source=SRC["edm"]),
    T("edm_resin", "wire_edm", "deionizing resin changed", ("h", 200), "floor", 0.5, kind="consumables",
      spares="DI resin", source=SRC["edm_al"] + "; every 200 h is assumed"),
    T("edm_weekly", "wire_edm", "EDM weekly cleaning: guides, heads, tank", ("days", 7), "floor", 0.75,
      source=SRC["edm"]),
    T("edm_test", "wire_edm", "test cut of a reference gauge, measured on the VHX", ("days", 7), "arm", 0.3,
      source="assumed"),
    T("edm_service", "wire_edm", "FANUC preventive maintenance", ("days", 365), "vendor", 8.0, source=SRC["edm"]),
    # ---- the tensile frames
    T("t_verify_floor", "instron_floor", "68FM-100: force verification, extensometer, annual service check",
      ("days", 365), "vendor", 6.0, source=SRC["e4"]),
    T("t_verify_tray", "tensile_h", "zwickiLine: force verification, extensometer", ("days", 365), "vendor", 4.0,
      source=SRC["e4"]),
    T("t_ref_floor", "instron_floor", "reference bar pulled (6061-T6), yield and modulus trended", ("days", 7), "arm",
      0.5, source="assumed"),
    T("t_ref_tray", "tensile_h", "reference specimen pulled, trended", ("days", 7), "arm", 0.3, source="assumed"),
    T("t_faces", "tensile_h", "grip faces replaced", ("n", 300, "tensile_rt"), "opening", 0.5, kind="consumables",
      spares="grip faces", source="assumed"),
    # ---- tray F: furnace, mounting press, polisher
    T("f_sat", "furnace", "furnace: system accuracy test against a test thermocouple", ("days", 91), "opening", 1.0,
      spares="type K test thermocouple (5 uses or 3 months)", source=SRC["ams2750"]),
    T("f_tus", "furnace", "furnace: temperature uniformity survey", ("days", 365), "vendor", 8.0,
      source=SRC["ams2750"] + "; once a year for a research furnace is assumed"),
    T("px_restock", "polisher", "SiC foils and cloths restocked in the magazine, suspensions refilled",
      ("n", 40, "polish"), "opening", 0.5, kind="consumables", spares="SiC 500# foils, cloths, OP-U suspension",
      source=SRC["leco"] + "; every 40 polishes is assumed"),
    T("px_waste", "polisher", "waste tank emptied, water tank filled (the coupling has no drain or process water)",
      ("days", 7), "opening", 0.5, kind="consumables", source="assumed"),
    T("mx_restock", "mount_press", "phenolic hopper refilled, ram and mould brushed", ("n", 60, "mount"), "opening",
      0.25, kind="consumables", spares="phenolic, about 20 g a mount", source=SRC["leco"]),
    # ---- tray M: XRF, CNC
    T("xrf_drift", "xrf", "XRF drift correction on the monitor sample", ("days", 1), "arm", 0.15, source="assumed"),
    T("xrf_he", "xrf", "He cylinder swapped (the coupling carries no He)", ("h", 120), "opening", 0.25,
      kind="consumables", spares="He cylinder", source="assumed"),
    T("cnc_tools", "cnc", "Carvera: end mills replaced, chips cleared", ("n", 80, "face"), "opening", 0.5,
      kind="consumables", spares="end mills", source="assumed"),
    # ---- tray D: XRD, SEM
    T("xrd_si", "xrd", "MiniFlex: NIST SRM 640 silicon scanned; peak positions and intensity trended", ("days", 7),
      "arm", 0.25, source=SRC["rigaku"] + "; weekly, between the two"),
    T("xrd_service", "xrd", "Rigaku service visit", ("days", 365), "vendor", 4.0, source="assumed"),
    T("sem_eds", "sem", "SEM: magnification standard and EDS energy check (Cu)", ("days", 7), "arm", 0.25,
      source="assumed"),
    T("sem_filament", "sem", "SEM filament exchanged (30 min to cool, then pump-down); anode every 5th",
      ("h", 100), "opening", 1.5, person=0.75, kind="consumables", spares="pre-centred cartridge filament",
      source=SRC["hitachi"]),
    T("sem_service", "sem", "Hitachi service visit: apertures, pumps", ("days", 365), "vendor", 4.0,
      source=SRC["hitachi"]),
    # ---- tray E: Mastersizer, iMicro, PIP
    T("ld_ref", "mastersizer", "Mastersizer: QAS3002 reference measured (Dv50 within 2.5 %)", ("days", 7), "arm", 0.3,
      source=SRC["malvern"] + "; weekly is assumed"),
    T("ld_clean", "mastersizer", "cell windows cleaned, Aero S hopper and venturi checked", ("days", 28), "opening",
      0.5, source=SRC["malvern"] + "; monthly is assumed"),
    T("nano_fs", "nanoindenter", "iMicro: indents in fused silica; area function and frame stiffness checked",
      ("days", 7), "arm", 0.5, source=SRC["keysight"] + "; weekly is assumed"),
    T("nano_tip", "nanoindenter", "Berkovich tip replaced and calibrated", ("n", 600, "nano"), "extracted", 2.0,
      kind="consumables", spares="Berkovich tip", source="assumed"),
    T("pip_cal", "pip", "PIP: profilometer calibrated on its sample", ("h", 3), "arm", 0.1, source=SRC["plastometrex"]),
    # ---- trays K, L: VHX, HM-220
    T("vhx_scale", "vhx", "VHX: stage micrometer imaged, calibration checked", ("days", 28), "arm", 0.2,
      source="assumed"),
    T("hv_block", "hardness", "HM-220: reference block indented, diagonals trended", ("days", 1), "arm", 0.2,
      source=SRC["mitutoyo"]),
    T("hv_verify", "hardness", "HM-220: indirect verification", ("days", 365), "vendor", 3.0, source=SRC["mitutoyo"]),
    # ---- tray B: the multi-doser, HR-202i, vacuum press
    T("bal_weights", "carousel", "HR-202i: check weight weighed 10 times (repeatability), then a calibration test",
      ("days", 1), "arm", 0.2, source=SRC["and"]),
    T("bal_cal", "carousel", "HR-202i calibrated with an external weight", ("days", 28), "arm", 0.2,
      source=SRC["and"] + "; monthly is assumed"),
    T("dose_clean", "carousel", "doser's funnels and cup nests cleaned, press die cleaned", ("days", 7), "opening", 0.5,
      source="assumed"),
    # ---- tray A: CubXL corrosion, OT-2
    T("cx_ref", "cubxl_corrosion", "reference electrode against a master in KCl (within 5 mV)", ("days", 7), "arm",
      0.25, source=SRC["gamry"] + "; weekly is assumed"),
    T("cx_cal", "cubxl_corrosion", "potentiostat calibrated on its dummy cell; OT-2 pipettes checked by weight",
      ("days", 182), "opening", 1.0, source=SRC["gamry"] + "; " + SRC["iso8655"]),
    T("cx_fluids", "cubxl_corrosion", "electrolyte refilled, waste emptied, tips restocked", ("days", 7), "opening",
      0.5, kind="consumables", spares="NaCl electrolyte, tips", source="assumed"),
    # ---- storage
    T("store_j", "tray:J", "tray J: cups, plugs, vials, stubs and coupons restocked", ("days", 7), "opening", 0.5,
      kind="consumables", route=False, source="assumed"),
    T("store_n", "tray:N", "tray N: new feedstock jars in", ("days", 7), "opening", 0.5, kind="consumables",
      route=False, source="assumed"),
    T("store_o", "tray:O", "tray O: finished lots out to the archive, empty jars in", ("days", 7), "opening", 0.5,
      kind="consumables", route=False, source="assumed"),
    T("spares_restock", "tray:S", "the spares tray restocked from deliveries; used spares logged", ("days", 28),
      "opening", 0.5, kind="consumables", route=False, source="assumed"),
    # ---- machines off the route (their people's time counts all the same)
    T("pm_c", "tray:C", "tray C: H2D and A1 mini nozzles, rods lubricated (off the route)", ("days", 28), "opening",
      1.0, route=False, source="assumed; a Bambu forum post quotes the wiki: lubricate every 3 months"),
    T("pm_g", "tray:G", "tray G: Form 4 tanks, Form Wash IPA (off the route)", ("days", 28), "opening", 1.0,
      route=False, source="assumed"),
    T("pm_i", "tray:I", "tray I: SnowPods' filters and chambers (off the route)", ("days", 28), "opening", 1.0,
      route=False, source="assumed"),
    T("pm_h", "tray:H", "tray H: stencil printer and LumenPnP nozzles (off the route)", ("days", 28), "opening", 0.5,
      route=False, source="assumed"),
    T("pm_ded", "ded", "DED: nozzle, protective window, powder feeders (off the route)", ("days", 28), "floor", 1.0,
      route=False, source="assumed"),
    T("pm_pack", "packaging", "packaging station: printheads cleaned, labels, ribbon, bags restocked (off the route)",
      ("days", 28), "floor", 0.5, route=False, source="assumed; Uline H-190 is sold with spare elements and covers"),
    # ---- software, IT and data (the orchestrator's brief, 2026-11-07): a person at a desk; the PC's instrument waits
    *[T(f"it_patch_{st}", st, "instrument PC: OS updates and a reboot (vendor software pinned)", ("days", 28),
        "desk", 0.25, kind="it", source="assumed: monthly, after Microsoft's monthly security release")
      for st in ("sem", "xrd", "xrf", "mastersizer", "nanoindenter", "pip", "vhx", "hardness", "tensile_h",
                 "instron_floor", "cubxl_corrosion", "aconity")],
    *[T(f"it_revalidate_{st}", st, "vendor software update: installed, then the reference check re-run and signed "
        "off", ("days", 182), "desk", 1.0, kind="it", source="assumed: two vendor updates a year")
      for st in ("sem", "xrd", "xrf", "mastersizer", "nanoindenter", "vhx", "hardness", "instron_floor", "aconity")],
    T("it_scheduler", "it", "the scheduler's own release: its instrument drivers run against every station's "
      "simulator, then one live check each", ("days", 28), "desk", 2.0, kind="it", source="assumed"),
    T("it_backup", "it", "backups verified; storage and the retention job checked", ("days", 7), "desk", 0.5,
      kind="it", source="assumed"),
    T("it_restore", "it", "a restore test from backup", ("days", 91), "desk", 2.0, kind="it", source="assumed"),
    T("it_network", "it", "network: switch and PoE firmware, the Pis' OS image, certificates", ("days", 91), "desk",
      1.0, kind="it", source="assumed; the cameras restart themselves (" + SRC["picam"] + ")"),
    T("it_licences", "it", "licence renewals and vendor support contracts", ("days", 365), "desk", 3.0, kind="it",
      source="assumed"),
    # ---- safety and compliance on a calendar
    T("c_xray", "xrd", "X-ray: radiation survey of the MiniFlex and the S2 PUMA, registration renewed (Utah DWMRC, "
      "[to confirm])", ("days", 365), "vendor", 2.0, kind="compliance",
      source="Utah Division of Waste Management and Radiation Control registers X-ray machines [to confirm]; the "
             "survey's interval assumed yearly"),
    T("c_laser", "aconity", "laser safety: interlocks and labels of the MIDI and the VHX's EA-300 LIBS audited by the "
      "laser safety officer", ("days", 365), "floor", 2.0, kind="compliance",
      source="ANSI Z136.1 (a laser safety programme and officer); yearly assumed"),
    T("c_eyewash", "site", "eyewash and safety shower activated", ("days", 7), "floor", 0.1, kind="compliance",
      source="ANSI/ISEA Z358.1: plumbed eyewash activated weekly"),
    T("c_extinguisher", "site", "extinguishers inspected (monthly visual); first-aid kit", ("days", 28), "floor", 0.25,
      kind="compliance", source="NFPA 10: monthly inspection, yearly maintenance by a contractor"),
    T("c_kardex", "vlm*", "Kardex: yearly safety inspection (with a service visit)", ("days", 365), "vendor", 2.0,
      kind="compliance", source="assumed; " + SRC["kardex"]),
    T("c_risk", "site", "MiR/UR risk assessment reviewed after a layout change (one a year assumed)", ("days", 365),
      "desk", 4.0, kind="compliance", source="ANSI/RIA R15.08 (industrial mobile robots) and ISO 10218-2 call for a "
                                             "risk assessment of the application; one change a year assumed"),
    T("c_ehs", "site", "EHS audit; people's training and SOP refreshers", ("days", 365), "desk", 8.0,
      kind="compliance", source="assumed"),
    # ---- people's own
    T("review", "staff", "control charts reviewed, next week's maintenance planned, spares reordered", ("days", 7),
      "floor", 1.0, at="fri", kind="review", route=False, source="assumed"),
]

# Beyond the first year: not booked by the model, counted in notes/upkeep.md's multi-year table.
LONG = [
    ("UPS batteries (15, VRLA)", "3-5 years at 25 °C, about half that per 10 °C warmer", "a person, the tray pulled "
     "out; Eaton's battery kit is hot-swappable", SRC["eaton"]),
    ("UPS batteries, if lithium (9PX Li-ion, LFP)", "8-10 years", "as above", SRC["eaton"]),
    ("MiR250 batteries", "at least 3,000 cycles", "a person", "MiR250 Li-NMC 47.7 V 34.2 Ah (reseller sheet)"),
    ("2F-85 overhaul", "2 million cycles", "Robotiq's factory, 5 business days plus shipping (a loan unit)",
     SRC["robotiq"]),
    ("MiR safety parts (stops, safety PLC, contactors, brakes)", "20 years", "vendor", SRC["mir"]),
    ("N2 generator catalyst module", "about 3 years", "a person (2 h to cool first)", SRC["parker"]),
    ("Glovebox purifier catalyst and sieve", "3 years (PureLab), 5-8 (EPFL)", "vendor", SRC["purelab"]),
    ("Glovebox O2 and H2O sensors", "1-2 years", "vendor", SRC["purelab"]),
    ("SEM turbo pump, diaphragm pump", "3-5 years", "vendor", SRC["hitachi"]),
    ("XRD tube", "about 10,000 h of beam (generic)", "vendor", "MicroXRay, generic sealed tube"),
    ("EDM power-feed cables", "3 years", "vendor", SRC["edm"]),
    ("UR10e CMOS battery", "up to 10 years", "a person", SRC["ur"]),
]

# Random failures. basis "op": per hour of the station's own work (a step can fail part-way and is run again after
# the repair); "cal": per calendar hour (the Shuttles, the units, the services). who: who repairs it; wait: hours for
# parts or a vendor before the repair starts. All assumed (no maker publishes an MTBF for these).
FAILS = [
    # asset, what, mtbf_h, basis, who, mttr_h, wait_h
    ("repowder", "induction, vacuum or nozzle fault", 400.0, "op", "floor", 3.0, 0.0),
    ("repowder", "a part from AMAZEMET (coil, generator, seal)", 3000.0, "op", "vendor", 8.0, 120.0),
    ("sieve_cell", "the tipper or the shaker stops; a cloth tears", 600.0, "op", "floor", 1.0, 0.0),
    ("aconity", "recoater crash or short feed", 300.0, "op", "floor", 2.0, 0.0),
    ("aconity", "laser, scanner or gas-loop fault", 4000.0, "op", "vendor", 16.0, 120.0),
    ("wire_edm", "the wire won't thread; a guide", 200.0, "op", "floor", 0.5, 0.0),
    ("instron_floor", "a grip or the chamber", 1000.0, "op", "floor", 1.0, 0.0),
    ("tensile_h", "a grip or the extensometer", 800.0, "op", "opening", 1.0, 0.0),
    ("furnace", "a thermocouple or a heater", 8000.0, "op", "extracted", 2.0, 72.0),
    ("polisher", "a disc that won't seat; a dispenser", 300.0, "op", "opening", 0.5, 0.0),
    ("mount_press", "a stuck mould; a seal", 1000.0, "op", "opening", 1.0, 0.0),
    ("cnc", "a broken end mill; the probe", 500.0, "op", "opening", 0.5, 0.0),
    ("sem", "vacuum or filament", 1500.0, "op", "opening", 1.0, 0.0),
    ("xrd", "goniometer or tube", 5000.0, "op", "vendor", 8.0, 120.0),
    ("xrf", "sample changer or He", 1500.0, "op", "opening", 0.5, 0.0),
    ("mastersizer", "the Aero S blocks; a dirty window", 300.0, "op", "opening", 0.5, 0.0),
    ("nanoindenter", "a broken tip; drift", 1500.0, "op", "extracted", 2.0, 72.0),
    ("pip", "the profilometer", 1500.0, "op", "opening", 1.0, 0.0),
    ("hardness", "focus or stage", 2000.0, "op", "opening", 0.5, 0.0),
    ("vhx", "stage or lens", 3000.0, "op", "opening", 0.5, 0.0),
    ("cubxl_corrosion", "a clogged or leaking cell; the reference electrode", 300.0, "op", "opening", 1.0, 0.0),
    ("carousel", "a jammed cup or a stuck feeder", 200.0, "op", "opening", 0.5, 0.0),
    ("vlm*", "a tray position error, a light-curtain trip, the shutter", 1500.0, "cal", "opening", 0.5, 0.0),
    ("vlm*", "a drive or extractor fault", 17520.0, "cal", "vendor", 8.0, 48.0),
    ("unit", "lost localization or a protective stop it can't clear", 400.0, "cal", "floor", 0.5, 0.0),
    ("unit", "a drive, joint or gripper fault", 8760.0, "cal", "vendor", 8.0, 72.0),
    ("tray:*", "a camera's Pi or SD card; a dock's link", 20000.0, "cal", "opening", 0.5, 0.0),
    ("chiller", "chiller fault (the XRD stops)", 8760.0, "cal", "vendor", 4.0, 48.0),
]
CHILLED = ["xrd"]          # stations that stop while the chilled water is off (the MiniFlex 600's tube)


def _phase(key: str, n: int) -> int:
    """A stable offset in [0, n) for a task, so tasks with the same interval don't all fall on the same day."""
    return int(hashlib.md5(key.encode()).hexdigest(), 16) % max(1, n)


def day_of(t: float) -> int:
    return int((t + 6.0) // 24)


def at(day: int, h: float) -> float:
    return day * 24.0 + h - 6.0


def crucible_hours(day: int) -> list:
    """The day's run slots' first hours, when the person is at the atomizer (timelapse.next_run_slot's rules)."""
    if day % 7 >= 5:
        return []
    starts = TL.PARAMS["run_starts"]["value"][:TL.runs_today(day)]
    if day % 7 == 4:
        starts = [s for s in starts if s < 12.0]
    p = TL.PARAMS["atomize_h"]["value"]["person"]
    return [(s, s + p) for s in starts]


RESERVE = (14.0, 16.0)      # Mon-Thu: kept free of calendar PM, for repairs and what use makes due (assumed policy)


def windows(day: int, reserve: bool = False, runs: bool = False) -> list:
    """The person's free time on a day (lab hours): the shift less the crucible hours. reserve: also less Mon-Thu's
    RESERVE (calendar PM keeps it free). runs: also less each run slot's whole run (a task on the atomizer itself)."""
    if day % 7 >= 5:
        return []
    s0, s1 = TL.PARAMS["shift"]["value"]
    busy = list(crucible_hours(day))
    if runs:
        busy += [(a, a + TL.STEPS[1][2]) for a, _ in crucible_hours(day)]
    if reserve and day % 7 < 4:
        busy.append(RESERVE)
    out, h = [], s0
    for a, b in sorted(busy):
        if a > h:
            out.append((at(day, h), at(day, min(a, s1))))
        h = max(h, b)
    if h < s1:
        out.append((at(day, h), at(day, s1)))
    return [(a, b) for a, b in out if b > a + 1e-9]


def fill(line, a: float, b: float):
    """Make [a, b] busy on a line, around what is already booked there (keeps the bookings non-overlapping)."""
    if b <= a:
        return
    gaps, t = [], a
    i = bisect.bisect_right(line.e, a)
    while i < len(line.s) and line.s[i] < b:
        if line.s[i] > t + 1e-9:
            gaps.append((t, line.s[i]))
        t = max(t, line.e[i])
        i += 1
    if t < b - 1e-9:
        gaps.append((t, b))
    for g in gaps:
        line.add(*g)


class Upkeep:
    """The hooks timelapse.simulate() calls: start() books the calendar tasks, presentable() keeps a step's load and
    unload off a Shuttle's opening while a person has a tray there, breaks() draws a failure for a step, repair()
    books the repair, used() counts a station's work and books the usage-driven tasks, finish() returns the record."""

    def __init__(self, seed: int = SEED, fails: bool = True, tasks=None):
        self.rng = np.random.default_rng(seed)
        self.fails_on = fails
        self.tasks = self._expand(tasks if tasks is not None else TASKS)
        self.log: list[dict] = []
        self.hours: dict[str, float] = {}
        self.count: dict = {}
        self.next_due: dict[str, float] = {}
        self.mates: dict[str, int] = {}
        self.grips = [0, 0]

    # ------------------------------------------------------------------------------------------ set-up
    def _expand(self, tasks) -> list:
        out = []
        for t in tasks:
            a = t["asset"]
            if a == "vlm*":
                for i in (1, 2):
                    out.append(dict(t, key=f"{t['key']}:{i}", asset=f"vlm{i}"))
            elif a == "unit":
                for u in (0, 1):
                    out.append(dict(t, key=f"{t['key']}:{u}", asset=f"unit{u}", unit=u))
            elif a == "tray:*":
                for k in TRAYS:
                    out.append(dict(t, key=f"{t['key']}:{k}", asset=f"tray:{k}"))
            else:
                out.append(dict(t))
        return out

    def shuttle(self, tray):
        return self.shuttles.get(tray, 1) if tray else None      # "S", the proposed spares tray: Shuttle 1

    def tray_stations(self, tray) -> list:
        return [s for s, k in TRAY_OF.items() if k == tray]

    def line(self, key):
        if key.startswith("unit"):
            return self.ulines[int(key[4:])]
        return self.lines.setdefault(key, TL.Line())

    def where(self, task_or_asset, who=None) -> tuple:
        """(tray or None, the lines a task blocks): the asset's own; at the opening or pulled out, also the tray's
        other stations and its Shuttle's opening."""
        asset = task_or_asset
        tray = None
        if asset.startswith("tray:"):
            tray = asset[5:]
        elif asset in TRAY_OF:
            tray = TRAY_OF[asset]
        elif asset in ("vlm1", "vlm2"):
            return None, [f"open{asset[-1]}"]
        keys = []
        if asset in ROUTE or asset.startswith("unit") or asset in ("n2", "chiller", "fumehood", "glovebox",
                                                                   "depowder", "ded", "packaging", "staff", "it",
                                                                   "site"):
            keys.append(asset)
        if tray and who in ("opening", "extracted"):
            keys += [s for s in self.tray_stations(tray) if s not in keys]
            keys.append(f"open{self.shuttle(tray)}")
        if asset == "chiller":
            keys += CHILLED
        return tray, keys

    def start(self, lines, ulines, book, ev, hours, shuttles):
        self.lines, self.ulines, self.book, self.ev, self.H = lines, ulines, book, ev, hours
        self.shuttles = shuttles
        self.staff = TL.Line()          # everything the person does (planned and repairs)
        self.staff_rep = TL.Line()      # the repairs alone: a repair goes ahead of planned work
        self.tr = TL.PARAMS["transfer_h"]["value"]
        for t in self.tasks:
            ev_ = t["every"]
            if ev_[0] in ("h", "n", "mates"):
                self.next_due[t["key"]] = float(ev_[1])
        occ = []
        for t in self.tasks:
            kind, n = t["every"][0], t["every"][1]
            if kind != "days":
                continue
            ph = _phase(t["key"], int(n))
            d = ph if n > 1 else 0
            while True:
                ready = self._ready(t, d)
                if ready is None or ready > hours:
                    break
                occ.append((ready, t["key"], t))
                d += int(n)
        occ.sort(key=lambda o: (o[0], o[1]))
        for ready, _, t in occ:
            self.do(t, ready)
        if self.fails_on:
            self._calendar_failures(hours)

    def _ready(self, t, d):
        """The time a calendar task becomes due on lab day d."""
        a = t["at"]
        if a == "night":
            return at(d, 2.0 + (_phase(t["key"], 7) * 0.5))      # 02:00-05:00, before people come in
        if a == "fri":
            wk = d // 7
            return at(wk * 7 + 4, 12.0)
        if a == "vendor":
            day = d
            while day % 7 not in (1, 2, 3):                           # Tuesday to Thursday
                day += 1
            return at(day, PARAMS["vendor_start_h"]["value"])
        day = d
        while day % 7 >= 5:
            day += 1
        return at(day, 8.0)

    # ------------------------------------------------------------------------------------------ booking
    def _segments(self, t, need, **wk):
        """From t, the person's free time that gives `need` hours: whole in one window if it fits one, split round
        the crucible hours of one day if it is over 2 h, over several days if it is over a day's free time."""
        d0 = day_of(t)
        for d in range(d0, d0 + 120):
            ws = [(max(a, t), b) for a, b in windows(d, **wk) if b - max(a, t) > 1e-6]
            if not ws:
                continue
            for a, b in ws:
                if b - a >= need - 1e-9:
                    return [(a, a + need)]
            if need > 2.0:
                segs, got, dd = [], 0.0, d
                while got < need - 1e-9 and dd < d + 30:
                    for a, b in (ws if dd == d else windows(dd, **wk)):
                        take = min(b - a, need - got)
                        if take > 1e-6:
                            segs.append((a, a + take))
                            got += take
                        if got >= need - 1e-9:
                            break
                    dd += 1
                    if need <= 6.0 and got < need - 1e-9:   # a job under 6 h stays within one day
                        segs = None
                        break
                if segs:
                    return segs
            t = at(d + 1, 0.0)
        return None

    def person_slot(self, ready, need, keys, urgent=False, reserve=False):
        """The earliest (start, end, segments) >= ready when one person can give `need` hours on shift and every
        line in keys is free from start to end. urgent (a repair): only other repairs hold the person up, since a
        repair goes ahead of planned work. reserve (calendar PM): not in Mon-Thu's RESERVE. A planned task on the
        atomizer itself stays clear of its run slots."""
        staff = self.staff_rep if urgent else self.staff
        runs = (not urgent) and "repowder" in keys
        t = ready
        for _ in range(3000):
            segs = self._segments(t, need, reserve=reserve, runs=runs)
            if segs is None:
                return None
            t0, t1 = segs[0][0], segs[-1][1]
            push = t0
            for k in keys:
                push = max(push, self.line(k).earliest(t0, t1 - t0))
            if push > t0 + 1e-9:
                t = push
                continue
            clash = None
            for a, b in segs:
                e = staff.earliest(a, b - a)
                if e > a + 1e-9:
                    clash = max(t0 + 0.25, t0 + (e - a))
                    break
            if clash is not None:
                t = clash
                continue
            return t0, t1, segs
        return None

    def vendor_slot(self, ready, dur, keys):
        """A vendor's visit: 08:00 on the first weekday at or after ready when the lines are free for the visit (a
        job over 8 h runs over several days, the machine down in between)."""
        d = day_of(ready)
        if at(d, PARAMS["vendor_start_h"]["value"]) < ready - 1e-9:
            d += 1
        for _ in range(400):
            while d % 7 >= 5:
                d += 1
            t0 = at(d, PARAMS["vendor_start_h"]["value"])
            days = max(1, math.ceil(dur / 8.0 - 1e-9))
            t1 = t0 + dur if days == 1 else at(d + days - 1 + 2 * ((d % 7 + days - 1) // 5), 16.0)
            if all(self.line(k).earliest(t0, t1 - t0) <= t0 + 1e-9 for k in keys):
                return t0, t1
            d += 1
        return None

    def record(self, t, t0, t1, down, keys, planned=True, extra=None, own=None):
        """One occurrence: [t0, t1] the work; down the asset's own outage (from a failure, not the repair's start);
        the other lines in stations are held [t0, t1]."""
        rec = dict(key=t["key"], task=t["key"].split(":")[0], asset=t["asset"], what=t["what"], who=t["who"],
                   kind=t["kind"], t0=round(t0, 3), t1=round(t1, 3), person_h=t["person"],
                   down=[round(down[0], 3), round(down[1], 3)], stations=list(keys), planned=planned,
                   own=own or t["asset"])
        if extra:
            rec.update(extra)
        self.log.append(rec)
        return rec

    def do(self, t, ready, planned=True):
        """Book one occurrence of a task at or after ready. -> its end."""
        who = t["who"]
        tray, keys = self.where(t["asset"], who)
        if who == "arm":
            if t["asset"] in ROUTE:
                t1 = self.book(t["asset"], ready, t["down"], f"check:{t['key'].split(':')[0]}", None, tray,
                               maint=t["key"])
                e = self.ev[-1]
                self.record(t, e["t0"], e["t1"], (e["t0"], e["t1"]), [t["asset"]], extra=dict(check=True))
                return t1
            ln = self.line(t["asset"])                                # a unit's own (the D405's calibration)
            t0 = ln.earliest(ready, t["down"])
            ln.add(t0, t0 + t["down"])
            self.record(t, t0, t0 + t["down"], (t0, t0 + t["down"]), [t["asset"]], extra=dict(check=True))
            return t0 + t["down"]
        if who == "auto":
            if t["down"] <= 0:
                self.record(t, ready, ready, (ready, ready), [])
                return ready
            t0 = max([ready] + [self.line(k).earliest(ready, t["down"]) for k in keys])
            for _ in range(50):
                t0n = max([t0] + [self.line(k).earliest(t0, t["down"]) for k in keys])
                if t0n <= t0 + 1e-9:
                    break
                t0 = t0n
            for k in keys:
                fill(self.line(k), t0, t0 + t["down"])
            self.record(t, t0, t0 + t["down"], (t0, t0 + t["down"]), keys)
            return t0 + t["down"]
        if who == "vendor":
            s = self.vendor_slot(ready, t["down"], keys)
            if s is None:
                return ready
            t0, t1 = s
            for k in keys:
                fill(self.line(k), t0, t1)
            self.record(t, t0, t1, (t0, t1), keys)
            return t1
        s = self.person_slot(ready, t["person"] or t["down"], keys, reserve=t["every"][0] == "days")
        if s is None:
            return ready
        t0, t1, segs = s
        for a, b in segs:
            fill(self.staff, a, b)
        for k in keys:
            fill(self.line(k), t0, t1)
        self.record(t, t0, t1, (t0, t1), keys, extra=dict(segments=[[round(a, 3), round(b, 3)] for a, b in segs]))
        return t1

    # ------------------------------------------------------------------------------------------ hooks
    def presentable(self, tray, t, dur):
        """A tray step's load at t and unload at t + dur each need its Shuttle's opening for a transfer; while a
        person has a tray there (or a vendor has the Shuttle) they wait."""
        if not tray:
            return t
        ol = self.lines.get(f"open{self.shuttle(tray)}")
        if ol is None or not ol.s:
            return t
        tr = self.tr
        a = ol.earliest(t - tr, tr) + tr
        if a > t + 1e-9:
            return a
        b = ol.earliest(t + dur, tr)
        if b > t + dur + 1e-9:
            return t + (b - (t + dur))
        return t

    def _modes(self, asset, basis):
        return [f for f in FAILS if f[0] == asset and f[3] == basis]

    def breaks(self, station, t, dur):
        """Does this step fail part-way? -> the failure's time, or None. Per hour of the station's work."""
        if not self.fails_on:
            return None
        modes = self._modes(station, "op")
        if not modes:
            return None
        lam = sum(1.0 / m[2] for m in modes)
        if self.rng.random() >= 1.0 - math.exp(-lam * dur):
            return None
        r = self.rng.random() * lam
        for m in modes:
            r -= 1.0 / m[2]
            if r <= 0:
                break
        self._pending = m
        return t + dur * float(self.rng.uniform(0.05, 0.95))

    def repair(self, station, t_f, mode=None):
        """Book the repair of a failure at t_f; the station is down from t_f to its end. -> the end."""
        m = mode or self._pending
        asset, what, _, _, who, mttr, wait = m
        t = T(f"fail:{asset}", asset if asset not in ("vlm*", "unit", "tray:*") else station, what, ("fail", 0), who,
              mttr, kind="repair", source="assumed MTBF and MTTR (upkeep.FAILS)")
        tray, keys = self.where(station, who)
        ready = t_f + wait
        if who == "vendor":
            s = self.vendor_slot(ready, mttr, [k for k in keys if k != station])
            t0, t1 = s if s else (ready, ready + mttr)
        else:
            s = self.person_slot(ready, mttr, [k for k in keys if k != station], urgent=True)
            if s is None:
                t0, t1 = ready, ready + mttr
            else:
                t0, t1, segs = s
                for a, b in segs:
                    self.staff_rep.add(a, b)
                    fill(self.staff, a, b)
        fill(self.line(station), t_f, t1)
        for k in keys:
            if k != station:
                fill(self.line(k), t0, t1)
        self.record(dict(t, key=f"fail:{station}", asset=station), t0, t1, (t_f, t1), keys, planned=False,
                    extra=dict(t_fail=round(t_f, 3), mode=what), own=station)
        return t1

    def _calendar_failures(self, hours):
        """The Shuttles', the units', the trays' and the services' failures, per calendar hour, drawn up front."""
        assets = {"vlm*": ["vlm1", "vlm2"], "unit": ["unit0", "unit1"], "tray:*": [f"tray:{k}" for k in TRAYS]}
        draws = []
        for m in FAILS:
            if m[3] != "cal":
                continue
            for a in assets.get(m[0], [m[0]]):
                t = 0.0
                while True:
                    t += float(self.rng.exponential(m[2]))
                    if t > hours:
                        break
                    draws.append((t, a, m))
        broken: dict[str, float] = {}
        for t, a, m in sorted(draws, key=lambda d: (d[0], d[1])):
            if t < broken.get(a, -1.0):                      # already down: it can't fail again until repaired
                continue
            broken[a] = self._cal_fail(a, t, m) or t

    def _cal_fail(self, asset, t_f, m):
        _, what, _, _, who, mttr, wait = m
        task = T(f"fail:{asset}", asset, what, ("fail", 0), who, mttr, kind="repair",
                 source="assumed MTBF and MTTR (upkeep.FAILS)")
        tray, keys = self.where(asset, who)
        own = {"vlm1": "open1", "vlm2": "open2"}.get(asset, asset)
        ready = t_f + wait
        if who == "vendor":
            s = self.vendor_slot(ready, mttr, [k for k in keys if k != own])
            t0, t1 = s if s else (ready, ready + mttr)
        else:
            s = self.person_slot(ready, mttr, [k for k in keys if k != own], urgent=True)
            if s is None:
                return
            t0, t1, segs = s
            for a, b in segs:
                self.staff_rep.add(a, b)
                fill(self.staff, a, b)
        if own in self.lines or own.startswith("unit") or own.startswith("open"):
            fill(self.line(own), t_f, t1)
        for k in keys:
            if k != own:
                fill(self.line(k), t0, t1)
        if asset == "chiller":
            for k in CHILLED:
                fill(self.line(k), t_f, t1)
        self.record(task, t0, t1, (t_f, t1), keys, planned=False, extra=dict(t_fail=round(t_f, 3), mode=what),
                    own=own)
        return t1

    def used(self, e):
        """Count a finished alloy step's work and book any usage-driven task it makes due."""
        st, step = e["station"], e["step"]
        dur = e["t1"] - e["t0"]
        self.hours[st] = self.hours.get(st, 0.0) + dur
        self.count[(st, None)] = self.count.get((st, None), 0) + 1
        self.count[(st, step)] = self.count.get((st, step), 0) + 1
        if e.get("unit") is not None and e["unit"] < 2:
            self.grips[e["unit"]] += PARAMS["grips_per_step"]["value"]
        if e.get("tray"):
            k = e["tray"]
            self.mates[k] = self.mates.get(k, 0) + PARAMS["presentations_per_step"]["value"] * \
                PARAMS["mates_per_presentation"]["value"]
        for t in self.tasks:
            kind = t["every"][0]
            if kind not in ("h", "n", "mates"):
                continue
            a = t["asset"]
            if kind == "mates":
                if not (a.startswith("tray:") and e.get("tray") == a[5:]):
                    continue
                v = self.mates.get(a[5:], 0)
            elif a.startswith("unit"):
                if kind != "n" or e.get("unit") != t["unit"]:
                    continue
                v = self.grips[t["unit"]]
            elif a != st:
                continue
            elif kind == "h":
                v = self.hours[st]
            else:
                sk = t["every"][2] if len(t["every"]) > 2 else None
                if sk is not None and sk != step:
                    continue
                v = self.count.get((st, sk), 0)
            due = self.next_due[t["key"]]
            if v >= due:
                self.next_due[t["key"]] = due + float(t["every"][1])
                self.do(t, e["t1"])

    def finish(self) -> list:
        self.log.sort(key=lambda r: r["t0"])
        return self.log


# ================================================================================================ the year
def run(seed: int = SEED, fails: bool = True) -> tuple[dict, dict]:
    """(the schedule with upkeep, the schedule as round 8 had it)."""
    up = Upkeep(seed=seed, fails=fails)
    sim = TL.simulate(upkeep=up)
    base = TL.simulate()
    return sim, base


def down_hours(log, asset, t0=0.0, t1=None) -> dict:
    """Hours an asset is down in [t0, t1], by planned / check / unplanned, overlaps merged (an unplanned hour wins)."""
    t1 = TL.YEAR_H if t1 is None else t1
    spans = {"unplanned": [], "planned": [], "check": []}
    for r in log:
        if asset == r.get("own") or (asset == r["asset"] and not r["stations"]):
            a, b = r["down"]
        elif asset in r["stations"]:
            a, b = r["t0"], r["t1"]
        else:
            continue
        a, b = max(a, t0), min(b, t1)
        if b <= a:
            continue
        k = "unplanned" if not r["planned"] else ("check" if r.get("check") else "planned")
        spans[k].append((a, b))
    out, taken = {}, []
    for k in ("unplanned", "planned", "check"):
        iv = sorted(spans[k])
        tot = 0.0
        for a, b in _merge(iv):
            tot += (b - a) - _overlap((a, b), taken)
        taken = _merge(sorted(taken + iv))
        out[k] = tot
    return out


def _merge(iv):
    out = []
    for a, b in iv:
        if out and a <= out[-1][1] + 1e-9:
            out[-1] = (out[-1][0], max(out[-1][1], b))
        else:
            out.append((a, b))
    return out


def _overlap(ab, iv):
    a, b = ab
    return sum(max(0.0, min(b, y) - max(a, x)) for x, y in iv)


# ================================================================================================ the realism checks
UPS_WH = dict(value=220.0, unit="Wh delivered",
              source="estimate from a 230 V 5PX 1500's 44 min at 300 W (a retailer's figure, notes/services.md)")
TRAY_W = {"A": 297, "B": 45, "C": 1244, "D": 1207, "E": 630, "F": 900}   # notes/services.md; F with its heaters paused
UNIT_W = dict(value=400.0, unit="W off the charger",
              source="assumed: the UR10e's 350 W typical (UR) and the MiR250's drive and computers")
MIR_KWH = dict(value=47.7 * 34.2 / 1000, unit="kWh", source="MiR250 battery, Li-NMC 47.7 V 34.2 Ah, at least "
                                                              "3,000 cycles (a reseller's spec sheet, robotsoflondon)")


def realism(sim: dict, years: float = 1.0) -> dict:
    """What the year's schedule asks of the parts that wear: couplings, UPSs, batteries, grippers, consumables."""
    ev, log = sim["events"], sim["maint"]
    pres: dict[str, int] = {}
    for e in ev:
        if e.get("tray"):
            pres[e["tray"]] = pres.get(e["tray"], 0) + PARAMS["presentations_per_step"]["value"]
    for r in log:
        if r["who"] in ("opening", "extracted"):
            for k in TRAYS + "S":
                if r["asset"] == f"tray:{k}" or TRAY_OF.get(r["asset"]) == k:
                    pres[k] = pres.get(k, 0) + 1
    shut = {1: 0, 2: 0}
    trays = {}
    for k, n in sorted(pres.items()):
        sh = TL._shuttles().get(k, 1)
        shut[sh] += n
        mates = n * PARAMS["mates_per_presentation"]["value"]
        w = TRAY_W.get(k, 60)
        dod = w * PARAMS["transit_s"]["value"] / 3600.0 / UPS_WH["value"]
        trays[k] = dict(presentations=n, plate_mates=mates, plate_years_to_100k=round(1e5 / max(1, mates), 1),
                        ups_transfers=2 * n, ups_dod_per_transfer_pct=round(100 * dod, 2),
                        ups_equiv_full_cycles=round(2 * n * dod, 1))
    docks = {f"bay dock, Shuttle {sh}": dict(mates=n, years_to_100k=round(1e5 / max(1, n), 1))
             for sh, n in shut.items()}
    # the units: off the charger from each transfer until the next, up to 1.5 h (the clip's linger)
    units = {}
    for u in (0, 1):
        tl = sorted((a, b) for a, b, uu, _ in sim["unit_log"] if uu == u)
        off = 0.0
        for i, (a, b) in enumerate(tl):
            nxt = tl[i + 1][0] if i + 1 < len(tl) else b + 1.5
            off += (b - a) + min(1.5, max(0.0, nxt - b))
        kwh = off * UNIT_W["value"] / 1000.0
        cyc = kwh / MIR_KWH["value"]
        grips = len(tl) * PARAMS["grips_per_step"]["value"]
        units[f"unit{u}"] = dict(transfers=len(tl), hours_off_charger=round(off), kwh=round(kwh),
                                 battery_equiv_cycles=round(cyc), battery_years_to_3000=round(3000 / max(cyc, 1), 1),
                                 grips=grips, fingertips_years_to_1M=round(1e6 / max(grips, 1), 1))
    hrs: dict[str, float] = {}
    cnt: dict[str, int] = {}
    for e in ev:
        if e.get("maint") or e.get("alloy") is None:
            continue
        hrs[e["station"]] = hrs.get(e["station"], 0.0) + (e["t1"] - e["t0"])
        cnt[e["step"]] = cnt.get(e["step"], 0) + 1
    tasks = {}
    for r in log:
        tasks[r["task"]] = tasks.get(r["task"], 0) + 1
    runs = sum(1 for e in ev if e["step"] == "atomize")
    return dict(
        tray_couplings=trays, bay_docks=docks,
        couplings_note="Stäubli rates the CombiTac's power, data and fluid inserts and the align frame at 100,000 "
                       "mating cycles (CombiTac overview, CT-Overview-11014010). A tray's plate mates twice per "
                       "presentation, its Shuttle's bay dock once per presentation of any of its trays.",
        ups_note=f"each transfer is about {PARAMS['transit_s']['value']:.0f} s on the battery; {UPS_WH['source']}. "
                 "VRLA is rated 200 cycles at 100 % depth of discharge, 1,200 at 30 % (Yuasa NP12-12): these "
                 "transfers add only a few equivalent full cycles a year, so float life and heat set the battery's "
                 "life (3-5 years at 25 °C, Eaton), not the transfers.",
        units=units, units_note=f"{UNIT_W['source']}; {MIR_KWH['source']}; Robotiq: fingertips at 1 million cycles, "
                                "overhaul at 2 million (2F-85 manual)",
        station_hours={k: round(v, 1) for k, v in sorted(hrs.items(), key=lambda kv: -kv[1])},
        step_counts=cnt, atomizer_runs=runs, task_counts=tasks)


# ================================================================================================ the record
def weekly_people(sim: dict) -> dict:
    """People's hours in each of the 52 weeks, by kind."""
    out = {k: [0.0] * 52 for k in KINDS}
    for e in sim["events"]:
        if e["step"] == "atomize":
            w = min(51, int(e["t0"] // 168))
            out["crucible"][w] += TL.PARAMS["atomize_h"]["value"]["person"]
    for r in sim["maint"]:
        if r["person_h"] <= 0:
            continue
        w = min(51, int(r["t0"] // 168))
        out[r["kind"]][w] += r["person_h"]
    return {k: [round(x, 2) for x in v] for k, v in out.items()}


AVAIL_ROWS = ROUTE + ["open1", "open2", "unit0", "unit1"]
ROW_NAMES = dict(TL.STATION_NAMES, open1="Shuttle 1 (its opening)", open2="Shuttle 2 (its opening)",
                 unit0="unit 1 (MiR250 + UR10e)", unit1="unit 2 (MiR250 + UR10e)")


def availability(sim: dict) -> dict:
    out = {}
    for st in AVAIL_ROWS:
        d = down_hours(sim["maint"], st)
        out[st] = dict(availability=round(1 - sum(d.values()) / TL.YEAR_H, 4),
                       **{f"{k}_h": round(v, 1) for k, v in d.items()})
    return out


def pick_week(sim: dict) -> int:
    """The week (after the ramp) whose maintenance shows the most kinds of who, then a repair, then the most tasks."""
    best = None
    for w in range(5, 51):
        a, b = w * 168.0, (w + 1) * 168.0
        rs = [r for r in sim["maint"] if a <= r["t0"] < b]
        whos = {r["who"] for r in rs}
        rep = any(not r["planned"] for r in rs)
        ven = any(r["who"] == "vendor" for r in rs)
        score = (len(whos), ven, rep, len(rs))
        if best is None or score > best[0]:
            best = (score, w)
    return best[1]


def week_data(sim: dict, w: int) -> dict:
    a, b = w * 168.0, (w + 1) * 168.0
    rows = {k: [] for k in AVAIL_ROWS + ["staff"]}
    for e in sim["events"]:
        if e["t1"] <= a or e["t0"] >= b:
            continue
        if e.get("maint"):
            continue                                    # the checks come from the maintenance record
        rows.setdefault(e["station"], []).append(dict(t0=round(e["t0"] - a, 3), t1=round(e["t1"] - a, 3),
                                                      what=e["step"], alloy=e["alloy"],
                                                      kind="interrupted" if e.get("interrupted") else "process"))
        if e["step"] == "atomize":
            p = TL.PARAMS["atomize_h"]["value"]["person"]
            rows["staff"].append(dict(t0=round(e["t0"] - a, 3), t1=round(e["t0"] + p - a, 3), what="crucible",
                                      kind="crucible"))
    for r in sim["maint"]:
        lo, hi = min(r["down"][0], r["t0"]), max(r["down"][1], r["t1"])
        if hi <= a or lo >= b:
            continue
        for st in set(r["stations"] + ([r["own"]] if r["own"] in rows else [])):
            if st not in rows:
                continue
            if st == r.get("own") and not r["planned"]:
                rows[st].append(dict(t0=round(r["down"][0] - a, 3), t1=round(r["t0"] - a, 3), what=r["what"],
                                     kind="waiting", who=r["who"]))
            rows[st].append(dict(t0=round(r["t0"] - a, 3), t1=round(r["t1"] - a, 3), what=r["what"],
                                 kind="repair" if not r["planned"] else ("check" if r.get("check") else "maint"),
                                 who=r["who"], task=r["task"]))
        if r["who"] in PEOPLE and r["person_h"] > 0:
            for s0, s1 in r.get("segments") or [[r["t0"], r["t1"]]]:
                rows["staff"].append(dict(t0=round(s0 - a, 3), t1=round(s1 - a, 3), what=r["what"],
                                          kind="repair" if not r["planned"] else "maint", who=r["who"],
                                          task=r["task"]))
    shifts = []
    for d in range(7):
        day = w * 7 + d
        if day % 7 < 5:
            s0, s1 = TL.PARAMS["shift"]["value"]
            shifts.append([round(at(day, s0) - a, 3), round(at(day, s1) - a, 3)])
    return dict(week=w + 1, starts_lab_h=a, hours_from="Monday 06:00 of the week", shifts=shifts,
                rows={k: sorted(v, key=lambda x: x["t0"]) for k, v in rows.items()})


def totals(sim, ncam) -> dict:
    c = TL.counters(sim, TL.YEAR_H, ncam)
    return {k: (round(v, 1) if isinstance(v, float) else v) for k, v in c.items()}


def storage(sim: dict, ncam: int) -> dict:
    """The stream video against the instrument data, kept two ways."""
    mbps = TL.PARAMS["stream_mbps"]["value"]
    tb_h = mbps / 8 * 3600 / 1e6                       # TB an hour, one camera
    keep_all = ncam * tb_h * TL.YEAR_H
    anomalies = [r for r in sim["maint"] if not r["planned"]]
    anomalies += [e for e in sim["events"] if e.get("failed") or e.get("interrupted")]
    clip_h, cams_each, rolling_days = 0.5, 3, 30
    kept = len(anomalies) * clip_h * cams_each * tb_h
    rolling = ncam * tb_h * 24 * rolling_days
    lapse = keep_all / 60.0                              # a time-lapse at a sixtieth of the frames, assumed
    c = TL.counters(sim, TL.YEAR_H, ncam)
    return dict(
        cameras=ncam, video_keep_all_tb=round(keep_all, 1), instrument_data_tb=round(c["data_gb"] / 1000, 2),
        retention=dict(rolling_days=rolling_days, rolling_buffer_tb=round(rolling, 1), anomalies=len(anomalies),
                       anomaly_clip_h=clip_h, cameras_per_anomaly=cams_each, anomaly_clips_tb=round(kept, 2),
                       timelapse_tb=round(lapse, 2), kept_a_year_tb=round(kept + lapse, 2)),
        note="Kept whole, a year of stream video needs about this much disk, mirrored, every year, against a few TB "
             "of instrument data. The retention policy (assumed) keeps a rolling buffer, a clip around every "
             "failure, interrupted step, dripped run and cracked build, and a time-lapse.")


def model(write=True) -> dict:
    up = Upkeep()
    sim = TL.simulate(upkeep=up)
    base = TL.simulate()
    planned = TL.simulate(upkeep=Upkeep(fails=False))
    ncam = TL.cameras()
    av = availability(sim)
    ppl = weekly_people(sim)
    wk_after = [sum(ppl[k][i] for k in KINDS) for i in range(52)]
    steady = list(range(8, 52))
    log = sim["maint"]
    who_counts: dict = {}
    for r in log:
        who_counts.setdefault(r["who"], {"planned": 0, "repairs": 0})
        who_counts[r["who"]]["planned" if r["planned"] else "repairs"] += 1
    w = pick_week(sim)
    out = dict(
        what="Upkeep (upkeep.py, round 10): the finale's greedy schedule (timelapse.simulate) with maintenance booked "
             "into it: calendar PM, usage-driven consumables, robot-run reference checks and random failures (seeded). "
             "A model, not a measurement; every task's interval, who does it, downtime, spares and source are in "
             "'tasks', and 'assumed' marks ours.",
        params=PARAMS, who=WHO, kinds=KINDS,
        tasks=[{k: v for k, v in t.items() if k != "unit"} for t in TASKS],
        failures=[dict(asset=a, what=wh, mtbf_h=m, basis=bs, who=who, mttr_h=r, wait_h=wt,
                       source="assumed") for a, wh, m, bs, who, r, wt in FAILS],
        totals=dict(round8=totals(base, ncam), planned_upkeep_only=totals(planned, ncam),
                    with_upkeep_and_failures=totals(sim, ncam)),
        availability=av,
        people_hours_per_week=dict(
            mean_after_ramp=round(float(np.mean([wk_after[i] for i in steady])), 1),
            max=round(max(wk_after), 1),
            by_kind_mean_after_ramp={k: round(float(np.mean([ppl[k][i] for i in steady])), 2) for k in KINDS},
            weekly=ppl,
            note="one person's weekday shift is 40 h; their crucible hours are the atomizer's run slots"),
        counts=dict(checks_run=sum(1 for r in log if r.get("check")),
                    pm_done=sum(1 for r in log if r["planned"] and not r.get("check") and r["who"] != "auto"),
                    auto=sum(1 for r in log if r["who"] == "auto"),
                    repairs=sum(1 for r in log if not r["planned"]), by_who=who_counts),
        realism=realism(sim),
        storage=storage(sim, ncam),
        beyond_the_first_year=[dict(what=w, interval=i, who=wh, source=src) for w, i, wh, src in LONG],
        spares_tray=SPARES_TRAY,
        week=week_data(sim, w),
    )
    if write:
        OUT.mkdir(exist_ok=True)
        (OUT / f"{NAME}_model.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    return out, sim


# ================================================================================================ the charts
# Categorical slots in the dataviz palette's fixed order (validated: adjacent CVD dE >= 9.1, normal >= 19.6)
SLOTS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
WHO_COL = dict(zip(WHO, SLOTS))
KIND_COL = dict(zip(KINDS, SLOTS))
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
KIND_SHORT = dict(crucible="crucible, every run", pm="preventive maint.", consumables="consumables, restocking",
                  repair="repairs", vendor="hosting vendors", review="control charts, planning",
                  it="software, IT, data", compliance="safety, compliance")
PROC = "#c9c8c2"


def _style(ax):
    ax.set_facecolor(SURF)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color("#9b9a94")
    ax.tick_params(colors=INK2, labelsize=9.5)
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)


def plot_year(m: dict, path=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    path = path or OUT / f"{NAME}_year.png"
    fig = plt.figure(figsize=(16, 10.6), dpi=110, facecolor=SURF)
    gs = fig.add_gridspec(2, 2, width_ratios=[1.0, 1.2], height_ratios=[1.0, 0.8], wspace=0.30, hspace=0.62,
                          left=0.215, right=0.925, top=0.855, bottom=0.115)
    fig.suptitle("Upkeep in the lab's first year (model)", x=0.012, y=0.975, ha="left", fontsize=17,
                 fontweight="bold", color=INK)
    tot = m["totals"]
    fig.text(0.012, 0.912, "The finale's schedule with maintenance booked into it: calendar PM, consumables by use, "
             "robot-run reference checks, and seeded random failures.\nEvery interval, who does it and its source: "
             "out/upkeep_model.json and notes/upkeep.md.", fontsize=10.5, color=INK2, ha="left", va="center",
             linespacing=1.5)
    # ---- availability
    ax = fig.add_subplot(gs[:, 0])
    _style(ax)
    av = m["availability"]
    rows = AVAIL_ROWS[::-1]
    y = np.arange(len(rows))
    left = np.zeros(len(rows))
    parts = [("unplanned_h", "unplanned: failures, incl. waiting for a person", SLOTS[0]),
             ("planned_h", "planned: PM, consumables, vendor visits", SLOTS[1]),
             ("check_h", "robot-run reference checks", SLOTS[2])]
    for k, lab, col in parts:
        v = np.array([av[r][k] for r in rows])
        ax.barh(y, v, left=left, color=col, height=0.62, label=lab, edgecolor=SURF, linewidth=1.5)
        left += v
    for i, r in enumerate(rows):
        ax.text(left[i] + 6, i, f"{100 * av[r]['availability']:.1f} %", va="center", fontsize=9, color=INK)
    ax.set_yticks(y)
    ax.set_yticklabels([ROW_NAMES.get(r, r) for r in rows], fontsize=9.5, color=INK)
    ax.set_xlabel("hours out of use in the year (label: availability)", color=INK2, fontsize=10)
    ax.set_xlim(0, max(left) * 1.22)
    ax.set_title("Availability per station", loc="left", fontsize=12.5, fontweight="bold", color=INK, pad=10)
    ax.legend(loc="upper left", bbox_to_anchor=(-0.02, -0.055), fontsize=9, frameon=False)
    # ---- people's hours per week
    ax = fig.add_subplot(gs[0, 1])
    _style(ax)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.grid(axis="x", visible=False)
    wk = m["people_hours_per_week"]["weekly"]
    x = np.arange(1, 53)
    bot = np.zeros(52)
    for k in KINDS:
        v = np.array(wk[k])
        if v.sum() <= 0:
            continue
        ax.bar(x, v, bottom=bot, width=0.8, color=KIND_COL[k], label=KIND_SHORT[k], edgecolor=SURF, linewidth=0.6)
        bot += v
    ax.axhline(40, color=INK2, lw=1.0, ls=(0, (4, 3)))
    ax.text(52.9, 40, "one\nperson's\n40 h week", fontsize=8.5, color=INK2, va="center", ha="left")
    ax.set_xlim(0.3, 52.7)
    ax.set_ylim(0, max(45, bot.max() * 1.1))
    ax.set_xlabel("week of the first year", color=INK2, fontsize=10)
    ax.set_ylabel("people's hours", color=INK2, fontsize=10)
    mean = m["people_hours_per_week"]["mean_after_ramp"]
    ax.set_title(f"People's hours per week, by kind of task (mean {mean:.0f} h from week 9)", loc="left",
                 fontsize=12.5, fontweight="bold", color=INK, pad=10)
    ax.legend(loc="upper left", bbox_to_anchor=(-0.01, -0.15), ncol=4, fontsize=9, frameon=False,
              columnspacing=1.2, handlelength=1.4)
    # ---- the year's totals
    ax = fig.add_subplot(gs[1, 1])
    _style(ax)
    ax.grid(axis="x", visible=False)
    ax.grid(axis="y", color=GRID, lw=0.8)
    keys = [("atomized", "alloys atomized"), ("tested", "fully tested"), ("promoted", "promoted"),
            ("runs", "atomizer runs")]
    series = [("round8", "round 8: no maintenance", "#9b9a94"),
              ("planned_upkeep_only", "with planned upkeep", SLOTS[0]),
              ("with_upkeep_and_failures", "with upkeep and failures", SLOTS[1])]
    xx = np.arange(len(keys))
    wbar = 0.26
    for j, (sk, lab, col) in enumerate(series):
        vals = [tot[sk][k] for k, _ in keys]
        bars = ax.bar(xx + (j - 1) * wbar, vals, width=wbar - 0.02, color=col, label=lab)
        for b_, v in zip(bars, vals):
            ax.text(b_.get_x() + b_.get_width() / 2, v + 8, f"{v:,}", ha="center", va="bottom", fontsize=8.5,
                    color=INK)
    ax.set_xticks(xx)
    ax.set_xticklabels([n for _, n in keys], fontsize=10, color=INK)
    ax.set_ylabel("count in the year", color=INK2, fontsize=10)
    ax.set_ylim(0, max(tot["round8"]["runs"], 1) * 1.15)
    ax.set_title("The year's totals against round 8's", loc="left", fontsize=12.5, fontweight="bold",
                 color=INK, pad=10)
    ax.legend(loc="upper left", fontsize=9, frameon=False)
    fig.savefig(path, facecolor=SURF)
    plt.close(fig)
    print("wrote", path)
    return path


def plot_week(m: dict, path=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    path = path or OUT / f"{NAME}_week.png"
    wd = m["week"]
    rows = ["staff"] + AVAIL_ROWS
    names = dict(ROW_NAMES, staff="the person on shift")
    fig, ax = plt.subplots(figsize=(16, 10.5), dpi=110, facecolor=SURF)
    fig.subplots_adjust(left=0.205, right=0.985, top=0.885, bottom=0.135)
    _style(ax)
    ax.grid(axis="x", visible=False)
    n = len(rows)
    for a, b in wd["shifts"]:
        ax.axvspan(a, b, color="#fbefd9", zorder=0, lw=0)
    for d in range(8):
        xm = 18 + 24 * d                                    # midnights (the week starts Monday 06:00)
        if xm <= 168:
            ax.axvline(xm, color="#d6d5cf", lw=0.8, zorder=0.5)
    for i, r in enumerate(rows):
        yy = n - 1 - i
        for bar in wd["rows"].get(r, []):
            a, b = max(0.0, bar["t0"]), min(168.0, bar["t1"])
            if b <= a:
                continue
            k = bar["kind"]
            if k == "process":
                ax.barh(yy, b - a, left=a, height=0.5, color=PROC, lw=0, zorder=2)
            elif k == "interrupted":
                ax.barh(yy, b - a, left=a, height=0.5, color=PROC, edgecolor=INK, lw=0.8, hatch="xx", zorder=2)
            elif k == "crucible":
                ax.barh(yy, b - a, left=a, height=0.72, color="#5a5955", lw=0, zorder=3)
            elif k == "waiting":
                ax.barh(yy, b - a, left=a, height=0.72, color="#f3f2ee", edgecolor=SLOTS[7], lw=0.8,
                        hatch="///", zorder=3)
            else:
                col = WHO_COL.get(bar.get("who"), SLOTS[0])
                ax.barh(yy, max(b - a, 0.35), left=a, height=0.72, color=col, lw=0.8 if k == "repair" else 0,
                        edgecolor=INK if k == "repair" else col, hatch="..." if k == "repair" else None, zorder=4)
    ax.set_yticks(range(n))
    ax.set_yticklabels([names.get(r, r) for r in rows][::-1], fontsize=9.5, color=INK)
    ax.set_ylim(-0.7, n - 0.3)
    ticks = [18 + 24 * d + 12 for d in range(7)]
    ax.set_xticks([0] + [18 + 24 * d for d in range(7)])
    ax.set_xticklabels(["Mon 06:00"] + ["00:00"] * 7, fontsize=8.5, color=INK2)
    for d, nm in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
        xc = max(3.0, 24 * d - 6 + 12)
        ax.text(xc, n - 0.15, nm, ha="center", va="bottom", fontsize=10.5, fontweight="bold", color=INK2)
    ax.set_xlim(0, 168)
    ax.set_xlabel("time in the week (shaded: the weekday shift, 08:00-16:00, the only time a person is on site)",
                  color=INK2, fontsize=10)
    fig.suptitle(f"One week of the lab with upkeep booked (model): week {wd['week']}", x=0.012, y=0.975,
                 ha="left", fontsize=17, fontweight="bold", color=INK)
    fig.text(0.012, 0.925, "Every station's bookings: process steps in grey; maintenance coloured by who does it. "
             "A tray task at the opening also holds the tray's other instruments and its Shuttle's opening.",
             fontsize=10.5, color=INK2, ha="left")
    handles = [Patch(color=PROC, label="process step"), Patch(color="#5a5955", label="the crucible (a person)")]
    handles += [Patch(color=WHO_COL[k], label=WHO[k]) for k in WHO]
    handles += [Patch(facecolor="#dddcd6", edgecolor=INK, hatch="...", label="a repair (who: its colour)"),
                Patch(facecolor="#f3f2ee", edgecolor=SLOTS[7], hatch="///", label="broken, waiting for a person"),
                Patch(facecolor=PROC, edgecolor=INK, hatch="xx", label="step cut short by a failure")]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(-0.22, -0.06), ncol=6, fontsize=9,
              frameon=False)
    fig.savefig(path, facecolor=SURF)
    plt.close(fig)
    print("wrote", path)
    return path


if __name__ == "__main__":
    args = sys.argv[1:]
    m, sim = model()
    print(json.dumps(dict(totals={k: {kk: v[kk] for kk in ("atomized", "printed", "tested", "promoted", "runs")}
                                  for k, v in m["totals"].items()},
                          people=m["people_hours_per_week"]["mean_after_ramp"],
                          by_kind=m["people_hours_per_week"]["by_kind_mean_after_ramp"],
                          counts={k: v for k, v in m["counts"].items() if k != "by_who"},
                          week=m["week"]["week"]), indent=1))
    if not args or args[0] != "model":
        plot_year(m)
        plot_week(m)
