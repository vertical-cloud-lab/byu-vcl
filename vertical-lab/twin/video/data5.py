"""Rounds 5 and later of the twin, as the two-year cut reads them (twin/video/cut5.py and replay5.py).

    TWIN_VIDEO_ROUND=5 python -m twin.video.data5          # out/twin5/video/replay.json: the replayed seed, both labs

One switch, TWIN_VIDEO_ROUND. The round's results are out/twin<R>/ (like<R>.json, runs/, events/), its analysis is
twin/like<R>.py and twin/bench<R>.py, and the cut is written to out/twin<R>/video/. Nothing about a round is typed in
here: the replayed arm is named once (REPLAY), its seed is the one the round's own ``median_seed()`` picks (the arm's
median seed for both campaigns together, as the round's notes name it), and everything else is read from that run's
row and event log. The conventional lab beside it is the same seed with the same policy and the same stock rule.

``prepare()`` writes replay.json so that the frames' own processes read one small file and two event logs, not the
round's 488 rows.
"""
from __future__ import annotations

import bisect
import importlib
import json
import os
import sys
from pathlib import Path

import numpy as np

from . import data as D

HERE = D.HERE
ROUND = D.ROUND
OUT = D.RES                                             # out/twin<ROUND>
VID = D.VID                                             # out/twin<ROUND>/video
HPD = 24.0
CAMPS = D.CAMPAIGNS
# the replayed arm: the automated lab (round 4's parallel plan with the round's set-up), stocked, time-aware BOFN on
# both campaigns. TWIN_VIDEO_POLICY / TWIN_VIDEO_STOCK / TWIN_VIDEO_SEED choose another arm or seed for a look; the cut
# as uploaded uses none of them.
REPLAY = dict(lab="vertical", plan="parallel", policy=os.environ.get("TWIN_VIDEO_POLICY", "bofn3"),
              stock=os.environ.get("TWIN_VIDEO_STOCK", "reorder"))
CONV = dict(lab="conventional", plan="external")       # the same policy, stock rule and seed
POLICY_WORDS = {"bofn3": "time-aware BOFN", "pkgfn3": "time-aware pKGFN", "fast": "the heuristic (Al) and the funnel (Cu)"}
STOCK_WORDS = {"reorder": "stocked", "lean": "ordering as it goes"}
_C: dict = {}


def like_mod():
    sys.path.insert(0, str(HERE))
    return importlib.import_module(f"twin.like{ROUND}")


def bench_mod():
    sys.path.insert(0, str(HERE))
    return importlib.import_module(f"twin.bench{ROUND}")


def like() -> dict:
    """like<R>.json: what the round's tables.md prints."""
    if "like" not in _C:
        _C["like"] = json.loads((OUT / f"like{ROUND}.json").read_text())
    return _C["like"]


def rows() -> dict:
    """{arm key: {seed: row}} for the whole round (slow: every row is read)."""
    if "rows" not in _C:
        _C["rows"] = like_mod().load_all()
    return _C["rows"]


def _rx(r: dict) -> dict:
    """A row's own-round block (r5 in round 5; a later round may name its own)."""
    return r.get(f"r{ROUND}") or r.get("r5") or {}


