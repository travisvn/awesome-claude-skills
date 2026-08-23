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
from basemap import (load_segment_labels, fixtures_near_segment,  # noqa: E402
                     fixtures_in_segment, segment_patches)
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

# TE5.1's bands are 32 m wide, so patch reconstruction must find the centreline
# lights running down the middle of them. A single-line buffer finds none - that
# regression is the whole reason segment_patches exists, so assert the difference.
pat, strips = segment_patches("TE5.1")
check("TE5.1 reconstructed patches", len(pat), 3)
inside = fixtures_in_segment("TE5.1", assets_only=True)
n_tcl = int((inside["asset_type"] == "Taxiway centreline light").sum())
ok = n_tcl >= 50 and len(inside) > len(near)
print(f"  [{'PASS' if ok else 'FAIL'}] TE5.1 centreline lights inside patches"
      f"{'':<7} {n_tcl:>9,} (buffer method finds "
      f"{int((near['asset_type'] == 'Taxiway centreline light').sum())})")
if not ok:
    fails.append(f"fixtures_in_segment(TE5.1) found {n_tcl} centreline lights and "
                 f"{len(inside)} assets vs {len(near)} for the buffer method - patch "
                 f"reconstruction is no longer capturing band interiors")
if "basis" not in inside.columns:
    fails.append("fixtures_in_segment lost the `basis` column - the register needs it "
                 "to record why each asset was selected")
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

print("\ndrawing output")
import tempfile  # noqa: E402
try:
    from drawing import sketch, write_dxf, load_title_block, PAPER, MARGIN, _pick_scale
    from basemap import segment_patches as _sp

    pats, strs = _sp("TE5.1")
    with tempfile.TemporaryDirectory() as td:
        files = sketch(inside, patches=pats, strips=strs,
                       out=os.path.join(td, "t.pdf"),
                       drawing_title="smoke test", paper="A3")
        both = sorted(os.path.splitext(f)[1] for f in files)
        check("sketch writes PDF + PNG", len(files), 2)
        if both != [".pdf", ".png"]:
            fails.append(f"sketch wrote {both}, expected ['.pdf', '.png']")
        for f in files:
            if os.path.getsize(f) < 20_000:
                fails.append(f"{os.path.basename(f)} is {os.path.getsize(f)} bytes - "
                             "suspiciously small for a full sheet")
        dxf = write_dxf(os.path.join(td, "t.dxf"), fixtures=inside, patches=pats,
                        strips=strs)
        raw = open(dxf).read().split("\n")
        codes = [(raw[i].strip(), raw[i + 1]) for i in range(0, len(raw) - 1, 2)]
        npoint = sum(1 for c, v in codes if c == "0" and v.strip() == "POINT")
        npoly = sum(1 for c, v in codes if c == "0" and v.strip() == "POLYLINE")
        nseq = sum(1 for c, v in codes if c == "0" and v.strip() == "SEQEND")
        check("DXF POINT per selected fixture", npoint, len(inside))
        check("DXF POLYLINE/SEQEND balanced", npoly, nseq)
        body = open(dxf).read()
        for token, why in (("NOT UTM", "local-grid disclaimer"),
                           ("RECONSTRUCTED", "reconstructed-patch warning")):
            ok = token in body
            print(f"  [{'PASS' if ok else 'FAIL'}] DXF carries {why:<34}")
            if not ok:
                fails.append(f"DXF is missing the {why} - the warning must travel "
                             f"with the geometry, not just the covering email")

    # The scale must come from the drafting series, and from the real axes box.
    pw, ph = PAPER["A3"]
    w = pw * (MARGIN["right"] - MARGIN["left"])
    h = ph * (MARGIN["top"] - MARGIN["bottom"])
    s = _pick_scale([(0, 0, 450, 450)], w, h)
    check("A3 scale for a 450 m extent", s, 2500)
    tb = load_title_block()
    ok = all(k in tb for k in ("project", "drawing_no", "rev", "status"))
    print(f"  [{'PASS' if ok else 'FAIL'}] titleblock.json has the expected fields")
    if not ok:
        fails.append("titleblock.json is missing expected fields")
except ImportError as e:
    notes.append(f"drawing checks skipped - {e} (matplotlib not installed)")

print("\n" + "=" * 72)
for n in notes:
    print("NOTE: " + n)
if fails:
    print(f"FAILED ({len(fails)}):")
    for f in fails:
        print("  - " + f)
    sys.exit(1)
print("ALL CHECKS PASSED")
