#!/usr/bin/env python3
"""Flatten Bambu Studio system presets into the self-contained JSON the CLI needs.

The CLI's --load-settings / --load-filaments read one JSON file each and do not
follow "inherits" or "include", so a system preset loaded straight from
resources/profiles/BBL/ silently falls back to built-in defaults for every key
its parents set. This walks the chain (parents first, then included G-code
templates, then the preset's own keys) and writes one complete file per preset.

    python flatten_presets.py <BambuStudio resources dir> <out dir>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PRESETS = {
    "machine": "Bambu Lab A1 mini 0.4 nozzle",
    "process": "0.20mm Standard @BBL A1M",
    "filament": "Bambu PLA Basic @BBL A1M",
}


def index(folder: Path) -> dict[str, Path]:
    out = {}
    for f in folder.rglob("*.json"):
        name = json.loads(f.read_text()).get("name")
        if name:
            out[name] = f
    return out


def resolve(name: str, files: dict[str, Path]) -> dict:
    own = json.loads(files[name].read_text())
    merged = resolve(own["inherits"], files) if own.get("inherits") else {}
    for inc in own.get("include", []):
        merged.update({k: v for k, v in resolve(inc, files).items()
                       if k not in ("name", "instantiation")})
    merged.update(own)
    return merged


def flatten(kind: str, name: str, profiles: Path) -> dict:
    cfg = resolve(name, index(profiles / kind))
    for k in ("inherits", "include", "instantiation"):
        cfg.pop(k, None)
    cfg.update({"name": name, "from": "system", "type": kind})
    return cfg


def main() -> None:
    profiles = Path(sys.argv[1]) / "profiles" / "BBL"
    out = Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    for kind, name in PRESETS.items():
        cfg = flatten(kind, name, profiles)
        (out / f"{kind}.json").write_text(json.dumps(cfg, indent=2) + "\n")
        print(f"{kind:8s} {name}: {len(cfg)} keys")


if __name__ == "__main__":
    main()
