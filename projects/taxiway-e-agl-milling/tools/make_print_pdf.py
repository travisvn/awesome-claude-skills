#!/usr/bin/env python3
"""Print / submission PDF — Rev P05 field-condition AGL shop drawings.
Vector A3 landscape, one page per location + cover + consolidated scope table."""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Circle, Rectangle, Polygon as MplPolygon

D = json.load(open("/tmp/claude-0/-home-user/aa0ed5d1-2db1-5aa5-a85c-5d1b22e050e8/scratchpad/dwg_data.json"))
OUT = "/home/user/awesome-claude-skills/projects/taxiway-e-agl-milling/drawings/TWY-E-AGL-SHOPDWG-RevP05_PRINT_A3.pdf"

NAVY, TEAL, GOLD = "#1E2761", "#0E7C86", "#C9A227"
RED, BLUE, ORANGE, GREEN = "#CC0000", "#0055CC", "#E8710A", "#1E8E3E"
CLGOLD, SBRED, EDGEGREY = "#C7A400", "#8B0000", "#7A8288"
MAGENTA, GREY, GREYD, ASSET, INK = "#BB00BB", "#9AA0A6", "#5F6368", "#12A5B8", "#1F2937"

ACTIONS = {
    "CORE_DUCT": (RED, BLUE, "CORE OUT + NEW CABLE (DUCT) — outer red / inner blue"),
    "CORE_SAW": (RED, ORANGE, "CORE OUT + NEW CABLE (SAWCUT) — outer red / inner orange"),
    "CABLE_DUCT": (BLUE, GREEN, "NEW SEC. CABLE ONLY (DUCT) — outer blue / inner green"),
    "CABLE_SAW": (ORANGE, GREEN, "NEW SEC. CABLE ONLY (SAWCUT) — outer orange / inner green"),
    "NOT_AFF": (GREY, None, "FIELD VERIFIED — NOT AFFECTED (grey)"),
    "RRM": (MAGENTA, "#FFFFFF", "RRM — REMOVE / PROTECT / RE-FIX (magenta / white)"),
}

META = {
    "LOC01": dict(no="1001", loc="LOCATION 1",
        sub="SCOPE PER FIELD SHEET Document_3 — FIELD CONDITION GOVERNS",
        scope=["CORE OUT SHALLOW BASE + NEW CABLE: 11 No.",
               "    VIA DUCT (6): SBC102-02/024, 01/027, 02/025, 01/028, 02/026, 01/029",
               "    VIA SAWCUT (5): TCCECH-04/034, 03/036, 04/035, 03/037, 04/036",
               "NEW SECONDARY CABLE ONLY: 3 No.",
               "    SBC102-02/027 (DUCT) · TCCECH-03/035, 03/018 (SAWCUT — bases OK,",
               "    verify at cut line)",
               "FIELD VERIFIED NOT AFFECTED: SBC102-01/026 (no works)",
               "TCC103 FITTINGS NOT IN FIELD SCOPE — SHOWN AS EXISTING ONLY",
               "ISOLATE CIRCUITS: SBC102.01/.02, TCCECH.03/.04",
               "SITE RECORD 23.07.2026: 9 cored + 2 reinstatement already worked"]),
    "LOC02": dict(no="1002", loc="LOCATION 2",
        sub="SCOPE PER FIELD SHEET Second_milling_area rev _1 — FIELD CONDITION GOVERNS",
        scope=["NEW SECONDARY CABLE ONLY (VIA DUCT): 5 No.",
               "    TCCECH-03/007, 04/007, 03/008, 04/008, 03/009",
               "NO SHALLOW BASES AFFECTED AT THIS LOCATION",
               "SECONDARY DUCT: CHAINED EDGE-CIRCUIT RUN HH.E.056 → 03/007 →",
               "    04/007 → 03/008 → 04/008 → 03/009 → HH.E.054 + SPUR FROM",
               "    HH.E.055 — INDICATIVE, CONFIRM VS DUCT-LAYOUT CAD (REV B)",
               "RRM.555 (0.41 m from cut): REMOVE / PROTECT BEFORE SAWCUT,",
               "    RE-FIX AFTER PAVING",
               "ISOLATE CIRCUITS: TCCECH.03, TCCECH.04"]),
    "LOC03": dict(no="1003", loc="LOCATION 3",
        sub="SCOPE PER FIELD SHEET Second_milling_area rev _1 — FIELD CONDITION GOVERNS (supersedes earlier all-NO rev)",
        scope=["NO CORING AT THIS LOCATION — SECONDARY CABLES ONLY (12 RUNS)",
               "NEW CABLE VIA SAWCUT: 4 No. — SBC102-01/038, 01/039, 02/035, 02/036",
               "    (EP7 STOP BAR — bases flagged per field rev _1: remove fitting &",
               "    protect base during works, NO coring)",
               "NEW SECONDARY CABLE ONLY (VIA DUCT): 8 No.",
               "    SBC102-01/040, 01/041, 02/037, 02/038,",
               "    TCCECH-03/002, 04/002, 03/003, 04/003",
               "RRM.557 (0.07 m — treat as within works) & RRM.670:",
               "    REMOVE / PROTECT / RE-FIX",
               "ISOLATE CIRCUITS: SBC102.01/.02, TCCECH.03/.04"]),
}

