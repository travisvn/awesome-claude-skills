# TWY E (E4–E6) — replacing indicative duct lines with real as-built geometry

A worked example of `zia-mta-basemap` used against a real deliverable: an ADB SAFEGATE
shop-drawing deck for AGL rectification works on Taxiway E between E4 and E6 at ZIA.

The input deck (Rev P05) drew its ducts as **construction lines** — a straight line from
each light to its nearest pit. Its own legend said so: *"INDICATIVE DUCT — LIGHT TO NEAREST
MH/HH"*, 86 such lines across three location sheets, plus general note 3: *"Confirm routes
vs AGL duct-layout CAD (Rev B) before works."*

This pipeline does that confirmation. It registers each drawing sheet onto the source DXF,
lifts the real duct / ductbank / conduit / sawcut geometry, and rewrites the sheets with it
as native editable PowerPoint shapes. Output is `out/…_RevP06.pptx`.

## The hard part: the sheets carry no coordinate grid

The Rev P05 sheets are labelled `UTM 40N (EPSG:32640)` but carry no grid ticks, no scale
bar anchor, and no georeferencing — nothing to hang a transform on. So the sheets are
registered to the source drawing by **matching the plotted AGL fitting pattern**, following
the method already set out in `references/coordinates.md`:

1. Type-matched 2-point RANSAC to establish the correspondence. Anchors are drawn from the
   rarest asset types first, so the candidate set stays small.
2. A **4-parameter Helmert** fit (translation, rotation, uniform scale) by least squares on
   the inliers — deliberately not an affine, which would absorb real error into fake shear
   and flatter the result.
3. Reflection allowed, because PowerPoint y grows downward while the grid y grows up.
4. Half the matched pairs held back from the fit. The **hold-out RMS** is the accuracy
   figure, and it is the number quoted on the drawing.

### Result

| Sheet | Symbols in frame | Matched ≤50 mm | Fit RMS | Hold-out RMS | Scale | Frame on ground |
|---|---|---|---|---|---|---|
| LOC-01 | 64 | 37 | 0.4 mm | **0.40 mm** on 14 pairs | 93,614 EMU/m | 102.1 m |
| LOC-02 | 18 | 9 | 0.3 mm | **0.46 mm** on 4 pairs | 87,716 EMU/m | 108.9 m |
| LOC-03 | 59 | 11 | 58.2 mm | **0.49 mm** on 13 pairs | 100,476 EMU/m | 95.1 m |

