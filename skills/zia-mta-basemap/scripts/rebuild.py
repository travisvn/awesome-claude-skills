#!/usr/bin/env python3
"""
Regenerate the basemap assets from a source DXF.

    python rebuild.py /path/to/Z1-Z2-Z3-MTA_SEGMENTATION.dxf --out ../assets

Streams the file line by line - never loads it into memory - so it copes with the
~550 MB / 66 M line export. Takes a few minutes. ezdxf is deliberately not used: it
builds a full document object graph and will exhaust memory on a file this size.

Accepts .dxf or .dxf.bz2.

--------------------------------------------------------------------------------
v2 changes (route geometry)
--------------------------------------------------------------------------------
v1 captured INSERT points everywhere and LWPOLYLINE only on `ADB_SEG_` layers.
Consequence: every duct, conduit, sawcut and secondary-cable route in the drawing
was discarded, because those layers carry 3 INSERTs in total - the routes are
LWPOLYLINE / LINE / ARC / SPLINE.

v2 captures ALL linear geometry on ALL layers into `civil_routes.csv.gz`. Total
geometry in the drawing is only ~53k entities, so an allowlist buys nothing and
costs a re-run every time a new layer turns out to matter.

Entity coverage and the group codes each one needs:

    LINE        10/20 start, 11/21 end
    LWPOLYLINE  repeated 10/20 vertices, 70 bit0 = closed
    POLYLINE    70 bit0 = closed, then n x VERTEX (10/20), terminated by SEQEND
    ARC         10/20 centre, 40 radius, 50 start angle, 51 end angle (deg, CCW)
    CIRCLE      10/20 centre, 40 radius
    ELLIPSE     10/20 centre, 11/21 major-axis vector, 40 ratio, 41/42 params
    SPLINE      11/21 fit points if present, else 10/20 control points (APPROX)

Curved entities are discretised to a point every ARC_STEP_M of arc length so the
output is a single uniform WKT LINESTRING/POLYGON type. `approx=1` marks features
whose geometry is an approximation of the true curve - splines especially, where
the control polygon is used when no fit points were written.

Both the route capture and the layer-index bbox are gated on `curblock in
TOP_XREFS`. Only those 12 xrefs insert at identity, so only their coordinates are
true model coordinates. v1 accumulated the layer-index bbox over every block,
which pushed block-local coordinates into the bbox and produced impossible extents
Geometry seen outside TOP_XREFS is counted, not emitted, and reported at the end.

The layer-index bbox is built from EMITTED geometry vertices and fixture points,
never from raw group codes 10/20. Codes 10/20 are not a position for every entity:
an ARC/CIRCLE/ELLIPSE code 10 is the CENTRE, so a near-straight duct curve drafted
as a large-radius arc throws its centre kilometres off site, and a legacy POLYLINE
header carries a dummy (0,0) with the real vertices in the following VERTEX
entities. Those two artefacts - not block-local coordinates - are what gave v1 its
impossible duct-layer extents (Y 0 -> 89,267 against a drawing $EXTMAX of 76,896).
Layers carrying only text/attribute entities get bbox = None rather than a guess.
"""
from __future__ import annotations

import argparse
import bz2
import csv
import gzip
import io
import json
import math
import os
import re
from collections import defaultdict

# The 12 xrefs inserted into model space at identity (0,0,0 / scale 1 / rot 0).
# Only entities owned by these carry true model coordinates.
TOP_XREFS = {
    "MTA-AGL-LAYOUT", "SEGMENTATION - MTA", "SEGMENTATION - ZONE 3",
    "SEGMENTATION-ZONE 1-2", "X_C-SPBASE", "ADB-ZONE-1-2-AGL LAYOUT",
    "ADB-ZONE-3-AGL-LAYOUT", "X_EL_Z3_SIGN INFRA LAYOUT", "X_EL_Z3_SECONDARY CABLE",
    "X_CV_Z3_PIT & DUCT SYSTEM", "X_EL_SECONDARY CABLE LAYOUT",
    "X_CV_PITS & DUCTS LAYOUT",
}

