"""Sum bom.csv into the totals the README quotes. Writes totals.json.

Rows with no price (quotes, McMaster pages the runner could not read) are listed, not guessed.
The three potentiostat options are summed separately, since only one is bought.

    python bom_totals.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OPTION = {"B23": 1, "B24": 1, "B28": 1, "B26": 1, "B25": 2, "B27": 3}  # B26 (dummy cell) goes with options 1 and 3


def main():
    rows = list(csv.DictReader((HERE / "bom.csv").open()))
    buy = [r for r in rows if r["kind"] == "buy"]
    price = lambda r: float(r["ext_price_usd"]) if r["ext_price_usd"] else None
    out = {"printed_parts": sum(1 for r in rows if r["kind"] == "print"),
           "buy_rows": len(buy), "unpriced": [f"{r['id']} {r['item'][:50]}" for r in buy if price(r) is None]}

    def total(sel):
        return round(sum(price(r) or 0 for r in buy if sel(r)), 2)

    core = lambda r: r["id"] not in OPTION and r["status"] not in ("optional", "fallback", "only if needed")
    out["core"] = {
        "both_hardware_and_consumables_excl_tips": total(lambda r: core(r) and r["for"] == "both" and r["group"] not in ("electrodes",) and r["id"] != "B35"),
        "tips_if_none_on_hand": total(lambda r: r["id"] == "B35"),
        "electrodes_both": total(lambda r: core(r) and r["for"] == "both" and r["group"] == "electrodes"),
        "aluminium_only": total(lambda r: core(r) and r["for"] == "Al"),
        "copper_only": total(lambda r: core(r) and r["for"] == "Cu"),
        "copper_optional": total(lambda r: r["for"] == "Cu" and r["status"] in ("optional", "only if needed")),
    }
    out["potentiostat_options"] = {
        "1_emstat_pico_module_with_box_and_dummy_cell": total(lambda r: r["id"] in ("B23", "B24", "B26")),
        "1_plus_usb_serial_adapter": total(lambda r: r["id"] in ("B23", "B24", "B26", "B28")),
        "2_emstat_pico_dev_kit": total(lambda r: r["id"] == "B25"),
        "3_mystat_parts_and_dummy_cell": total(lambda r: r["id"] in ("B27", "B26")),
    }
    c = out["core"]
    out["aluminium_start"] = {"phase_A_shakedown_borrowed_potentiostat": round(c["both_hardware_and_consumables_excl_tips"] + c["aluminium_only"], 2),
                              "plus_electrodes_and_option_1": round(c["both_hardware_and_consumables_excl_tips"] + c["aluminium_only"] + c["electrodes_both"]
                                                                    + out["potentiostat_options"]["1_emstat_pico_module_with_box_and_dummy_cell"], 2)}
    (HERE / "totals.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