def _lab_part(r: dict, T: dict) -> dict:
    L, B = like_mod(), bench_mod()
    rid = B.run_id(r["cfg"])
    rx, r4 = _rx(r), r.get("r4") or {}
    camps = {}
    for c in CAMPS:
        cc = r["campaigns"][c]
        days = {}
        for tn in ("T1", "T2"):
            d, ok = L.to_target(r, c, T[tn][c])
            days[tn] = dict(day=float(d), hit=bool(ok))
        hp = ((rx.get("hpc") or {}).get("campaigns") or {}).get(c) or {}
        camps[c] = dict(budget=cc.get("budget"), spent=cc.get("spent"), best_new=cc.get("best_new"),
                        curve_new=cc.get("curve_new") or [], spend_curve=cc.get("spend_curve") or [],
                        spend_by=cc.get("spend_by") or {}, counters=(rx.get("counters") or {}).get(c) or {},
                        days=days, idle=((rx.get("idle") or {}).get("stretches") or {}).get(c) or {},
                        hpc=dict(evaluated=hp.get("evaluated"), seen=hp.get("materialized")),
                        stock={k: v for k, v in ((rx.get("stock") or {}).get(c) or {}).items()
                               if not isinstance(v, (list, dict))})
    hpc = rx.get("hpc") or {}
    return dict(run_id=rid, events=f"out/twin{ROUND}/events/{rid}.json.xz", cfg=r["cfg"], campaigns=camps,
                build=r4.get("build") or {}, station_online=r4.get("station_online") or {}, cell_h=r4.get("cell_h"),
                full_h=r4.get("full_h"), room_h=rx.get("room_h"), atom=rx.get("atom") or {},
                used={k: dict(name=v.get("name"), fault=v.get("fault"), usd_saved=v.get("usd_saved"))
                      for k, v in (rx.get("used") or {}).items()},
                hpc=dict(cores=hpc.get("cores"), per_day=hpc.get("per_day"), add_per_day=hpc.get("add_per_day"),
                         keep=hpc.get("keep")),
                cpu=(r.get("env") or {}).get("cpu"), commit=(r.get("code") or {}).get("commit"))


def prepare() -> dict:
    """replay.json: the replayed seed's two rows (the automated lab and the conventional lab with the same policy,
    stock rule and seed), with what the round's notes say about that seed."""
    L = like_mod()
    A, T = rows(), like()["targets"]
    kv = L.gk(REPLAY["lab"], REPLAY["plan"], REPLAY["policy"], REPLAY["stock"])
    kc = L.gk(CONV["lab"], CONV["plan"], REPLAY["policy"], REPLAY["stock"])
    ms = L.median_seed(A[kv], T)
    seed = int(os.environ.get("TWIN_VIDEO_SEED", ms["seed"]))
    stats = {}
    for name, key in (("auto", kv), ("conv", kc)):
        for c in CAMPS:
            for tn in ("T1", "T2"):
                st = L.arm_stats(A[key], c, T[tn][c])
                stats[f"{name}|{c}|{tn}"] = dict(n=st["n"], hit=st["hit"], median=st["median"])
    out = dict(round=ROUND, arm=kv, conv_arm=kc, seed=seed, n_seeds=len(A[kv]), n_seeds_conv=len(A[kc]),
               median_seed=ms, is_median_seed=bool(seed == ms["seed"]), targets=T, policy=REPLAY["policy"],
               stock=REPLAY["stock"], policy_words=POLICY_WORDS.get(REPLAY["policy"], REPLAY["policy"]),
               stock_words=STOCK_WORDS.get(REPLAY["stock"], REPLAY["stock"]),
               auto=_lab_part(A[kv][seed], T), conv=_lab_part(A[kc][seed], T), arm_stats=stats,
               horizon_days=float(L.HORIZON))
    VID.mkdir(parents=True, exist_ok=True)
    (VID / "replay.json").write_text(json.dumps(out, indent=1) + "\n")
    _C["info"] = out
    return out


def info() -> dict:
    """replay.json (made by prepare() when it isn't there)."""
    if "info" not in _C:
        p = VID / "replay.json"
        _C["info"] = json.loads(p.read_text()) if p.exists() else prepare()
    return _C["info"]


