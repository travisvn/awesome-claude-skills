# Rev P08 — the final scope of work

Rev P06/P07 drew the scope the field sheets recorded. The AGL Team Leader then issued a
**final scope of work on 30.07.2026** that changes the method and cuts the affected-asset
list roughly in half. This directory rebuilds the deck to it.

```bash
pip install python-pptx pymupdf
cd skills/zia-mta-basemap/examples/twy-e-asbuilt-ducts
python finalscope/build_p08.py     # -> out/TWY-E-AGL-SHOPDWG_RevP08_FINAL-SCOPE.pptx
python finalscope/check_p08.py     # re-reads the saved deck and verifies it
```

## What the final scope says

| | Rev P06 / P07 | **Rev P08** |
|---|---|---|
| LOC-01 | 11 cored (6 via duct, 5 via sawcut) + 3 cable-only + 1 not affected | **11 cored, 8" + side-entry shallow base, all via saw cut** |
| LOC-02 | 5 cable-only via duct, no bases | **1 — TCCECH-03/008: saw cut, existing base cored out, new 12" side entry** |
| LOC-03 | 4 SBC sawcut (EP7 stop bar) + 8 via duct, no coring | **4 TCC only, new 12" side-entry shallow base, via saw cut** |
| Route | mixed duct / sawcut | **saw cut throughout — no duct route remains in the AGL scope** |
| Coring | Location 1 only | **all three locations** |
| Affected fittings | 30 | **16** |

Two sheets are added: the **Scope of Work & Sequence** sheet (carried over from the sheet
issued after Rev P07, updated), and a new **Saw Cut & Side-Entry Shallow Base Detail** sheet,
which is a HOLD — the detail drawing has not been issued.

## Three decisions worth knowing about

**1. Assets that dropped out are marked SUPERSEDED, not deleted and not "not affected."**

Deleting the marker would erase the asset from the sheet: on these sheets a works marker
*replaces* the base asset symbol rather than sitting over it, so removing it leaves nothing.
And re-drawing them as "FIELD VERIFIED — NOT AFFECTED" would assert a field verification
nobody carried out — the final scope simply does not name them. So they get their own grey
marker and their own legend row, and the consolidated table records each one as
`NOT IN REV P08 SCOPE` with the reason. 15 assets are in this state.

`SBC102-01/026` is the exception: Rev P06 already recorded it as field verified not affected,
so it keeps that marker.

**2. The red AGL works area is NOT redrawn.**

It is the Rev P05 *field-condition milling extent* — what the civil team is milling — carried
through every revision since. It is not a hull of the affected assets, so cutting the AGL
scope does not shrink it. Re-cutting it to the 16 remaining fittings would have produced a
polygon with no source, on a field-governed drawing. It is left alone and the sheets say so,
in note 2 and on the scope panel.

(Rev P07's LOC-02 sheet *did* recompute its polygon as a 2.0 m buffered hull of the affected
assets and labelled it a demarcation. That is a different object from the milling extent on
the P06 sheets this build starts from; they should not be conflated.)

**3. Coring at all three locations is stated explicitly.**

Rev P06 carried `2. AGL works area (red) per field condition. Coring at Location 1 only.` on
**all three** sheets. Under the final scope every location cores, so that note was wrong on
every sheet — it is replaced, not appended to. `check_p08.py` fails the build if the old text
survives anywhere.

## Marker positions

Positions come from `../fieldsheet/marker_positions.json` (built by PR #4), where each
field-sheet light's plotted centre was verified against the source DXF — ≤0.7 mm at LOC-01
and LOC-02, and a uniform 34–52 mm at LOC-03 which is that sheet's known registration bias,
not a drawing error. No marker is moved by this build; only its colours change.

## Text edits made to the Scope of Work sheet

Carried over from the issued sheet with four corrections, all recorded in
`sheet_scope.py`'s docstring:

- item 2's `8" to SBC shallow base positions and 12" to TCC deep base can positions` — the
  final scope makes every new base a side-entry shallow base, so the diameters no longer
  split by fitting family and "deep base can" is wrong;
- item 5's `through saw cut / new ducts provided by the civil team` — no duct route remains;
- the technical query's `4 x 19 mm secondary duct` — the source layer is
  `CV_OUTER/INNER DUCT 4x110mm dia` and the LOC-02 sheet note says 4 x 110 mm, so 19 mm was
  a typo;
- hold point H4's `Item A3` — the pre-asphalt list has one item and it is numbered A1.

The **AGL team proposal** (lay a full-stretch new duct, minimise saw cutting) is marked
**NOT ADOPTED**: the final scope saw cuts every route at all three locations, which answers
Q3 the other way. Q1 and Q2 on the existing duct bank stay open.

## Files

| Path | What |
|---|---|
| `scope_final.json` | the governing scope — the only place the asset lists live |
| `build_p08.py` | the build: re-marks, rewrites panels, notes, legends, table, cover |
| `check_p08.py` | re-reads the saved deck and verifies it against `scope_final.json` |
| `legend_p08.py` | rewrites column 1 of each sheet's legend and re-packs the rows |
| `sheet_scope.py` | the Scope of Work & Sequence sheet |
| `sheet_sawcut.py` | the Saw Cut & Side-Entry Shallow Base Detail sheet (HOLD) |
| `deckkit.py` / `sheetkit.py` | shape, text and sheet-furniture helpers |

## Still open

- **The saw cut detail drawing.** Sheet 7 lists the thirteen things it has to answer.
  Items 8 and 9 — the transition into the non-construction area, and the clash with the
  4 x 110 mm duct bank found at 50 mm — are not detailing questions and cannot be closed
  out on site.
- **Whether the 12" bases at LOC-03 require coring out an existing base.** The final scope
  says "new 12 inch side entry shallow base will be installed" for LOC-03 without saying
  the existing base is cored out, where for LOC-02 it says so explicitly. The sheets and
  the schedule state 12" coring at LOC-03; confirm before ordering.
- **RRM.555 at LOC-02** is retained as remove / protect / re-fix even though the only
  fitting now in scope there is TCCECH-03/008. It sits 0.41 m from the cut line, and the
  milling extent has not changed, so the protection requirement has not gone away.
- Everything in `../HANDOFF-improve-drawings.md` §5 is still outstanding, and the Rev P06
  limits on sheets 8–10 still apply unchanged.
