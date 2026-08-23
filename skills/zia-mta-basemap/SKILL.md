---
name: zia-mta-basemap
description: The canonical AGL, civil-duct and MTA segmentation basemap for Zayed International Airport (ZIA/OMAA), pre-extracted and indexed from the Z1-Z2-Z3 MTA Segmentation drawing. Use for any ZIA airfield geometry task: plotting or counting AGL assets (centreline, edge, stop bar, lead-in, holding, RGL/RRM, signs, light bases), tracing secondary cable, duct, ductbank, conduit or sawcut routes, locating handholes and transformer pits, working with MTA milling/overlay segmentation IDs, or producing AGL impact sketches, RFI location plans, defect overlays and work completion drawings. Trigger on casual asks like "plot the stop bars", "how many centreline lights here", "is there secondary cable under the patch", "AGL impact of the milling", or any segment ID like TE5.1 / K1.3 / 601.1 - and before reaching for the source DWG/DXF, because the data here is already parsed.
---

# ZIA MTA Basemap

Pre-extracted, queryable geometry from `Z1-Z2-Z3-MTA_SEGMENTATION.dxf` (549 MB raw,
66.6 M lines, 2,564 layers). The source file is **not** bundled — parsing it takes
about a minute and 500 MB+ of disk. Everything routinely needed has been extracted
into compact assets that load in under a second.

## What is in here

| Asset | Rows | Contents |
|---|---|---|
| `assets/agl_fixtures.csv.gz` | 33,720 | Every AGL / civil fixture as a point: xref, full layer path, leaf layer, block name, x, y, rotation |
| `assets/civil_routes.csv.gz` | 49,505 | Every linear feature as WKT: ducts, ductbanks, conduit, sawcut, secondary cable, pavement edges, roads. 1,878 km total, of which **466 km is duct / conduit / secondary** |
| `assets/seg_geometry.csv` | 2,428 | MTA segmentation geometry as WKT (2,418 division lines; 10 closed polygons) |
| `assets/seg_labels.csv` | 2,207 | Segmentation label points (`TE5.1`, `K1.3`, `601.1`, …) with x, y |
| `assets/layer_index.json.gz` | 2,533 | Per-layer entity counts, entity-type mix and geometry-derived bounding box |
| `assets/titleblock.json` | — | Title block fields for `drawing.sketch()`. Set project/client once; empty fields print `- not set -` |

## Read this before using any coordinate

**The grid is local, not UTM.** X ≈ −8,100 → 9,500, Y ≈ 52,200 → 58,300, units metres
(`$INSUNITS = 6`). The DXF carries **no GEODATA object** and no georeferencing of any
kind. Nothing in this skill can be labelled UTM, WGS84 or Nahrwan without an external
transform. See `references/coordinates.md`. Do not publish a coordinate from here to
ADA, Injaz or any contractor until the transform is applied and checked.

**But most questions don't need the transform.** Fixtures, duct routes and segmentation
all come from the same DXF and all twelve source xrefs insert at identity, so they share
one grid. "Is there 100 mm secondary under this patch", "which conduit crosses TE5.1",
"how far is this handhole from that duct run" are all answerable in local grid with no
transform and no survey control. The transform is only needed to join to an external
register in UTM. Do the analysis in local grid; transform last, if at all.

## Workflow

1. `python scripts/basemap.py --list-leaves` to see the fixture layers and counts.
2. Load and filter in Python. **Use the absolute skill path** — the snippet below fails
   if you `sys.path.insert` a relative `scripts`:

```python
import sys; sys.path.insert(0, "/mnt/skills/user/zia-mta-basemap/scripts")
from basemap import load_fixtures, load_segments, load_routes, segments_in_bbox, plot

BB   = (7297, 52769, 7737, 53209)
fx   = load_fixtures(bbox=BB, assets_only=True)
duct = load_routes(leaf_regex=r"DUCT|CONDUIT|SAWCUT|SECONDARY|SEC[_ ]", bbox=BB)
seg  = segments_in_bbox(load_segments(), BB)

print(duct.groupby("leaf").agg(n=("wkt", "size"), m=("length_m", "sum")))
plot(fx, seg, duct, out="agl_impact.png", bbox=BB,
     title="TWY … AGL + duct vs MTA segmentation")
```

Always pass `bbox=` to `plot()` when you clipped by bbox: membership is per-feature,
so one kept polyline with a distant vertex otherwise zooms the view out to the whole
airfield and the sketch is unreadable.

3. **Asked "which assets are affected by segment X"?** Use `fixtures_in_segment`:

