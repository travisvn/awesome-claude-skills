# Coordinate system

## What the file actually says

| Item | Value |
|---|---|
| `$ACADVER` | AC1032 (AutoCAD 2018 format) |
| `$INSUNITS` | 6 → **metres** |
| `$EXTMIN` | −5869.378, 51833.130, −2672.388 |
| `$EXTMAX` | 9584.875, 76895.790, 337.109 |
| `$UCSORG` | 0, 0, 0 |
| `GEODATA` object | **absent** (zero occurrences in the file) |
| Model-space INSERTs | 12, all at (0,0,0), scale 1, rotation 0 |

Observed extent of extracted fixtures: X −8,116 → 9,486, Y 52,245 → 58,312.

## What this means

The drawing sits on a **local project grid in metres**, not a projected CRS. UTM Zone
40N for Abu Dhabi would put easting around 230,000–800,000 and northing around
2,650,000–2,750,000. Nothing here is close. There is no georeferencing object to read
a transform from, so the local → UTM relationship must come from a source outside this
file.

## Getting the transform

Two known points is the worst available method, not the minimum acceptable one. A
similarity transform has four unknowns (tx, ty, rotation, scale); two point pairs give
four equations, so the fit is exact by construction, the residuals are zero whatever the
points, and you learn nothing about accuracy. Do not do this.

Fit it by least squares over as many matched pairs as you can get:

1. **Match point sets.** You already hold 33,720 fixtures in local grid. If you also
   hold an AGL asset register in UTM 40N / EPSG:32640 describing the same physical
   lights, those are two point clouds of the same objects. Taxiway centreline runs at
   ~15 m spacing are a distinctive enough signature to register on.
2. **Solve a 4-parameter Helmert** (translation, rotation, uniform scale) by least
   squares. Not a full affine — an affine will absorb real error into fake shear and
   flatter you with a lower residual.
3. **Hold points back.** Fit on a subset, validate on pairs the fit never saw. The
   held-out residual RMS is your accuracy figure, and it is the number that belongs on
   the drawing.
4. **Read the fitted scale as a diagnostic.** A local grid derived from UTM by
   translation and rotation should return scale ≈ 1.0, or ≈ 0.9996 if a UTM grid scale
   factor is embedded. Anything else means the local grid is not a rigid transform of
   UTM and you have a different problem than the one you set out to solve.
5. **Confirm the datum on the receiving side.** Nahrwan 1967 and WGS84 differ by
   hundreds of metres in this region — a plausible-looking result is not a checked
   result.
6. **Sanity-check in Google Earth via KML** before it goes into an RFI or a client
   drawing.

ADA survey control is still worth having, as an independent check on the fitted
transform rather than as its only source.

Until this is done, label every coordinate from this skill **"ZIA local grid (m) — not
surveyed, not UTM"** on any drawing, table or register. That label is cheap. A milling
patch set out against an unverified transform is not.

## Most work does not need the transform at all

Fixtures, civil routes and MTA segmentation all come from the same DXF, and all twelve
source xrefs insert at identity (0,0,0 / scale 1 / rotation 0), so they are mutually
co-registered. Anything internal to the drawing needs no transform and no survey
control:

- is there secondary duct under this milling patch
- which conduit crosses segment TE5.1
- distance from this handhole to that duct run
- AGL asset count inside a bbox

The transform is only needed to join to an external register in UTM. Run the analysis in
local grid and transform at the last step, or avoid the coordinate join entirely.

## Vertical

`$EXTMIN`/`$EXTMAX` Z spans −2,672 to +337 m, which is not a real elevation range for an
airfield. Z values in this drawing are unreliable — some geometry carries junk Z. Treat
this as a **2D basemap only** and take levels from survey, never from here.
