#!/usr/bin/env python3
"""Field-condition AGL shop drawings — Rev P04 (civil details removed).

Scope membership per FIELD VERIFICATION SHEETS (Document_3 for LOC-01;
Second_milling_area rev _1 for LOC-02/LOC-03) — field data governs over
civil / desk coordinates. The works demarcation is redrawn around the
field-affected assets (convex hull + 2.0 m); the civil milling polygon is
retained on a dashed reference layer only. Every asset position is as-built
(asset survey / overlay DXF, UTM 40N). Each works action has its own
compound symbol (outer/inner circle colours) and its own legend entry.
"""
import os
import json
import ezdxf
from shapely.geometry import MultiPoint

SRC = "/root/.claude/uploads/aa0ed5d1-2db1-5aa5-a85c-5d1b22e050e8/8d7ca18c-TWYEAGLIMPACTOVERLAY_UTM40N.dxf"
OUT = "/home/user/awesome-claude-skills/projects/taxiway-e-agl-milling/drawings"
os.makedirs(OUT, exist_ok=True)
MARGIN = 30.0
BUF = 2.0  # works demarcation buffer around affected assets (m)

# ---- as-built coordinates (asset survey / overlay DXF, UTM 40N) ----
XY = {
    "SBC102-01/026": (261130.071, 2704469.540), "SBC102-01/027": (261126.314, 2704464.859),
    "SBC102-01/028": (261122.556, 2704460.179), "SBC102-01/029": (261118.799, 2704455.499),
    "SBC102-02/024": (261128.192, 2704467.200), "SBC102-02/025": (261124.435, 2704462.519),
    "SBC102-02/026": (261120.678, 2704457.839), "SBC102-02/027": (261116.977, 2704453.174),
    "TCCECH-03/018": (261125.704, 2704459.607), "TCCECH-03/035": (261125.221, 2704459.542),
    "TCCECH-03/036": (261135.446, 2704448.575), "TCCECH-03/037": (261144.010, 2704436.274),
    "TCCECH-04/034": (261130.541, 2704454.245), "TCCECH-04/035": (261139.947, 2704442.571),
    "TCCECH-04/036": (261147.631, 2704429.700),
    "TCCECH-03/007": (260922.272, 2704622.948), "TCCECH-04/007": (260933.955, 2704613.556),
    "TCCECH-03/008": (260945.665, 2704604.147), "TCCECH-04/008": (260957.377, 2704594.758),
    "TCCECH-03/009": (260969.063, 2704585.374),
    "SBC102-01/038": (260852.411, 2704692.495), "SBC102-01/039": (260848.647, 2704687.783),
    "SBC102-01/040": (260844.902, 2704683.114), "SBC102-01/041": (260841.134, 2704678.432),
    "SBC102-02/035": (260850.527, 2704690.141), "SBC102-02/036": (260846.783, 2704685.439),
    "SBC102-02/037": (260843.011, 2704680.776), "SBC102-02/038": (260839.265, 2704676.090),
    "TCCECH-03/002": (260846.204, 2704683.980), "TCCECH-04/002": (260852.058, 2704679.310),
    "TCCECH-03/003": (260857.920, 2704674.589), "TCCECH-04/003": (260863.744, 2704669.882),
    "RRM.555": (260930.020, 2704633.469), "RRM.557": (260871.990, 2704681.111),
    "RRM.670": (260860.795, 2704690.943),
}

