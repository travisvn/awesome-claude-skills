# ELECTRICAL / AGL SCOPE OF WORK PACKAGE

## RECTIFICATION OF TWY E BETWEEN E4 & E6 (ADIA) — CIVIL MILLING OF DEPRESSED ASPHALT AT THREE (3) LOCATIONS

| Field | Detail |
|---|---|
| Employer | Abu Dhabi Airports (adairports.ae) |
| Facility | Abu Dhabi International Airport (ADIA) |
| Project | Rectification of TWY E between E4 & E6 — Civil Milling of Depressed Asphalt at 3 Locations |
| Package | Electrical / AGL Scope of Work against Civil Affected Areas |
| Document No. | [XXX-ELE-SHD-0001] |
| Revision | P03 — Field-governed scope (drawings re-issued per field verification sheets, 28.07.2026) |
| Prepared By | Mohammed — AGL Team Leader, ADB SAFEGATE AGL Team |
| Date | 27-07-2026 |
| Coordinate System | UTM Zone 40N (EPSG:32640) — single datum for all drawings and set-out |
| Base Reference | Existing As-Built / asset survey records (single source of truth for all existing assets) |
| Overlay Reference | Civil Drawing IZ-ADAC-056-2024-TO9-RT-02 (milling demarcation only) |

> **Governing Principle:** All existing asset positions, cable routes, duct alignments, pit locations and dimensions stated in this package are derived **strictly from the as-built / asset survey records** (asset survey file `assets_20260726120533.xlsx`, 636 AGL assets, UTM 40N). The Civil milling drawing IZ-ADAC-056-2024-TO9-RT-02 is used **only** as an overlay to establish the demarcation limits of the three (3) milling locations. Impact analysis: point-in-polygon against the milling polygons plus a 3 m proximity band, on the common UTM 40N grid.

**Overall summary (Final Working Issue 27.07.2026):**

| Milling Location | Area (m²) | Fittings INSIDE cut | Assets within ≤3 m | Secondary runs affected | Cable (m) |
|---|---|---|---|---|---|
| LOCATION-01 (Phase-1, merged) | 458.23 | 16 | 4 | 19 | 628.5 |
| LOCATION-02 (L02-A + L02-B) | 205.51 + 1.00 | 0 | 1 | 5 | 198.5 |
| LOCATION-03 (L03-A) | 255.28 | 0 | 6 | 12 | 358.5 |
| **TOTAL** | **920.02** | **16** | **11** | **36** | **1,185.5** |

Works actions across all locations: **16** shallow-base core-outs (no dummy plate), **2** reinstatement fittings (per site record 23.07.2026), **6** dummy plates on retained bases, **14** new-secondary-cable-only runs, **3** RRM remove/protect, **28** secondary duct-run crossings of the cut.

> **REVISION P03 — FIELD-GOVERNED SCOPE (SUPERSEDING NOTE, 28.07.2026).** Following instruction from the AGL Team Leader, scope membership is taken from the **field verification sheets** (Document_3 for Location 1; Second_milling_area rev _1 for Locations 2–3) — field data governs over the civil/desk coordinate analysis, whose demarcation coordinates were found unreliable. The shop drawings (Rev P03) now show an **AGL works demarcation drawn around the field-verified affected assets** (convex hull + 2.0 m, as-built positions); the civil milling polygon is retained on a dashed reference layer only. Field-governed quantities: **Location 1** — 11 core-outs (6 duct + 5 sawcut), 3 cable-only runs, SBC102-01/026 field-verified not affected, TCC103 fittings out of scope; **Location 2** — 5 cable-only runs (duct), RRM.555; **Location 3** — 4 shallow bases affected + new cable (sawcut, per rev _1), 8 cable-only runs (duct), RRM.557 & RRM.670. Totals: **15 core-outs / base works, 31 secondary cable runs, 3 RRMs.** Isolation scope: SBC102.01/.02, TCCECH.03/.04 (TCC103 no longer in scope per field). Where the Section A tables below state desk-study quantities, the Rev P03 drawings and this note govern.

