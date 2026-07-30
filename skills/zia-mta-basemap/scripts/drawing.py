#!/usr/bin/env python3
"""
Deliverable drawings from the ZIA MTA basemap.

`basemap.plot()` is a working view - fine for checking your own filter, wrong to
attach to an RFI. `sketch()` here is the drawing: real drafting scale, graphic
scale bar, grid-north arrow, legend with counts, context assets behind the
selection, automatic panels when the selection is in disjoint clusters, and a
title block whose fields come from `assets/titleblock.json`.

    from drawing import sketch
    from basemap import fixtures_in_segment, segment_patches

    fx = fixtures_in_segment("TE5.1", assets_only=True)
    patches, strips = segment_patches("TE5.1")
    sketch(fx, patches=patches, out="TE5.1_agl_impact.pdf",
           drawing_title="TWY D7/D8 milling - AGL impact",
           title_block={"drawing_no": "ZIA-AGL-RFI-0142", "rev": "A"})

Two things this module refuses to fake, because both would be read as surveyed
fact off a drawing that carries neither:

  * North is **grid north of the local drawing grid**, not true north. The DXF has
    no GEODATA object, so the rotation between the two is unknown. The arrow is
    labelled GRID N and the note says so.
  * Scale is exact only at the stated paper size, printed at 100%. The scale is
    chosen from a drafting series so it is a real ratio rather than "whatever fit",
    and the graphic bar survives rescaling even when the printed ratio does not.
"""
from __future__ import annotations

import json
import os

import pandas as pd

from basemap import TYPE_COLORS, _type_color, load_fixtures, wkt_coords

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

# ISO paper, landscape, millimetres.
PAPER = {"A4": (297, 210), "A3": (420, 297), "A2": (594, 420), "A1": (841, 594)}
# Sheet layout as figure fractions. These are the single source of truth: the axes
# box is derived from them to pick the scale, and subplots_adjust is set from them.
# Guessing the box separately is how a drawing ends up at 1:5000 when 1:2500 fits.
MARGIN = {"left": 0.055, "right": 0.985, "top": 0.865, "bottom": 0.175,
          "wspace": 0.14, "hspace": 0.20}
# Drafting scale series. A drawing at 1:1873 is a drawing nobody can scale off.
SCALES = [100, 200, 250, 500, 1000, 1250, 2000, 2500, 5000, 10000, 20000]
MM_PER_IN = 25.4

LOCAL_GRID_NOTE = ("COORDINATES: ZIA LOCAL DRAWING GRID, METRES - NOT UTM / WGS84 / "
                   "NAHRWAN. No georeferencing exists in the source drawing; apply and "
                   "check the survey transform before setting out or issuing coordinates.")


# --------------------------------------------------------------- title block
def load_title_block(**overrides) -> dict:
    """Title block fields, `assets/titleblock.json` overlaid with kwargs."""
    with open(os.path.join(ASSETS, "titleblock.json")) as fh:
        tb = {k: v for k, v in json.load(fh).items() if not k.startswith("_")}
    tb.update({k: v for k, v in overrides.items() if v is not None})
    return tb


def _tb_value(tb, key):
    v = str(tb.get(key, "") or "").strip()
    return v if v else "- not set -"


# --------------------------------------------------------------- clustering
def cluster_points(pts, gap: float = 200.0):
    """Single-linkage grouping of points; a gap wider than `gap` starts a cluster.

    A milling segment often runs in disjoint stretches - TE5.1 has three, ~500 m
    apart. Drawing them on one axes wastes 80% of the sheet on empty apron and
    shrinks the part being reviewed to nothing, which is why the panels exist.
    """
    import numpy as np
    p = np.asarray(pts, dtype=float)
    n = len(p)
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[rj] = ri

    # n is a few hundred for a segment-scale selection, so pairwise is fine.
    d = np.linalg.norm(p[:, None, :] - p[None, :, :], axis=-1)
    for i, j in zip(*np.where(d <= gap)):
        if i < j:
            union(int(i), int(j))
    groups = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)
    return sorted(groups.values(), key=len, reverse=True)


