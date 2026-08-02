# Drawing generator tools — TWY E (E4–E6) AGL shop drawings

Current issue: **Rev P05** (field condition scope, 28.07.2026).

| File | Purpose |
|---|---|
| `dwg_data.json` | Single source of drawing data: per-location bbox, as-built assets/labels, duct lines, chained LOC-02 duct, feed pits, field-governed scope, works-area polygons (LOC-01 = field-drawn grey boxes), taxiway markings (centerline/stop bar/edge) |
| `make_field_dwgs.py` | Generates the 6 DXFs (3 locations × standard + R12) — requires `ezdxf`, `shapely`; reads the source as-built overlay DXF for base entities |
| `make_editable_pptx.js` | Generates the editable A3 PPTX (`pptxgenjs`) — every element a native shape |
| `make_print_pdf.py` | Generates the 5-page print/submission PDF (`matplotlib`) |

Scripts write outputs into `../drawings/`. Edit `dwg_data.json` (scope/geometry) or the script META/notes, then re-run all three.

Scope basis: field sheets Document_3 (LOC-01) and Second_milling_area rev _1 (LOC-02/03) — field condition governs.
Totals: 11 core-outs (LOC-01 only), 31 secondary cable runs, 3 RRMs.
Open items: real drawing numbers (placeholders XXX-ELE-SHD-100x), AGL duct-layout CAD Rev B re-measure, 12"/8" main duct data, 23 m edge-width confirmation.