# ---- works actions: layer, outer colour, inner colour, legend text ----
ACTIONS = {
    "CORE_DUCT": ("ACT_CORE_DUCT", 1, 5, "CORE OUT SHALLOW BASE + NEW SEC. CABLE (VIA DUCT) - OUTER RED / INNER BLUE"),
    "CORE_SAW":  ("ACT_CORE_SAW", 1, 30, "CORE OUT SHALLOW BASE + NEW SEC. CABLE (VIA SAWCUT) - OUTER RED / INNER ORANGE"),
    "CABLE_DUCT": ("ACT_CABLE_DUCT", 5, 3, "NEW SECONDARY CABLE ONLY (VIA DUCT) - OUTER BLUE / INNER GREEN"),
    "CABLE_SAW": ("ACT_CABLE_SAW", 30, 3, "NEW SECONDARY CABLE ONLY (VIA SAWCUT) - OUTER ORANGE / INNER GREEN"),
    "NOT_AFF":   ("ACT_NOT_AFFECTED", 8, None, "FIELD VERIFIED - NOT AFFECTED (NO WORKS) - GREY"),
    "RRM":       ("ACT_RRM", 6, 7, "RRM - REMOVE / PROTECT / RE-FIX - OUTER MAGENTA / INNER WHITE"),
}