```python
from basemap import fixtures_in_segment, segment_patches, segment_extent
fx = fixtures_in_segment("TE5.1", assets_only=True)   # adds basis + dist_m
patches, strips = segment_patches("TE5.1")            # for the sketch and the caveat
```

or in one shot from the CLI (counts by type + register CSV + shaded sketch):

```bash
python scripts/basemap.py --seg TE5.1 --assets-only \
    --out te51.png --csv-out te51_register.csv
```

**Why not a simple buffer.** A milling segment is drawn as *pairs* of division lines
bounding a band of pavement, and the assets that matter most — taxiway centreline
and lead-in lights — run down the **middle** of that band. TE5.1's bands are 32 m
wide, so a buffer small enough to defend around a single line (12–15 m) reports
**zero taxiway centreline lights for a taxiway milling job**. That is not a tight
answer, it is a wrong one, and it will read as authoritative in an RFI.
`segment_patches()` pairs each line with its mutually-nearest partner and closes the
pair, so the band interior is captured: on TE5.1 that is 373 assets including 73
centreline and 18 lead-in lights, against 335 with **no** centreline lights from a
15 m buffer.

`fixtures_near_segment(seg_id, buffer=…)` still exists for genuine proximity
questions ("how far is the nearest handhole from this line"). Reach for it when the
question is about distance to a line, not about a milling area.

Two things to carry into whatever you write:

- The patches are **reconstructed**, not read from the drawing. Say "inside the
  reconstructed TE5.1 patches", and attach the sketch — the shaded bands let a
  reviewer check the reconstruction instead of trusting it. Where a division line
  has no partner, `strip_width` (default 25 m) is a pure assumption about which side
  the milling falls; state it, and say how many patches came from it.
- Ducts and cable are separate. A point-fixture register says nothing about what
  runs beneath the patch — cross-check with
  `load_routes(..., bbox=segment_extent(seg_id, pad=30))`.

4. For a register or an RFI attachment, write `fx.to_csv(...)` and quote counts by
   `asset_type`, not by raw layer name. Quote duct quantities by `leaf`, because the
   layer name is the only place the duct size and way-count is recorded
   (`CV-EX DUCTBANK 6-way x150mm dia`).

5. `python scripts/smoke_test.py` after any rebuild. See *Regenerating*.

## Drawings

Two renderers, and picking the wrong one is the usual mistake:

| | Use for | Gives you |
|---|---|---|
| `basemap.plot()` | checking your own filter | quick PNG, no scale, no title block |
| `drawing.sketch()` | anything anyone else sees | A4–A1 sheet at a real drafting scale, title block, graphic scale bar, grid-north arrow, legend with counts, context assets in grey, automatic panels — PDF **and** PNG |

```python
from basemap import fixtures_in_segment, segment_patches
from drawing import sketch, write_dxf

fx = fixtures_in_segment("TE5.1", assets_only=True)
patches, strips = segment_patches("TE5.1")
sketch(fx, patches=patches, strips=strips, out="TE5.1_agl_impact.pdf", paper="A3",
       drawing_title="TWY D7/D8/D10 milling - AGL impact",
       title_block={"drawing_no": "ZIA-AGL-RFI-0142", "rev": "A"})
write_dxf("TE5.1.dxf", fixtures=fx, patches=patches, strips=strips)
```

or straight from the CLI, alongside the register:

```bash
python scripts/basemap.py --seg TE5.1 --assets-only \
    --csv-out te51_register.csv --sketch te51.pdf --dxf-out te51.dxf \
    --drawing-title "TWY D7/D8/D10 milling - AGL impact" \
    --drawing-no ZIA-AGL-RFI-0142 --rev A
```

**Title block fields live in `assets/titleblock.json`** — set the project and client
once, pass the per-drawing fields (`drawing_no`, `rev`, `date`, `drawn_by`) at call
time. Anything left empty prints `- not set -` on the sheet rather than a plausible
value, because a wrong drawing number on an RFI attachment is worse than a blank one.

Three things the renderer will not fake, and you shouldn't either:

- **North is grid north of the local drawing grid**, labelled `GRID N`. The rotation
  to true north is unknown — there is no GEODATA object to read it from. Never
  relabel that arrow as true north.
- **The printed scale is exact only at the stated paper size, printed at 100%.**
  It is chosen from a drafting series (1:250 … 1:20000) so it is a ratio someone can
  scale off, not "whatever fitted". The graphic bar survives rescaling; the ratio
  does not.
