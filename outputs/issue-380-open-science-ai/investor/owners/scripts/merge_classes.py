#!/usr/bin/env python3
"""Merge the owner classifications into data/owner_classes.csv and check them against the input list.

Organization accounts were classified in four passes (one per quarter of the list, interleaved by rank) under the
rules in classify_rules.md; personal accounts are `individual` by rule. Manual corrections made on review are in
data/owner_class_overrides.csv (owner, cls, entity, parent, basis, judgment, reason) and are applied last, so each
correction stays visible. Run from owners/.
"""
import glob, sys
import pandas as pd

parts = sorted(glob.glob(sys.argv[1] if len(sys.argv) > 1 else "data/classify_passes/output_*.csv"))
c = pd.concat([pd.read_csv(p, dtype=str).assign(pass_file=p.split("/")[-1]) for p in parts], ignore_index=True)
c["owner"] = c["owner"].str.strip()
o = pd.read_csv("data/owners_github.csv")
orgs = set(o.loc[o.owner_type == "Organization", "owner"])
missing, extra = orgs - set(c.owner), set(c.owner) - orgs
dups = c[c.owner.duplicated(keep=False)]
print(f"rows {len(c)}, orgs {len(orgs)}, missing {len(missing)}, extra {len(extra)}, duplicated {dups.owner.nunique()}")
if missing:
    print("missing:", sorted(missing)[:50])
if extra:
    print("extra:", sorted(extra)[:50])
c = c[c.owner.isin(orgs)].drop_duplicates("owner", keep="first")
bad = c[~c.cls.isin(["core", "complement", "nonprofit", "academic", "government", "community", "unknown"])]
if len(bad):
    print("bad classes:", bad[["owner", "cls"]].to_string())
users = o.loc[o.owner_type == "User", ["owner"]].assign(cls="individual", basis="personal account (rule)",
                                                         judgment="0", crypto="0")
c = pd.concat([c, users], ignore_index=True)
c["override_reason"] = ""
try:
    ov = pd.read_csv("data/owner_class_overrides.csv", dtype=str)
    for _, r in ov.iterrows():
        m = c.owner == r.owner
        if not m.any():
            print("override for unknown owner", r.owner); continue
        for k in ["cls", "entity", "parent", "basis", "judgment", "crypto", "country"]:
            if k in ov.columns and isinstance(r.get(k), str) and r.get(k) != "":
                c.loc[m, k] = r[k]
        c.loc[m, "override_reason"] = r.reason
    print("overrides applied:", len(ov))
except FileNotFoundError:
    pass
c.to_csv("data/owner_classes.csv", index=False)
print(c.cls.value_counts().to_string())