Rotation solved to +0.0001° / −0.000001° / +0.0027° — the sheets are plotted axis-aligned
to the local grid, at a different scale per sheet (each window is auto-fitted to its own
content, so the sheets' "Scale 1:250" note is not literally true).

Two independent confirmations, neither used in the fit:

- The deck's own *"as-built taxiway centreline"* polyline lands on `EL-TAXICL` fixtures at
  0.3–0.4 mm median on LOC-01/02.
- Consecutive deck asset IDs map to **consecutive rows** of the extracted fixture table
  (e.g. `TCCECH.04.016 → .03.016 → .04.015` = rows 10985 → 10986 → 10987), so the deck's
  register enumerates the same entities in the same file order.

### What was hard about LOC-02

LOC-02 has only 21 plotted symbols, 12 of them centreline lights strung along a nearly
one-dimensional feature — registration slides freely along the taxiway and the first three
search strategies each converged somewhere different. It was resolved using the asset-ID
ordering: LOC-03 carries `TCCECH .003–.006`, LOC-02 `.006–.010`, LOC-01 `.015–.020`, and
those bracket source rows 10990–11002, which sit at x 5909–6085. Searching only that gap
snapped LOC-02 to a 0.34 mm fit. `register4.py` and the earlier attempts are kept here
deliberately — the failures are the interesting part.

## Two findings the registration exposed

**1. The Rev P05 coordinate label is wrong.** The plotted positions are ZIA local project
grid metres (X ≈ 5,800–6,200, Y ≈ 54,400–54,700), not UTM 40N — which here would read
easting ~230,000–800,000, northing ~2,650,000–2,750,000. The source DXF has no GEODATA
object, so no local→UTM transform can be derived from it at all. Any coordinate previously
issued from Rev P05 as UTM needs withdrawing and re-checking against survey control.

**2. The Rev P05 LOC-02 scope note describes the wrong topology.** It states
*"SECONDARY DUCT: CHAINED RUN HH.E.056 → 03/007 → 04/007 → 03/008 → 04/008 → 03/009 →
HH.E.054"*. There is no chain. Every affected light is fed by its own spur from **one**
transformer handhole: 20.5, 21.1, 29.1, 30.3 and 41.5 m — 142.5 m of separate home runs.
That changes cable quantity, pull count and isolation sequence.

Finding 2 is also the strongest evidence the geometry is genuine. Chaining the conduit
fragments at a 0.30 m snap tolerance yields a working distribution network, not a bag of
lines: every hub node lands on a `CV_ETRANS HH` fixture at 0.000–0.002 m, and 40 of 45
spurs terminating at a light land within 50 mm of that light's insertion point. Invented or
inferred geometry does not terminate on insertion points to the millimetre, nor converge
specifically on transformer handholes rather than any nearby pit.

## What this pipeline deliberately does NOT do

Per-asset route attribution. The consolidated table's `Route` column is left exactly as
Rev P05 had it. Attributing a specific duct layer to a *named* asset was attempted
(`asset_routes.py`) and rejected: the sheets' labels sit 3–8 m from their markers with
neighbours only 10–15% further, and several markers resolve to the same label. Only 1 of 32
works-action markers mapped unambiguously. A wrong duct layer against a named asset in a
shop drawing is worse than a blank, so the sheet says so instead (sheet 6, limit d).

## Running it

```bash
pip install python-pptx matplotlib pandas shapely scipy pymupdf
export ZIA_BASEMAP_SCRIPTS=../../../scripts        # or an absolute path to the skill's scripts/
cd pipeline
cp ../input/TWYEAGLSHOPDWGEDITABLE_RevP05.pptx src.pptx
mkdir -p pptx_in && (cd pptx_in && unzip -o ../src.pptx)

python deck_points.py     # extract plotted fitting symbols + labels per sheet
python register.py        # LOC-01 by type-matched RANSAC  -> registration.json
python register4.py       # LOC-02/03 anchored on the sub-mm fitting classes
python ducts.py           # clip real duct geometry to each sheet -> sheet_ducts.json
python topology.py        # chain secondary conduit, find hubs   -> topology.json
python build_asbuilt.py   # rewrite the deck, add sheets 6 and 7
python proof_csv.py       # machine-readable proof pack
```

`register2.py` / `register3.py` are the two intermediate LOC-02/03 attempts that did not
converge; they are kept for the record, not needed for the build. `verify_fig.py` renders
the figure embedded on sheet 6.

Each step reads and writes its JSON in the **current directory**, so run them all from
`pipeline/`. The copies under `data/` are the archived results of the run that produced
`out/`, kept so the findings can be checked without re-running anything.

Order matters: `register.py` must run before `register4.py` (which seeds from LOC-01's
solution), and both before `ducts.py`.

## Files

| Path | What |
|---|---|
| `pipeline/parse_deck.py` | pull shapes out of the slide XML with style + geometry |
| `pipeline/deck_points.py` | fitting symbols, dedupe concentric markers, associate labels |
| `pipeline/register.py` | Helmert fit, RANSAC, `apply`/`fwd` transform helpers |
| `pipeline/register4.py` | final LOC-02/03 registration |
| `pipeline/ducts.py` | layer→style map, sheet-window clipping, local↔EMU conversion |
| `pipeline/topology.py` | endpoint snapping, hub detection, spur walking |
| `pipeline/build_asbuilt.py` | strips indicative lines, draws freeforms, rewrites notes/legend |
| `pipeline/proof_sheet.py` | sheet 6 — provenance, registration table, limits |
| `pipeline/sheet7.py` | sheet 7 — derived spur schedule |
| `data/registration.json` | per-sheet transform, inliers, residuals |
| `data/sheet_ducts.json` | clipped duct geometry, local grid + slide EMU |
| `data/topology.json` | hubs, spurs, snap tolerance |
| `out/*.csv` | duct schedule, every segment as WKT, registration stats, spurs, fitting matches |

## Limits carried onto the drawing

Stated on sheet 6 of the output, and they are the skill's own limits showing through:

- **Runs are fragments, not proven pulls.** No endpoint snapping in the source data;
  the chaining on sheet 7 is derived at a stated 0.30 m tolerance. Do not order cable to a
  length scaled off these sheets.
- **Coordinates are local grid, not surveyed and not UTM.** Nothing here may be issued as a
  setting-out coordinate without an externally checked transform.
- **Civil symbols are ~2.1–2.3 m off** (mean, sd 0.3–0.45 m) from the source insertion
  point — handholes, manholes, transformer pits, RRM — while AGL light fittings match to
  sub-millimetre. Set out civil features from survey.
- **Z is unreliable** in the source drawing. 2D basemap only.

## Rev P08 — final-submission review pass

`pipeline/final_review_p08.py` takes the Rev P08 working deck
(`input/TWYEAGLSHOPDWG_RevP08.pptx`) and produces the issue copy in `out/`. It is a
checking pass, not a rebuild: every drawing coordinate is left alone except where the
sheet contradicted its own text.

What it resolves:

- **Quantities that did not reconcile.** Sheet 7's TOTAL row read `11 @ 8" · 5 @ 12"`
  coring and `16 side-entry shallow bases`; the per-location rows give 11 coring
  (6 @ 8" · 5 @ 12") and 13 new bases — 3 No. at LOC-03 take cable into existing bases.
  Sheets 1, 2, 6 and 7 now state the same figures.
- **Works area vs. its own caption.** Every sheet notes the red area as the Rev P05
  field-condition milling extent, unchanged at P08. Sheet 1001 matched (425.3 m²); the
  patches on 1002 and 1003 had drifted to 99.7 m² and 292.9 m² against the stated
  257.1 m² and 676.7 m². Both are redrawn from the Rev P05 geometry, and 1002 gains the
  caption it was missing.
- **Symbols vs. scope.** Three green "secondary cable affected" markers on sheet 1001 sat
  on assets the panel lists as out of scope — removed. RRM.557 and RRM.670 were in scope
  and legended on sheet 1003 but never plotted — rings added. Per-sheet legends now list
  only the symbols that sheet actually uses.
- **Stale references.** The `see sheet 6` cross-reference (a registration sheet that no
  longer exists), the EPSG:32640 note, working file names on the cover, the blank
  `Base layer` row, and the hold-point list starting at H2 with no H1.
- **Tone.** Statements set against the civil team, and against the deck's own earlier
  revisions, are re-worded as requests for confirmation or as superseded status.
- **Layout.** Panels fitted to their text with columns levelled, titles on one line,
  tables inside their frames, sheet footers on every page, ADB SAFEGATE logo throughout.

`pipeline/textfit.py` measures wrapped text in Liberation Sans (metric-compatible with
Arial) so the panel and table fitting is computed, not eyeballed.

### Sheet 3 — 5-day AGL installation schedule

The review pass also adds a programme sheet after the scope & sequence sheet. It covers
**Phase 3 AGL installation only** — Phase 1 asset removal and coring is recorded complete,
and Phase 2 civil attendance sits outside the five days.

Every figure on it comes from the deck itself: 16 No. fittings, 11 No. 8" bases at LOC-01,
1 No. 12" at LOC-02 and LOC-03, 3 No. RRM, 4 No. circuits, and saw cut lengths measured off
the Rev P08 new-saw-cut runs on sheets 1001–1003 (approx. 300 m / 24 m / 95 m, approx. 420 m
total) using the per-sheet EMU-per-metre scale from `data/registration.json`. The sheet
states that those lengths are scaled for programme only.

The five days are allocated across the three locations rather than by trade, so each
location is cut, cabled, tested and sealed as one front before the next is opened —
**LOC-01 over Days 1–3** (11 No. fittings, approx. 300 m of cut), **LOC-03 on Day 4**
(4 No., approx. 95 m), **LOC-02 on Day 5** (1 No., approx. 24 m). Only two items span all
three: the setting-out on Day 1, taken in a single survey visit, and the circuit testing and
commissioning on Day 5, which cannot complete until every location is cabled because the
circuits run through all three.

The programme is gated on the deck's own hold points: Day 1 cannot start until H1 (curing
confirmed) and H5 (saw cut detail issued and accepted) are released, and neither is released
at Rev P08. Sealant cure time before return to operational service is per the awaited detail,
so the sheet says handover moves to the following shift if the cure exceeds the Day 5 window.
Shift hours and resourcing are marked indicative, to be set against the approved AWAN.