# ---- field-governed scope ----
LOCATIONS = {
    "LOC01": {
        "title2": "TAXIWAY E (E4-E6) - LOCATION 1 - AGL WORKS PER FIELD VERIFICATION (Document_3)",
        "dwgno": "XXX-ELE-SHD-1001 REV P05",
        "scope": {
            "CORE_DUCT": ["SBC102-02/024", "SBC102-01/027", "SBC102-02/025", "SBC102-01/028",
                          "SBC102-02/026", "SBC102-01/029"],
            "CORE_SAW":  ["TCCECH-04/034", "TCCECH-03/036", "TCCECH-04/035", "TCCECH-03/037",
                          "TCCECH-04/036"],
            "CABLE_DUCT": ["SBC102-02/027"],
            "CABLE_SAW": ["TCCECH-03/035", "TCCECH-03/018"],
            "NOT_AFF":   ["SBC102-01/026"],
        },
        "civil": [[(261122.260, 2704464.861), (261122.325, 2704464.809), (261123.561, 2704466.351),
                   (261127.949, 2704471.804), (261131.299, 2704469.101), (261126.903, 2704463.653),
                   (261125.677, 2704462.123), (261155.019, 2704438.606), (261147.846, 2704430.207),
                   (261116.608, 2704457.825)]],
        "notes": [
            "SCOPE PER FIELD SHEET Document_3 (15 ROWS) - FIELD CONDITION GOVERNS.",
            "CORE OUT SHALLOW BASE + NEW CABLE: 11 No. - 6 VIA DUCT (SBC102-02/024, 01/027, 02/025, 01/028, 02/026, 01/029) + 5 VIA SAWCUT (TCCECH-04/034, 03/036, 04/035, 03/037, 04/036)",
            "NEW SECONDARY CABLE ONLY: 3 No. - SBC102-02/027 (DUCT), TCCECH-03/035 & 03/018 (SAWCUT - BASES NOT AFFECTED, VERIFY AT CUT LINE)",
            "FIELD VERIFIED NOT AFFECTED: SBC102-01/026 (NO CABLE / NO BASE WORKS)",
            "TCC103 CIRCUIT FITTINGS NOT IN FIELD SCOPE - SHOWN AS EXISTING ONLY",
            "ISOLATE CIRCUITS: SBC102.01, SBC102.02, TCCECH.03, TCCECH.04 - PROVE DEAD BEFORE WORKS",
            "SITE RECORD 23.07.2026: 9 CORED OUT + 2 REINSTATEMENT FITTINGS ALREADY WORKED AT THIS LOCATION",
        ],
    },
    "LOC02": {
        "title2": "TAXIWAY E (E4-E6) - LOCATION 2 - AGL WORKS PER FIELD VERIFICATION (Second_milling_area rev _1)",
        "dwgno": "XXX-ELE-SHD-1002 REV P05",
        "scope": {
            "CABLE_DUCT": ["TCCECH-03/007", "TCCECH-04/007", "TCCECH-03/008", "TCCECH-04/008",
                           "TCCECH-03/009"],
            "RRM": ["RRM.555"],
        },
        "civil": [[(260955.518, 2704616.358), (260947.994, 2704606.892), (260934.696, 2704617.442),
                   (260942.218, 2704626.932)],
                  [(260929.690, 2704633.714), (260928.920, 2704634.344), (260928.289, 2704633.559),
                   (260929.066, 2704632.932)]],
        "notes": [
            "SCOPE PER FIELD SHEET Second_milling_area rev _1 (LOCATION-02, 5 ROWS) - FIELD CONDITION GOVERNS.",
            "NEW SECONDARY CABLE ONLY (VIA DUCT): 5 No. - TCCECH-03/007, 04/007, 03/008, 04/008, 03/009. NO SHALLOW BASES AFFECTED.",
            "SECONDARY DUCT: CHAINED EDGE-CIRCUIT RUN HH.E.056 > 03/007 > 04/007 > 03/008 > 04/008 > 03/009 > HH.E.054, SPUR FROM HH.E.055 - INDICATIVE, CONFIRM VS DUCT-LAYOUT CAD (REV B)",
            "RRM.555: REMOVE / PROTECT BEFORE SAWCUT, RE-FIX ON ORIGINAL LINE AFTER PAVING",
            "ISOLATE CIRCUITS: TCCECH.03, TCCECH.04 - PROVE DEAD BEFORE WORKS",
        ],
    },
    "LOC03": {
        "title2": "TAXIWAY E (E4-E6) - LOCATION 3 - AGL WORKS PER FIELD VERIFICATION (Second_milling_area rev _1)",
        "dwgno": "XXX-ELE-SHD-1003 REV P05",
        "scope": {
            "CABLE_SAW": ["SBC102-01/038", "SBC102-01/039", "SBC102-02/035", "SBC102-02/036"],
            "CABLE_DUCT": ["SBC102-01/040", "SBC102-01/041", "SBC102-02/037", "SBC102-02/038",
                           "TCCECH-03/002", "TCCECH-04/002", "TCCECH-03/003", "TCCECH-04/003"],
            "RRM": ["RRM.557", "RRM.670"],
        },
        "civil": [[(260874.462, 2704679.034), (260854.951, 2704694.694), (260848.570, 2704686.736),
                   (260868.079, 2704671.070)]],
        "notes": [
            "SCOPE PER FIELD SHEET Second_milling_area rev _1 (12 ROWS) - FIELD CONDITION GOVERNS. rev _1 SUPERSEDES EARLIER REV (ALL-NO).",
            "NO CORING AT THIS LOCATION - SECONDARY CABLES ONLY (12 RUNS)",
            "NEW CABLE VIA SAWCUT: 4 No. - SBC102-01/038, 01/039, 02/035, 02/036 (EP7 STOP BAR). BASES FLAGGED AFFECTED PER FIELD rev _1: REMOVE FITTING & PROTECT BASE DURING WORKS - NO CORING.",
            "NEW SECONDARY CABLE ONLY (VIA DUCT): 8 No. - SBC102-01/040, 01/041, 02/037, 02/038, TCCECH-03/002, 04/002, 03/003, 04/003",
            "RRM.557 & RRM.670: REMOVE / PROTECT BEFORE SAWCUT, RE-FIX ON ORIGINAL LINE AFTER PAVING",
            "ISOLATE CIRCUITS: SBC102.01, SBC102.02, TCCECH.03, TCCECH.04 - PROVE DEAD BEFORE WORKS",
        ],
    },
}