NOTES = [
    "1. All asset positions as-built (asset survey assets_20260726120533.xlsx,",
    "    UTM 40N / EPSG:32640).",
    "2. AGL works area (red) per field condition — rectangular strips aligned",
    "    to stop bar / centerline around field-verified affected assets.",
    "    Coring at Location 1 only.",
    "3. Secondary cables: no joints — full manhole-to-light replacement. Confirm",
    "    routes vs AGL duct-layout CAD (Rev B) before works.",
    "4. Isolate, lock out & prove dead all listed circuits at CCR under permit",
    "    before any cutting, coring or excavation.",
    "5. Reinstatement setting-out by civil survey from as-built E/N, checked",
    "    against adjacent undisturbed fittings before coring.",
    "6. Taxiway centerline & stop bar alignments derived from as-built AGL",
    "    fitting positions (TCC / SBC). Edge / pavement boundary indicative at",
    "    23 m width from as-built CL — confirm on site.",
]

A3 = (16.54, 11.69)
pdf = PdfPages(OUT)

# ---------------- cover ----------------
fig = plt.figure(figsize=A3)
ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
ax.add_patch(Rectangle((0, 0), 1, 1, color=NAVY))
ax.text(0.06, 0.80, "SHOP DRAWINGS — ELECTRICAL / AGL SCOPE", color="white", fontsize=34, weight="bold")
ax.text(0.06, 0.72, "RECTIFICATION OF TWY E BETWEEN E4 & E6 (ADIA)\nAGL WORKS AT THREE (3) MILLING LOCATIONS — FIELD CONDITION SCOPE",
        color="#CADCFC", fontsize=17, va="top", linespacing=1.5)
rows = [
    ("Document No.", "[XXX-ELE-SHD-1001 / 1002 / 1003]  ·  Revision P05 — PRINT / SUBMISSION ISSUE"),
    ("Basis of scope", "Field verification sheets: Document_3 (LOC-01) · Second_milling_area rev _1 (LOC-02/03)"),
    ("Base layer", "As-built AGL asset survey assets_20260726120533.xlsx — UTM 40N (EPSG:32640)"),
    ("Sheets", "1 of 4 Cover · 2 of 4 Location 1 · 3 of 4 Location 2 · 4 of 4 Location 3 · Annex A Scope Table"),
    ("Prepared by", "Mohammed — AGL Team Leader, ADB SAFEGATE AGL Team  ·  Issued 28.07.2026"),
]
y = 0.52
for k, v in rows:
    ax.text(0.06, y, k, color=GOLD, fontsize=12.5, weight="bold")
    ax.text(0.26, y, v, color="white", fontsize=12.5)
    y -= 0.05
ax.set_xlim(0, 1); ax.set_ylim(0, 1)
pdf.savefig(fig); plt.close(fig)

