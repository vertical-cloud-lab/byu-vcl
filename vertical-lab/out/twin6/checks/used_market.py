"""Round 6, item 2: what the used-equipment survey changes in the automated lab's build-out (a check, not rows).

    cd vertical-lab && TWIN_PIN=portable python out/twin6/checks/used_market.py      # writes used_market.md

For each of the grid's 16 seeds, the parallel plan's build-out (``round6.build_schedule6``) with round 5's stand-ins
(no market file) and with the survey (``out/twin6/market/summary.csv``): which stations are bought used, the day the
cell is integrated, the day the last station is online, and the capital paid. Then each station the lab buys, with
the survey's verdict on its used market and the expected days a used unit saves (round 5's rule buys used at 14).
"""
import os
import statistics as st
import sys
from pathlib import Path

VL = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(VL))
os.environ.setdefault("TWIN_PIN", "portable")
from twin import round4 as R4  # noqa: E402
from twin import round6 as R6  # noqa: E402
from twin import econ as E  # noqa: E402

HERE = Path(__file__).resolve().parent
H = 24.0


def main():
    mk = R6.load_market()
    items = {it.key: it for it in E.items("vertical_lab")}
    L = ["# Round 6: the used-equipment survey in the automated lab's build-out", "",
         "Made by `python out/twin6/checks/used_market.py`, from `out/twin6/market/summary.csv` (sha256 "
         f"`{R6.market_sha256()[:16]}…`) and the engine at this commit. The parallel plan, the grid's 16 seeds. "
         "Everything is simulated.", "",
         "| Seed | Bought used, round 5's stand-ins | Bought used, the survey | Cell integrated (day), stand-ins / survey "
         "| Last station online (day) | Capital paid ($M) |", "|---|---|---|---|---|---|"]
    agg = dict(cell5=[], cell6=[], full5=[], full6=[], cap5=[], cap6=[], n5=[], n6=[])
    for seed in range(16):
        a = R6.build_schedule6(seed, "parallel", market={})
        b = R6.build_schedule6(seed, "parallel", market=mk)
        cap = lambda s: sum(u for _, u, _ in s["payments"]) / 1e6
        u5 = sorted(a["used"]) or ["-"]
        u6 = [f"{k}{' (faulty)' if v['fault'] else ''}" for k, v in sorted(b["used"].items())] or ["-"]
        L.append(f"| {seed} | {', '.join(u5)} | {', '.join(u6)} | {a['cell_h'] / H:.0f} / {b['cell_h'] / H:.0f} | "
                 f"{a['full_h'] / H:.0f} / {b['full_h'] / H:.0f} | {cap(a):.2f} / {cap(b):.2f} |")
        agg["cell5"].append(a["cell_h"] / H); agg["cell6"].append(b["cell_h"] / H)
        agg["full5"].append(a["full_h"] / H); agg["full6"].append(b["full_h"] / H)
        agg["cap5"].append(cap(a)); agg["cap6"].append(cap(b))
        agg["n5"].append(len(a["used"])); agg["n6"].append(len(b["used"]))
    m = {k: st.median(v) for k, v in agg.items()}
    L += ["", f"Medians over the 16 seeds, stand-ins against the survey: stations bought used {m['n5']:.0f} against "
              f"{m['n6']:.0f}; cell integrated on day {m['cell5']:.0f} against {m['cell6']:.0f}; last station online "
              f"on day {m['full5']:.0f} against {m['full6']:.0f}; capital ${m['cap5']:.2f}M against ${m['cap6']:.2f}M.",
          "", "## Each station the automated lab buys", "",
          "The survey's verdict (`market`: `yes` a market the lab would buy from; `thin` too few listings to count on; "
          "`none` no listing of the model or its line; `n/a (new only)` not surveyed: commodity or building work), "
          "and round 5's rule with the survey's numbers. A station bought partly used (`yes (parts)`) is on site when "
          "its new parts are, so its lead is theirs.", "",
          "| Station | What | New lead (weeks) | Market | Used OK | Listings | Used lead (weeks, after the PO) | Price "
          "(fraction of new) | Fault risk | Expected days saved | Bought used |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for k in sorted(R4.BUILD):
        it = items.get(k)
        if it is None or k in ("cubxl", "services") or it.kind == "owned":
            continue
        p = R6.used_params(k, mk)
        r = R6.used_rule6(k, p)
        nl = p.get("n_listings")
        L.append(f"| {k} | {it.name.split(' (')[0]} | {R4.BUILD[k][0]:g} | {p['market']} | {'yes' if p['ok'] else 'no'} "
                 f"| {'' if nl is None else f'{nl:.0f}'} | {p['lead_w']:g} | {p['price_frac']:.2f} | "
                 f"{p['p_fault']:.2f} | {r['expected_days_saved']:g} | {'**yes**' if r['ok'] else 'no'} |")
    none = R6.no_used_market(mk)
    L += ["", "**No used market the lab would buy from** (`round6.no_used_market()`): "
          + "; ".join(f"{k} ({v['market']})" for k, v in none.items()) + "."]
    (HERE / "used_market.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