GEOM_ENTS = {"LINE", "LWPOLYLINE", "POLYLINE", "ARC", "CIRCLE", "ELLIPSE", "SPLINE"}

ARC_STEP_M = 0.5      # target chord length when discretising curves
ARC_MAX_PTS = 512     # guard against absurd radii


def opener(path):
    if path.endswith(".bz2"):
        return io.TextIOWrapper(bz2.open(path, "rb"), encoding="utf-8", errors="replace")
    return open(path, "r", encoding="utf-8", errors="replace")


def leaf(name: str) -> str:
    return name.split("$0$")[-1]


# MTEXT inline formatting (\pxqc; {\fArial;...} \P) that leaks into label text.
_MTEXT_CODE = re.compile(r"\\[A-Za-z][^;\\{}]*;|[{}]|\\P")

# Zone 3 segment layers carry no ADB_SEG_ prefix - they are ADB_SIG.2,
# ADB_TDZC31R.1, ADB_TE.3 etc. The ".<n>" suffix is what separates a segment
# layer from an AGL layer (ADB_TAXICL) inside the same segmentation xref.
_Z3_SEG = re.compile(r"^ADB_.+\.\d+$")


def seg_tag(curblock, layer_leaf):
    """Segment ID for a segmentation layer, else None."""
    if "ADB_SEG_" in layer_leaf:
        return layer_leaf.split("ADB_SEG_")[-1]
    if (curblock and curblock.startswith("SEGMENTATION")
            and not layer_leaf.endswith("-AT") and _Z3_SEG.match(layer_leaf)):
        return layer_leaf[4:]
    return None


# ------------------------------------------------------------------ geometry
def _npts(sweep_rad: float, radius: float) -> int:
    length = abs(sweep_rad) * max(radius, 1e-9)
    return max(4, min(ARC_MAX_PTS, int(length / ARC_STEP_M) + 1))


def arc_pts(cx, cy, r, a0_deg, a1_deg):
    """DXF arcs run counter-clockwise from a0 to a1."""
    a0 = math.radians(a0_deg)
    a1 = math.radians(a1_deg)
    if a1 <= a0:
        a1 += 2 * math.pi
    n = _npts(a1 - a0, r)
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / n),
             cy + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def circle_pts(cx, cy, r):
    n = _npts(2 * math.pi, r)
    return [(cx + r * math.cos(2 * math.pi * i / n),
             cy + r * math.sin(2 * math.pi * i / n)) for i in range(n + 1)]


def ellipse_pts(cx, cy, mx, my, ratio, t0, t1):
    """mx,my = major-axis endpoint RELATIVE to centre. ratio = minor/major."""
    maj = math.hypot(mx, my)
    if maj < 1e-9:
        return []
    ux, uy = mx / maj, my / maj          # major unit
    vx, vy = -uy, ux                     # minor unit (CCW perpendicular)
    minor = maj * ratio
    if t1 <= t0:
        t1 += 2 * math.pi
    n = _npts(t1 - t0, maj)
    out = []
    for i in range(n + 1):
        t = t0 + (t1 - t0) * i / n
        ca, sa = math.cos(t) * maj, math.sin(t) * minor
        out.append((cx + ca * ux + sa * vx, cy + ca * uy + sa * vy))
    return out


def wkt_of(pts, closed):
    if len(pts) < 2:
        return None
    if closed:
        if pts[0] != pts[-1]:
            pts = pts + [pts[0]]
        body = ", ".join(f"{a:.4f} {b:.4f}" for a, b in pts)
        return f"POLYGON(({body}))"
    body = ", ".join(f"{a:.4f} {b:.4f}" for a, b in pts)
    return f"LINESTRING({body})"


