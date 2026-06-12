"""Parse the alloy-discovery answer into a clean alloys.json list.

Looks for the trailing ```json fenced code block in artifacts/alloy_discovery.md
(emitted by submit_alloy_discovery.py's query) and writes it to alloys.json as a
list of {"designation", "family", "nominal_composition"} objects. De-duplicates by
designation and caps at 100 entries.
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
DISCOVERY = HERE / "artifacts" / "alloy_discovery.md"
ALLOYS = HERE / "alloys.json"

JSON_BLOCK = re.compile(r"^```json[ \t]*\n(.*?)^```", re.DOTALL | re.MULTILINE)


def extract_alloys(text: str) -> list[dict]:
    blocks = JSON_BLOCK.findall(text)
    if not blocks:
        raise SystemExit("No ```json block found in alloy_discovery.md")
    # Use the last JSON block (the query asks for it at the very end).
    data = json.loads(blocks[-1].strip())
    if not isinstance(data, list):
        raise SystemExit("JSON block is not a list")

    seen: set[str] = set()
    out: list[dict] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        desig = str(item.get("designation", "")).strip()
        if not desig or desig.lower() in seen:
            continue
        seen.add(desig.lower())
        out.append(
            {
                "designation": desig,
                "family": str(item.get("family", "")).strip(),
                "nominal_composition": str(item.get("nominal_composition", "")).strip(),
            }
        )
        if len(out) >= 100:
            break
    return out


def main() -> None:
    if not DISCOVERY.exists():
        raise SystemExit(f"{DISCOVERY} not found; run fetch_alloy_discovery.py first")
    alloys = extract_alloys(DISCOVERY.read_text())
    ALLOYS.write_text(json.dumps(alloys, indent=2))
    print(f"Wrote {ALLOYS} with {len(alloys)} alloys")
    for a in alloys:
        print(f"  - {a['designation']}: {a['nominal_composition']}")


if __name__ == "__main__":
    main()