# ---------------------------------------------------------------------------------------------------- the event log
HELPERS = ("robot", "operator")
ITEM_WORDS = {  # twin/supply.py's keys, as a viewer would say them (the stock log names items by key)
    "cc_plate": "atomizer plates", "bn_nozzle": "nozzles", "graphite_crucible": "crucibles", "build_plate":
        "build plates", "ded_substrate": "DED substrates", "argon": "argon", "bn_spray": "BN spray",
    "al_bar_hp": "aluminium rod", "cu_ofe_bar": "copper bar", "cu_shot": "copper shot", "al_shot": "aluminium shot",
    "ni_pellet": "nickel", "fe_powder": "iron powder", "mn_flake": "manganese", "li_metal": "lithium",
}


def item_words(key: str) -> str:
    if key in ITEM_WORDS:
        return ITEM_WORDS[key]
    try:
        sys.path.insert(0, str(HERE))
        from twin import supply
        it = supply.ITEMS.get(key)
        if it is not None and getattr(it, "element", None):
            return f"{it.element} feedstock"
    except Exception:                                   # noqa: BLE001
        pass
    if key.startswith("al_") and key[3:].rstrip("0123456789"):
        return f"{key[3:].rstrip('0123456789').capitalize()} master alloy"
    return key.replace("_", " ")