# ---------------- drawing sheets ----------------
for idx, loc in enumerate(["LOC01", "LOC02", "LOC03"], start=2):
    d, m = D[loc], META[loc]
    fig = plt.figure(figsize=A3)
    fig.patch.set_facecolor("white")
    fig.text(0.021, 0.972,
             "SHOP DRAWING — ELECTRICAL / AGL SCOPE (FIELD-GOVERNED)   ·   TAXIWAY E (E4–E6) — %s   ·   DWG NO [XXX-ELE-SHD-%s] REV P05   ·   SHEET %d OF 4"
             % (m["loc"], m["no"], idx), fontsize=10.8, weight="bold", color=NAVY, va="top")

    # ---- plan ----
    ax = fig.add_axes([0.05, 0.025, 0.587, 0.91])
    x0, y0, x1, y1 = d["bbox"]
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1)
    ax.set_aspect("equal", adjustable="datalim")
    ax.set_facecolor("white")
    for sp in ax.spines.values():
        sp.set_color(GREYD)
    ax.tick_params(labelsize=6, colors=GREYD, length=2)
    ax.grid(True, lw=0.25, color="#E3E6EA")
    ax.ticklabel_format(useOffset=False, style="plain")

    mk = d["marks"]
    for ch in mk["edge"]:
        ax.plot([q[0] for q in ch], [q[1] for q in ch], color=EDGEGREY, lw=1.0, zorder=1)
    for ch in mk["cl"]:
        ax.plot([q[0] for q in ch], [q[1] for q in ch], color=CLGOLD, lw=1.4, ls=(0, (9, 3, 2, 3)), zorder=1)
    for ch in mk["sb"]:
        ax.plot([q[0] for q in ch], [q[1] for q in ch], color=SBRED, lw=2.2, zorder=2)
    if mk["cl"]:
        c = mk["cl"][0][len(mk["cl"][0]) // 2]
        ax.annotate("TWY CENTERLINE (AS-BUILT TCC FITTINGS)", (c[0], c[1]), xytext=(6, 6),
                    textcoords="offset points", fontsize=5.5, color=CLGOLD, zorder=6)
    for l in d["ducts"]:
        ax.plot([l[0], l[2]], [l[1], l[3]], color="#C9CDD2", lw=0.6, ls=(0, (4, 3)), zorder=1)
    for l in d["cross"]:
        ax.plot([l[0], l[2]], [l[1], l[3]], color=MAGENTA, lw=1.1, ls=(0, (5, 3)), zorder=2)
    for p in d["pits"]:
        ax.add_patch(MplPolygon(p, closed=True, fill=False, ec=MAGENTA, lw=1.2, zorder=3))
    for t in d["pitlabels"]:
        ax.text(t[1], t[2], t[0], fontsize=5.5, color=MAGENTA, weight="bold", zorder=6)
    for wp in d["works"]:
        ax.add_patch(MplPolygon(wp, closed=True, fill=False, ec=RED, lw=2.0, zorder=4))
    tp = max((q for wp in d["works"] for q in wp), key=lambda q: q[1])
    ax.annotate("AGL WORKS AREA — FIELD CONDITION (%.1f m² TOTAL)" % d["works_area"],
                (tp[0], tp[1]), xytext=(-70, 16), textcoords="offset points",
                fontsize=7, color=RED, weight="bold", zorder=6)
    for a in d["assets"]:
        ax.add_patch(Circle((a[0], a[1]), 0.28, color=ASSET, zorder=5))
    for t in d["alabels"]:
        ax.text(t[1] + 0.3, t[2] - 0.35, t[0], fontsize=4.2, color="#AEB4BB", zorder=5)
    for act, items in d["scope"].items():
        co, ci, _ = ACTIONS[act]
        for it in items:
            x, yy = it[1], it[2]
            ax.add_patch(Circle((x, yy), 1.0, fill=False, ec=co, lw=1.8, zorder=7))
            if ci:
                ax.add_patch(Circle((x, yy), 0.5, color=ci, ec=ci, zorder=7))
            ax.annotate(it[0], (x, yy), xytext=(9, 7), textcoords="offset points",
                        fontsize=6, weight="bold", color=INK, zorder=8)
    ax.text(0.01, 0.012, "UTM 40N (EPSG:32640) — AS-BUILT POSITIONS · GRID = 10 m NOMINAL",
            transform=ax.transAxes, fontsize=6, style="italic", color=GREY)

    # ---- right panel ----
    px = fig.add_axes([0.655, 0.02, 0.335, 0.925]); px.axis("off")
    px.set_xlim(0, 1); px.set_ylim(0, 1)

    def panel_box(ytop, h, fc, ec="#D5DAE0"):
        px.add_patch(Rectangle((0, ytop - h), 1, h, facecolor=fc, edgecolor=ec, lw=0.8))
        return ytop - h

    yt = 1.0
    yb = panel_box(yt, 0.105, NAVY)
    px.text(0.03, yt - 0.026, "%s — %s  ·  REV P05 (PRINT ISSUE)" % (m["loc"], m["no"]),
            fontsize=11.5, weight="bold", color="white")
    px.text(0.03, yt - 0.055, m["sub"], fontsize=6.8, color="#CADCFC", wrap=True)
    px.text(0.03, yt - 0.085, "Scale 1:250 @ A1 equiv. · UTM 40N · Issued 28.07.2026 · Prepared: Mohammed, AGL Team Leader — ADB SAFEGATE",
            fontsize=6.2, color="#CADCFC")
    yt = yb - 0.012

    sc_h = 0.028 + len(m["scope"]) * 0.0195 + 0.012
    yb = panel_box(yt, sc_h, "#F4F6F8")
    px.text(0.03, yt - 0.021, "SCOPE / QUANTITIES (PER FIELD VERIFICATION)", fontsize=8.5, weight="bold", color=NAVY)
    yy = yt - 0.042
    for lnt in m["scope"]:
        px.text(0.03, yy, lnt, fontsize=6.6, color=INK)
        yy -= 0.0195
    yt = yb - 0.012

    nt_h = 0.028 + len(NOTES) * 0.0185 + 0.012
    yb = panel_box(yt, nt_h, "white")
    px.text(0.03, yt - 0.021, "GENERAL NOTES", fontsize=8.5, weight="bold", color=NAVY)
    yy = yt - 0.042
    for lnt in NOTES:
        px.text(0.03, yy, lnt, fontsize=6.2, color=GREYD)
        yy -= 0.0185
    yt = yb - 0.012

    acts = list(d["scope"].keys())
    extra = [("assetdot", "EXISTING AGL ASSET (AS-BUILT)"),
             ("ductind", "INDICATIVE DUCT — LIGHT TO NEAREST MH/HH"),
             ("cross", "SECONDARY DUCT RUN CROSSING CUT (INDICATIVE)"),
             ("hull", "AGL WORKS AREA — FIELD CONDITION (GOVERNING)"),
             ("pit", "AGL FEED MANHOLE / HANDHOLE"),
             ("mkcl", "TAXIWAY CENTERLINE (AS-BUILT, THROUGH TCC FITTINGS)"),
             ("mksb", "STOP BAR (AS-BUILT, THROUGH SBC FITTINGS)"),
             ("mkedge", "TWY EDGE / PAVEMENT BOUNDARY (INDICATIVE 23 m — CONFIRM ON SITE)")]
    extra = [e for e in extra if not (e[0] == "mksb" and not mk["sb"])]
    lg_h = 0.03 + (len(acts) + len(extra)) * 0.026 + 0.01
    yb = panel_box(yt, lg_h, "#F4F6F8")
    px.text(0.03, yt - 0.021, "LEGEND — WORKS ACTIONS (THIS SHEET)", fontsize=8.5, weight="bold", color=NAVY)
    yy = yt - 0.048
    for act in acts:
        co, ci, lab = ACTIONS[act]
        px.add_patch(Circle((0.06, yy + 0.004), 0.011, fill=False, ec=co, lw=1.8, transform=px.transData))
        if ci:
            px.add_patch(Circle((0.06, yy + 0.004), 0.0055, color=ci, transform=px.transData))
        px.text(0.11, yy, lab, fontsize=6.6, color=INK, va="center")
        yy -= 0.026
    for kind, lab in extra:
        if kind == "assetdot":
            px.add_patch(Circle((0.06, yy + 0.004), 0.005, color=ASSET))
        elif kind == "cross":
            px.plot([0.035, 0.085], [yy + 0.004] * 2, color=MAGENTA, lw=1.2, ls=(0, (5, 3)))
        elif kind == "hull":
            px.plot([0.035, 0.085], [yy + 0.004] * 2, color=RED, lw=2.0)
        elif kind == "pit":
            px.add_patch(Rectangle((0.045, yy - 0.004), 0.03, 0.016, fill=False, ec=MAGENTA, lw=1.2))
        elif kind == "ductind":
            px.plot([0.035, 0.085], [yy + 0.004] * 2, color="#C9CDD2", lw=0.8, ls=(0, (4, 3)))
        elif kind == "mkcl":
            px.plot([0.035, 0.085], [yy + 0.004] * 2, color=CLGOLD, lw=1.4, ls=(0, (9, 3, 2, 3)))
        elif kind == "mksb":
            px.plot([0.035, 0.085], [yy + 0.004] * 2, color=SBRED, lw=2.2)
        elif kind == "mkedge":
            px.plot([0.035, 0.085], [yy + 0.004] * 2, color=EDGEGREY, lw=1.0)
        px.text(0.11, yy, lab, fontsize=6.6, color=INK, va="center")
        yy -= 0.026

    pdf.savefig(fig); plt.close(fig)

# ---------------- annex: scope table ----------------
fig = plt.figure(figsize=A3)
ax = fig.add_axes([0.03, 0.03, 0.94, 0.9]); ax.axis("off")
fig.text(0.03, 0.965, "ANNEX A — CONSOLIDATED FIELD-GOVERNED SCOPE · TWY E (E4–E6) · REV P05",
         fontsize=17, weight="bold", color=NAVY, va="top")
actName = {"CORE_DUCT": "CORE OUT + NEW CABLE", "CORE_SAW": "CORE OUT + NEW CABLE",
           "CABLE_DUCT": "NEW CABLE ONLY", "CABLE_SAW": "NEW CABLE ONLY",
           "NOT_AFF": "NOT AFFECTED", "RRM": "RRM REMOVE / PROTECT"}
routeN = {"CORE_DUCT": "Duct", "CORE_SAW": "Sawcut", "CABLE_DUCT": "Duct",
          "CABLE_SAW": "Sawcut", "NOT_AFF": "—", "RRM": "—"}
remark = {"CORE_DUCT": "Core out shallow base + full manhole-to-light cable replacement",
          "CORE_SAW": "Core out shallow base + full manhole-to-light cable replacement",
          "CABLE_DUCT": "Full manhole-to-light cable replacement",
          "CABLE_SAW": "Full manhole-to-light cable replacement",
          "NOT_AFF": "Field verified — no works",
          "RRM": "Remove / protect before sawcut, re-fix after paving"}
cols = [0.0, 0.07, 0.22, 0.44, 0.52, 1.0]
head = ["Loc", "Asset", "Works Action", "Route", "Remarks"]
rows = []
for loc in ["LOC01", "LOC02", "LOC03"]:
    for act, items in D[loc]["scope"].items():
        for it in items:
            rows.append([loc.replace("LOC0", "LOC-0"), it[0], actName[act], routeN[act], remark[act]])
rh = 0.88 / (len(rows) + 1)
ax.add_patch(Rectangle((0, 0.9 - rh), 1, rh, color=NAVY))
for j, h in enumerate(head):
    ax.text(cols[j] + 0.005, 0.9 - rh / 2, h, fontsize=8.5, weight="bold", color="white", va="center")
for i, r in enumerate(rows):
    ytop = 0.9 - rh * (i + 1)
    if i % 2 == 1:
        ax.add_patch(Rectangle((0, ytop - rh), 1, rh, color="#F4F6F8"))
    for j, v in enumerate(r):
        ax.text(cols[j] + 0.005, ytop - rh / 2, v, fontsize=7.5,
                weight="bold" if j == 1 else "normal", color=INK, va="center")
ax.text(0, 0.9 - rh * (len(rows) + 1) - 0.02,
        "Totals: 11 core-outs (Location 1 only — no coring at Locations 2/3) · 31 secondary cable runs · 3 RRMs · 1 field-verified not affected.",
        fontsize=9.5, style="italic", color=GREYD)
ax.set_xlim(0, 1); ax.set_ylim(0, 1)
pdf.savefig(fig); plt.close(fig)

info = pdf.infodict()
info["Title"] = "TWY E (E4-E6) AGL Shop Drawings Rev P05 - Field-Governed Scope"
info["Author"] = "Mohammed - AGL Team Leader, ADB SAFEGATE AGL Team"
info["Subject"] = "Electrical / AGL scope of work - civil milling affected areas"
pdf.close()
print("WROTE", OUT)
