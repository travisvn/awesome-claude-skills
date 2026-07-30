#!/usr/bin/env python3
"""
ZIA MTA basemap - load, filter and plot AGL assets and MTA segmentation.

All coordinates are ZIA LOCAL GRID, metres. NOT UTM. See references/coordinates.md
before putting any number from here into a client-facing document.

Usage as a library:
    from basemap import load_fixtures, load_segments, fixtures_in_segment, plot

    fx  = load_fixtures(leaf=["EL-TAXICL", "EL-STOPBAR"])
    seg = load_segments(label_prefix="Z1")
    plot(fx, seg, out="twy_z1.png", title="TWY Z1 - AGL vs MTA segmentation")

    # AGL impact of milling segment TE5.1 - patches reconstructed from its
    # division lines, so assets mid-band (centreline, lead-in) are included
    fx = fixtures_in_segment("TE5.1", assets_only=True)

Usage from CLI:
    python basemap.py --list-leaves
    python basemap.py --leaf EL-TAXICL EL-STOPBAR --bbox 5800 55800 6400 56400 --out z1.png
    python basemap.py --seg TE5.1 --assets-only --out te51.png --csv-out te51.csv
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import re
import sys

import pandas as pd

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

from classify import classify, NON_ASSET_TYPES  # noqa: E402

# Back-compat alias. Classification now lives in classify.py and keys on the
# BLOCK name as well as the layer - see the docstring there for why.
__all__ = ["load_fixtures", "load_segments", "load_segment_labels", "load_routes",
           "load_layer_index", "bbox_filter", "routes_in_bbox", "wkt_length",
           "segments_in_bbox", "segment_extent", "segment_patches",
           "fixtures_in_segment", "fixtures_near_segment",
           "wkt_coords", "plot", "classify", "NON_ASSET_TYPES"]


# MTEXT inline formatting codes (\pxqc; \fArial|b0; {\H0.7x;...}) leak into some
# extracted labels. Strip them so "C.53" is "C.53" everywhere.
_MTEXT_CODE = re.compile(r"\\[A-Za-z][^;\\{}]*;|[{}]|\\P")


def _clean_label(s):
    if not isinstance(s, str):
        return s
    return _MTEXT_CODE.sub("", s).strip()


def load_segment_labels() -> pd.DataFrame:
    """Every segmentation label point (a long segment has several), MTEXT codes stripped."""
    lab = pd.read_csv(os.path.join(ASSETS, "seg_labels.csv"))
    lab["label"] = lab["label"].map(_clean_label)
    return lab


# ----------------------------------------------------------------- loading
def load_fixtures(leaf=None, xref=None, layer_regex=None, bbox=None,
                  assets_only=False) -> pd.DataFrame:
    """AGL fixtures (INSERT entities) in local grid metres.

    leaf        : str or list, exact leaf-layer name(s), e.g. "EL-TAXICL"
    xref        : str or list, source xref, e.g. "ADB-ZONE-1-2-AGL LAYOUT"
    layer_regex : regex matched against the full layer path
    bbox        : (xmin, ymin, xmax, ymax)
    assets_only : drop non-AGL basemap, segmentation arrows and unclassified
    """
    df = pd.read_csv(os.path.join(ASSETS, "agl_fixtures.csv.gz"))
    if leaf is not None:
        leaf = [leaf] if isinstance(leaf, str) else list(leaf)
        df = df[df["leaf"].isin(leaf)]
    if xref is not None:
        xref = [xref] if isinstance(xref, str) else list(xref)
        df = df[df["xref"].isin(xref)]
    if layer_regex:
        df = df[df["layer"].str.contains(layer_regex, regex=True, na=False)]
    if bbox:
        df = bbox_filter(df, bbox)
    df = df.copy()
    df["asset_type"] = [classify(b, l) for b, l in zip(df["block"], df["leaf"])]
    if assets_only:
        df = df[~df["asset_type"].isin(NON_ASSET_TYPES)]
    return df.reset_index(drop=True)


def load_segments(label_prefix=None, seg_id=None, xref=None, closed_only=False) -> pd.DataFrame:
    """MTA segmentation: division-line / patch geometry (WKT) + its label anchor.

    One row per geometry feature. `seg_layer` is NOT unique on either side -
    69 seg_layers carry several geometries and one (SIG3.3) carries 38 label
    points - so the label table is collapsed to one anchor per seg_layer BEFORE
    the merge. Merging raw produced a 7.2x cartesian blow-up (17,377 rows for
    2,428 features) and every downstream count was wrong by that factor.

    Columns: xref, seg_layer, nverts, closed, wkt, label, x, y, n_label_pts
    where (x, y) is the centroid of that seg_layer's label points.
    """
    lab = load_segment_labels()
    geo = pd.read_csv(os.path.join(ASSETS, "seg_geometry.csv"))
    anchor = (lab.groupby("seg_layer")
                 .agg(label=("label", "first"),
                      x=("x", "mean"),
                      y=("y", "mean"),
                      n_label_pts=("label", "size"))
                 .reset_index())
    df = geo.merge(anchor, on="seg_layer", how="left", validate="many_to_one")
    if len(df) != len(geo):                       # cannot happen, but fail loud
        raise AssertionError(
            f"segment merge changed row count: {len(geo)} -> {len(df)}")
    if label_prefix:
        df = df[df["seg_layer"].astype(str).str.startswith(label_prefix)]
    if seg_id is not None:
        ids = [seg_id] if isinstance(seg_id, str) else list(seg_id)
        ids = {s.upper() for s in ids}
        df = df[df["seg_layer"].astype(str).str.upper().isin(ids)]
    if xref:
        df = df[df["xref"] == xref]
    if closed_only:
        df = df[df["closed"] == 1]
    return df.reset_index(drop=True)


def load_routes(leaf=None, leaf_regex=None, xref=None, etype=None, bbox=None,
                with_length=True) -> pd.DataFrame:
    """Linear civil / AGL geometry (ducts, conduit, sawcut, secondary cable,
    pavement edges, roads) as WKT, in local grid metres.

    These are the LWPOLYLINE / LINE / ARC / SPLINE routes that the v1 extraction
    discarded. `approx=1` means the geometry is a discretised or approximated
    curve (all ARC, CIRCLE, ELLIPSE, SPLINE), so a length from those is close but
    not exact - never quote a spline length as surveyed.

    leaf        : str or list, exact leaf-layer name(s), e.g. "CV_SEC_100MM"
    leaf_regex  : regex matched against the leaf layer, e.g. "DUCT|CONDUIT"
    etype       : str or list, "LINE" / "LWPOLYLINE" / "ARC" / ...
    bbox        : (xmin, ymin, xmax, ymax) - keeps a route if ANY vertex falls in
    with_length : add a `length_m` column (polyline length, not chainage)
    """
    df = pd.read_csv(os.path.join(ASSETS, "civil_routes.csv.gz"))
    if leaf is not None:
        leaf = [leaf] if isinstance(leaf, str) else list(leaf)
        df = df[df["leaf"].isin(leaf)]
    if leaf_regex:
        df = df[df["leaf"].str.contains(leaf_regex, case=False, regex=True, na=False)]
    if xref is not None:
        xref = [xref] if isinstance(xref, str) else list(xref)
        df = df[df["xref"].isin(xref)]
    if etype is not None:
        etype = [etype] if isinstance(etype, str) else list(etype)
        df = df[df["etype"].isin(etype)]
    if bbox:
        df = routes_in_bbox(df, bbox)
    df = df.copy()
    if with_length:
        df["length_m"] = [wkt_length(w) for w in df["wkt"]]
    return df.reset_index(drop=True)


def wkt_length(wkt: str) -> float:
    pts = wkt_coords(wkt)
    return sum(((pts[i + 1][0] - pts[i][0]) ** 2 +
                (pts[i + 1][1] - pts[i][1]) ** 2) ** 0.5
               for i in range(len(pts) - 1))


def routes_in_bbox(df: pd.DataFrame, bbox) -> pd.DataFrame:
    xmin, ymin, xmax, ymax = bbox
    keep = []
    for w in df["wkt"]:
        keep.append(any(xmin <= x <= xmax and ymin <= y <= ymax
                        for x, y in wkt_coords(w)))
    return df[pd.Series(keep, index=df.index)]


def load_layer_index() -> dict:
    with gzip.open(os.path.join(ASSETS, "layer_index.json.gz"), "rt") as fh:
        return json.load(fh)


# ----------------------------------------------------------------- helpers
def bbox_filter(df, bbox) -> pd.DataFrame:
    xmin, ymin, xmax, ymax = bbox
    return df[(df.x >= xmin) & (df.x <= xmax) & (df.y >= ymin) & (df.y <= ymax)]


def wkt_coords(wkt: str):
    body = re.sub(r"^\s*(LINESTRING|POLYGON)\s*\(+|\)+\s*$", "", wkt)
    return [tuple(float(v) for v in p.split()) for p in body.split(",")]


def segments_in_bbox(seg: pd.DataFrame, bbox) -> pd.DataFrame:
    xmin, ymin, xmax, ymax = bbox
    keep = []
    for w in seg["wkt"]:
        pts = wkt_coords(w)
        keep.append(any(xmin <= x <= xmax and ymin <= y <= ymax for x, y in pts))
    return seg[pd.Series(keep, index=seg.index)]


def segment_extent(seg_id: str, pad: float = 0.0):
    """Bounding box (xmin, ymin, xmax, ymax) of a segment's geometry + label points.

    Remember the caveat from SKILL.md: most segments are division LINES, not closed
    areas, so this extent is a working window around the segment, not its area.
    Returns None if the ID is unknown (e.g. a Zone 3 ID missing from the extraction).
    """
    seg = load_segments(seg_id=seg_id)
    lab = load_segment_labels()
    lab = lab[lab["seg_layer"].astype(str).str.upper() == seg_id.upper()]
    xs, ys = list(lab["x"]), list(lab["y"])
    for w in seg["wkt"]:
        for x, y in wkt_coords(w):
            xs.append(x)
            ys.append(y)
    if not xs:
        return None
    return (min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad)


def _point_line_dist(pts, line):
    """min distance from each of pts (n,2) to polyline `line`."""
    import numpy as np
    a = np.asarray(line[:-1], dtype=float)
    b = np.asarray(line[1:], dtype=float)
    p = np.asarray(pts, dtype=float)[:, None, :]
    ab = (b - a)[None, :, :]
    ap = p - a[None, :, :]
    t = np.clip((ap * ab).sum(-1) / np.maximum((ab * ab).sum(-1), 1e-12), 0.0, 1.0)
    return np.linalg.norm(ap - t[..., None] * ab, axis=-1).min(axis=1)


def _points_in_ring(ring, pts):
    """Ray-casting point-in-polygon for a closed ring, vectorised over pts."""
    import numpy as np
    P = np.asarray(ring, dtype=float)
    q = np.asarray(pts, dtype=float)
    x, y = q[:, 0], q[:, 1]
    inside = np.zeros(len(q), dtype=bool)
    x1, y1, x2, y2 = P[:-1, 0], P[:-1, 1], P[1:, 0], P[1:, 1]
    for i in range(len(x1)):
        straddles = (y1[i] > y) != (y2[i] > y)
        if not straddles.any():
            continue
        with np.errstate(divide="ignore", invalid="ignore"):
            xint = (x2[i] - x1[i]) * (y - y1[i]) / (y2[i] - y1[i]) + x1[i]
        inside ^= straddles & (x < xint)
    return inside


def _band_ring(A, B):
    """Close two roughly-parallel division lines into one band polygon."""
    import numpy as np
    if (np.linalg.norm(np.array(A[-1]) - np.array(B[0]))
            > np.linalg.norm(np.array(A[-1]) - np.array(B[-1]))):
        B = B[::-1]
    ring = list(A) + list(B)
    if ring[0] != ring[-1]:
        ring.append(ring[0])
    return ring


def segment_patches(seg_id: str, max_pair_sep: float = 90.0):
    """Reconstruct a segment's milling patches from its division lines.

    The drawing stores a milling segment as division lines, not closed areas, and
    the lines come in pairs that bound a band of pavement. This pairs each line
    with its mutually-nearest neighbour (median point-to-line separation, capped at
    `max_pair_sep`) and closes each pair into a band polygon; already-closed
    features are kept as drawn.

    Pairing matters because the *interior* of a band is where the centreline and
    lead-in lights sit. On TE5.1 the two bands are 32 m apart, so any buffer small
    enough to be defensible around a single line (12-15 m) reports zero taxiway
    centreline lights for a taxiway milling job - which is obviously wrong, and is
    exactly the failure this function exists to prevent.

    Returns (patches, strips) where patches is [(label, ring), ...] and strips is
    [(label, line), ...] for lines that found no partner. Strips are a genuine
    unknown: a single division line does not say which side of it the milling is,
    so callers must apply a width and say so.
    """
    seg = load_segments(seg_id=seg_id)
    if not len(seg):
        raise KeyError(
            f"segment {seg_id!r} not in the extraction - check the ID, and note "
            "Zone 3 segmentation is absent until the assets are rebuilt (SKILL.md).")
    import numpy as np

    closed = [wkt_coords(w) for w, c in zip(seg["wkt"], seg["closed"]) if c == 1]
    opens = [wkt_coords(w) for w, c in zip(seg["wkt"], seg["closed"]) if c != 1]
    # A 2-point division line is the common case (2,177 of 2,428 features) and pairs
    # exactly like a longer one - excluding them would leave most segments with no
    # reconstructed patch at all.
    pairable = [o for o in opens if len(o) >= 2]
    stubs = []

    n = len(pairable)
    med = np.full((n, n), np.inf)
    for i in range(n):
        for j in range(n):
            if i != j:
                med[i, j] = float(np.median(_point_line_dist(pairable[i], pairable[j])))

    patches = [(f"closed patch {k + 1} (as drawn)", r) for k, r in enumerate(closed)]
    used = set()
    for _, i in sorted((med[i].min(), i) for i in range(n)):
        if i in used:
            continue
        j = int(np.argmin(med[i]))
        if j in used or med[i, j] > max_pair_sep or int(np.argmin(med[j])) != i:
            continue
        used.add(i)
        used.add(j)
        patches.append((f"band {len([p for p in patches if p[0].startswith('band')]) + 1} "
                        f"({med[i, j]:.0f} m wide)", _band_ring(pairable[i], pairable[j])))
    strips = [(f"unpaired division line {k + 1}", ln) for k, ln in
              enumerate([pairable[i] for i in range(n) if i not in used] + stubs)]
    return patches, strips


def fixtures_in_segment(seg_id: str, strip_width: float = 25.0,
                        line_buffer: float = 3.0, **load_kwargs) -> pd.DataFrame:
    """Fixtures inside a segment's reconstructed milling patches.

    Use this, not `fixtures_near_segment`, for "which AGL assets does milling
    segment X affect" - it is the only one of the two that captures assets in the
    *middle* of a milling band (centreline lights, lead-in lights). See
    `segment_patches` for why, and SKILL.md for how to caveat the result: the
    patches are reconstructed, so this is "inside the reconstructed TE5.1 patches",
    never "inside TE5.1" as if the drawing said so.

    strip_width : half-width applied to division lines with no partner. Cannot be
                  derived from the drawing - state the assumption in the register.
    line_buffer : catches assets sitting on a patch boundary.

    Adds `basis` (why each row was selected) and `dist_m` (distance to the nearest
    segment line, 0 for interior assets).
    """
    import numpy as np

    patches, strips = segment_patches(seg_id)
    rings = [r for _, r in patches]
    lines = [ln for _, ln in strips]
    allpts = [p for r in rings for p in r] + [p for ln in lines for p in ln]
    pad = max(strip_width, line_buffer) + 5.0
    xs = [p[0] for p in allpts]
    ys = [p[1] for p in allpts]
    fx = load_fixtures(bbox=(min(xs) - pad, min(ys) - pad,
                             max(xs) + pad, max(ys) + pad), **load_kwargs)
    if not len(fx):
        return fx.assign(basis=pd.Series(dtype=object), dist_m=pd.Series(dtype=float))

    pts = fx[["x", "y"]].to_numpy()
    basis = np.array([""] * len(fx), dtype=object)
    for label, ring in patches:
        m = _points_in_ring(ring, pts) & (basis == "")
        basis[m] = f"inside {label}"
    for label, line in strips:
        m = (_point_line_dist(pts, line) <= strip_width) & (basis == "")
        basis[m] = f"within {strip_width:g} m of {label} (assumed width)"
    for label, ring in patches:
        m = (_point_line_dist(pts, ring) <= line_buffer) & (basis == "")
        basis[m] = f"within {line_buffer:g} m of {label} boundary"

    d = np.min([_point_line_dist(pts, g) for g in rings + lines], axis=0)
    fx = fx.assign(basis=basis, dist_m=d.round(2))
    return fx[fx["basis"] != ""].reset_index(drop=True)


def fixtures_near_segment(seg_id: str, buffer: float = 15.0, **load_kwargs) -> pd.DataFrame:
    """Fixtures within `buffer` metres of a segment's division LINES.

    Pure proximity - "what is close to this line". Right for "how far is the
    nearest handhole", wrong for milling impact: a band of pavement is bounded by a
    pair of lines 30-45 m apart, so a defensible single-line buffer skips
    everything down the middle of it. For impact work use `fixtures_in_segment`.

    load_kwargs pass through to load_fixtures (leaf=, assets_only=, ...).
    Adds a `dist_m` column. Raises KeyError for an unknown segment ID.
    """
    import numpy as np

    seg = load_segments(seg_id=seg_id)
    if not len(seg):
        raise KeyError(
            f"segment {seg_id!r} not in the extraction - check the ID, and note "
            "Zone 3 segmentation is absent until the assets are rebuilt (SKILL.md).")
    ext = segment_extent(seg_id, pad=buffer)
    fx = load_fixtures(bbox=ext, **load_kwargs)
    if not len(fx):
        return fx.assign(dist_m=pd.Series(dtype=float))

    # distance from each fixture to the nearest point on any segment polyline
    a, b = [], []
    for w in seg["wkt"]:
        pts = wkt_coords(w)
        a.extend(pts[:-1])
        b.extend(pts[1:])
    a = np.asarray(a)
    b = np.asarray(b)
    p = fx[["x", "y"]].to_numpy()[:, None, :]          # (n, 1, 2)
    ab = (b - a)[None, :, :]                           # (1, m, 2)
    ap = p - a[None, :, :]
    t = np.clip((ap * ab).sum(-1) / np.maximum((ab * ab).sum(-1), 1e-12), 0.0, 1.0)
    d = np.linalg.norm(ap - t[..., None] * ab, axis=-1).min(axis=1)
    fx = fx.assign(dist_m=d.round(2))
    return fx[fx["dist_m"] <= buffer].reset_index(drop=True)


# ----------------------------------------------------------------- plotting
# Fixed colours for the common types so the same asset looks the same on every
# sketch produced from this skill. Types not listed get a stable hash-picked
# colour from tab20.
TYPE_COLORS = {
    "Taxiway centreline light": "#2ecc40",
    "Taxiway edge light": "#0074d9",
    "Stop bar light": "#ff4136",
    "Lead-in light": "#b10dc9",
    "Holding position light": "#ff851b",
    "Runway guard light": "#ffdc00",
    "Runway guard light / RRM": "#ffdc00",
    "Guidance sign": "#111111",
    "Sign foundation": "#555555",
    "New light base": "#39cccc",
    "Existing light base": "#7fdbff",
    "Handhole": "#8b4513",
    "Existing handhole": "#a0783c",
    "Transformer pit": "#e91e63",
    "Existing transformer pit": "#f48fb1",
    "Manhole": "#795548",
}


def _type_color(name: str):
    if name in TYPE_COLORS:
        return TYPE_COLORS[name]
    import matplotlib.cm as cm
    return cm.tab20(sum(ord(c) for c in name) % 20)


def plot(fixtures=None, segments=None, routes=None, out="basemap.png", title="",
         figsize=(16, 12), dpi=200, label_segments=True, bbox=None, patches=None):
    """bbox clamps the axes - pass it whenever segments/routes are clipped by bbox
    membership, because a single far-away vertex in a kept polyline otherwise
    stretches the view to the whole airfield.

    patches : [(label, ring), ...] from segment_patches(), shaded so a reviewer can
              see which area the register was taken from."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=figsize)

    if patches:
        for label, ring in patches:
            ax.fill([p[0] for p in ring], [p[1] for p in ring],
                    color="#c0392b", alpha=0.12, zorder=0)
            ax.plot([p[0] for p in ring], [p[1] for p in ring],
                    color="#c0392b", lw=1.4, zorder=3)

    if segments is not None and len(segments):
        for _, r in segments.iterrows():
            pts = wkt_coords(r["wkt"])
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            ax.plot(xs, ys, lw=0.9, color="#c0392b", zorder=3)
        if label_segments:
            lab = segments.dropna(subset=["label"]).drop_duplicates("seg_layer")
            for _, r in lab.iterrows():
                ax.annotate(str(r["label"]), (r["x"], r["y"]), fontsize=5,
                            color="#7b241c", zorder=4)

    if routes is not None and len(routes):
        for name, grp in routes.groupby("leaf"):
            first = True
            for w in grp["wkt"]:
                pts = wkt_coords(w)
                ax.plot([p[0] for p in pts], [p[1] for p in pts], lw=1.1,
                        alpha=0.85, zorder=1,
                        label=f"{name} ({len(grp)})" if first else None)
                first = False

    if fixtures is not None and len(fixtures):
        for name, grp in fixtures.groupby("asset_type"):
            ax.scatter(grp.x, grp.y, s=6, color=_type_color(name),
                       label=f"{name} ({len(grp)})", zorder=2)
    if (fixtures is not None and len(fixtures)) or (routes is not None and len(routes)):
        ax.legend(loc="upper right", fontsize=7, markerscale=2, framealpha=0.9)

    if bbox:
        ax.set_xlim(bbox[0], bbox[2])
        ax.set_ylim(bbox[1], bbox[3])
    ax.set_aspect("equal")
    ax.set_xlabel("ZIA local grid E (m)")
    ax.set_ylabel("ZIA local grid N (m)")
    ax.set_title(title or "ZIA MTA basemap - LOCAL GRID (not UTM)")
    ax.grid(alpha=0.25, lw=0.4)
    fig.tight_layout()
    fig.savefig(out, dpi=dpi)
    plt.close(fig)
    return out