# ------------------------------------------------------------------ parse
def parse(path, route_writer):
    fixtures, seg_lines, seg_labels = [], [], []
    layer_idx = defaultdict(lambda: {"n": 0, "types": defaultdict(int),
                                     "xmin": 1e30, "xmax": -1e30,
                                     "ymin": 1e30, "ymax": -1e30})
    stats = {"routes": 0, "verts": 0, "approx": 0,
             "skipped_nontop": defaultdict(int), "degenerate": defaultdict(int)}

    section = curblock = ent = layer = blockname = None
    code = None
    expect_bn = False
    x = y = rot = None
    xs, ys, x2s, y2s, txt = [], [], [], [], []
    closed = 0
    r40 = a50 = a51 = a41 = a42 = None
    pending_poly = None          # legacy POLYLINE accumulator

    def emit_route(lyr, etype, pts, is_closed, approx=0):
        wkt = wkt_of(pts, is_closed)
        if wkt is None:
            stats["degenerate"][etype] += 1
            return
        route_writer.writerow((curblock, lyr, leaf(lyr), etype,
                               len(pts), int(bool(is_closed)), approx, wkt))
        d = layer_idx[lyr]
        for px, py in pts:
            if px < d["xmin"]: d["xmin"] = px
            if px > d["xmax"]: d["xmax"] = px
            if py < d["ymin"]: d["ymin"] = py
            if py > d["ymax"]: d["ymax"] = py
        stats["routes"] += 1
        stats["verts"] += len(pts)
        stats["approx"] += approx

    def flush():
        nonlocal ent, layer, blockname, x, y, rot, xs, ys, x2s, y2s, txt, closed
        nonlocal r40, a50, a51, a41, a42, pending_poly

        # legacy POLYLINE closes on SEQEND, which carries no layer of its own
        if ent == "SEQEND" and pending_poly is not None:
            if curblock in TOP_XREFS:
                emit_route(pending_poly["layer"], "POLYLINE",
                           pending_poly["pts"], pending_poly["closed"])
            pending_poly = None

        if ent and layer:
            top = curblock in TOP_XREFS

            # ---- v1 behaviour: fixture points
            if ent == "INSERT" and x is not None and top:
                fixtures.append((curblock, layer, leaf(layer), leaf(blockname or ""),
                                 round(x, 4), round(y, 4), round(rot or 0.0, 4)))
                d = layer_idx[layer]
                if x < d["xmin"]: d["xmin"] = x
                if x > d["xmax"]: d["xmax"] = x
                if y < d["ymin"]: d["ymin"] = y
                if y > d["ymax"]: d["ymax"] = y

            # ---- v1 behaviour: MTA segmentation (v3: + Zone 3 layers, which
            # carry no ADB_SEG_ prefix - see seg_tag)
            tag = seg_tag(curblock, leaf(layer))
            if tag is not None:
                if ent == "LWPOLYLINE" and len(xs) >= 2 and len(ys) >= 2:
                    pts = list(zip(xs, ys))
                    seg_lines.append((curblock, tag, len(pts), closed & 1,
                                      wkt_of(pts, closed & 1)))
                elif ent in ("MTEXT", "TEXT") and xs and ys:
                    label = _MTEXT_CODE.sub("", "".join(txt)).strip()
                    if label:
                        seg_labels.append((curblock, tag, label,
                                           round(xs[0], 4), round(ys[0], 4)))

            # ---- v2: route geometry, all layers
            if ent in GEOM_ENTS:
                if not top:
                    stats["skipped_nontop"][ent] += 1
                elif ent == "LINE":
                    if xs and ys and x2s and y2s:
                        emit_route(layer, "LINE",
                                   [(xs[0], ys[0]), (x2s[0], y2s[0])], 0)
                    else:
                        stats["degenerate"]["LINE"] += 1
                elif ent == "LWPOLYLINE":
                    emit_route(layer, "LWPOLYLINE", list(zip(xs, ys)), closed & 1)
                elif ent == "ARC":
                    if xs and ys and r40 and a50 is not None and a51 is not None:
                        emit_route(layer, "ARC",
                                   arc_pts(xs[0], ys[0], r40, a50, a51), 0, 1)
                    else:
                        stats["degenerate"]["ARC"] += 1
                elif ent == "CIRCLE":
                    if xs and ys and r40:
                        emit_route(layer, "CIRCLE",
                                   circle_pts(xs[0], ys[0], r40), 1, 1)
                    else:
                        stats["degenerate"]["CIRCLE"] += 1
                elif ent == "ELLIPSE":
                    if xs and ys and x2s and y2s and r40 is not None:
                        t0 = a41 if a41 is not None else 0.0
                        t1 = a42 if a42 is not None else 2 * math.pi
                        emit_route(layer, "ELLIPSE",
                                   ellipse_pts(xs[0], ys[0], x2s[0], y2s[0],
                                               r40, t0, t1), 0, 1)
                    else:
                        stats["degenerate"]["ELLIPSE"] += 1
                elif ent == "SPLINE":
                    # No knot-vector evaluation. Fit points lie on the curve;
                    # control points do not, hence approx=1 either way.
                    pts = list(zip(x2s, y2s)) if len(x2s) >= 2 else list(zip(xs, ys))
                    emit_route(layer, "SPLINE", pts, closed & 1, 1)
                elif ent == "POLYLINE":
                    pending_poly = {"layer": layer, "closed": closed & 1, "pts": []}

            # ---- legacy POLYLINE vertices arrive as separate VERTEX entities
            if ent == "VERTEX" and pending_poly is not None and xs and ys:
                pending_poly["pts"].append((xs[0], ys[0]))

        ent = layer = blockname = None
        x = y = rot = None
        xs, ys, x2s, y2s, txt = [], [], [], [], []
        closed = 0
        r40 = a50 = a51 = a41 = a42 = None

    with opener(path) as fh:
        for raw in fh:
            if code is None:
                code = raw.strip()
                continue
            val = raw.rstrip("\r\n")
            c, code = code, None

            if c == "0":
                v = val.strip()
                flush()
                if v == "SECTION":
                    section = "?"
                elif v == "ENDSEC":
                    section = curblock = None
                    pending_poly = None
                elif v == "BLOCK":
                    expect_bn = True
                elif v == "ENDBLK":
                    curblock = None
                    pending_poly = None
                else:
                    ent = v
            elif c == "2":
                if section == "?":
                    section = val.strip()
                elif expect_bn:
                    curblock = val.strip()
                    expect_bn = False
                elif ent == "INSERT":
                    blockname = val.strip()
            elif c == "8":
                layer = val.strip()
                if section == "BLOCKS" and curblock and ent:
                    d = layer_idx[layer]
                    d["n"] += 1
                    d["types"][ent] += 1
            elif c == "10" and ent:
                try:
                    v = float(val)
                except ValueError:
                    continue
                xs.append(v)
                if x is None:
                    x = v
            elif c == "20" and ent:
                try:
                    v = float(val)
                except ValueError:
                    continue
                ys.append(v)
                if y is None:
                    y = v
            elif c == "11" and ent in ("LINE", "ELLIPSE", "SPLINE"):
                try:
                    x2s.append(float(val))
                except ValueError:
                    pass
            elif c == "21" and ent in ("LINE", "ELLIPSE", "SPLINE"):
                try:
                    y2s.append(float(val))
                except ValueError:
                    pass
            elif c == "40" and ent in ("ARC", "CIRCLE", "ELLIPSE"):
                try:
                    r40 = float(val)          # radius, or ellipse minor/major ratio
                except ValueError:
                    pass
            elif c == "41" and ent == "ELLIPSE":
                try:
                    a41 = float(val)
                except ValueError:
                    pass
            elif c == "42" and ent == "ELLIPSE":
                try:
                    a42 = float(val)
                except ValueError:
                    pass
            elif c == "50":
                if ent == "INSERT":
                    try:
                        rot = float(val)
                    except ValueError:
                        pass
                elif ent == "ARC":
                    try:
                        a50 = float(val)
                    except ValueError:
                        pass
            elif c == "51" and ent == "ARC":
                try:
                    a51 = float(val)
                except ValueError:
                    pass
            elif c == "70" and ent in ("LWPOLYLINE", "POLYLINE", "SPLINE"):
                try:
                    closed = int(val)
                except ValueError:
                    pass
            elif c in ("1", "3") and ent in ("MTEXT", "TEXT"):
                txt.append(val)
        flush()

    idx = {k: {"n": v["n"], "types": dict(v["types"]),
               "bbox": [round(v["xmin"], 3), round(v["ymin"], 3),
                        round(v["xmax"], 3), round(v["ymax"], 3)]
               if v["xmin"] < 1e29 else None}
           for k, v in layer_idx.items() if v["n"]}
    return fixtures, seg_lines, seg_labels, idx, stats