def assign_to_cluster(items, idx, pts, reach=75.0):
    """Which of `items` [(label, coords)] belong to the cluster given by `idx`.

    Proximity to the cluster's actual points, not a bbox overlap test: segment
    clusters are long diagonals, so their bounding boxes overlap each other even
    when the geometry is half a kilometre apart. A bbox test therefore pulls a
    distant patch into a panel, which both draws it in the wrong place and inflates
    the panel extent enough to drop the whole sheet a scale step.
    """
    import numpy as np
    cp = np.asarray([pts[i] for i in idx], dtype=float)
    out = []
    for label, coords in items:
        q = np.asarray(coords, dtype=float)
        d = np.linalg.norm(q[:, None, :] - cp[None, :, :], axis=-1).min()
        if d <= reach:
            out.append((label, coords))
    return out


def _extent(idx, pts, rings, pad):
    xs = [pts[i][0] for i in idx]
    ys = [pts[i][1] for i in idx]
    for ring in rings:
        xs += [p[0] for p in ring]
        ys += [p[1] for p in ring]
    return min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad


def _pick_scale(extents, axes_w_mm, axes_h_mm):
    """Smallest drafting scale that fits every panel in the axes box."""
    need = 1.0
    for xmin, ymin, xmax, ymax in extents:
        need = max(need, (xmax - xmin) * 1000.0 / axes_w_mm,
                   (ymax - ymin) * 1000.0 / axes_h_mm)
    for s in SCALES:
        if s >= need:
            return s
    return SCALES[-1]


# --------------------------------------------------------------- decorations
def _scale_bar(ax, scale, axes_w_mm):
    """Graphic bar ~45 mm of paper, rounded to a whole number of metres."""
    span_m = 45.0 * scale / 1000.0
    step = next((s for s in (5, 10, 20, 25, 50, 100, 200, 250, 500, 1000)
                 if s * 4 >= span_m), 1000)
    total = step * 4
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    bx = x0 + (x1 - x0) * 0.035
    by = y0 + (y1 - y0) * 0.045
    h = (y1 - y0) * 0.010
    for k in range(4):
        ax.add_patch(__import__("matplotlib").patches.Rectangle(
            (bx + k * step, by), step, h, facecolor="black" if k % 2 == 0 else "white",
            edgecolor="black", lw=0.6, zorder=12))
    for k in range(5):
        ax.annotate(f"{k * step:g}", (bx + k * step, by + h * 1.5), ha="center",
                    va="bottom", fontsize=5.5, zorder=12)
    ax.annotate(f"metres    1:{scale:g} at {ax._zia_paper}", (bx, by - h * 1.2),
                ha="left", va="top", fontsize=5.5, style="italic", zorder=12)


def _north_arrow(ax):
    """Grid north. NOT true north - the drawing carries no georeferencing."""
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    x = x1 - (x1 - x0) * 0.055
    y = y1 - (y1 - y0) * 0.16
    L = (y1 - y0) * 0.075
    ax.annotate("", xy=(x, y + L), xytext=(x, y),
                arrowprops=dict(arrowstyle="-|>", color="black", lw=1.1), zorder=12)
    ax.annotate("GRID N", (x, y + L * 1.08), ha="center", va="bottom", fontsize=6,
                fontweight="bold", zorder=12)
    ax.annotate("(local grid -\nnot true north)", (x, y - L * 0.1), ha="center",
                va="top", fontsize=4.6, style="italic", color="#444", zorder=12)


