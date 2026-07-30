#!/usr/bin/env python3
"""
Regression guard for the extracted assets.

    python smoke_test.py

Run this after every `rebuild.py`. It exists because the failure that motivated it
was silent: v1 discarded 466 km of duct geometry and 143 km more would have gone
missing from the naive fix, and in both cases the output looked entirely plausible.
Counts that look reasonable are not the same as counts that reconcile.

Every check compares the assets against either a figure documented in SKILL.md or
an independent census taken from the layer index. A failure here means either the
source DXF revision genuinely changed - in which case update SKILL.md and re-issue
any coordinate already sent out - or the extraction broke.
"""
from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd  # noqa: E402

from basemap import (load_fixtures, load_segments, load_routes,  # noqa: E402
                     load_layer_index, wkt_coords)

# Figures documented in SKILL.md for the current DXF revision.
EXPECT = {
    "fixtures": 33_720,
    "fixtures_assets_only": 33_424,
    "seg_geometry": 2_428,
    "seg_closed": 10,
    "seg_labels": 2_207,
    "routes": 49_505,
    "layers": 2_533,
}
GEOM_ENTS = {"LWPOLYLINE", "LINE", "ARC", "SPLINE", "POLYLINE", "CIRCLE", "ELLIPSE"}
# Generous envelope around the fixture extent. AGL and civil geometry must sit inside.
SITE_ENV = (-9_000, 50_000, 11_000, 60_000)

fails: list[str] = []
notes: list[str] = []


def check(name, got, want, tol=0):
    ok = abs(got - want) <= tol
    print(f"  [{'PASS' if ok else 'FAIL'}] {name:<44} {got:>9,}  expected {want:>9,}"
          + (f" (+/-{tol})" if tol else ""))
    if not ok:
        fails.append(f"{name}: got {got:,}, expected {want:,}")


print("counts vs SKILL.md")
fx = load_fixtures()
check("fixtures", len(fx), EXPECT["fixtures"])
check("fixtures (assets_only)", len(load_fixtures(assets_only=True)),
      EXPECT["fixtures_assets_only"])
seg = load_segments()
check("segmentation features", len(seg), EXPECT["seg_geometry"])
check("segmentation closed polygons", int((seg["closed"] == 1).sum()),
      EXPECT["seg_closed"])
check("segmentation labels resolved", int(seg["label"].notna().sum()),
      EXPECT["seg_geometry"], tol=2)
rt = load_routes(with_length=False)
check("civil routes", len(rt), EXPECT["routes"])
idx = load_layer_index()
check("layers indexed", len(idx), EXPECT["layers"])

print("\nsegmentation merge cardinality")
raw = pd.read_csv(os.path.join(os.path.dirname(__file__), "..", "assets",
                               "seg_geometry.csv"))
check("load_segments rows == seg_geometry.csv rows", len(seg), len(raw))

print("\nroute reconciliation vs layer-index census")
census = {}
for v in idx.values():
    for t, n in v["types"].items():
        if t in GEOM_ENTS:
            census[t] = census.get(t, 0) + n
emitted = rt.groupby("etype").size().to_dict()
# 3,375 geometry entities sit outside TOP_XREFS in block-local coordinates and are
# deliberately not emitted. Reconciliation therefore allows emitted <= census only.
for t in sorted(census):
    e, c = emitted.get(t, 0), census[t]
    ok = e <= c + 2
    print(f"  [{'PASS' if ok else 'FAIL'}] {t:<20} emitted {e:>7,}  census {c:>7,}")
    if not ok:
        fails.append(f"{t}: emitted {e:,} exceeds census {c:,}")
if emitted.get("LWPOLYLINE", 0) != census.get("LWPOLYLINE", 0):
    notes.append("LWPOLYLINE reconciles to within 2 of the census - 2 entities in the "
                 "drawing carry no code-8 layer record. Known, 0.007%.")

print("\ncoordinate sanity")
cv = rt[rt["leaf"].str.match(r"^(CV|EL|ADB)", case=False, na=False)]
off = 0
for w in cv["wkt"]:
    if any(not (SITE_ENV[0] <= x <= SITE_ENV[2] and SITE_ENV[1] <= y <= SITE_ENV[3])
           for x, y in wkt_coords(w)):
        off += 1
check("CV/EL/ADB routes outside site envelope", off, 0)
duct = rt[rt["leaf"].str.contains(r"DUCT|CONDUIT|SAWCUT|SECONDARY|SEC[_ ]",
                                  case=False, regex=True, na=False)]
print(f"  [INFO] duct/conduit/secondary features: {len(duct):,}")
if len(duct) < 15_000:
    fails.append(f"duct feature count collapsed to {len(duct):,} - the v1 failure "
                 f"mode. Check the entity filter in rebuild.py.")

print("\nbbox sanity (layer_index must be geometry-derived, not raw group codes)")
pat = re.compile(r"DUCT|CONDUIT|SAWCUT|SECONDARY|SEC[_ ]", re.I)
bad = [k for k, v in idx.items()
       if pat.search(k.split("$")[-1]) and v["bbox"]
       and (v["bbox"][1] < 40_000 or v["bbox"][3] > 70_000)]
check("duct layers with impossible bbox", len(bad), 0)

print("\nsegment labels and helpers")
from basemap import load_segment_labels, fixtures_near_segment  # noqa: E402
lbl = load_segment_labels()
dirty = int(lbl["label"].astype(str).str.contains(r"\\|[{}]", regex=True,
                                                  na=False).sum())
check("labels still carrying MTEXT codes", dirty, 0)
near = fixtures_near_segment("TE5.1", buffer=15, assets_only=True)
ok = len(near) > 0 and "dist_m" in near.columns
print(f"  [{'PASS' if ok else 'FAIL'}] fixtures_near_segment(TE5.1)"
      f"{'':<21} {len(near):>9,} rows")
if not ok:
    fails.append("fixtures_near_segment(TE5.1) returned no rows")
z3 = pd.read_csv(os.path.join(os.path.dirname(__file__), "..", "assets",
                              "seg_geometry.csv"))
n_z3 = int((z3["xref"] == "SEGMENTATION - ZONE 3").sum())
if n_z3 == 0:
    notes.append("SEGMENTATION - ZONE 3 still absent from seg_geometry.csv - "
                 "expected until the first rebuild from the source DXF with the "
                 "Zone 3 capture fix. After that rebuild, update EXPECT and the "
                 "SKILL.md Known limits entry.")
else:
    notes.append(f"SEGMENTATION - ZONE 3 now contributes {n_z3:,} features - "
                 "update EXPECT and remove the Zone 3 gap entry from SKILL.md.")

print("\n" + "=" * 72)
for n in notes:
    print("NOTE: " + n)
if fails:
    print(f"FAILED ({len(fails)}):")
    for f in fails:
        print("  - " + f)
    sys.exit(1)
print("ALL CHECKS PASSED")