COMMON_NOTES = [
    "1. BASE LAYER: AS-BUILT AGL ASSET SURVEY assets_20260726120533.xlsx (636 ASSETS, UTM 40N / EPSG:32640). ALL ASSET POSITIONS AS-BUILT.",
    "2. AGL WORKS AREA (RED) PER FIELD CONDITION - RECTANGULAR STRIPS ALIGNED TO STOP BAR / CENTERLINE AROUND FIELD-VERIFIED AFFECTED ASSETS. CORING AT LOCATION 1 ONLY.",
    "3. DUCT ROUTES INDICATIVE (LIGHT -> NEAREST MH/HH). CONFIRM AGAINST AGL DUCT-LAYOUT CAD (REV B) BEFORE WORKS.",
    "4. SECONDARY CABLES: NO JOINTS PERMITTED - FULL MANHOLE-TO-LIGHT REPLACEMENT.",
    "5. ISOLATE, LOCK OUT & PROVE DEAD ALL LISTED CIRCUITS AT CCR UNDER PERMIT BEFORE ANY CUTTING, CORING OR EXCAVATION.",
    "6. REINSTATEMENT SETTING-OUT BY CIVIL SURVEY FROM AS-BUILT EASTING/NORTHING (UTM 40N), CHECKED AGAINST ADJACENT UNDISTURBED FITTINGS BEFORE CORING.",
    "7. TAXIWAY CENTERLINE & STOP BAR ALIGNMENTS DERIVED FROM AS-BUILT AGL FITTING POSITIONS (TCC / SBC). EDGE / PAVEMENT BOUNDARY INDICATIVE AT 23 m WIDTH FROM AS-BUILT CL - CONFIRM ON SITE.",
]

MARKS = json.load(open("/tmp/claude-0/-home-user/aa0ed5d1-2db1-5aa5-a85c-5d1b22e050e8/scratchpad/dwg_data.json"))
src = ezdxf.readfile(SRC)
smsp = src.modelspace()
src_layers = {l.dxf.name: (l.dxf.color, l.dxf.linetype) for l in src.layers}
# base layers copied from the as-built overlay (existing context only)
BASE_LAYERS = {"AGL_ASSETS_ALL", "LABELS_ASSETS_ALL", "DUCTS_INDICATIVE_ALL", "DUCTS_CROSSING",
               "AGL_FEED_PITS"}


def ent_points(e):
    t = e.dxftype()
    if t == "CIRCLE":
        c = e.dxf.center
        return [(c.x, c.y)]
    if t == "LINE":
        return [(e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)]
    if t == "TEXT":
        p = e.dxf.insert
        return [(p.x, p.y)]
    if t == "LWPOLYLINE":
        return [(p[0], p[1]) for p in e.get_points("xy")]
    if t == "POLYLINE":
        return [(v.dxf.location.x, v.dxf.location.y) for v in e.vertices]
    return []


