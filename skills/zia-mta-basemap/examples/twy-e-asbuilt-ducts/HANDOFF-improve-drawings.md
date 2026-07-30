# Handoff — improving the TWY E (E4–E6) AGL shop drawings

Paste this into a new chat. It contains everything needed to pick the work up cold.

---

## 1. Where things stand

**Current issue: Rev P06**, 7 sheets, produced from your Rev P05 deck.

| Location | On disk (repo) |
|---|---|
| Deck + pipeline + data | `mohammed5150/awesome-claude-skills`, branch `claude/asbuilt-ppt-duct-roots-isycfo`, path `skills/zia-mta-basemap/examples/twy-e-asbuilt-ducts/` |
| PR | [#3](https://github.com/mohammed5150/awesome-claude-skills/pull/3) — draft, no CI configured on that repo |
| Output deck | `out/TWY-E-AGL-SHOPDWG-ASBUILT-DUCTS_RevP06.pptx` (+ `.pdf`) |
| Read `README.md` in that directory first — it has the full method. |

**What Rev P06 changed from P05:** the 86 "INDICATIVE DUCT — LIGHT TO NEAREST MH/HH" straight
construction lines were deleted and replaced with 125 real duct/ductbank/conduit/sawcut
segments (2,886 m on-sheet) lifted from the ADA source drawing. Two new sheets added:
sheet 6 (provenance + registration + limits), sheet 7 (derived secondary spur schedule).

## 2. Verified facts — do not re-derive these

**The sheets are in ZIA local project grid metres, NOT UTM 40N.** The Rev P05
`EPSG:32640` label was wrong. Registration per sheet (4-param Helmert, half the pairs held
back):

| Sheet | Scale (EMU/m) | Rotation | y | Hold-out RMS | Window (local grid) |
|---|---|---|---|---|---|
| LOC-01 | 93,614 | +0.0001° | mirrored | 0.40 mm / 14 pairs | x 6089.0–6191.7, y 54388.4–54488.4 |
| LOC-02 | 87,716 | −0.000001° | mirrored | 0.46 mm / 4 pairs | x 5898.2–6005.4, y 54553.3–54639.0 |
| LOC-03 | 100,476 | +0.0027° | mirrored | 0.49 mm / 13 pairs | x 5811.1–5909.0, y 54628.5–54709.6 |

Exact transforms are in `data/registration.json` (`s`, `theta`, `t`, `reflect`) and
`out/registration.csv`. Helpers `apply()` / `fwd()` / `inv()` live in `pipeline/register.py`
and `pipeline/ducts.py`. **The sheets are ordered LOC-03 → LOC-02 → LOC-01 along the
taxiway**, matching the `TCCECH` asset-ID series (.003–.006 / .006–.010 / .015–.020).

**Duct source layers present** (layer name is the only place bore and way-count are
recorded): `CV_OUTER/INNER DUCT 4x110mm dia`, `CV_STH DUCT 6x110mm dia`,
`CV_DUCT CROSSING 6x110mm dia`, `CV-EX SEC CONDUIT`, `CV-NEW SEC CONDUIT`,
`CV-NEW SEC SAWCUT`, `CV_GRND DUCT`. Zero approximated curve geometry. Per-sheet
quantities in `out/duct_schedule.csv`, every segment as WKT in `out/duct_segments.csv`.

**Secondary is a star, not a chain.** Hubs land on `CV_ETRANS HH` fixtures at
0.000–0.002 m; 40 of 45 spurs terminate within 50 mm of their light. LOC-01 4 hubs /
26 spurs, LOC-02 1 hub / 6 spurs, LOC-03 2 hubs / 20 spurs. See `out/spur_schedule.csv`.

**MTA segmentation IDs covering the sheets** (real, verified):
- LOC-01: `E5.4`, `E6.21`, `E6.23`, `E6.24`, `E6.28`, `E6.29`, `STB-E6.6`, `SIG2.2`, `TE2.2`
- LOC-02: `E5.1`, `E5.2`
- LOC-03: `E4.25`, `E5.1`, `STB-E4.7`, `SIG2.2`

## 3. Dead ends already tested — don't repeat these

- **Milling-patch polygons cannot be built for these segments.** `segment_patches()` in the
  skill pairs division lines to close a band. `E6.23`, `E5.1` and `E4.25` each return
  **0 patches / 1 unpaired strip** — they carry a single division line, no partner. The
  deck's red works areas stay field-estimated rectangles; that is the correct treatment.
- **Per-asset route attribution from the drawing alone is impossible.** Only 1 of 32
  works-action markers mapped unambiguously to a named table asset — labels sit 3–8 m from
  their markers with neighbours only 10–15% further, and several markers resolve to the same
  label. Needs the asset register. `pipeline/asset_routes.py` is the attempt.
- **No local→UTM transform can come from the source drawing.** No GEODATA object, no
  georeferencing of any kind. Needs external survey control.
- **Z / levels are unusable.** Source drawing Z spans −2,672 to +337 m. 2D basemap only.
- **The installed skill is older than the repo skill.** Use
  `ZIA_BASEMAP_SCRIPTS=/home/user/awesome-claude-skills/skills/zia-mta-basemap/scripts` —
  the installed copy lacks `segment_patches`, `fixtures_in_segment`, `segment_extent`,
  `load_segment_labels`.

## 4. Improvements doable now, no new inputs

Rough priority order.

1. **Corridor-wide duct topology → real pull lengths.** The current chaining runs only
   inside each sheet window at a 0.30 m snap, so spur lengths are branch geometry, not
   proven pulls. Chain the whole E4–E6 corridor (`x 5400–6560, y 53850–55120`), build
   handhole-to-handhole runs, then produce a **cable cutting schedule** with pull lengths
   plus waste allowance. This is the highest-value item for the field.
2. **Duct-vs-works-area conflict list.** The red works-area polygons are already in the
   deck as shapes and the real ducts are now registered to the same grid. Intersect them:
   which duct runs pass under each milling patch, which cross the cut line and where, and
   which of the 11 LOC-01 core-out positions sit on or near a duct. Answers "what will we
   hit" directly. Nothing new is needed for this.
3. **Correct the LOC-02 scope panel.** Sheet 7 flags the chained-run error but **sheet 3's
   own SCOPE panel still says** *"SECONDARY DUCT: CHAINED RUN HH.E.056 → 03/007 → 04/007 →
   03/008 → 04/008 → 03/009 → HH.E.054"*. That text should be rewritten to the five
   separate home runs (20.5 / 21.1 / 29.1 / 30.3 / 41.5 m, 142.5 m total) and the quantity
   re-priced. **This is a known-wrong statement still on a drawing sheet.**
4. **Overlay the MTA segmentation.** Draw the division lines and label the segment IDs from
   §2 on each sheet. Ties the AGL scope to the civil milling programme, which the deck
   currently does not reference at all. State clearly that proximity to a segment label is a
   triage screen, not containment.
5. **Real graphic scale bar + north arrow + local-grid ticks.** Each sheet is at a
   different scale yet all three say "Scale 1:250 @ A1". A drawn scale bar survives
   rescaling and retires the "NOT TO SCALE WHEN EDITED" caveat. Grid ticks also make any
   future re-registration trivial.
6. **Verify the P05 scope quantities against the real geometry.** LOC-01 still asserts
   "VIA DUCT (6)" and "VIA SAWCUT (5)" per asset. Those splits were assigned before real
   duct geometry existed and have never been checked against it.
7. **Circuit isolation sketch.** The deck lists circuits to isolate (`SBC102.01/.02`,
   `TCCECH.03/.04`). A per-sheet circuit diagram can be derived from the fixture layer and
   block naming.

## 5. Blocked — needs an input from you

| Need | Unlocks |
|---|---|
| **`assets_20260726120533.xlsx`** (the as-built asset register) | Per-asset route attribution (§3 dead end); resolves the ~2.1–2.3 m civil-symbol offset; lets sheet 5's `Route` column be populated; validates the deck's plotted positions against their stated source |
| **ADA survey control** — ≥4 points with both local grid and UTM 40N coordinates | The local→UTM transform, so coordinates can be issued to ADA / Injaz / contractors at all. Until then nothing from these sheets is a setting-out coordinate |
| **"AGL duct-layout CAD (Rev B)"**, named in P05 note 3 | Independent cross-check of the duct routes; may carry duct depth and cover that the MTA drawing does not |
| **Field sheets `Document_3`, `Second_milling_area rev _1`** | Confirming which assets are genuinely affected — currently taken on trust from P05 |
| **The MAFP** | Confirming the zone-to-taxiway mapping before any "TWY Z1"-style label is written |

## 6. Limits that must stay on any revision

Already on sheet 6 of Rev P06. They are the data's limits, not drafting caution:

- Duct runs are **drafted fragments, not proven pulls**. No endpoint snapping exists in the
  source; sheet 7's chaining is derived at a stated 0.30 m tolerance.
- Coordinates are **ZIA local grid, not surveyed, not UTM**.
- **Civil symbols sit ~2.1–2.3 m off** (mean, sd 0.3–0.45 m) from the source insertion
  point — handholes, manholes, transformer pits, RRM — while AGL light fittings match to
  sub-millimetre. Set out civil features from survey.
- 3,375 geometry entities and 2,409 nested fixtures were excluded drawing-wide because they
  sit outside the twelve identity-inserted xrefs. If something looks absent, check this.

## 7. How to run the pipeline

```bash
pip install python-pptx matplotlib pandas shapely scipy pymupdf
export ZIA_BASEMAP_SCRIPTS=/home/user/awesome-claude-skills/skills/zia-mta-basemap/scripts
cd skills/zia-mta-basemap/examples/twy-e-asbuilt-ducts/pipeline
cp ../input/TWYEAGLSHOPDWGEDITABLE_RevP05.pptx src.pptx
mkdir -p pptx_in && (cd pptx_in && unzip -o ../src.pptx)

python deck_points.py    # plotted fitting symbols + labels per sheet
python register.py       # LOC-01 by type-matched RANSAC   -> registration.json
python register4.py      # LOC-02/03, seeded from LOC-01
python ducts.py          # clip real ducts to each sheet    -> sheet_ducts.json
python topology.py       # chain secondary, find hubs       -> topology.json
python build_asbuilt.py  # rewrite deck, add sheets 6 and 7
python proof_csv.py      # machine-readable proof pack
```

Order matters: `register.py` before `register4.py` before `ducts.py`. Each step reads and
writes JSON in the current directory. `data/` holds the archived results of the run that
produced `out/`, so the findings can be checked without re-running. Rendering to PDF needs
`libreoffice-impress` (`apt-get install -y libreoffice-impress` — `libreoffice-core` alone
cannot open a `.pptx`).

**Ask me to start with §4 item 1 or 2** unless you have one of the §5 inputs to hand, in
which case that comes first.