---

# SECTION A — CONSTRUCTION / SHOP DRAWINGS (3 No.)

---

## A.1 — DRAWING 1 OF 3

### SHOP DRAWING – ELECTRICAL / AGL SCOPE
### TAXIWAY E (E4–E6) – LOCATION 1 (PHASE-1, MERGED)
### CIVIL MILLING AFFECTED AREA

#### 1. Drawing Identification

| Field | Detail |
|---|---|
| Drawing No. | [XXX-ELE-SHD-1001] Rev. [P02] — Scale [1:250] @ A1 |
| CAD File | `drawings/TWY-E-AGL-SHOPDWG-LOC01_UTM40N.dxf` (+ `_R12` variant) — as-built base layers, UTM 40N |
| Demarcation | Single merged 10-vertex polygon, 458.23 m² (L01-A + L01-B bridged across the 1.96 m gap, bridge +8.46 m²), at the TWY E / E6 area |
| Demarcation vertices (UTM 40N) | (261122.260, 2704464.861) · (261122.325, 2704464.809) · (261123.561, 2704466.351) · (261127.949, 2704471.804) · (261131.299, 2704469.101) · (261126.903, 2704463.653) · (261125.677, 2704462.123) · (261155.019, 2704438.606) · (261147.846, 2704430.207) · (261116.608, 2704457.825) |

#### 2. Reference Drawings / Documents

| Ref | Description | Number / File | Rev. |
|---|---|---|---|
| R1 | As-Built — AGL asset survey (positions basis, UTM 40N) | assets_20260726120533.xlsx (636 assets) | 26.07.2026 |
| R2 | As-Built — AGL duct-layout CAD (duct-laid details) | [………………] | [Rev B — pending issue] |
| R3 | AGL Impact Assessment — Final Working Issue (overlay drawing) | TWY-E-AGL-IMPACT-FINAL_20260727.pdf / TWY-E-AGL-IMPACT-OVERLAY_UTM40N.dxf | 27.07.2026 |
| R4 | Civil Milling Drawing (demarcation only) | IZ-ADAC-056-2024-TO9-RT-02 | [ ] |
| R5 | Affected circuits — single line diagrams: TCC103.11 / TCC103.12 / TCCECH.03 / TCCECH.04 / SBC102.01 / SBC102.02 | [………………] | [ ] |

#### 3. Scope of Work — Location 1

- Overlay the Civil demarcation (Ref. R4) onto the as-built base (Refs. R1–R3) on the UTM 40N grid; confirm on site the 16 inside fittings and 4 near-edge assets listed in Table 4 before any activity.
- Isolate, lock out, tag and prove dead circuits **TCC103.11, TCC103.12, TCCECH.03, TCCECH.04, SBC102.01, SBC102.02** at the CCRs under permit-to-work (night possession).
- Near-edge fittings with base retained: remove fitting and install **dummy plate** on the base (TCC103.12.020, TCCECH.04.017 — both pending joint verification); store fittings labelled.
- Inside fittings: remove fitting and **core out the shallow base** (14 inside cored, plus near-edge SBC102.01.029 and TCCECH.04.036 cored per site record 23.07.2026 = 16 core-outs); no dummy plate on cored bases — protect/cover the open core until reinstatement. Cap and protect live secondary ducts/pits at the cut line.
- Support Civil works (sawcut, mill 120 mm, geogrid + 60 mm binder + 60 mm PMB wearing course per Ref. R4) with a standing AGL supervisor — 19 secondary runs cross this cut.
- After new asphalt: civil survey setting-out of each fitting point from the as-built Easting/Northing (UTM 40N, same datum as the DXF overlay); check line/spacing against adjacent undisturbed fittings before coring; core new asphalt; install new shallow bases on epoxy grout to level and azimuth; pull new secondary cables (**full manhole-to-light replacement — no joints permitted in secondary circuits**); refit, level and torque fittings.
- Testing: baseline and acceptance IR/continuity per circuit, function test at CCR, photometric spot-check; remove dummy plates and refit original fittings at near-edge positions; as-built survey of reinstated fittings; handback.