def _draw_title_block(fig, tb, scale, paper, extra_notes):
    """Frame + title block strip along the bottom of the sheet."""
    fig.patches.append(__import__("matplotlib").patches.Rectangle(
        (0.012, 0.012), 0.976, 0.976, transform=fig.transFigure, fill=False,
        edgecolor="black", lw=1.3, zorder=20))

    mpl = __import__("matplotlib")
    top, mid = 0.128, 0.070
    fig.patches.append(mpl.patches.Rectangle(
        (0.012, 0.012), 0.976, top - 0.012, transform=fig.transFigure, fill=False,
        edgecolor="black", lw=1.0, zorder=20))
    # cells live above `mid`; the notes band below it spans the full sheet width, so
    # the vertical dividers must stop at `mid` or they cut through the notes
    fig.lines.append(mpl.lines.Line2D(
        [0.012, 0.988], [mid, mid], transform=fig.transFigure, color="black",
        lw=0.7, zorder=21))

    def cell(x, w, label, value, bold=False, size=6.4):
        fig.text(x + 0.006, top - 0.012, label.upper(), fontsize=4.6, color="#555",
                 va="top", zorder=21)
        fig.text(x + 0.006, top - 0.028, value, fontsize=size, va="top", zorder=21,
                 fontweight="bold" if bold else "normal")
        fig.lines.append(mpl.lines.Line2D(
            [x + w, x + w], [mid, top], transform=fig.transFigure, color="black",
            lw=0.7, zorder=21))

    cell(0.012, 0.30, "project", _tb_value(tb, "project"), size=6.0)
    cell(0.312, 0.20, "drawing title", _tb_value(tb, "drawing_title"), bold=True, size=6.2)
    cell(0.512, 0.11, "client", _tb_value(tb, "client"), size=5.8)
    cell(0.622, 0.10, "discipline", _tb_value(tb, "discipline"), size=5.4)
    cell(0.722, 0.12, "drawing no", _tb_value(tb, "drawing_no"), bold=True)
    cell(0.842, 0.05, "rev", _tb_value(tb, "rev"), bold=True)
    cell(0.892, 0.096, "scale / sheet", f"1:{scale:g}  {paper}", bold=True, size=5.8)

    row = "   |   ".join(f"{k.replace('_', ' ').title()}: {_tb_value(tb, k)}"
                         for k in ("date", "drawn_by", "checked_by", "approved_by",
                                   "status"))
    fig.text(0.018, mid - 0.006, row, fontsize=5.0, color="#333", va="top", zorder=21)

    # Notes wrapped by hand: matplotlib's wrap= measures against the figure edge, not
    # the block, so a long note silently runs off the sheet.
    import textwrap
    notes = [LOCAL_GRID_NOTE] + list(extra_notes or [])
    body = "   ".join(f"({i + 1}) {n}" for i, n in enumerate(notes))
    for k, line in enumerate(textwrap.wrap(body, width=235)[:3]):
        fig.text(0.018, mid - 0.021 - k * 0.0115, line, fontsize=4.4,
                 color="#b03a2e", va="top", zorder=21)