### Sheet 7 — works quantities

A quantities sheet ahead of the asset-by-asset consolidated scope, carrying one row per
location plus a total:

| | Affected | Core out 8" | Core out 12" | New coring 8" | New coring 12" | Saw cut | Secondary cable |
|---|---|---|---|---|---|---|---|
| LOC-01 | 11 No. | 6 No. | 3 No. † | 11 No. | — | ~300 m | 11 No. runs |
| LOC-02 | 1 No. | — | 1 No. | — | 1 No. | ~24 m | 1 No. run |
| LOC-03 | 4 No. | — | 1 No. | — | 1 No. | ~95 m | 4 No. runs |
| **TOTAL** | **16 No.** | **6 No.** | **5 No.** | **11 No.** | **2 No.** | **~420 m** | **16 No. runs** |

† 2 No. further 12" bases at LOC-01 were removed earlier and need no coring out, so 11 No.
new 8" bases are set against 9 No. cored positions — which is why core-out and new-coring
do not match at LOC-01.

*Core out* is removal of the existing shallow base by coring; *new coring* is the core taken
to receive the new side-entry base. A second table lists the asset IDs behind each count. The
figures are counts, not dimensions — core diameter, core depth, saw cut width and depth all
sit behind the awaited detail (hold point H5), and cable figures are route lengths with no
allowance for terminations, base entry or manhole tails.