#### 4. Affected Assets Table — Location 1

| Item | Description | Quantity | Unit | Remarks |
|---|---|---|---|---|
| 1 | Saw cuts for secondary cable installation (runs routed "via sawcut") | 11 | Runs | TCC103.11 ×2, TCC103.12 ×2, TCCECH.03 ×4, TCCECH.04 ×3 — per field sheets |
| 2 | Main duct / conduit 12 inch inside demarcation | [TBD] | No. / m | To be confirmed against AGL duct-layout CAD (Ref. R2, Rev B) before works |
| 3 | Main duct / conduit 8 inch inside demarcation | [TBD] | No. / m | To be confirmed against AGL duct-layout CAD (Ref. R2, Rev B) before works |
| 4 | Coring-out locations inside/at demarcation (shallow bases, no dummy plate) | 16 | No. | 14 inside + SBC102.01.029 & TCCECH.04.036 near-edge, cored per site record 23.07.2026. Phase-1 worked to date: 9 cored + 2 reinstatement fittings |
| 5 | Secondary cable runs to be exposed / protected / replaced | 19 | Runs (628.5 m) | 8 via duct + 11 via sawcut; full manhole-to-light replacement, manhole basis. Phase-1 record: 386 m → 400 m ordered |
| 6 | Inset light fittings inside cut (remove & reinstate) | 16 | No. | SBC102.01.026/.027/.028, SBC102.02.024/.025/.026, TCC103.11.021/.126, TCC103.12.021/.022, TCCECH.03.018/.035/.036/.037, TCCECH.04.034/.035 — types ADB-UNI-R-INSET-8IN-40W and ADB-BI-GG-S/C-INSET-8IN-2x40W |
| 7 | Near-edge fittings — dummy plate on retained base | 2 | No. | TCC103.12.020 (1.17 m), TCCECH.04.017 (1.83 m) — both pending joint verification |
| 8 | Reinstatement fittings (site record 23.07.2026) | 2 | No. | TCCECH.04.035, TCCECH.03.037 |
| 9 | Feed manholes / handholes serving affected runs | 8 | No. | HH.E6.034 / .035 / .036 / .037 / .038 / .039 / .040 / .041 — protect covers and frames |
| 10 | Circuits requiring isolation | 6 | Circuits | TCC103.11, TCC103.12, TCCECH.03, TCCECH.04, SBC102.01, SBC102.02 |

#### 5. Important Notes — Location 1