class Replay5(D.Replay):
    """One lab's run of the replayed seed, indexed for per-frame questions (data.Replay's), with what rounds 5 and
    later add: where each booking ran (the new lab's own station, BYU's existing equipment, or a partner), the
    build-out's dates, counters as the round defines them, the run's own spend curve, and why a campaign's best new
    alloy is not moving (flat())."""

    def __init__(self, which: str = "auto"):
        I = info()
        self.which = which
        self.part_info = P = I[which]
        self.path = HERE / P["events"]
        self.placeholder = False
        js = D._load_json(self.path)
        m0 = js.get("meta", {})
        cfg = m0.get("cfg") if isinstance(m0.get("cfg"), dict) else {}
        self.meta = dict(cfg, **{k: v for k, v in m0.items() if k != "cfg"})
        self.horizon_days = float(self.meta.get("horizon_days", I.get("horizon_days", 730)))
        self.horizon_h = self.horizon_days * HPD
        st_all = js.get("stations", {})
        self.designs = {c: {str(k): v for k, v in d.items()} for c, d in js.get("designs", {}).items()}
        evs = js.get("events", [])
        self.helper_h = {h: sum(e["t1_h"] - e["t0_h"] for e in evs if e.get("station") == h) for h in HELPERS}
        evs = [e for e in evs if e.get("station") not in HELPERS]
        self.ev = evs
        self.t0 = np.array([e["t0_h"] for e in evs], float)
        self.t1 = np.array([max(e["t1_h"], e["t0_h"] + 1e-3) for e in evs], float)
        self.camp = np.array([e.get("campaign") or "" for e in evs])
        full = [e.get("station") or "" for e in evs]
        self.station_full = np.array(full)
        self.station = np.array([s.split("@")[0] for s in full])           # the station kind, wherever it ran
        # where: "lab" the new lab's own station (<kind>@vcl), "partner" an outside facility, "own" BYU's existing
        # equipment and core facilities (and the simulations on the HPC)
        self.where = np.array(["lab" if "@" in s else ("partner" if st_all.get(s, {}).get("external") else "own")
                               for s in full])
        self.stations = {}
        for k, v in st_all.items():
            if k in HELPERS:
                continue
            self.stations.setdefault(k.split("@")[0], v)
        self.stations_full = {k: v for k, v in st_all.items() if k not in HELPERS}
        self.what = [e.get("what") for e in evs]
        self.design = [None if e.get("design") is None else str(e.get("design")) for e in evs]
        self.node = np.array([D.node_of(c, e.get("node"), _what(e.get("what"))) or "" for c, e in zip(self.camp, evs)])
        self.results = sorted(js.get("results", []), key=lambda r: r.get("t_h", 0.0))
        self.facility = "vertical_lab" if which == "auto" else "conventional"
        self.policy = str(self.meta.get("policy", I["policy"]))
        self.seed = self.meta.get("seed", I["seed"])
        self.curves, self.spend, self.budget = {}, {}, {}
        for c in CAMPS:
            cc = P["campaigns"][c]
            self.curves[c] = np.array(cc["curve_new"] or [], float).reshape(-1, 3)      # (day, spent, best new)
            self.spend[c] = np.array(cc["spend_curve"] or [[0.0, 0.0]], float).reshape(-1, 2)
            self.budget[c] = float(cc["budget"] or 0.0)
        self.curves_all = {c: np.array(v, float).reshape(-1, 3) for c, v in js.get("curves", {}).items()}
        rs = self.results

        def times(c, types):
            return sorted(r["t_h"] for r in rs if r.get("campaign") == c and r.get("type") in types)

        def firsts(c, types):
            seen = {}
            for r in rs:
                if r.get("campaign") == c and r.get("type") in types and r.get("design") is not None:
                    seen.setdefault(r["design"], r["t_h"])
            return sorted(seen.values())
        # powder lots: the log has a "lot" result for every atomization that came back, and a second charge atomized
        # into a lot it already has (copper tops lots up) is a result too. The row counts lots, so the series is the
        # one of the two (every result, or each design's first) that ends on the row's own count; check_counters()
        # reports it when neither does.
        self._lots = {}
        for c in CAMPS:
            every, first = times(c, ("lot",)), firsts(c, ("lot",))
            want = (P["campaigns"][c].get("counters") or {}).get("lots_made")
            self._lots[c] = first if (want is not None and len(first) == want and len(every) != want) else every
        self._made = {c: firsts(c, ("lot", "deposit")) for c in CAMPS}                  # alloys with a lot or a blend
        self._built = {c: firsts(c, ("build", "deposit")) for c in CAMPS}               # alloys printed or deposited
        self._tested = {c: firsts(c, ("demonstrated",)) for c in CAMPS}                 # alloys through the chain
        self._sims = {c: times(c, ("sim",)) for c in CAMPS}
        self._span = {c: {} for c in CAMPS}
        for i in range(len(evs)):
            c, d = self.camp[i], self.design[i]
            if self.station[i] == "hpc":
                continue
            if d is not None and c in self._span:
                a, b = self._span[c].get(d, (self.t0[i], self.t1[i]))
                self._span[c][d] = (min(a, self.t0[i]), max(b, self.t1[i]))
        self._designs_t = {c: [] for c in CAMPS}
        rr = js.get(f"round{ROUND}") or js.get("round5") or {}
        self.daily = {c: {int(k): v for k, v in (rr.get("daily") or {}).get(c, {}).items()} for c in CAMPS}
        self.stockouts = {c: sorted((float(a), list(b), float(w)) for a, b, w in
                                    ((rr.get("stock") or {}).get(c) or {}).get("stockouts", [])) for c in CAMPS}
        self.imm = {c: sorted((float(self.t0[i]), float(self.t1[i])) for i in range(len(evs))
                              if self.camp[i] == c and self.station[i] == "immersion") for c in CAMPS}
        self.room_h = P.get("room_h")
        self.cell_h = P.get("cell_h")
        self.build = P.get("build") or {}
        self.station_online = {k.split("@")[0]: float(v) for k, v in (P.get("station_online") or {}).items()}
        self._improve = {}
        for c in CAMPS:
            best, out = 0.0, []
            for day, _, b in self.curves[c]:
                if b > best + 1e-9:
                    out.append(float(day))
                    best = b
            self._improve[c] = out

    # ---------------------------------------------------------------------------------------- counters and money
    def counts(self, campaign: str, t_h: float) -> dict:
        """The round's counters at lab hour t_h (round5.counters' definitions): designed on the HPC stream (linear to
        the run's own total), powder lots made, alloys made, alloys printed or deposited, alloys tested through the
        full chain."""
        br = bisect.bisect_right
        hp = self.part_info["campaigns"][campaign]["hpc"]
        ev = float(hp.get("evaluated") or 0.0)
        return dict(designed=ev * min(1.0, max(0.0, t_h / self.horizon_h)),
                    lots=br(self._lots[campaign], t_h), made=br(self._made[campaign], t_h),
                    built=br(self._built[campaign], t_h), tested=br(self._tested[campaign], t_h),
                    sims=br(self._sims[campaign], t_h))

    def check_counters(self) -> list:
        """The counters at the end of the run against the row's own (round5.counters): [(campaign, name, ours, row)]
        for any that differ."""
        bad = []
        for c in CAMPS:
            mine = self.counts(c, self.horizon_h + 1.0)
            row = self.part_info["campaigns"][c]["counters"]
            for a, b in (("lots", "lots_made"), ("made", "alloys_made"), ("built", "alloys_printed"),
                         ("tested", "alloys_tested")):
                if b in row and mine[a] != row[b]:
                    bad.append((c, b, mine[a], row[b]))
        return bad

    def spent_at(self, campaign: str, t_h: float) -> float:
        sc = self.spend[campaign]
        return float(np.interp(t_h / HPD, sc[:, 0], sc[:, 1]))

    def spend_upto(self, campaign: str, t_h: float) -> np.ndarray:
        """The run's own (day, cumulative spend) points up to t_h, ending at t_h."""
        sc = self.spend[campaign]
        d = t_h / HPD
        m = sc[:, 0] <= d
        pts = sc[m]
        return np.vstack([pts, [[d, self.spent_at(campaign, t_h)]]]) if len(pts) else np.array([[0.0, 0.0]])

    # ---------------------------------------------------------------------------------------- the build-out
    def online(self, station: str) -> float:
        """Lab hour from which the new lab's own station of this kind is online (inf: never, or not the new lab)."""
        return float(self.station_online.get(station, float("inf")))

    def milestones(self) -> list:
        """[(lab hour, key, words)] of the build-out, in order: the money, the space, each station, the cell."""
        out = [(0.0, "money", "The money arrives; every station is ordered")]
        if self.room_h is not None and self.which == "auto":
            out.append((float(self.room_h), "room", "The space is ready: installation starts"))
        for k, h in sorted(self.station_online.items(), key=lambda kv: kv[1]):
            out.append((float(h), f"st:{k}", STATION_WORDS.get(k, k) + " online"))
        if self.cell_h is not None:
            out.append((float(self.cell_h), "cell", "The cell is integrated: robots run the stations round the clock"))
        return sorted(out)

    # ---------------------------------------------------------------------------------------- why it is flat
    def flat(self, campaign: str, t_h: float, min_days: float = 21.0) -> dict | None:
        """When the campaign's best new alloy has not moved for a while and will not soon: since when, until when,
        and why, from the run's own idle-cause report (the idle stretches at its pacing stations and their causes),
        its stock log and its bookings. None while the curve is moving."""
        d = t_h / HPD
        imp = self._improve[campaign]
        i = bisect.bisect_right(imp, d)
        since = imp[i - 1] if i else 0.0
        until = imp[i] if i < len(imp) else self.horizon_days
        if until - since < min_days or d - since < 3.0:
            return None
        return dict(since=since, until=until, reasons=self.reasons(campaign, d), first=(i == 0))

    def reasons(self, campaign: str, d: float) -> list:
        """What holds the campaign on day d, most telling first: [(key, words)]."""
        P = self.part_info["campaigns"][campaign]
        out = []
        idle = P.get("idle") or {}
        causes = []
        for grp in ("fab", "atomizer"):
            for x in idle.get(grp, []):
                if x["start_d"] <= d < x["end_d"]:
                    causes.append((grp, x["cause"]))
        dl = self.daily[campaign].get(int(d))
        left = dl["budget_left"] if dl else None
        budget = self.budget[campaign]
        money = any(c == "money" for _, c in causes) or (left is not None and budget and left < 0.02 * budget)
        if money:
            out.append(("money", f"the money is spent ({_usd(self.spent_at(campaign, d * HPD))} of {_usd(budget)})"))
        fabw = "a printer" if campaign == "flaime_al" else "a DED slot"
        for grp, c in causes:
            if c == "money":
                continue
            if c == "capacity":
                out.append(("queue", f"the queue for {fabw if grp == 'fab' else 'the atomizer'}"))
            elif c == "WIP limit":
                out.append(("queue", f"lots already waiting for {fabw}"))
            elif c == "sign-off":
                out.append(("signoff", "a sign-off"))
            elif c == "decision time":
                out.append(("decision", "results waiting for a person's decision"))
            elif c == "spending plan":
                out.append(("money", "the last money, held for the partners' slots"))
            elif c.startswith("policy waiting"):
                out.append(("results", "results still in flight"))
        if campaign == "onr_cu":
            run = [(a, b) for a, b in self.imm[campaign] if a <= d * HPD < b]
            if run:
                a, b = max(run, key=lambda ab: ab[0])
                out.append(("immersion", f"a {round((b - a) / HPD):.0f}-day immersion (day "
                                         f"{int((d * HPD - a) / HPD) + 1})"))
        so = [(a, items, w) for a, items, w in self.stockouts[campaign] if a <= d < a + w]
        if so and not money:
            a, items, w = max(so, key=lambda x: x[0] + x[2])
            names = []
            for it in items:
                nm = item_words(it)
                if nm not in names:
                    names.append(nm)
            out.append(("stock", f"stock: {', '.join(names[:2])}{' and more' if len(names) > 2 else ''} "
                                 f"(due day {a + w:.0f})"))
        seen, uniq = set(), []
        for k, wds in out:
            if wds not in seen and not (k == "queue" and "queue" in {u[0] for u in uniq}):
                uniq.append((k, wds))
                seen.add(wds)
        return uniq