The sheet reconciles against the consolidated scope sheet and the saw cut & coring schedule:
16 No. fittings, 11 No. cores (6 @ 8" · 5 @ 12"), 13 No. new side-entry bases (11 @ 8" ·
2 @ 12").

### Rev P08 update — technical query closed by agreement

The existing secondary duct exposed at 50 mm milling depth is **4 x 19 mm**, not the
4 x 110 mm the earlier revisions recorded. (The as-built duct layers lifted from the DXF do
carry real 110 mm ducts — `CV_OUTER DUCT 4x110mm dia` and similar — those are different ducts
and keep their source labels. Only the technical-query narrative changes.)

Q1, Q2 and Q3 are no longer open. Raised with the civil team and with ADA AGL, it was agreed
that the 4 x 19 mm duct cannot accommodate the new secondary cable and that the civil scope
covers the milling area only, so a full-stretch duct cannot be delivered under this work. Saw
cut is adopted for every milling-affected asset as an **interim arrangement**, with permanent
duct provision to follow under the South Rehabilitation works where the saw cut routes are
replaced with duct to the standard design.

The deck records this on the cover, in the technical-query panel (now headed *closed by
agreement*), in the way-forward panel, in *what changed*, in the quantity exclusions, and on
the detail sheet — where item 8 becomes a termination detail at the milling edge rather than
an open query.

### Rev P08 update — 3 No. LOC-01 fittings back in scope

`SBC102-02/027`, `TCCECH-03/035` and `TCCECH-03/018` at Location 1 are **secondary cable only**:
new saw cut, **no coring**, the existing base kept and protected by a dummy plate during
milling. They had been carried as out of scope. The saw cut runs plotted on sheet 1001 already
reach all three (two sit on a run, the third 3.0 m off), so the ~300 m at LOC-01 and ~420 m
overall are unchanged.

Every count moves with them — affected fittings **16 → 19**, LOC-01 **11 → 14**, cable runs
**16 → 19**, not-in-scope **15 → 12**. Coring stays 11 No. and new bases stay 13 No., since
these three need neither.

### Material requirement (separate deliverable)

`material/build_material_requirement.py` writes
`material/Material Requirement - TWY E AGL Installation - Rev P08.xlsx` — deliberately a
separate workbook, not a deck sheet. Each line carries its basis against the Rev P08 plan, and
three lines move:

- **Shallow base 12"** — 2 No., added; the plan needs 13 No. new bases (11 @ 8" + 2 @ 12").
- **Dummy plate** — 16 No., added; 13 No. open bases plus the 3 No. LOC-01 fittings kept
  under a plate during milling.
- **Secondary connectors** — 33 → **38 pair** (2 per fitting × 19 No.), so 5 pair short of
  what is held.

Sealant, mortar and backer-rod quantities cannot be firmed until the saw cut detail fixes cut
width, depth and core diameter (hold point H5), and the sheet says so.