1. **As-built governs.** All set-out derives from the as-built asset survey coordinates (UTM 40N); the Civil drawing IZ-ADAC-056-2024-TO9-RT-02 defines the demarcation only.
2. **Boundary checks (27.07.2026):** TCCECH.03.035 verified **2.30 m inside** the cut (no boundary conflict); SBC102.01.029 is **0.29 m outside** — watch on site; SBC102.01.026 is **0.43 m inside**.
3. **Open conflicts — resolve before finalising scope.** TCC103.11.021/.126 and TCC103.12.021/.022 are inside the milling area per drawing coordinates but absent from the field lists — fittings inside the mill must be removed regardless; raise with the field team. SBC102.01.026: desk study inside cut, field says unaffected — joint site check before dropping. TCCECH.03.018 / .03.035: field records base OK — verify base condition at the sawcut line.
4. **Electrical isolation.** All six circuits isolated, locked out and proven dead at the CCR under permit before any intrusive work; re-energisation only after permit cancellation and satisfactory testing.
5. **Protection during milling.** No milling pass over asset-bearing areas until fittings are removed, cores protected, and secondary ducts/pits capped at the cut line; AGL banksman escorts the milling machine — 19 runs cross this cut.
6. **Secondary cables.** No joints permitted — every affected run is replaced full-length manhole-to-light. Route lengths are indicative (straight-line light → nearest MH/HH + 10 % + 3.5 m termination slack); re-measure from the AGL duct-layout CAD (Rev B) before final ordering.
7. **Coring / reinstatement.** Cores concentric with surveyed fitting centres; new shallow bases set on epoxy grout to level and azimuth; fittings re-levelled flush to the new surface, torqued to specification; dummy plates only on retained (non-cored) bases.
8. **Coordination with Civil.** Daily joint pre-start; milling sequence, 120 mm depth and machine routing agreed each shift; any change to the demarcation re-verified on the UTM 40N overlay before work continues.
9. **Airside safety.** Airside permits, ATC coordination, escorting, low-visibility restrictions, FOD control; FOD-free inspection before reopening.
10. **Records.** Photograph and log all removals, cores, exposed ducts, tests and reinstatements; red-line mark-up feeds the as-built update.

---

## A.2 — DRAWING 2 OF 3

### SHOP DRAWING – ELECTRICAL / AGL SCOPE
### TAXIWAY E (E4–E6) – LOCATION 2
### CIVIL MILLING AFFECTED AREA

#### 1. Drawing Identification

| Field | Detail |
|---|---|
| Drawing No. | [XXX-ELE-SHD-1002] Rev. [P02] — Scale [1:250] @ A1 |
| CAD File | `drawings/TWY-E-AGL-SHOPDWG-LOC02_UTM40N.dxf` (+ `_R12` variant) — as-built base layers, UTM 40N |
| Demarcation | L02-A: 205.51 m²; L02-B: 1.00 m² (isolated patch at RRM.555) |
| L02-A vertices (UTM 40N) | (260955.518, 2704616.358) · (260947.994, 2704606.892) · (260934.696, 2704617.442) · (260942.218, 2704626.932) |
| L02-B vertices (UTM 40N) | (260929.690, 2704633.714) · (260928.920, 2704634.344) · (260928.289, 2704633.559) · (260929.066, 2704632.932) |

#### 2. Reference Drawings / Documents

As Location 1 (Refs. R1–R5). Affected circuits at this location: **TCCECH.03, TCCECH.04**.

#### 3. Scope of Work — Location 2

- Overlay and confirm on site: **no fittings inside** either polygon; one near-edge asset (RRM.555, 0.41 m from L02-B edge).
- Remove / protect **RRM.555** before sawcut; re-fix on line/edge after new asphalt.
- Isolate, lock out and prove dead circuits **TCCECH.03 and TCCECH.04** under permit before intrusive works (5 secondary runs cross the cut).
- Mark the five crossing duct routes on the pavement from the as-built overlay; cap/protect at the cut line; AGL supervisor on standby during milling.
- Replace the five affected secondary runs full-length manhole-to-light after paving; test and return to service as Location 1.

#### 4. Affected Assets Table — Location 2

| Item | Description | Quantity | Unit | Remarks |
|---|---|---|---|---|
| 1 | Saw cuts for secondary cable installation | 0 | Runs | All 5 affected runs at this location route via existing duct |
| 2 | Main duct / conduit 12 inch inside demarcation | [TBD] | No. / m | Confirm against AGL duct-layout CAD (Ref. R2, Rev B) |
| 3 | Main duct / conduit 8 inch inside demarcation | [TBD] | No. / m | Confirm against AGL duct-layout CAD (Ref. R2, Rev B) |
| 4 | Coring-out locations inside demarcation | 0 | No. | No fittings inside either polygon |
| 5 | Secondary cable runs to be replaced (via duct) | 5 | Runs (198.5 m) | TCCECH.03.007/.008/.009, TCCECH.04.007/.008 — feed MHs HH.E.054/.055/.056 |
| 6 | Inset light fittings inside cut | 0 | No. | Nearest fittings outside demarcation — protect in place |
| 7 | RRM — remove / protect / re-fix | 1 | No. | RRM.555 at 0.41 m from cut edge (L02-B) |
| 8 | Feed manholes / handholes serving affected runs | 3 | No. | HH.E.054, HH.E.055, HH.E.056 — protect covers and frames |
| 9 | Circuits requiring isolation | 2 | Circuits | TCCECH.03, TCCECH.04 |
| 10 | Dummy plates | 0 | No. | Not applicable at this location |

