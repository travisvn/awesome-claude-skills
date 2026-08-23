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

## Legends: rebuilt so every plotted symbol is accounted for

Rev P06's legends did not describe what the sheets drew. Auditing each sheet's legend
against the symbols actually plotted in the map frame found **13 defects** across the
three sheets:

| Sheet | Defect |
|---|---|
| all three | AGL feed manhole / handhole (magenta square) plotted, no legend row — P05 had one, P06 dropped it and reused the row to relabel the grey ring "Dummy Plate" |
| all three | milling / cut area shading plotted, never legended on any revision |
| all three | indicative duct (grey dashed, 31 / 4 / 22 lines) plotted, no legend row — P05 legended this exact colour as "INDICATIVE DUCT — LIGHT TO NEAREST MH/HH" and P06 deleted the row while leaving the lines |
| LOC-01 | the stray red / green marker on TCC103-11/021 matched no legend row |
| LOC-01 | legend rows for blue/green and orange/green markers that P06 had greyed off the sheet |
| LOC-02 | a STOP BAR legend row, though LOC-02 has no stop bar linework and no SBC asset |

Each legend is now laid out in two columns and built from a declarative spec, and
`legend.audit()` checks it **both ways**: every point symbol and every linework colour
plotted must have a legend row, and every legend row must correspond to something on the
sheet. Run against Rev P06 it reports all 13 defects above. Swatch dash styles are read
off the linework rather than inherited from whichever template they were cloned from, so
a solid line does not get a dashed swatch.

The indicative-duct reading was confirmed two ways before restoring P05's wording: P05's
own legend paired that colour swatch with that text, and 30 of 31 / 22 of 22 of those
lines start on a plotted light and run to a pit.

### Existing assets: one symbol and one legend row per as-built class

Rev P06 drew every existing asset as the same teal dot, so a reader could only tell a
stop bar light from a handhole by its label prefix. Each as-built class now has its own
symbol and its own legend row, as the as-built drawing does. Shape carries the family,
colour carries the AGL optical colour where the asset has one:

| Class | Symbol | Class | Symbol |
|---|---|---|---|
| Taxiway centreline light | green circle | Handhole | teal outlined square |
| Stop bar light | red circle | Manhole | slate filled square |
| Taxiway edge light | blue circle | Existing manhole | slate outlined square |
| Runway guard light / RRM | yellow circle | Existing transformer handhole | teal diamond |
| Existing light base | grey outlined circle | Earthing pit | olive outlined diamond |
| Sign foundation | grey filled square | Earthing point | olive triangle |

Works action is conveyed only by the ring drawn over the symbol, so a green dot inside a
red ring is unambiguous: green = centreline light, red ring = core out. Where a works
marker is drawn the asset symbol sits beneath it, so legend counts include assets under
works markers — general note 7 says so on the sheet.

`asset_symbols.py` resolves the class of **every** plotted symbol, including the majority
that carry no label. Two things make that a measurement rather than a guess:

- **The systematic plot offset is removed first.** Civil symbols sit ~1.4–1.9 m from
  their surveyed insertion point and AGL symbols ~0.7–1.0 m. The offset is estimated per
  sheet per family from the labelled symbols, then subtracted before matching.
- **Where a symbol is labelled, the label governs** — it is the drawing's own assertion
  of what the asset is, and it outranks a proximity match. Nearest-fixture matching is
  used only for the unlabelled symbols, and the labelled ones measure how well it
  performs: **93 of 95 agree (97.9%)**, and the script refuses to write its output below
  95%. The two disagreements are `EL.EBASE.13330/13331`, where the label says "light
  base" and proximity says "centreline light" — a light base *is* the base of a light, so
  the label is right and proximity is not wrong so much as unhelpful.

124 symbols across the three sheets, 12 classes, 4 ambiguous (a rival class nearly as
close), 0 unclassified. Ambiguous ones keep their resolved class but are flagged in
`asset_symbols.json`; anything with no fixture within 3 m falls back to the generic dot
and gets its own "Other existing asset" legend row rather than being forced into a class.

`asset_key.json` (label prefix → class, from `asset_key.py`) is kept as the provenance
record for the prefix mapping, though the drawing no longer needs a prefix key now that
the symbols carry the class.

### A trap worth knowing about

`shape.line.color` and `shape.fill.fore_color` in python-pptx are **not read-only**:
asking a shape with no explicit `<a:ln>` for its line colour inserts
`<a:ln><a:solidFill/></a:ln>`, which renders as a black outline. An early version of the
legend audit put a visible border on every unstyled shape it inspected. `legend.py` reads
stroke and fill straight out of the XML instead — an audit must not alter the drawing it
inspects. The four TCC103 labels are also normalised to the sheet's 6.5 pt dark-grey
label style; P06 had them at 7.0 pt navy, which reads as emphasis on assets that are
explicitly *not* in scope.

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
cd fieldsheet
python asset_key.py                            # label prefix -> as-built class
python asset_symbols.py                        # class of every plotted asset symbol
python reconcile_fieldsheet.py                 # rewrites the deck, then audits its own output
python declutter_labels.py                     # resolve label collisions (replayed thereafter)
python check_all.py                            # 12 end-to-end checks
```

`asset_key.py` reads the previous output deck for its label inventory, so on a clean
checkout run `reconcile_fieldsheet.py` once first (the committed `asset_key.json` already
covers this) and re-run it after.

`reconcile_fieldsheet.py` re-opens the file it just wrote and asserts that all 32
field-sheet lights carry the marker their columns imply, at the verified position, and
that each legend accounts for every symbol its sheet plots. Run
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
`reconcile_fieldsheet.py` needs only `python-pptx` and the JSON files. `check_all.py` and
`declutter_labels.py` additionally need PyMuPDF and LibreOffice **with Impress** —
`libreoffice-core` alone cannot open a .pptx, and `check_all.py` reports the layout
checks as SKIPPED rather than passing them if it is missing.

## Files

| Path | What |
|---|---|
| `Document_3_LOC-01.pdf` | field sheet, LOC-01 — 15 lights, has a Duct/Sawcut column |
| `Second_milling_area_rev1_LOC-02-03.pdf` | field sheet, LOC-03 (1st table) and LOC-02 (2nd table) |
| `Second_milling_area_rev0_LOC-02-03.pdf` | superseded revision, kept for the record |
| `field_sheets.json` | the three sheets transcribed; `route_deck` flags a route the PDF does not state, `base_blank_on_sheet` a shallow-base value it does not print |
| `build_marker_positions.py` | plotted positions from Rev P05, verified against the DXF |
| `asset_key.py` | label prefix -> as-built class, from the skill's classifier |
| `asset_key.json` | per-prefix class, observed classes, count, match distance |
| `legend.py` | symbology + legend spec + two-column builder + both-ways completeness audit |
| `asset_symbols.py` | classify every plotted asset symbol; writes `asset_symbols.json` |
| `asset_symbols.json` | per-symbol class, source (label / fixture), match distance, margin |
| `declutter_labels.py` | resolve rendered label collisions; writes `label_offsets.json` |
| `label_offsets.json` | the base-layer label nudges, replayed by `reconcile_fieldsheet.py` |
| `check_all.py` | the 12 end-to-end checks; run it against any revision |
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
- Civil items (HH / MH / pits / RRM) plot about 2.1 m from the surveyed insertion point;
  set out from survey, not from these sheets.
- A pit prefix can cover more than one civil class; confirm the individual pit.
- Positions are ZIA local project grid, not UTM, despite the sheet's label — the
  finding from `../README.md` still stands and is not fixed by this revision.