def main():
    p = argparse.ArgumentParser()
    p.add_argument("dxf")
    p.add_argument("--out", default="../assets")
    a = p.parse_args()
    os.makedirs(a.out, exist_ok=True)

    routes_path = os.path.join(a.out, "civil_routes.csv.gz")
    with gzip.open(routes_path, "wt", newline="") as rf:
        w = csv.writer(rf)
        w.writerow(("xref", "layer", "leaf", "etype", "nverts", "closed",
                    "approx", "wkt"))
        fx, lines, labels, idx, stats = parse(a.dxf, w)

    with gzip.open(os.path.join(a.out, "agl_fixtures.csv.gz"), "wt", newline="") as o:
        w = csv.writer(o)
        w.writerow(("xref", "layer", "leaf", "block", "x", "y", "rot"))
        w.writerows(fx)

    with open(os.path.join(a.out, "seg_geometry.csv"), "w", newline="") as o:
        w = csv.writer(o)
        w.writerow(("xref", "seg_layer", "nverts", "closed", "wkt"))
        w.writerows(lines)

    with open(os.path.join(a.out, "seg_labels.csv"), "w", newline="") as o:
        w = csv.writer(o)
        w.writerow(("xref", "seg_layer", "label", "x", "y"))
        w.writerows(labels)

    with gzip.open(os.path.join(a.out, "layer_index.json.gz"), "wt") as o:
        json.dump(idx, o)

    xs = [f[4] for f in fx]
    ys = [f[5] for f in fx]
    print(f"fixtures        : {len(fx):,}")
    print(f"seg geometry    : {len(lines):,}")
    print(f"seg labels      : {len(labels):,}")
    print(f"layers indexed  : {len(idx):,}")
    print(f"routes emitted  : {stats['routes']:,}  ({stats['verts']:,} vertices, "
          f"{stats['approx']:,} approximated)")
    if stats["skipped_nontop"]:
        tot = sum(stats["skipped_nontop"].values())
        print(f"routes SKIPPED (outside TOP_XREFS, block-local coords): {tot:,}")
        for k, v in sorted(stats["skipped_nontop"].items(), key=lambda kv: -kv[1]):
            print(f"    {k:<12}{v:>8,}")
    if stats["degenerate"]:
        print("degenerate / unparsable:", dict(stats["degenerate"]))
    print(f"fixture extent  : X {min(xs):,.0f} -> {max(xs):,.0f}   "
          f"Y {min(ys):,.0f} -> {max(ys):,.0f}")
    print("\nRe-check the extent above against SKILL.md. If it moved, the drawing "
          "origin changed and every previously issued coordinate needs re-checking.")


if __name__ == "__main__":
    main()