#### 5. Important Notes — Location 2

1. **As-built governs.** Demarcation from IZ-ADAC-056-2024-TO9-RT-02 as overlay only; all asset positions from the as-built survey (UTM 40N).
2. **No fittings inside the cut** — the electrical exposure at this location is the five crossing secondary runs and RRM.555; do not permit any widening of the demarcation without re-running the overlay check.
3. **Field additions.** TCCECH.03.007 and TCCECH.03.009 were field-identified (chained edge-circuit ducts not visible to the straight-line model) — treat the field-confirmed routes as governing and verify all five routes against the AGL duct-layout CAD (Rev B) before works.
4. **Isolation.** TCCECH.03 / TCCECH.04 isolated and proven dead before sawcut or milling over the crossing routes; the SBC102 and TCC103 circuits are unaffected here but their routes shall still be confirmed clear on the overlay.
5. **Protection during milling.** Crossing routes marked and capped at the cut line; AGL supervisor on standby; hand excavation only within 500 mm of any as-built duct alignment.
6. **Secondary cables.** Full manhole-to-light replacement, no joints; lengths indicative pending Rev B duct-layout re-measure.
7. **RRM.555** removed before sawcut, stored, and re-fixed to the reinstated surface on its original line; verify reflectivity/orientation on refit.
8. **Coordination, airside safety and records** as Location 1 Notes 8–10.

---

## A.3 — DRAWING 3 OF 3

### SHOP DRAWING – ELECTRICAL / AGL SCOPE
### TAXIWAY E (E4–E6) – LOCATION 3
### CIVIL MILLING AFFECTED AREA

#### 1. Drawing Identification

| Field | Detail |
|---|---|
| Drawing No. | [XXX-ELE-SHD-1003] Rev. [P02] — Scale [1:250] @ A1 |
| CAD File | `drawings/TWY-E-AGL-SHOPDWG-LOC03_UTM40N.dxf` (+ `_R12` variant) — as-built base layers, UTM 40N |
| Demarcation | L03-A: 255.28 m² |
| L03-A vertices (UTM 40N) | (260874.462, 2704679.034) · (260854.951, 2704694.694) · (260848.570, 2704686.736) · (260868.079, 2704671.070) |

#### 2. Reference Drawings / Documents

As Location 1 (Refs. R1–R5). Affected circuits at this location: **SBC102.01, SBC102.02, TCCECH.03, TCCECH.04**.

#### 3. Scope of Work — Location 3

- Overlay and confirm on site: **no fittings inside** the polygon; six near-edge assets (4 EP7 stop-bar inset lights and 2 RRMs).
- Near-edge EP7 stop-bar fittings (SBC102.01.038 @0.61 m, SBC102.01.039 @0.59 m, SBC102.02.035 @0.60 m, SBC102.02.036 @2.21 m): isolate circuit, remove fitting, install **dummy plate** on the retained base (bases confirmed affected per field rev _1); refit originals after paving.
- Remove / protect **RRM.557** (0.07 m — treat as within works, remove before sawcut) and **RRM.670** (0.73 m); re-fix after new asphalt.
- Isolate, lock out and prove dead circuits **SBC102.01, SBC102.02, TCCECH.03, TCCECH.04** under permit (12 secondary runs cross the cut: 4 via sawcut, 8 via duct).
- Mark all twelve crossing routes from the as-built overlay; cap/protect at the cut line; AGL supervisor on standby during milling.
- Replace the twelve affected secondary runs full-length manhole-to-light after paving; test and return to service as Location 1.