def build(loc_key, cfg, version):
    doc = ezdxf.new(version, setup=True)
    if version != "R12":
        doc.header["$INSUNITS"] = 6
    for name, (color, lt) in src_layers.items():
        if name not in BASE_LAYERS:
            continue
        if lt not in doc.linetypes:
            lt = "CONTINUOUS"
        doc.layers.add(name, color=color, linetype=lt)
    doc.layers.add("AGL_WORKS_DEMARCATION", color=1)
    doc.layers.add("MARK_CENTERLINE", color=2, linetype="DASHDOT" if "DASHDOT" in doc.linetypes else "CONTINUOUS")
    doc.layers.add("MARK_STOPBAR", color=12)
    doc.layers.add("MARK_EDGE", color=8)
    doc.layers.add("LABELS_WORKS", color=7)
    doc.layers.add("TITLE", color=7)
    for key, (layer, co, ci, _txt) in ACTIONS.items():
        doc.layers.add(layer, color=co)
    msp = doc.modelspace()

    # bbox from field scope + civil polygons
    pts = [XY[n] for lst in cfg["scope"].values() for n in lst]
    pts += [p for poly in cfg["civil"] for p in poly]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    bb = (min(xs) - MARGIN, min(ys) - MARGIN, max(xs) + MARGIN, max(ys) + MARGIN)
    x0, y0, x1, y1 = bb

    def add_poly(pl, close, attribs):
        if version == "R12":
            msp.add_polyline2d(pl, close=close, dxfattribs=attribs)
        else:
            msp.add_lwpolyline(pl, close=close, dxfattribs=attribs)

    # ---- as-built base (existing context) copied verbatim from the overlay ----
    for e in smsp:
        if e.dxf.layer not in BASE_LAYERS:
            continue
        t = e.dxftype()
        p = ent_points(e)
        if not p or not any(x0 <= x <= x1 and y0 <= y <= y1 for x, y in p):
            continue
        a = {"layer": e.dxf.layer}
        if t == "CIRCLE":
            msp.add_circle(p[0], e.dxf.radius, dxfattribs=a)
        elif t == "LINE":
            msp.add_line(p[0], p[1], dxfattribs=a)
        elif t == "TEXT":
            a["height"] = e.dxf.height
            a["rotation"] = e.dxf.rotation
            msp.add_text(e.dxf.text, dxfattribs=a).dxf.insert = p[0]
        elif t in ("LWPOLYLINE", "POLYLINE"):
            add_poly(p, e.is_closed if t == "POLYLINE" else e.closed, a)

    # ---- as-built taxiway markings (derived from TCC / SBC fittings) ----
    mk = MARKS[loc_key]["marks"]
    for ch in mk["cl"]:
        add_poly(ch, False, {"layer": "MARK_CENTERLINE"})
    for ch in mk["sb"]:
        add_poly(ch, False, {"layer": "MARK_STOPBAR"})
    for ch in mk["edge"]:
        add_poly(ch, False, {"layer": "MARK_EDGE"})
    if mk["cl"]:
        c = mk["cl"][0][0]
        msp.add_text("TWY CENTERLINE (AS-BUILT TCC FITTINGS)",
                     dxfattribs={"layer": "MARK_CENTERLINE", "height": 0.6}).dxf.insert = (c[0] + 1.0, c[1] + 1.0)

    # ---- AGL works area (field condition) ----
    works = MARKS[loc_key]["works"]
    area = MARKS[loc_key]["works_area"]
    for wp in works:
        add_poly(wp, True, {"layer": "AGL_WORKS_DEMARCATION"})
    lab_pt = max((p for wp in works for p in wp), key=lambda p: p[1])
    msp.add_text("AGL WORKS AREA - FIELD CONDITION (%.1f m2 TOTAL)" % area,
                 dxfattribs={"layer": "AGL_WORKS_DEMARCATION", "height": 0.7}).dxf.insert = (lab_pt[0] - 15, lab_pt[1] + 1.5)

    # ---- works action symbols (compound circles) + labels ----
    for key, names in cfg["scope"].items():
        layer, co, ci, _t = ACTIONS[key]
        for n in names:
            x, y = XY[n]
            msp.add_circle((x, y), 1.0, dxfattribs={"layer": layer, "color": co})
            if ci is not None:
                msp.add_circle((x, y), 0.55, dxfattribs={"layer": layer, "color": ci})
            msp.add_text(n, dxfattribs={"layer": "LABELS_WORKS", "height": 0.55}).dxf.insert = (x + 1.3, y + 1.0)

    # ---- title block, notes, legend ----
    tx, ty = x0, y0 - 4.0
    H1, H2, HN = 1.6, 1.0, 0.7

    def line(text, h, dy, layer="TITLE"):
        nonlocal ty
        ty -= dy
        msp.add_text(text, dxfattribs={"layer": layer, "height": h}).dxf.insert = (tx, ty)

    line("SHOP DRAWING - ELECTRICAL / AGL SCOPE (FIELD-GOVERNED)", H1, H1 * 1.5)
    line(cfg["title2"], H2, H2 * 1.8)
    line("DWG NO: %s  ·  SCALE 1:250 @ A1  ·  UTM 40N (EPSG:32640)  ·  ISSUED 28.07.2026  ·  PREPARED: MOHAMMED, AGL TEAM LEADER - ADB SAFEGATE AGL TEAM" % cfg["dwgno"], HN, HN * 2.2)
    line("REFS: FIELD SHEETS Document_3 / Second_milling_area rev _1 (26.07.2026) · AS-BUILT ASSET SURVEY assets_20260726120533.xlsx", HN, HN * 1.8)

    ty -= 1.2
    line("SCOPE / QUANTITIES (PER FIELD VERIFICATION)", H2, H2 * 1.8)
    for n in cfg["notes"]:
        line(n, HN, HN * 1.15 + 0.35)

    ty -= 1.2
    line("GENERAL NOTES", H2, H2 * 1.8)
    for n in COMMON_NOTES:
        line(n, HN, HN * 1.15 + 0.35)

    ty -= 1.2
    line("LEGEND - WORKS ACTIONS (THIS SHEET)", H2, H2 * 1.8)
    for key in cfg["scope"]:
        layer, co, ci, txt = ACTIONS[key]
        ty -= 2.2
        msp.add_circle((tx + 1.0, ty + 0.35), 1.0, dxfattribs={"layer": layer, "color": co})
        if ci is not None:
            msp.add_circle((tx + 1.0, ty + 0.35), 0.55, dxfattribs={"layer": layer, "color": ci})
        msp.add_text(txt, dxfattribs={"layer": "TITLE", "height": HN}).dxf.insert = (tx + 3.0, ty)
    # base-context legend rows
    for name, sample, txt in [
        ("AGL_ASSETS_ALL", "circle", "EXISTING AGL ASSET (AS-BUILT)"),
        ("DUCTS_CROSSING", "lineD", "SECONDARY DUCT RUN CROSSING CUT (INDICATIVE)"),
        ("DUCTS_INDICATIVE_ALL", "lineD", "INDICATIVE DUCT - LIGHT TO NEAREST PIT"),
        ("AGL_WORKS_DEMARCATION", "rect", "AGL WORKS AREA - FIELD CONDITION (GOVERNING)"),
        ("AGL_FEED_PITS", "rect", "AGL FEED MANHOLE / HANDHOLE"),
        ("MARK_CENTERLINE", "lineD", "TAXIWAY CENTERLINE (AS-BUILT, THROUGH TCC FITTINGS)"),
        ("MARK_STOPBAR", "lineD", "STOP BAR (AS-BUILT, THROUGH SBC FITTINGS)"),
        ("MARK_EDGE", "lineD", "TAXIWAY EDGE / PAVEMENT BOUNDARY (INDICATIVE 23 m - CONFIRM ON SITE)"),
    ]:
        if name == "MARK_STOPBAR" and not MARKS[loc_key]["marks"]["sb"]:
            continue
        ty -= 2.2
        if sample == "circle":
            msp.add_circle((tx + 1.0, ty + 0.35), 0.5, dxfattribs={"layer": name})
        elif sample == "lineD":
            msp.add_line((tx, ty + 0.35), (tx + 2.0, ty + 0.35), dxfattribs={"layer": name})
        else:
            add_poly([(tx, ty), (tx + 2.0, ty), (tx + 2.0, ty + 0.8), (tx, ty + 0.8)], True, {"layer": name})
        msp.add_text(txt, dxfattribs={"layer": "TITLE", "height": HN}).dxf.insert = (tx + 3.0, ty)

    suffix = "_R12" if version == "R12" else ""
    out = os.path.join(OUT, "TWY-E-AGL-SHOPDWG-%s_UTM40N%s.dxf" % (loc_key, suffix))
    doc.saveas(out)
    return out, area


for key, cfg in LOCATIONS.items():
    for ver in ("R2000", "R12"):
        out, area = build(key, cfg, ver)
    n_core = len(cfg["scope"].get("CORE_DUCT", [])) + len(cfg["scope"].get("CORE_SAW", []))
    n_cab = len(cfg["scope"].get("CABLE_DUCT", [])) + len(cfg["scope"].get("CABLE_SAW", []))
    print("%s: works demarcation %.1f m2 · core-outs %d · cable-only %d · RRM %d · not-affected %d" %
          (key, area, n_core, n_cab, len(cfg["scope"].get("RRM", [])), len(cfg["scope"].get("NOT_AFF", []))))
print("DONE")
