# Reconciling the TWY E shop drawing against the issued field sheets

Rev P06 of the TWY E (E4–E6) AGL shop drawing was checked line-by-line against the
three field sheets and re-issued as **Rev P07**. Every asset symbol on the three
location sheets is now driven directly from the field sheet's own columns.

## Marking rule

| Secondary cable | Shallow base | Route | Marker |
|---|---|---|---|
| YES | YES | Duct | outer **red** / inner **blue** — core out + new cable |
| YES | YES | Sawcut | outer **red** / inner **orange** — core out + new cable |
| YES | NO | Duct | outer **blue** / inner **green** — new secondary cable only |
| YES | NO | Sawcut | outer **orange** / inner **green** — new secondary cable only |
| NO | NO | — | **grey** ring, existing-asset dot only — not affected |

LOC-03's four shallow-base lights keep the base-retained + dummy-plate treatment
(amber / orange) already agreed on Rev P06. The field sheet supplies the YES; it does
not specify the method, and that decision is not re-opened here.

## What Rev P06 had wrong

Three LOC-01 lights that `Document_3` records as **secondary cable YES / shallow base
NO** were drawn grey — "field verified not affected" — while P06's own scope note still
listed all three in scope. P06 had also relabelled the grey ring in the legend as
"Dummy Plate", so grey carried two contradictory meanings on one sheet.

| Light | Field sheet | Rev P06 drew | Rev P07 draws |
|---|---|---|---|
| SBC102-02/027 | sec YES / base NO / Duct | grey — not affected | blue / green — new cable only |
| TCCECH-03/035 | sec YES / base NO / Sawcut | grey — not affected | orange / green — new cable only |
| TCCECH-03/018 | sec YES / base NO / Sawcut | grey — not affected | orange / green — new cable only |
| TCC103-11/021 | not listed at all | red / green — in no legend | grey — not on field sheet |

Rev P06 had also **re-plotted** those symbols. Its added rings sit 0.15–1.16 m from the
nearest surveyed light, while every Rev P05 works ring lands on a fixture insertion
point to ≤0.7 mm (checked against `Z1-Z2-Z3-MTA_SEGMENTATION.dxf` through
`../data/registration.json`). In the TCCECH-03/035 // 03/018 cluster the two nearest
fixtures are 0.49 m apart and P06's rings are near-equidistant from both, so those
positions could not be repaired by snapping — the P05 positions are used and P06's
off-fixture symbols are deleted.

`marker_positions.json` records, per light, the plotted position, its local-grid
coordinate, the distance to the nearest surveyed light fixture and the distance to the
second nearest. LOC-01 and LOC-02 are sub-millimetre. LOC-03 carries a uniform
34–52 mm residual shared by all twelve lights — that is the known bias in LOC-03's
registration (fit RMS 58.2 mm, see `../README.md`), not a drawing error.

Also on LOC-01: the `TCCECH-03/035` and `TCCECH-03/018` labels printed on top of each
other (the fittings are 0.49 m apart) and rendered as garble. They carry an identical
works action, so they now share one label. `TCC103-12/022`'s label box was 8.27" wide
and overran the sheet; it is now 1.25".

## Quantities, restated from the field sheets

| | LOC-01 | LOC-02 | LOC-03 | Total |
|---|---|---|---|---|
| Lights listed | 15 | 5 | 12 | 32 |
| Secondary cable affected | 14 | 5 | 12 | 31 |
| Core-outs | 11 | 0 | 0 | 11 |
| Dummy plates | 0 | 0 | 4 | 4 |
| Not affected | 1 | 0 | 0 | 1 |

31 secondary cable runs = 20 via duct + 11 via sawcut. The four TCC103 assets are not
listed on any field sheet and are excluded from every count; they are shown grey and
flagged for confirmation rather than removed from the drawing.

`Second_milling_area_rev0_LOC-02-03.pdf` is the superseded revision — it reads shallow
base "NO" for every light at LOC-02 and LOC-03. `rev _1` governs.

The LOC-02 field sheet leaves its shallow-base column **blank**. It was confirmed as
"NO" on 30.07.2026 and is recorded as `false` in `field_sheets.json`, with
`base_blank_on_sheet: true` preserving where the value came from. The sheet states both
the reading and the confirmation, so the provenance survives on the drawing. Those five
lights therefore mark as new-secondary-cable-only — which is what the sheet already
showed, so no marker changed at LOC-02.

## Running it

```bash
pip install python-pptx numpy pandas scipy shapely
# from the example root (the directory holding data/ and input/):
python fieldsheet/build_marker_positions.py    # positions from Rev P05, verified vs the DXF
cd fieldsheet && python reconcile_fieldsheet.py # rewrites the deck, then audits its own output
```

`reconcile_fieldsheet.py` re-opens the file it just wrote and asserts that all 32
field-sheet lights carry the marker their columns imply, at the verified position. Run
against Rev P06 the same audit reports the four defects above, so the check has teeth:

```
$ python -c "import json,reconcile_fieldsheet as R; from pptx import Presentation; \
    print(R.audit(Presentation('src_RevP06.pptx'), json.load(open('field_sheets.json')), \
    json.load(open('marker_positions.json'))))"
LOC-01 SBC102-02/027: ring 9AA0A6 != 0055CC
LOC-01 SBC102-02/027: inner disc expected 1 oval d=0.120" near (3.647,5.827), found 0
LOC-01 TCCECH-03/035: expected 1 oval d=0.230" near (4.491,5.175), found 0
LOC-01 TCCECH-03/018: expected 1 oval d=0.230" near (4.540,5.169), found 0
```

`build_marker_positions.py` needs the skill's `scripts/` on the path (it points at the
installed skill by default) and reads `../input/TWYEAGLSHOPDWGEDITABLE_RevP05.pptx`.
`reconcile_fieldsheet.py` needs only `python-pptx` and the two JSON files.

## Files

| Path | What |
|---|---|
| `Document_3_LOC-01.pdf` | field sheet, LOC-01 — 15 lights, has a Duct/Sawcut column |
| `Second_milling_area_rev1_LOC-02-03.pdf` | field sheet, LOC-03 (1st table) and LOC-02 (2nd table) |
| `Second_milling_area_rev0_LOC-02-03.pdf` | superseded revision, kept for the record |
| `field_sheets.json` | the three sheets transcribed; `route_deck` flags a route the PDF does not state, `base_blank_on_sheet` a shallow-base value it does not print |
| `build_marker_positions.py` | plotted positions from Rev P05, verified against the DXF |
| `marker_positions.json` | per-light position + distance to nearest surveyed fixture |
| `reconcile_fieldsheet.py` | rewrites the deck from the field sheets, then audits itself |
| `src_RevP06.pptx` | input |
| `TWY_E_AGL_Shop_Drawing_ZIA_P07.pptx` / `.pdf` | output |
| `before_RevP06_LOC01.png`, `after_RevP07_LOC01.png` | the LOC-01 cluster before and after |

## Carried onto the drawing

- The four TCC103 assets are not on any field sheet. No works action is assumed for
  them; confirm before works.
- LOC-02's shallow-base column is blank on the field sheet; confirmed "NO" 30.07.2026.
- TCCECH-03/035 and 03/018 are 0.49 m apart and share one label.
- Positions are ZIA local project grid, not UTM, despite the sheet's label — the
  finding from `../README.md` still stands and is not fixed by this revision.