#### 4. Affected Assets Table — Location 3

| Item | Description | Quantity | Unit | Remarks |
|---|---|---|---|---|
| 1 | Saw cuts for secondary cable installation | 4 | Runs | SBC102.01.038/.039, SBC102.02.035/.036 (EP7 stop bar) |
| 2 | Main duct / conduit 12 inch inside demarcation | [TBD] | No. / m | Confirm against AGL duct-layout CAD (Ref. R2, Rev B) |
| 3 | Main duct / conduit 8 inch inside demarcation | [TBD] | No. / m | Confirm against AGL duct-layout CAD (Ref. R2, Rev B) |
| 4 | Coring-out locations inside demarcation | 0 | No. | No fittings inside polygon |
| 5 | Secondary cable runs to be replaced | 12 | Runs (358.5 m) | 4 via sawcut + 8 via duct — SBC102.01.038/.039/.040/.041, SBC102.02.035/.036/.037/.038, TCCECH.03.002/.003, TCCECH.04.002/.003 |
| 6 | Near-edge fittings — dummy plate on retained base | 4 | No. | SBC102.01.038/.039, SBC102.02.035/.036 — EP7 bases affected per field rev _1 |
| 7 | RRM — remove / protect / re-fix | 2 | No. | RRM.557 (0.07 m — remove before sawcut), RRM.670 (0.73 m) |
| 8 | Feed manholes / handholes serving affected runs | 4 | No. | HH.E.058, HH.E.059, HH.E.061, HH.E.144 — protect covers and frames |
| 9 | Circuits requiring isolation | 4 | Circuits | SBC102.01, SBC102.02, TCCECH.03, TCCECH.04 |
| 10 | Coring-out inside demarcation | 0 | No. | Dummy-plate method applies; bases retained |

#### 5. Important Notes — Location 3

1. **As-built governs**, Civil drawing as overlay only, as Location 1 Note 1.
2. **EP7 stop-bar bases.** Field rev _1 confirms the four EP7 shallow bases affected (closes Open Item 3); an earlier revision of the same field sheet recorded all bases unaffected — confirm rev _1 is current before works.
3. **RRM.557 sits 0.07 m from the cut** — treat as within the works; remove before the sawcut pass.
4. **Field additions.** SBC102.01.041, SBC102.02.037/.038 are field-identified chained EP7 duct runs not visible to the straight-line model — field-confirmed routes govern; verify against the AGL duct-layout CAD (Rev B).
5. **Isolation** of all four listed circuits, proven dead, before sawcut/milling over crossing routes.
6. **Protection during milling** as Location 1 Note 5 (12 crossing runs at this location).
7. **Secondary cables** — full manhole-to-light replacement, no joints; lengths indicative pending Rev B re-measure.
8. **Dummy plates** flush with surface, matched to the shallow-base bolt pattern, torqued to spec — protect bases and bolt threads under milling/paving traffic; originals refitted, levelled and torqued after paving.
9. **Coordination, airside safety and records** as Location 1 Notes 8–10.

---

# SECTION B — CONSOLIDATED MATERIAL REQUIREMENT SHEET

## TWY E (E4–E6) — Electrical / AGL Works — All Three Locations