# ----------------------------------------------------------------- CLI
def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--leaf", nargs="*")
    p.add_argument("--xref", nargs="*")
    p.add_argument("--layer-regex")
    p.add_argument("--bbox", nargs=4, type=float, metavar=("XMIN", "YMIN", "XMAX", "YMAX"))
    p.add_argument("--seg-prefix")
    p.add_argument("--seg", help="segment ID, e.g. TE5.1 - register + sketch of the "
                                 "fixtures inside its reconstructed milling patches")
    p.add_argument("--strip-width", type=float, default=25.0,
                   help="assumed half-width for division lines with no partner")
    p.add_argument("--buffer", type=float,
                   help="with --seg, switch to pure proximity to the division LINES "
                        "instead of patch reconstruction. Skips assets mid-band - "
                        "only right for 'what is near this line' questions.")
    p.add_argument("--out", default="basemap.png")
    p.add_argument("--title", default="")
    p.add_argument("--csv-out")
    p.add_argument("--list-leaves", action="store_true")
    p.add_argument("--list-xrefs", action="store_true")
    p.add_argument("--list-types", action="store_true")
    p.add_argument("--assets-only", action="store_true")
    a = p.parse_args()

    if a.list_leaves:
        df = pd.read_csv(os.path.join(ASSETS, "agl_fixtures.csv.gz"))
        c = df.groupby("leaf").size().sort_values(ascending=False)
        for k, v in c.items():
            print(f"{v:>7}  {k:<32}")
        return
    if a.list_xrefs:
        df = pd.read_csv(os.path.join(ASSETS, "agl_fixtures.csv.gz"))
        print(df.groupby("xref").size().sort_values(ascending=False).to_string())
        return

    if a.list_types:
        f = load_fixtures()
        print(f.groupby("asset_type").size().sort_values(ascending=False).to_string())
        return

    if a.seg:
        patches = None
        if a.buffer is not None:
            fx = fixtures_near_segment(a.seg, buffer=a.buffer, leaf=a.leaf,
                                       xref=a.xref, layer_regex=a.layer_regex,
                                       assets_only=a.assets_only)
            basis = f"within {a.buffer:g} m of the {a.seg} division lines"
            pad = a.buffer * 2
        else:
            fx = fixtures_in_segment(a.seg, strip_width=a.strip_width, leaf=a.leaf,
                                     xref=a.xref, layer_regex=a.layer_regex,
                                     assets_only=a.assets_only)
            patches, strips = segment_patches(a.seg)
            basis = (f"inside the reconstructed {a.seg} milling patches "
                     f"({len(patches)} patches"
                     + (f", {len(strips)} unpaired lines at {a.strip_width:g} m"
                        if strips else "") + ")")
            pad = a.strip_width * 2
        ext = segment_extent(a.seg, pad=pad)
        seg = segments_in_bbox(load_segments(), ext)
        if not a.title:
            a.title = f"Segment {a.seg} - AGL assets {basis} (ZIA local grid, not UTM)"
        print(fx.groupby("asset_type").size().sort_values(ascending=False).to_string(),
              file=sys.stderr)
        print(f"\nselection basis: {basis}", file=sys.stderr)
        print(f"fixtures: {len(fx)}   segmentation features: {len(seg)}", file=sys.stderr)
        if a.csv_out:
            fx.to_csv(a.csv_out, index=False)
            print(f"wrote {a.csv_out}", file=sys.stderr)
        plot(fx, seg, out=a.out, title=a.title, bbox=ext, patches=patches)
        print(f"wrote {a.out}", file=sys.stderr)
        return

    fx = load_fixtures(leaf=a.leaf, xref=a.xref, layer_regex=a.layer_regex,
                       bbox=a.bbox, assets_only=a.assets_only)
    seg = load_segments(label_prefix=a.seg_prefix)
    if a.bbox:
        seg = segments_in_bbox(seg, a.bbox)
    print(f"fixtures: {len(fx)}   segmentation features: {len(seg)}", file=sys.stderr)
    if a.csv_out:
        fx.to_csv(a.csv_out, index=False)
        print(f"wrote {a.csv_out}", file=sys.stderr)
    plot(fx, seg, out=a.out, title=a.title, bbox=a.bbox)
    print(f"wrote {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