def _what(w):
    """An event's step, without the '(side)' tag round 5 gives booked-after steps."""
    return None if w is None else str(w).replace(" (side)", "")


def _usd(v: float) -> str:
    return f"${v / 1e3:.0f}k" if abs(v) >= 1e3 else f"${v:.0f}"


STATION_WORDS = {"utah_midi": "LPBF (Aconity MIDI)", "utah_mxlab": "DED (InssTek MX-Lab)", "edm": "Wire EDM",
                 "byu_sem": "SEM + EDS", "byu_icpms": "ICP-MS", "density": "Density and cracks (VHX)",
                 "tensile": "Tensile frames", "tensile_hot": "Hot tensile", "sieve": "Sieving cell",
                 "psd": "Particle size", "doser": "Multi-doser", "shop": "Machining cell", "xrd": "XRD", "xrf": "XRF",
                 "prep": "Metallography", "hardness": "Micro-Vickers", "nanoindent": "Nanoindenter", "pip": "PIP",
                 "furnace": "Furnaces"}


if __name__ == "__main__":
    out = prepare()
    a = out["auto"]
    print(f"round {ROUND}: {out['arm']} seed {out['seed']} of {out['n_seeds']} "
          f"({'the' if out['is_median_seed'] else 'NOT the'} arm's median seed for both campaigns); "
          f"conventional: {out['conv_arm']}")
    for nm in ("auto", "conv"):
        for c in CAMPS:
            cc = out[nm]["campaigns"][c]
            print(f"  {nm:5s} {c:10s} T1 {cc['days']['T1']}  T2 {cc['days']['T2']}  best {cc['best_new']:.3f}  "
                  f"spent {cc['spent']:.0f} of {cc['budget']:.0f}")
    for nm in ("auto", "conv"):
        bad = Replay5(nm).check_counters()
        print(f"  {nm}: counters from the event log {'match the row' if not bad else 'DIFFER: ' + str(bad)}")