| S.No | Material Description | Size / Spec | Unit | Total Required | Current Stock | Project Stock | To Be Ordered / Procured | Remarks |
|---|---|---|---|---|---|---|---|---|
| 1 | Secondary cable (match existing — L-824 style 2-core secondary, ADIA AGL spec; confirm size per circuit) | 600 V, 2-core | m | 1,350 | [ ] | [ ] | [ ] | 36 runs, 1,185.5 m manhole basis + 10 % spare, rounded to 50 m. Phase-1 portion (400 m) already ordered per site record — deduct from balance |
| 2 | Shallow bases (new, to replace cored-out bases) | 8-inch inset pattern per fitting schedule | No. | 18 | [ ] | [ ] | [ ] | 16 core-outs + 10 % spares (≈2). 9 already worked in Phase-1 |
| 3 | Epoxy grout sets (shallow base setting) | Per specification | Set | 18 | [ ] | [ ] | [ ] | One per new base incl. spares |
| 4 | Dummy plates (blanking plates, shallow-base bolt pattern) | Match base bolt pattern, flush | No. | 6 | [ ] | [ ] | [ ] | 2 at LOC-01 (pending verification) + 4 at LOC-03; none on cored bases |
| 5 | Secondary connector kits / re-terminations | FAA L-823 secondary | Set | 72 + 10 % = 80 | [ ] | [ ] | [ ] | 2 ends × 36 runs + spares |
| 6 | Core drilling bits / barrels | Ø to suit 8-inch shallow bases | No. | 2 | [ ] | [ ] | [ ] | Plus standby spare per machine |
| 7 | Diamond saw blades (asphalt, secondary cable sawcuts) | Per machine, full slot depth | No. | [ ] | [ ] | [ ] | [ ] | 15 sawcut runs (11 LOC-01 + 4 LOC-03) |
| 8 | Duct end caps / sealant plugs (secondary ducts at cut line) | To suit secondary ducts | No. | 56 + spares | [ ] | [ ] | [ ] | 28 crossings × 2 ends |
| 9 | Split protection sleeves (exposed secondary runs) | Ø 50–75 mm split type | m | [ ] | [ ] | [ ] | [ ] | Per exposed length at cut line |
| 10 | Fitting fixing bolts, washers, O-rings | Per fitting type (ADB inset 8-in) | Set | 24 | [ ] | [ ] | [ ] | 22 fittings worked (16 core-out + 2 reinstatement + 4 dummy LOC-03) + spares; no O-ring reuse |
| 11 | Steel plates / core covers (open-core protection) | To suit core Ø | No. | 16 | [ ] | [ ] | [ ] | One per open core until reinstatement |
| 12 | Clean washed sand / selected backfill | Per specification | m³ | [ ] | [ ] | [ ] | [ ] | Sawcut slot and core reinstatement |
| 13 | Pavement joint / fitting sealant | P-606 or approved equal | kg / cart. | [ ] | [ ] | [ ] | [ ] | Fittings and sawcut slots |
| 14 | RRM fixing adhesive / hardware | Per RRM type | Set | 4 | [ ] | [ ] | [ ] | 3 RRMs re-fixed + spare |
| 15 | LOTO sets (locks, tags, hasps) | — | Set | 8 | [ ] | [ ] | [ ] | 6 circuits + spares |
| 16 | Cable route warning tape | "ELECTRICAL CABLE" | m | [ ] | [ ] | [ ] | [ ] | Where trenched/backfilled runs occur |
| 17 | Marking paint / survey pins | Airside-approved | Lot | 1 | [ ] | [ ] | [ ] | Set-out of as-built alignments and core centres |
| 18 | IR / continuity test consumables & record sheets | 500 V / 1 kV / 5 kV regime | Lot | 1 | [ ] | [ ] | [ ] | Baseline + acceptance, 6 circuits |
| 19 | Isolating transformers (contingency spares) | Rating per fitting schedule | No. | [ ] | [ ] | [ ] | [ ] | Replacement of any unit damaged during works |
| 20 | FOD bins, dust sheets, cable end caps | — | Lot | 1 | [ ] | [ ] | [ ] | FOD prevention |

