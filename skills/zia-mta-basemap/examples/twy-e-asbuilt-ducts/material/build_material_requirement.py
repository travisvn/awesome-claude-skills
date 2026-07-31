from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

NAVY = "1E2761"; TINT = "F4F6F8"; RULE = "C8CDD3"
thin = Side(style="thin", color=RULE)
box = Border(left=thin, right=thin, top=thin, bottom=thin)

wb = Workbook()
ws = wb.active
ws.title = "Material Requirement"

def cell(r, c, v, *, bold=False, size=10, fill=None, align="left", wrap=False,
         color="1F2937", fmt=None, border=True):
    x = ws.cell(row=r, column=c, value=v)
    x.font = Font(name="Arial", size=size, bold=bold, color=color)
    if fill:
        x.fill = PatternFill("solid", fgColor=fill)
    x.alignment = Alignment(horizontal=align, vertical="center", wrap_text=wrap)
    if border:
        x.border = box
    if fmt:
        x.number_format = fmt
    return x

# ---------------------------------------------------------------- title block
cell(1, 1, "MATERIAL REQUIREMENT — AGL INSTALLATION", bold=True, size=14,
     color=NAVY, border=False)
cell(2, 1, "Rectification of TWY E between E4 & E6 (ZIA) — AGL works at three milling "
           "locations", size=10, color="5F6368", border=False)
meta = [
    ("Document No.", "AUH-SK-AGL-TWYE-001 — Rev P08 (final scope of work)"),
    ("Scope basis", "Rev P08 final scope of work issued 30.07.2026 — 19 No. affected fittings; "
                    "13 No. new side-entry shallow bases; approx. 420 m of saw cut"),
    ("Prepared by", "Mohammed Faheem — AGL Team Leader, ADB SAFEGATE"),
    ("Approved by", "Ragesh Menon — AGL Manager, ADB SAFEGATE"),
    ("Date", "31.07.2026"),
]
for i, (k, v) in enumerate(meta, start=4):
    cell(i, 1, k, bold=True, size=10, color="AD841F", border=False)
    cell(i, 2, v, size=10, border=False)

# ---------------------------------------------------------------- table
HDR = ["Sl No", "Material", "Unit", "Required Qty", "Available with ADB SAFEGATE",
       "Remaining Qty to procure", "Basis / check against the Rev P08 plan"]
HR = 10
for c, h in enumerate(HDR, start=1):
    cell(HR, c, h, bold=True, size=10, fill=NAVY, color="FFFFFF",
         align="center" if c != 7 else "left", wrap=True)

ROWS = [
    ("Nitoseal", "ltr", 20, 20,
     "Saw cut sealant. Against approx. 420 m of cut this is approx. 0.05 l/m — cannot be "
     "firmed until the saw cut detail fixes cut width and depth (hold point H5)."),
    ("Nito mortar", "ltr", 15, 15,
     "Grout / bedding to the new bases — 13 No. at approx. 1.15 l each. Depends on the core "
     "diameter, which is pending the same detail."),
    ("Backer rod", "Roll", 8, 8,
     "Approx. 400 m at 50 m/roll against approx. 420 m of saw cut — confirm the roll length; "
     "a 9th roll may be needed."),
    ("Shallow base 8 inch", "No", 11, 4,
     "Matches the plan: 11 No. 8\" side-entry shallow bases at LOC-01. The 3 No. cable-only "
     "fittings at LOC-01 keep their existing base and need none."),
    ("Earth cable", "Mtr", 900, 900,
     "As advised. No earthing quantity is derived in the Rev P08 deck."),
    ("Secondary connectors (plug & receptacle)", "Pair", 38, 33,
     "REVISED — 2 pair per fitting x 19 No. = 38 No. The 33 No. advised was against 16 No. "
     "fittings, before the 3 No. cable-only fittings at LOC-01 came into scope."),
    ("Secondary cable (2c x 4 sq.mm)", "mtr", 1500, 600,
     "1 No. 2-core 4 sq.mm cable to each fitting, SBC and TCC alike — 7 No. SBC and 12 No. "
     "TCC = 19 No. runs. Saw cut route length is approx. 420 m; 1500 m covers the full "
     "manhole-to-light runs (no joints) plus terminations and tails — confirm against the "
     "run-by-run lengths."),
    ("Masking tape", "Box", 50, 50,
     "As advised, for general protection. The signboard masking is by matt black vinyl "
     "sticker — see the separate line below."),
    ("Shallow base 12 inch", "No", 2, None,
     "ADDED — the plan needs 13 No. new bases: 11 No. 8\" plus 2 No. 12\" (LOC-02 "
     "TCCECH-03/008 and LOC-03 TCCECH-03/003). Not in the list as issued."),
    ("Vinyl sticker, matt black — signboard masking", "m²", None, None,
     "ADDED — masks the direction signboards leading to E4 and E6 under Phase 1, R4; removed "
     "in Phase 3 before the functionality check. Quantity depends on the number of sign faces "
     "and their area, which the deck does not carry — to be measured on site."),
    ("Dummy plate (8\" / 12\")", "No", 16, None,
     "ADDED — 13 No. open bases plus the 3 No. LOC-01 fittings kept under a plate during "
     "milling (Phase 1, R3). Confirm whether the plates already installed are recovered for "
     "reuse, and whether the 3 No. at LOC-03 also need one."),
]
r = HR + 1
for i, (mat, unit, req, avail, basis) in enumerate(ROWS, start=1):
    added = basis.startswith("ADDED")
    fill = "FFF4D6" if added else (TINT if i % 2 == 0 else None)
    cell(r, 1, i, align="center", fill=fill)
    cell(r, 2, mat, fill=fill, wrap=True)
    cell(r, 3, unit, align="center", fill=fill)
    cell(r, 4, req, align="center", fill=fill, fmt="#,##0")
    cell(r, 5, avail, align="center", fill="FFFF00" if avail is None else fill, fmt="#,##0")
    cell(r, 6, f"=IF(E{r}=\"\",\"\",D{r}-E{r})", align="center", fill=fill, fmt="#,##0",
         bold=True)
    cell(r, 7, basis, size=9, wrap=True, color="5F6368", fill=fill)
    r += 1