- **Reconstructed patches are drawn with a "RECONSTRUCTED" note** and unpaired
  division lines are dashed and flagged as assumed-width, in the legend and in the
  sheet notes. Leave both in.

`write_dxf()` writes DXF R12 (opens anywhere) with assets on
`ZIA-AGL-<TYPE>` layers, reconstructed patches on `ZIA-MTA-PATCH-RECONSTRUCTED`, and
the local-grid disclaimer as text inside the file, so the warning travels with the
geometry rather than only in the covering email. Coordinates are written unchanged —
it will only land correctly when inserted into a drawing on the same local grid.

## Layer naming and classification

Layers use bound-xref paths: `ADB-ZONE-1-2-AGL LAYOUT$0$EL-TAXICL`. Always filter on
the **leaf** (`EL-TAXICL`), never the full path, because the same asset type carries
different prefixes in different xrefs:

- Zone 1–2 xref uses `EL-*` (`EL-TAXICL`, `EL-STOPBAR`, `EL-TAXIWAY EDGE`)
- Zone 3 xref uses `ADB_*` (`ADB_TAXICL`, `ADB_STOPBAR`, `ADB_TAXIWAY EDGE`)
- Civil duct and cable uses `CV*` (`CV-EX SEC CONDUIT`, `CV_SEC_100MM`)
- `AUH_*` is the aerodrome basemap, not AGL — and see the warning below

`scripts/classify.py` resolves both AGL families to one plain-English `asset_type`. It
is **layer-first with a block-name fallback**: the layer is the drafter's stated intent
and is right almost everywhere, but it is uninformative on the default layer `0`, on
circuit layers (`LTCC8`), on annotation-line layers (`EL-IHP-LINE`), on the scratch
layer (`ADB_TO CHECK`) and on `*-AT` layers. For those, the block name decides. The
reverse rule was tried and rejected — generic block names (`Pit` covers both handholes
and transformer pits) destroy information the layer had.

Residual `Unclassified`: 3 fixtures, all anonymous blocks on layer `0`.

`load_fixtures(assets_only=True)` drops the four non-asset categories
(`Non-AGL basemap`, `Segmentation annotation`, `Floodlight (non-AGL)`, `Unclassified`),
giving **33,424 AGL/civil assets** out of 33,720 INSERT records.

`classify.py` does not apply to `civil_routes` — routes carry no block name, and the
leaf layer already states the duct type, size and way-count.

## Known limits — state these when you use the data

- **Zone 3 segmentation is missing from the bundled assets.** `seg_geometry.csv` /
  `seg_labels.csv` cover only the `SEGMENTATION-ZONE 1-2` and `SEGMENTATION - MTA`
  xrefs. The `SEGMENTATION - ZONE 3` xref names its segment layers without the
  `ADB_SEG_` prefix (`ADB_SIG.2`, `ADB_TE.1`, `ADB_TDZC31R.1`, …), so the extraction
  filter missed them. `rebuild.py` captures them now, but the bundled CSVs predate the
  fix — Zone 3 segment IDs will not resolve until the assets are rebuilt from the
  source DXF. If an ID doesn't resolve, say so and check whether it is a Zone 3 ID
  before concluding it doesn't exist. Zone 3 *fixtures* and *routes* are unaffected;
  only the segmentation overlay is missing. `smoke_test.py` reports when this clears.
- **Segmentation patches are not polygons.** 2,418 of 2,428 segmentation features are
  division lines; only 10 are closed. A milling *area* has to be constructed from
  division lines against the pavement edge — it cannot be read straight out of the
  drawing. Never claim a segment area from this data without building it. Proximity to
  a segment label is a triage screen, not containment; label it as such.
  `segment_patches()` does build the area — by pairing division lines — but the result
  is a reconstruction: pairing can mis-associate lines where three or more run close
  together, and an unpaired line gets an assumed width. Show the shaded sketch so the
  reconstruction is auditable, and never present a reconstructed patch area as a
  surveyed quantity.
- **A long segment carries many label points** (up to 38 for `SIG3.3`), and 69
  segment IDs carry several geometry features. `load_segments()` collapses labels to
  one anchor per ID before merging — merging raw produced a 7.2× cartesian blow-up
  (17,377 rows for 2,428 features) and inflated every downstream count by that factor.
  `load_segment_labels()` returns the full label set when you need it. A few label
  texts disagree with their layer-derived ID (drafting slips like `610.1a` on layer
  `610.1C`): `seg_layer` is the authoritative ID, `label` is just drawing text.
