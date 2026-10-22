"""Evaluate a FeatureScript lambda in the Part Studio and print a plain-Python version of the result (1 API call)."""
import json
import sys

from client import Onshape


def plain(v):
    t = v.get("btType", "") if isinstance(v, dict) else ""
    if "BTFSValueMap" in t:
        return {plain(e["key"]): plain(e["value"]) for e in v["value"]}
    if "BTFSValueArray" in t:
        return [plain(x) for x in v["value"]]
    if "BTFSValueWithUnits" in t:
        return round(v["value"] * (1000 if v.get("unitToPower") == {"METER": 1} else 1), 4)
    if isinstance(v, dict) and "value" in v:
        return v["value"]
    return v


def evaluate(script: str):
    api = Onshape()
    st = json.load(open("state.json"))
    r = api.call("POST", f"/partstudios/d/{st['did']}/w/{st['wid']}/e/{st['elements']['Viewport cameras']['id']}/featurescript",
                 json={"script": script, "queries": {}})
    return plain(r.get("result") or {}), r.get("notices"), r.get("console")


if __name__ == "__main__":
    res, notices, console = evaluate(open(sys.argv[1]).read())
    print(json.dumps(res, indent=1)[:12000])
    if notices:
        print("NOTICES", json.dumps(notices)[:3000])
    if console:
        print("CONSOLE", console[:3000])