**Notes to Material Sheet:**
1. Cable quantity basis: manhole-to-light routes (ducts originate at AGL manholes), route × 1.10 + 2.0 m manhole slack + 1.5 m light tail, rounded up to 0.5 m — **indicative**; re-measure from the AGL duct-layout CAD (Rev B) before final procurement (Open Item 1). The earlier pit-based revision totalled 980 m (procure 1,100 m); the manhole basis (1,185.5 m → 1,350 m) is the governing figure for ordering.
2. "To Be Ordered / Procured" = Total Required − (Current Stock + Project Stock); Phase-1 quantities already ordered/consumed (400 m cable, 9 bases) to be deducted.
3. All materials to project specification and FAA AC 150/5345 series / ICAO Annex 14 as applicable; material approval required before use.
4. Long-lead items (shallow bases, L-823 kits, secondary cable) to be confirmed and ordered immediately upon Rev B quantity freeze.

---

# SECTION C — GENERAL METHODOLOGY NOTE

## TWY E (E4–E6) — Electrical / AGL Works Associated with Civil Milling — Basis of Set-Out and Measurement

**1. The as-built record is the base layer.**
The as-built AGL asset survey (`assets_20260726120533.xlsx`, 636 assets, UTM 40N / EPSG:32640) and the AGL duct-layout CAD constitute the single source of truth for the position, alignment and identity of all existing AGL assets — inset fittings, secondary circuits and ducts, feed manholes/handholes, RRMs. Every drawing in this package is constructed with this record as the base layer; every coordinate and asset position stated herein is taken from, and traceable to, it.

**2. The Civil demarcation is an overlay only.**
Civil drawing IZ-ADAC-056-2024-TO9-RT-02 serves one purpose: to define the demarcation limits of the three milling locations (total 920.02 m²). These boundaries were transformed onto the as-built UTM 40N grid and analysed by point-in-polygon plus a 3 m proximity band. The Civil drawing shall not be used to derive the position of any existing asset.

**3. All cutting, coring and cable works are measured only from as-built positions.**
Every core, dummy-plate position, cable route and crossing in this package derives from the as-built coordinates, verified by joint site inspection and the field team's affected-asset sheets (received 26.07.2026, reconciled 27.07.2026). Duct routes shown are **indicative** (straight-line light → nearest MH/HH); the duct-laid details shall be taken from the AGL duct-layout CAD (Rev B) before works and before final cable procurement. Reinstatement setting-out is by civil survey from the as-built Easting/Northing on the same datum as the DXF overlay (`TWY-E-AGL-IMPACT-OVERLAY_UTM40N.dxf`).

**4. Coordinate discipline — previous-phase issues shall not be repeated.**
Controls in force for this package: (a) one coordinate system — UTM 40N (EPSG:32640) — on all drawings, analysis and set-out; (b) desk study formally reconciled against field verification: 24 of 28 desk-study crossings field-confirmed, 8 field additions accepted, and the open conflicts (TCC103 ×4 inside the cut but absent from field lists; SBC102.01.026 desk-inside/field-unaffected) are held as stop-work items in the affected zone until jointly resolved; (c) boundary-sensitive fittings dimensioned to the cut line (TCCECH.03.035 at 2.30 m inside; SBC102.01.029 at 0.29 m outside; RRM.557 at 0.07 m) and verified on site before cutting; (d) all deviations red-lined and incorporated into the as-built update at completion.

**5. Hold points (Engineer's release required).**
(i) Joint overlay verification at each location; (ii) confirmation of the six-circuit isolation before first cut/core; (iii) inspection of capped ducts, protected cores and removed fittings before milling over them; (iv) survey setting-out check against adjacent undisturbed fittings before coring the new asphalt; (v) acceptance testing (IR, continuity, CCR function, photometric spot-check) before re-energisation and reopening.

---

*End of Package — Rev P02, 27.07.2026. Remaining [bracketed] items: formal drawing numbers, as-built duct-layout CAD reference (Rev B), 12-inch / 8-inch main duct data (pending Rev B), and stock/procurement balances.*