- **Routes are fragments, not connected runs.** 17,101 duct features across 51 layers
  are individual LINE / LWPOLYLINE / ARC segments. "This duct runs HH-A → HH-B" needs
  endpoint snapping within tolerance and graph chaining, which this skill does not do.
  Do not present a route length as a continuous run without building the topology.
- **`approx=1` routes are discretised curves.** All ARC, CIRCLE, ELLIPSE and SPLINE
  geometry is resampled to a point every 0.5 m of arc length. Lengths are close but not
  exact. SPLINE is worse: with no knot-vector evaluation, fit points are used where
  present and the control polygon otherwise, so 69 splines carry real shape error.
  16.4 km of the 466 km duct total comes from approximated geometry.
- **`AUH_*` route coordinates are not trustworthy.** 442 features on the aerodrome
  basemap layers (`AUH_Service Road`, `AUH_Facility-Terminal 3`, `AUH_Aircraft Stand-*`)
  carry vertices at ±54,000 — impossible against a drawing `$EXTMAX` of 76,896, and far
  outside the site. Cause not resolved. **Zero** `CV*` / `EL*` / `ADB*` routes are
  affected, so all duct, cable and AGL geometry is clean; `smoke_test.py` asserts this.
  Filter `AUH_*` out, or bbox-clip it, before plotting a basemap.
- **3,375 geometry entities were not extracted.** They sit outside the twelve
  identity-inserted xrefs, so their coordinates are block-local and would plot in the
  wrong place. They are excluded rather than shown wrong. Mostly `LINE` (2,340).
- **2,409 nested fixtures were dropped** for the same reason. If a count looks light in
  a given area, this is the first thing to check.
- **No named-location lookup exists.** There is no gazetteer: nothing in this skill
  resolves "CP10", "TWY E6" or a holding-point name to a coordinate. Every query starts
  from a numeric bbox or a segment ID. Get the bbox from a segment label anchor, from
  `layer_index` bboxes, or from the MAFP.
- **Zones, not taxiways.** The xrefs are `SEGMENTATION-ZONE 1-2` and
  `SEGMENTATION - ZONE 3`. Confirm the zone-to-taxiway mapping against the MAFP before
  writing "TWY Z1" anywhere.
- One fixture on layer `0` sits at the origin (drawing furniture, not an asset). It is
  why the raw Y extent reads `0.0`. `assets_only=True` does not remove it — it is
  classified by block name. Bbox-filter it out if it matters.
- **Never classify or exclude by layer suffix.** `-AT` means *ATtribute*: across all
  `-AT` layers the content is 641,705 `ATTRIB` + 2,766 `ATTDEF` and only **726
  `INSERT`** (0.11%). Those 726 are real, distinct fixtures — none coincides with a
  same-type fixture on the paired non-`-AT` layer — so excluding `-AT` layers wholesale
  loses 726 assets, and including `-AT` entities wholesale adds 644,471 text records
  that are not assets. The extraction filters on **entity type**, which is the right
  discriminator. See `references/at-layers.md`.
- **Layer-index bboxes are geometry-derived, and only for layers that carry geometry.**
  Layers holding only text or attributes have `bbox: None`. Earlier revisions built the
  bbox from raw group codes 10/20, which is wrong: an ARC/CIRCLE code 10 is the
  **centre**, so a near-straight duct curve drafted as a large-radius arc threw its
  centre kilometres off site, and a legacy `POLYLINE` header carries a dummy `(0,0)`.
  Those two artefacts produced impossible duct extents (Y 0 → 89,267). Never rebuild a
  bbox from raw group codes.

## Regenerating

If ADA issues a new revision of the DXF:

```bash
python scripts/rebuild.py /path/to/new.dxf --out assets/   # accepts .dxf or .dxf.bz2
python scripts/smoke_test.py                                # MANDATORY
```

`smoke_test.py` asserts every count quoted in this file, reconciles the extracted
routes against an independent layer-index census, and checks that no `CV*`/`EL*`/`ADB*`
route escapes the site envelope. It exists because the failure it guards against was
silent: the previous extraction discarded all 466 km of duct geometry and the output
looked entirely plausible. Counts that look reasonable are not counts that reconcile.

The first rebuild after the Zone 3 capture fix will add `SEGMENTATION - ZONE 3`
features to `seg_geometry.csv`, so the segmentation counts in this file and in
`smoke_test.py`'s `EXPECT` will legitimately change. `smoke_test.py` prints a NOTE
when that happens — update `EXPECT`, update the counts here, and delete the Zone 3
gap entry from *Known limits*.

If the printed extents move, the drawing origin has changed and every previously issued
coordinate needs re-checking.