TOT = r
cell(TOT, 1, "", fill=TINT)
cell(TOT, 2, "Lines to procure", bold=True, fill=TINT)
cell(TOT, 3, "", fill=TINT)
cell(TOT, 4, "", fill=TINT)
cell(TOT, 5, "", fill=TINT)
cell(TOT, 6, f"=COUNTIF(F{HR+1}:F{TOT-1},\">0\")", bold=True, align="center", fill=TINT)
cell(TOT, 7, "Count of lines with a shortfall against the required quantity.", size=9,
     color="5F6368", wrap=True, fill=TINT)

# ---------------------------------------------------------------- notes
n = TOT + 2
cell(n, 1, "NOTES", bold=True, size=11, color=NAVY, border=False)
NOTES = [
    "1.  Rows 1–8 are the quantities as advised. Rows 9 to 11 are added, and the connector "
    "quantity is revised, so the list covers what the Rev P08 plan requires. Availability "
    "of the added lines is to be filled in (yellow cells).",
    "2.  The plan needs 13 No. new side-entry shallow bases in total — 11 No. 8\" at LOC-01, "
    "1 No. 12\" at LOC-02 (TCCECH-03/008) and 1 No. 12\" at LOC-03 (TCCECH-03/003).",
    "3.  Sealant, mortar and backer rod quantities depend on the saw cut width and depth and on "
    "the core diameter. Both are set by the saw cut & side-entry shallow base detail drawing, "
    "which had not been issued at Rev P08 (hold point H5). Re-check these three lines when it "
    "is issued.",
    "4.  One 2-core 4 sq.mm secondary cable serves each fitting, SBC and TCC alike — 7 No. SBC "
    "and 12 No. TCC. Cable is ordered against the full manhole-to-light runs (19 No.), not the "
    "saw cut length — the cut measures approx. 420 m across the three locations (approx. 300 m "
    "LOC-01, 24 m LOC-02, 95 m LOC-03).",
    "5.  Saw cut is an interim arrangement agreed between the AGL team, the civil team and "
    "ADA AGL. Permanent duct provision follows under the South Rehabilitation works, and is "
    "not covered by this requirement.",
    "6.  The direction signboards leading to E4 and E6 are masked with matt black vinyl "
    "sticker under Phase 1 (R4) and unmasked in Phase 3 before the functionality check. The "
    "vinyl quantity depends on the number of sign faces and their area — measure on site "
    "before ordering.",
    "7.  Testing and commissioning is carried out at circuit level and covers the affected "
    "fittings together with the fittings on the same circuits that fall outside these works — "
    "the series circuits are proved end to end before handover.",
    "8.  Remaining Qty is a formula (Required − Available). Edit only the Required and "
    "Available columns.",
]
for i, t in enumerate(NOTES):
    c = cell(n + 1 + i, 1, t, size=9, color="5F6368", wrap=True, border=False)
    ws.merge_cells(start_row=n + 1 + i, start_column=1, end_row=n + 1 + i, end_column=7)
    c.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
    ws.row_dimensions[n + 1 + i].height = 26

for col, w in zip("ABCDEFG", (7, 34, 8, 13, 16, 15, 62)):
    ws.column_dimensions[col].width = w
for rr in range(HR, TOT + 1):
    ws.row_dimensions[rr].height = 34
ws.row_dimensions[HR].height = 42
ws.freeze_panes = "A11"
ws.print_title_rows = "10:10"
ws.page_setup.orientation = "landscape"
ws.page_setup.fitToWidth = 1
ws.sheet_properties.pageSetUpPr.fitToPage = True

wb.save("Material Requirement - TWY E AGL Installation - Rev P08.xlsx")
print("saved")
