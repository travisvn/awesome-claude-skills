"""Sheet 2 — SCOPE OF WORK & SEQUENCE.

Carried over from the sheet the AGL Team Leader added after Rev P07 and updated
for the Rev P08 final scope. Three substantive changes to that text:

  * item 2 read "8" to SBC shallow base positions and 12" to TCC deep base can
    positions". The final scope makes every new base a SIDE-ENTRY SHALLOW BASE,
    8" at LOC-01 and 12" at LOC-02/03, so the diameters no longer split by
    fitting family and the "deep base can" wording is wrong.
  * item 5 read "through saw cut / new ducts provided by the civil team". No duct
    route remains in the AGL scope, so the alternative is gone.
  * the technical query's subject read "4 x 19 mm secondary duct". The source
    drawing layer is CV_OUTER/INNER DUCT 4x110mm dia and the LOC-02 sheet note
    says 4 x 110 mm, so 19 mm was a typo and is corrected here.

The hold-point reference "Item A3" is also corrected to A1 — the pre-asphalt list
has a single item and it is numbered A1.
"""

from pptx.util import Emu, Inches, Pt

from deckkit import BODY, NAVY
from sheetkit import footer, new_sheet, stack

RED = "B3261E"

SEQUENCE = [
    ("PRE-ASPHALT — AGL ATTENDANCE", True, NAVY),
    ("A1  Where secondary duct or secondary cable is laid by the civil team, a mandrel test is "
     "to be carried out on every duct and witnessed by the AGL team BEFORE asphalt laying. No "
     "asphalt to be laid over an unwitnessed duct.", False, BODY),
    ("POST-ASPHALT — AGL", True, NAVY),
    ("1.  AGL installation works to commence only after written confirmation from the civil "
     "team that the asphalt curing period is complete.", False, BODY),
    ("2.  Coring after setting-out coordinates are issued by the civil survey team — 8\" at "
     "Location 1 and 12\" at Locations 2 and 3. Core diameter per the sheet schedule; do not "
     "assume one diameter throughout.", False, BODY),
    ("3.  Saw cutting to commence only after the survey points are confirmed in the field by "
     "the civil survey team, and not before the saw cut detail drawing is issued. At Rev P08 "
     "EVERY secondary route at all three locations is saw cut — no duct route remains in the "
     "AGL scope.", False, BODY),
    ("4.  Installation of new bases — SIDE-ENTRY SHALLOW BASE throughout: 8\" at Location 1, "
     "12\" at Locations 2 and 3. At Location 2 the existing shallow base is cored out first.",
     False, BODY),
    ("5.  Laying of new secondary cable through the saw cut. No joints — full manhole-to-light "
     "replacement.", False, BODY),
    ("6.  Secondary cable termination, insulation resistance and continuity testing.", False, BODY),
    ("7.  Testing and commissioning of all affected circuits.", False, BODY),
    ("8.  Final functionality check, then handover to Operations for final inspection and "
     "return of the area to operational service.", False, BODY),
]

HOLD_POINTS = [
    ("H2   Curing complete — Civil.  Written confirmation of the asphalt curing period before "
     "AGL works start (Item 1).", False, BODY),
    ("H3   Setting-out — Civil survey.  Coordinates issued and field points confirmed before "
     "coring (Item 2) and before saw cutting (Item 3).", False, BODY),
    ("H4   Mandrel test — AGL witness.  Every duct laid by the civil team, before asphalt "
     "laying (Item A1).", False, BODY),
    ("H5   Functionality check — AGL / Operations.  Witnessed before handover (Item 8).",
     False, BODY),
    ("H6   Saw cut detail — AGL / Engineer.  No saw cutting before the saw cut and side-entry "
     "base detail drawing is issued and accepted (Rev P08).", False, RED),
]

QUERY = [
    ("Subject:  existing 4 x 110 mm secondary duct — cover, reuse and continuity", True, BODY),
    ("Field condition:  the existing 4 x 110 mm secondary duct bank was exposed at 50 mm "
     "milling depth.", False, BODY),
    ("Q1.  Confirmation required from the civil team before any duct is re-laid on the "
     "existing duct alignment.", False, BODY),
    ("Q2.  The existing duct cannot be reused for the new secondary cable. The existing cables "
     "are obsolete and are to be withdrawn, and the existing duct cross-section will not "
     "accommodate the new secondary cable.", False, BODY),
    ("Q3.  If new duct sized for the new secondary cable is laid within the construction area, "
     "confirmation is required from Civil on how the transition into the duct in the "
     "non-construction area is to be made. The same condition is expected over the full "
     "length, which would otherwise require saw cutting for the full length.", False, BODY),
]

PROPOSAL = [
    ("Lay a full-stretch new secondary duct sized to accommodate the new secondary cable, "
     "giving a continuous route end to end and minimising saw cutting in the finished "
     "pavement.", False, BODY),
    ("Status at Rev P08:  NOT ADOPTED. The final scope of work issued 30.07.2026 adopts SAW CUT "
     "for every secondary route at all three locations, which answers Q3 — the full length is "
     "saw cut and no new duct is laid under the AGL scope.", True, RED),
    ("Q1 and Q2 remain OPEN on the existing 4 x 110 mm duct bank: whether it is to be left in "
     "place, and confirmation that the obsolete cables are withdrawn. To be raised under RFI "
     "AUH-WP-AGL-TWYE-001. Not a construction instruction until answered.", False, BODY),
]


WHAT_CHANGED = [
    ("All secondary routes saw cut at all three locations; no duct route remains in the AGL "
     "scope.", False, BODY),
    ("All new bases are SIDE-ENTRY SHALLOW BASE — 8\" core at LOC-01, 12\" at LOC-02/03.",
     False, BODY),
    ("Affected fittings reduce from 30 to 16: LOC-01 11, LOC-02 1 (TCCECH-03/008), LOC-03 4 "
     "(TCC only).", False, BODY),
    ("Coring now applies at all three locations. Rev P06/P07 stated coring at Location 1 only.",
     False, RED),
]


def build(prs):
    slide = new_sheet(prs, "SCOPE OF WORK & SEQUENCE — TWY E (E4–E6)  ·  REV P08 (FINAL SCOPE)")

    lx, rx, cw = Inches(0.5), Inches(8.42), Inches(7.61)

    stack(slide, lx, Inches(1.00), cw, [
        ("SCOPE OF WORK — SEQUENCE OF AGL ACTIVITIES", SEQUENCE, 10.5, 8, Emu(0)),
        ("HOLD POINTS & WITNESS REQUIREMENTS", HOLD_POINTS, 10.5, 9, Emu(0)),
    ])

    stack(slide, rx, Inches(1.00), cw, [
        ("TECHNICAL QUERY — CONFIRMATION REQUIRED (NOT A CONSTRUCTION INSTRUCTION)",
         QUERY, 10.5, 9, Emu(0)),
        ("AGL TEAM PROPOSAL", PROPOSAL, 10.5, 9, Emu(0)),
        ("REV P08 — WHAT CHANGED", WHAT_CHANGED, 10.5, 8, Emu(0)),
    ])

    footer(slide,
           "Sequence and hold points apply to all three milling locations (sheets 1001, 1002, "
           "1003). Field condition governs. Where this sequence conflicts with a civil "
           "programme instruction, the AGL Team Leader is to be notified before work proceeds."
           "     ·     AUH-SK-AGL-TWYE-001 REV P08 (FINAL SCOPE)  ·  Prepared: Mohammed, AGL "
           "Team Leader — ADB SAFEGATE  ·  Approved: Ragesh Menon, AGL Manager")
    return slide