# --------------------------------------------------------------- the drawing
def sketch(fixtures, patches=None, strips=None, segments=None, routes=None,
           out="sketch.pdf", drawing_title=None, title_block=None, paper="A3",
           context=True, context_pad=60.0, cluster_gap=200.0, max_panels=4,
           notes=None, dpi=300):
    """Render a deliverable AGL drawing. Returns the list of files written.

    fixtures : the selection (from fixtures_in_segment / load_fixtures)
    patches  : [(label, ring)] from segment_patches() - shaded as the milling area
    strips   : [(label, line)] unpaired division lines, drawn dashed with a warning
    context  : draw all other nearby assets in grey, so the reader sees what was
               NOT selected. Reviewers catch a wrong filter from the greys.
    out      : .pdf or .png; the other format is written alongside it

    Panels are laid out automatically when the selection falls in disjoint
    clusters, all at one shared scale so panels stay comparable.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    if fixtures is None or not len(fixtures):
        raise ValueError("nothing to draw - the fixture selection is empty")

    tb = load_title_block(drawing_title=drawing_title, **(title_block or {}))
    rings = [r for _, r in (patches or [])]
    lines = [ln for _, ln in (strips or [])]
    pts = fixtures[["x", "y"]].to_numpy()

    groups = cluster_points(pts, gap=cluster_gap)
    if len(groups) > max_panels:            # keep the big ones, fold the rest in
        head, tail = groups[:max_panels - 1], groups[max_panels - 1:]
        groups = head + [[i for g in tail for i in g]]

    pw, ph = PAPER[paper]
    fig = plt.figure(figsize=(pw / MM_PER_IN, ph / MM_PER_IN))
    n = len(groups)
    cols = 1 if n == 1 else 2
    rows = (n + cols - 1) // cols
    # One panel's axes box in millimetres of paper, derived from MARGIN so the scale
    # is chosen against the box the panel will actually get.
    m = MARGIN
    axes_w_mm = pw * (m["right"] - m["left"]) / (cols + (cols - 1) * m["wspace"])
    axes_h_mm = ph * (m["top"] - m["bottom"]) / (rows + (rows - 1) * m["hspace"])

    # Patches and strips belong to the panel whose assets they sit among.
    panel_patches = [assign_to_cluster(patches or [], g, pts) for g in groups]
    panel_strips = [assign_to_cluster(strips or [], g, pts) for g in groups]
    # Small pad on purpose. The axes box is a fixed size on the sheet, so whenever the
    # geometry is smaller than the box the margin appears by itself; a generous pad
    # here only risks tipping the extent past a scale step (933 m vs 910 m of paper
    # at 1:5000 is the difference between 1:5000 and 1:10000, because the drafting
    # series has no rung between them).
    extents = [_extent(g, pts, [r for _, r in pp], pad=10.0)
               for g, pp in zip(groups, panel_patches)]
    scale = _pick_scale(extents, axes_w_mm, axes_h_mm)

    ctx = None
    if context:
        xs = [e[0] for e in extents] + [e[2] for e in extents]
        ys = [e[1] for e in extents] + [e[3] for e in extents]
        ctx = load_fixtures(bbox=(min(xs) - context_pad, min(ys) - context_pad,
                                 max(xs) + context_pad, max(ys) + context_pad),
                            assets_only=True)
        if len(fixtures):
            key = set(zip(fixtures.x, fixtures.y, fixtures.block))
            ctx = ctx[[k not in key for k in zip(ctx.x, ctx.y, ctx.block)]]

    seen = {}
    for k, (g, ext, pp, ps) in enumerate(zip(groups, extents, panel_patches,
                                             panel_strips)):
        ax = fig.add_subplot(rows, cols, k + 1)
        ax._zia_paper = paper
        # centre each panel on its cluster at the shared scale
        cx, cy = (ext[0] + ext[2]) / 2, (ext[1] + ext[3]) / 2
        half_w = axes_w_mm * scale / 1000.0 / 2
        half_h = axes_h_mm * scale / 1000.0 / 2
        ax.set_xlim(cx - half_w, cx + half_w)
        ax.set_ylim(cy - half_h, cy + half_h)

        if ctx is not None and len(ctx):
            ax.scatter(ctx.x, ctx.y, s=1.8, color="#d2d2d2", zorder=1, linewidths=0)
        if segments is not None and len(segments):
            for w in segments["wkt"]:
                q = wkt_coords(w)
                ax.plot([p[0] for p in q], [p[1] for p in q], lw=0.4,
                        color="#e3cdc9", zorder=2)
        if routes is not None and len(routes):
            for w in routes["wkt"]:
                q = wkt_coords(w)
                ax.plot([p[0] for p in q], [p[1] for p in q], lw=0.8,
                        color="#8e44ad", alpha=0.75, zorder=3)
        for label, ring in pp:
            ax.fill([p[0] for p in ring], [p[1] for p in ring], color="#c0392b",
                    alpha=0.11, zorder=4)
            ax.plot([p[0] for p in ring], [p[1] for p in ring], color="#c0392b",
                    lw=1.5, zorder=5)
        for label, ln in ps:
            ax.plot([p[0] for p in ln], [p[1] for p in ln], color="#c0392b", lw=1.3,
                    ls=(0, (5, 3)), zorder=5)

        sub = fixtures.iloc[g]
        for name, grp in sub.groupby("asset_type"):
            h = ax.scatter(grp.x, grp.y, s=15, color=_type_color(name),
                           edgecolors="#222", linewidths=0.3, zorder=6)
            seen.setdefault(name, h)

        ax.set_aspect("equal")
        ax.tick_params(labelsize=5)
        ax.set_xlabel("ZIA local grid E (m)", fontsize=5.5)
        ax.set_ylabel("ZIA local grid N (m)", fontsize=5.5)
        ax.grid(alpha=0.2, lw=0.3)
        if n > 1:
            ax.set_title(f"Panel {k + 1} of {n} - {len(g)} assets", fontsize=7,
                         fontweight="bold")
        _scale_bar(ax, scale, axes_w_mm)
        _north_arrow(ax)

    counts = fixtures.groupby("asset_type").size().to_dict()
    order = sorted(seen, key=lambda k: -counts.get(k, 0))
    handles = [seen[k] for k in order]
    labels = [f"{k}  ({counts.get(k, 0)})" for k in order]
    if ctx is not None and len(ctx):
        handles.append(plt.Line2D([], [], marker="o", ls="", color="#c8c8c8", ms=3))
        labels.append(f"Other AGL assets, not in scope  ({len(ctx)})")
    if patches:
        handles.append(plt.Line2D([], [], color="#c0392b", lw=1.5))
        labels.append(f"Milling patch, reconstructed  ({len(patches)})")
    if strips:
        handles.append(plt.Line2D([], [], color="#c0392b", lw=1.3, ls=(0, (5, 3))))
        labels.append(f"Division line, width assumed  ({len(strips)})")
    # Legend as a band across the reserved strip at the top of the sheet. Anchored
    # inside a panel it covers the geometry the drawing exists to show.
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.976),
               ncol=min(6, max(3, (len(labels) + 2) // 3)), fontsize=5.4,
               framealpha=0.95, borderpad=0.5, columnspacing=1.4, handletextpad=0.5,
               title=f"{drawing_title or _tb_value(tb, 'drawing_title')}"
                     f"   -   {len(fixtures)} assets in scope",
               title_fontsize=6.6)

    extra = list(notes or [])
    if strips:
        extra.append(f"{len(strips)} division line(s) had no paired partner; the width "
                     "shown is an assumption, not drawing geometry.")
    if patches:
        extra.append("Milling patches are RECONSTRUCTED from division lines - verify "
                     "against the segmentation drawing before use.")
    _draw_title_block(fig, tb, scale, paper, extra)
    fig.subplots_adjust(**MARGIN)

    base, ext_ = os.path.splitext(out)
    written = []
    for suffix in (".pdf", ".png"):
        path = base + suffix
        fig.savefig(path, dpi=dpi)
        written.append(path)
    plt.close(fig)
    return written


# --------------------------------------------------------------- DXF export
_R12_COLOR = {"Taxiway centreline light": 3, "Taxiway edge light": 5,
              "Stop bar light": 1, "Lead-in light": 6, "Holding position light": 30,
              "Runway guard light": 2, "Guidance sign": 7, "Sign foundation": 8,
              "Handhole": 33, "Existing handhole": 42, "Transformer pit": 6,
              "Existing transformer pit": 221, "Manhole": 34}


def _dxf_layer_name(s: str) -> str:
    """R12 layer names: no spaces or punctuation that old readers choke on."""
    out = "".join(c if (c.isalnum() or c in "-_$") else "-" for c in s.upper())
    while "--" in out:
        out = out.replace("--", "-")
    return out.strip("-")[:31] or "MISC"


def write_dxf(path, fixtures=None, patches=None, strips=None, segments=None,
              routes=None, prefix="ZIA"):
    """Write the selection and reconstructed geometry as DXF R12 ASCII.

    R12 deliberately: it is the format every AutoCAD, BricsCAD and viewer opens
    without a version negotiation, and this file carries points, polylines and text
    only. Assets go on `<prefix>-AGL-<TYPE>` layers with a text label carrying the
    asset type and, when present, the selection basis; reconstructed patches go on
    `<prefix>-MTA-PATCH-RECONSTRUCTED` so nobody mistakes them for issued geometry.

    Coordinates are written in the ZIA local drawing grid, unchanged. The file will
    only land in the right place if it is inserted into a drawing on that same grid.
    """
    layers, ents = {}, []

    def layer(name, color=7):
        layers.setdefault(name, color)
        return name

    def point(lyr, x, y):
        ents.append(f"0\nPOINT\n8\n{lyr}\n10\n{x:.4f}\n20\n{y:.4f}\n30\n0.0\n")

    def text(lyr, x, y, s, h=1.2):
        s = str(s).replace("\n", " ")[:250]
        ents.append(f"0\nTEXT\n8\n{lyr}\n10\n{x:.4f}\n20\n{y:.4f}\n30\n0.0\n"
                    f"40\n{h:.3f}\n1\n{s}\n")

    def polyline(lyr, pts, closed=False):
        if len(pts) < 2:
            return
        ents.append(f"0\nPOLYLINE\n8\n{lyr}\n66\n1\n70\n{1 if closed else 0}\n")
        for x, y in pts:
            ents.append(f"0\nVERTEX\n8\n{lyr}\n10\n{x:.4f}\n20\n{y:.4f}\n30\n0.0\n")
        ents.append(f"0\nSEQEND\n8\n{lyr}\n")

    if fixtures is not None and len(fixtures):
        has_basis = "basis" in fixtures.columns
        for _, r in fixtures.iterrows():
            t = str(r.get("asset_type", "MISC"))
            lyr = layer(f"{prefix}-AGL-{_dxf_layer_name(t)}", _R12_COLOR.get(t, 7))
            point(lyr, r["x"], r["y"])
            lbl = layer(f"{prefix}-AGL-LABEL", 8)
            text(lbl, r["x"] + 1.0, r["y"] + 1.0,
                 f"{t}{' | ' + str(r['basis']) if has_basis else ''}", h=0.9)

    for label, ring in (patches or []):
        lyr = layer(f"{prefix}-MTA-PATCH-RECONSTRUCTED", 1)
        polyline(lyr, ring, closed=True)
        cx = sum(p[0] for p in ring) / len(ring)
        cy = sum(p[1] for p in ring) / len(ring)
        text(lyr, cx, cy, f"RECONSTRUCTED - {label}", h=2.0)
    for label, ln in (strips or []):
        lyr = layer(f"{prefix}-MTA-DIVISION-UNPAIRED", 2)
        polyline(lyr, ln)
        text(lyr, ln[0][0], ln[0][1], f"WIDTH ASSUMED - {label}", h=2.0)
    if segments is not None and len(segments):
        lyr = layer(f"{prefix}-MTA-DIVISION", 2)
        for w in segments["wkt"]:
            q = wkt_coords(w)
            polyline(lyr, q, closed=w.strip().upper().startswith("POLYGON"))
    if routes is not None and len(routes):
        for _, r in routes.iterrows():
            lyr = layer(f"{prefix}-CV-{_dxf_layer_name(str(r['leaf']))}", 6)
            polyline(lyr, wkt_coords(r["wkt"]))

    note = layer(f"{prefix}-NOTES", 1)
    ents.append("")  # keep list non-empty even with no geometry

    head = ["0\nSECTION\n2\nHEADER\n0\nENDSEC\n", "0\nSECTION\n2\nTABLES\n",
            f"0\nTABLE\n2\nLAYER\n70\n{len(layers)}\n"]
    for name, color in layers.items():
        head.append(f"0\nLAYER\n2\n{name}\n70\n0\n62\n{color}\n6\nCONTINUOUS\n")
    head += ["0\nENDTAB\n", "0\nENDSEC\n", "0\nSECTION\n2\nENTITIES\n"]

    with open(path, "w", encoding="ascii", errors="replace") as fh:
        fh.write("".join(head))
        fh.write("".join(ents))
        # the disclaimer travels with the geometry, not just the covering email
        fh.write(f"0\nTEXT\n8\n{note}\n10\n0.0\n20\n0.0\n30\n0.0\n40\n5.0\n1\n"
                 f"{LOCAL_GRID_NOTE}\n")
        fh.write("0\nENDSEC\n0\nEOF\n")
    return path
