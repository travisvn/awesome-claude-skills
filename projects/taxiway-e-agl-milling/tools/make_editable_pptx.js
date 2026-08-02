// Editable AGL shop drawings — Rev P04 (field condition — civil details removed) — A3 landscape PPTX
// Every plan element is a native, individually editable PowerPoint shape.
const pptxgen = require("pptxgenjs");
const fs = require("fs");

const D = JSON.parse(fs.readFileSync(__dirname + "/dwg_data.json", "utf8"));

const pres = new pptxgen();
pres.defineLayout({ name: "A3", width: 16.54, height: 11.69 });
pres.layout = "A3";

const C = {
  navy: "1E2761", teal: "0E7C86", gold: "C9A227",
  red: "CC0000", blue: "0055CC", orange: "E8710A", green: "1E8E3E",
  magenta: "BB00BB", grey: "9AA0A6", greyDark: "5F6368", asset: "12A5B8",
  ink: "1F2937", light: "F4F6F8", white: "FFFFFF",
  clgold: "C7A400", sbred: "8B0000", edgegrey: "7A8288",
};
const FONT = "Arial";

const META = {
  LOC01: {
    no: "1001", loc: "LOCATION 1",
    sub: "SCOPE PER FIELD SHEET Document_3 — FIELD CONDITION GOVERNS",
    scope: [
      "CORE OUT SHALLOW BASE + NEW CABLE: 11 No.",
      "   • VIA DUCT (6): SBC102-02/024, 01/027, 02/025, 01/028, 02/026, 01/029",
      "   • VIA SAWCUT (5): TCCECH-04/034, 03/036, 04/035, 03/037, 04/036",
      "NEW SECONDARY CABLE ONLY: 3 No.",
      "   • SBC102-02/027 (DUCT) · TCCECH-03/035, 03/018 (SAWCUT — bases OK, verify at cut line)",
      "FIELD VERIFIED NOT AFFECTED: SBC102-01/026 (no works)",
      "TCC103 FITTINGS NOT IN FIELD SCOPE — SHOWN AS EXISTING ONLY",
      "ISOLATE CIRCUITS: SBC102.01/.02, TCCECH.03/.04",
      "SITE RECORD 23.07.2026: 9 cored + 2 reinstatement already worked",
    ],
  },
  LOC02: {
    no: "1002", loc: "LOCATION 2",
    sub: "SCOPE PER FIELD SHEET Second_milling_area rev _1 — FIELD CONDITION GOVERNS",
    scope: [
      "NEW SECONDARY CABLE ONLY (VIA DUCT): 5 No.",
      "   • TCCECH-03/007, 04/007, 03/008, 04/008, 03/009",
      "NO SHALLOW BASES AFFECTED AT THIS LOCATION",
      "SECONDARY DUCT: CHAINED RUN HH.E.056 → 03/007 → 04/007 → 03/008 → 04/008 → 03/009 → HH.E.054",
      "   + SPUR FROM HH.E.055 — INDICATIVE, CONFIRM VS DUCT-LAYOUT CAD (REV B)",
      "RRM.555 (0.41 m from cut): REMOVE / PROTECT BEFORE SAWCUT, RE-FIX AFTER PAVING",
      "ISOLATE CIRCUITS: TCCECH.03, TCCECH.04",
    ],
  },
  LOC03: {
    no: "1003", loc: "LOCATION 3",
    sub: "SCOPE PER FIELD SHEET Second_milling_area rev _1 — FIELD CONDITION GOVERNS (rev _1 supersedes earlier all-NO rev)",
    scope: [
      "NO CORING AT THIS LOCATION — SECONDARY CABLES ONLY (12 RUNS)",
      "NEW CABLE VIA SAWCUT: 4 No. — SBC102-01/038, 01/039, 02/035, 02/036",
      "   (EP7 STOP BAR — bases per field rev _1: remove fitting & protect base, NO coring)",
      "NEW SECONDARY CABLE ONLY (VIA DUCT): 8 No.",
      "   • SBC102-01/040, 01/041, 02/037, 02/038, TCCECH-03/002, 04/002, 03/003, 04/003",
      "RRM.557 (0.07 m — treat as within works) & RRM.670: REMOVE / PROTECT / RE-FIX",
      "ISOLATE CIRCUITS: SBC102.01/.02, TCCECH.03/.04",
    ],
  },
};

const NOTES = [
  "1. All asset positions as-built (asset survey assets_20260726120533.xlsx, UTM 40N / EPSG:32640).",
  "2. AGL works area (red) per field condition — rectangular strips aligned to stop bar / centerline around field-verified affected assets. Coring at Location 1 only.",
  "3. Secondary cables: no joints — full manhole-to-light replacement. Confirm routes vs AGL duct-layout CAD (Rev B) before works.",
  "4. Isolate, lock out & prove dead all listed circuits at CCR under permit before any cutting, coring or excavation.",
  "5. Reinstatement setting-out by civil survey from as-built E/N, checked against adjacent undisturbed fittings before coring.",
  "6. Taxiway centerline & stop bar alignments derived from as-built AGL fitting positions (TCC / SBC). Edge / pavement boundary indicative at 23 m width from as-built CL — confirm on site.",
];

const ACTIONS = {
  CORE_DUCT: { outer: C.red, inner: C.blue, label: "CORE OUT + NEW CABLE (DUCT) — outer red / inner blue" },
  CORE_SAW: { outer: C.red, inner: C.orange, label: "CORE OUT + NEW CABLE (SAWCUT) — outer red / inner orange" },
  CABLE_DUCT: { outer: C.blue, inner: C.green, label: "NEW SEC. CABLE ONLY (DUCT) — outer blue / inner green" },
  CABLE_SAW: { outer: C.orange, inner: C.green, label: "NEW SEC. CABLE ONLY (SAWCUT) — outer orange / inner green" },
  NOT_AFF: { outer: C.grey, inner: null, label: "FIELD VERIFIED — NOT AFFECTED (grey)" },
  RRM: { outer: C.magenta, inner: C.white, label: "RRM — REMOVE / PROTECT / RE-FIX (magenta / white)" },
};

// ---------- cover ----------
{
  const s = pres.addSlide();
  s.background = { color: C.navy };
  s.addText("SHOP DRAWINGS — ELECTRICAL / AGL SCOPE", {
    x: 1.0, y: 2.1, w: 14.5, h: 1.0, fontFace: FONT, fontSize: 40, bold: true, color: C.white, margin: 0,
  });
  s.addText("RECTIFICATION OF TWY E BETWEEN E4 & E6 (ADIA)\nAGL WORKS AT THREE (3) MILLING LOCATIONS — FIELD CONDITION SCOPE", {
    x: 1.0, y: 3.2, w: 14.5, h: 1.2, fontFace: FONT, fontSize: 20, color: "CADCFC", margin: 0,
  });
  const rows = [
    ["Document No.", "[XXX-ELE-SHD-1001 / 1002 / 1003]  ·  Revision P05 (EDITABLE ISSUE)"],
    ["Basis of scope", "Field verification sheets: Document_3 (LOC-01) · Second_milling_area rev _1 (LOC-02/03)"],
    ["Base layer", "As-built AGL asset survey assets_20260726120533.xlsx — UTM 40N (EPSG:32640)"],
    ["Prepared by", "Mohammed — AGL Team Leader, ADB SAFEGATE AGL Team  ·  Issued 28.07.2026"],
  ];
  let y = 5.4;
  rows.forEach(r => {
    s.addText(r[0], { x: 1.0, y, w: 3.2, h: 0.42, fontFace: FONT, fontSize: 13, bold: true, color: C.gold, margin: 0 });
    s.addText(r[1], { x: 4.4, y, w: 11.2, h: 0.42, fontFace: FONT, fontSize: 13, color: C.white, margin: 0 });
    y += 0.52;
  });
  s.addText("EDITABLE VERSION — every symbol, polygon, label, note and legend entry on the drawing sheets is a native PowerPoint shape. Click any element to move, restyle or retype it, then export to PDF for issue.", {
    x: 1.0, y: 8.6, w: 14.5, h: 0.9, fontFace: FONT, fontSize: 12, italic: true, color: "CADCFC", margin: 0,
  });
}

// ---------- drawing sheets ----------
const PLAN = { x: 0.35, y: 0.85, w: 10.45, h: 10.45 };
const PANEL_X = 11.05, PANEL_W = 5.15;

// Liang–Barsky segment clip to bbox
function clipSeg(x1, y1, x2, y2, bb) {
  const [xmin, ymin, xmax, ymax] = bb;
  let t0 = 0, t1 = 1;
  const dx = x2 - x1, dy = y2 - y1;
  const p = [-dx, dx, -dy, dy], q = [x1 - xmin, xmax - x1, y1 - ymin, ymax - y1];
  for (let i = 0; i < 4; i++) {
    if (p[i] === 0) { if (q[i] < 0) return null; continue; }
    const r = q[i] / p[i];
    if (p[i] < 0) { if (r > t1) return null; if (r > t0) t0 = r; }
    else { if (r < t0) return null; if (r < t1) t1 = r; }
  }
  return [x1 + t0 * dx, y1 + t0 * dy, x1 + t1 * dx, y1 + t1 * dy];
}

function polyOpenPts(s, ch, opt, bbox, pt) {
  for (let i = 0; i < ch.length - 1; i++) {
    const c = clipSeg(ch[i][0], ch[i][1], ch[i + 1][0], ch[i + 1][1], bbox);
    if (c) segLine(s, pt(c[0], c[1]), pt(c[2], c[3]), opt);
  }
}

function mapper(bbox) {
  const [x0, y0, x1, y1] = bbox;
  const sc = Math.min(PLAN.w / (x1 - x0), PLAN.h / (y1 - y0));
  const ox = PLAN.x + (PLAN.w - (x1 - x0) * sc) / 2;
  const oy = PLAN.y + (PLAN.h - (y1 - y0) * sc) / 2;
  return { pt: (X, Y) => [ox + (X - x0) * sc, oy + (y1 - Y) * sc], sc };
}

function segLine(s, a, b, opt) {
  const x = Math.min(a[0], b[0]), y = Math.min(a[1], b[1]);
  const w = Math.abs(b[0] - a[0]), h = Math.abs(b[1] - a[1]);
  const rising = (b[0] - a[0]) * (b[1] - a[1]) < 0; // goes up left-to-right
  s.addShape("line", { x, y, w: Math.max(w, 0.001), h: Math.max(h, 0.001), flipV: rising, line: { color: opt.color, width: opt.width, dashType: opt.dash || "solid" } });
}

function poly(s, pts, opt) {
  for (let i = 0; i < pts.length; i++) segLine(s, pts[i], pts[(i + 1) % pts.length], opt);
}

for (const loc of ["LOC01", "LOC02", "LOC03"]) {
  const d = D[loc], m = META[loc];
  const s = pres.addSlide();
  s.background = { color: C.white };
  const { pt, sc } = mapper(d.bbox);

  // sheet header
  s.addText("SHOP DRAWING — ELECTRICAL / AGL SCOPE (FIELD-GOVERNED)   ·   TAXIWAY E (E4–E6) — " + m.loc + "   ·   DWG NO [XXX-ELE-SHD-" + m.no + "] REV P05", {
    x: 0.35, y: 0.18, w: 15.85, h: 0.5, fontFace: FONT, fontSize: 15, bold: true, color: C.navy, margin: 0,
  });

  // plan frame
  s.addShape("rect", { x: PLAN.x, y: PLAN.y, w: PLAN.w, h: PLAN.h, fill: { color: C.white }, line: { color: C.greyDark, width: 1 } });
  s.addText("UTM 40N (EPSG:32640) — AS-BUILT POSITIONS · NOT TO SCALE WHEN EDITED", {
    x: PLAN.x + 0.08, y: PLAN.y + PLAN.h - 0.3, w: 7.5, h: 0.25, fontFace: FONT, fontSize: 7, italic: true, color: C.grey, margin: 0,
  });

  // as-built taxiway markings (derived from TCC / SBC fittings)
  const mk = d.marks;
  mk.edge.forEach(ch => polyOpenPts(s, ch, { color: C.edgegrey, width: 1.0 }, d.bbox, pt));
  mk.cl.forEach(ch => polyOpenPts(s, ch, { color: C.clgold, width: 1.5, dash: "dashDot" }, d.bbox, pt));
  mk.sb.forEach(ch => polyOpenPts(s, ch, { color: C.sbred, width: 2.25 }, d.bbox, pt));

  // indicative ducts (clipped to map window)
  d.ducts.forEach(l => {
    const c = clipSeg(l[0], l[1], l[2], l[3], d.bbox);
    if (c) segLine(s, pt(c[0], c[1]), pt(c[2], c[3]), { color: "C9CDD2", width: 0.75, dash: "dash" });
  });
  // crossing runs (clipped to map window)
  d.cross.forEach(l => {
    const c = clipSeg(l[0], l[1], l[2], l[3], d.bbox);
    if (c) segLine(s, pt(c[0], c[1]), pt(c[2], c[3]), { color: C.magenta, width: 1.5, dash: "dash" });
  });
  // feed pits
  d.pits.forEach(p => {
    const xs = p.map(q => q[0]), ys = p.map(q => q[1]);
    const a = pt(Math.min(...xs), Math.max(...ys)), b = pt(Math.max(...xs), Math.min(...ys));
    s.addShape("rect", { x: a[0], y: a[1], w: Math.max(b[0] - a[0], 0.08), h: Math.max(b[1] - a[1], 0.08), fill: { type: "none" }, line: { color: C.magenta, width: 1.5 } });
  });
  d.pitlabels.forEach(t => {
    const p = pt(t[1], t[2]);
    s.addText(t[0], { x: p[0], y: p[1] - 0.12, w: 1.2, h: 0.2, fontFace: FONT, fontSize: 6.5, bold: true, color: C.magenta, margin: 0 });
  });
  // AGL works area (field condition)
  d.works.forEach(wp => poly(s, wp.map(q => pt(q[0], q[1])), { color: C.red, width: 2.5 }));
  const topPt = d.works.flat().reduce((a, b) => (b[1] > a[1] ? b : a));
  const tp = pt(topPt[0], topPt[1]);
  s.addText("AGL WORKS AREA — FIELD CONDITION (" + d.works_area + " m² TOTAL)", {
    x: Math.max(PLAN.x + 0.05, tp[0] - 2.6), y: Math.max(PLAN.y + 0.05, tp[1] - 0.3), w: 5.4, h: 0.22, fontFace: FONT, fontSize: 8, bold: true, color: C.red, margin: 0,
  });
  // existing assets + labels
  d.assets.forEach(a => {
    const p = pt(a[0], a[1]);
    s.addShape("ellipse", { x: p[0] - 0.032, y: p[1] - 0.032, w: 0.064, h: 0.064, fill: { color: C.asset }, line: { color: C.asset, width: 0.5 } });
  });
  d.alabels.forEach(t => {
    const p = pt(t[1], t[2]);
    s.addText(t[0], { x: p[0] + 0.03, y: p[1] - 0.09, w: 1.15, h: 0.16, fontFace: FONT, fontSize: 5, color: "AEB4BB", margin: 0 });
  });
  // works action symbols + labels
  for (const [act, items] of Object.entries(d.scope)) {
    const a = ACTIONS[act];
    items.forEach(it => {
      const p = pt(it[1], it[2]);
      s.addShape("ellipse", { x: p[0] - 0.115, y: p[1] - 0.115, w: 0.23, h: 0.23, fill: { type: "none" }, line: { color: a.outer, width: 2.25 } });
      if (a.inner) s.addShape("ellipse", { x: p[0] - 0.06, y: p[1] - 0.06, w: 0.12, h: 0.12, fill: { color: a.inner }, line: { color: a.inner, width: 0.5 } });
      s.addText(it[0], { x: p[0] + 0.13, y: p[1] - 0.24, w: 1.25, h: 0.18, fontFace: FONT, fontSize: 6.5, bold: true, color: C.ink, margin: 0 });
    });
  }

  // ---------- right panel ----------
  let py = 0.85;
  const box = (h, fill) => s.addShape("rect", { x: PANEL_X, y: py, w: PANEL_W, h, fill: { color: fill }, line: { color: "D5DAE0", width: 0.75 } });

  box(1.28, C.navy);
  s.addText(m.loc + " — " + META[loc].no + "  ·  REV P05 (EDITABLE)", { x: PANEL_X + 0.15, y: py + 0.1, w: PANEL_W - 0.3, h: 0.3, fontFace: FONT, fontSize: 12.5, bold: true, color: C.white, margin: 0 });
  s.addText(m.sub, { x: PANEL_X + 0.15, y: py + 0.44, w: PANEL_W - 0.3, h: 0.42, fontFace: FONT, fontSize: 8, color: "CADCFC", margin: 0 });
  s.addText("Scale 1:250 @ A1 equivalent · UTM 40N · Issued 28.07.2026 · Prepared: Mohammed, AGL Team Leader — ADB SAFEGATE", { x: PANEL_X + 0.15, y: py + 0.9, w: PANEL_W - 0.3, h: 0.34, fontFace: FONT, fontSize: 7, color: "CADCFC", margin: 0 });
  py += 1.4;

  const scopeH = 0.34 + m.scope.length * 0.253 + 0.12;
  box(scopeH, C.light);
  s.addText("SCOPE / QUANTITIES (PER FIELD VERIFICATION)", { x: PANEL_X + 0.15, y: py + 0.08, w: PANEL_W - 0.3, h: 0.24, fontFace: FONT, fontSize: 9.5, bold: true, color: C.navy, margin: 0 });
  s.addText(m.scope.join("\n"), { x: PANEL_X + 0.15, y: py + 0.36, w: PANEL_W - 0.3, h: scopeH - 0.42, fontFace: FONT, fontSize: 7.6, color: C.ink, margin: 0, lineSpacingMultiple: 1.12 });
  py += scopeH + 0.12;

  const notesH = 0.34 + NOTES.length * 0.34 + 0.1;
  box(notesH, C.white);
  s.addText("GENERAL NOTES", { x: PANEL_X + 0.15, y: py + 0.08, w: PANEL_W - 0.3, h: 0.24, fontFace: FONT, fontSize: 9.5, bold: true, color: C.navy, margin: 0 });
  s.addText(NOTES.join("\n"), { x: PANEL_X + 0.15, y: py + 0.36, w: PANEL_W - 0.3, h: notesH - 0.42, fontFace: FONT, fontSize: 6.8, color: C.greyDark, margin: 0, lineSpacingMultiple: 1.1 });
  py += notesH + 0.12;

  const acts = Object.keys(d.scope);
  const extra = [
    ["assetdot", "EXISTING AGL ASSET (AS-BUILT)"],
    ["ductind", "INDICATIVE DUCT — LIGHT TO NEAREST MH/HH"],
    ["cross", "SECONDARY DUCT RUN CROSSING CUT (INDICATIVE)"],
    ["hull", "AGL WORKS AREA — FIELD CONDITION (GOVERNING)"],
    ["mkcl", "TAXIWAY CENTERLINE (AS-BUILT, THROUGH TCC FITTINGS)"],
    ["mksb", "STOP BAR (AS-BUILT, THROUGH SBC FITTINGS)"],
    ["mkedge", "TWY EDGE / PAVEMENT BOUNDARY (INDICATIVE 23 m — CONFIRM ON SITE)"],
    ["pit", "AGL FEED MANHOLE / HANDHOLE"],
  ].filter(e => !(e[0] === "mksb" && d.marks.sb.length === 0));
  const legH = 0.36 + (acts.length + extra.length) * 0.30 + 0.08;
  box(legH, C.light);
  s.addText("LEGEND — WORKS ACTIONS (THIS SHEET)", { x: PANEL_X + 0.15, y: py + 0.08, w: PANEL_W - 0.3, h: 0.24, fontFace: FONT, fontSize: 9.5, bold: true, color: C.navy, margin: 0 });
  let ly = py + 0.42;
  acts.forEach(act => {
    const a = ACTIONS[act];
    s.addShape("ellipse", { x: PANEL_X + 0.22, y: ly + 0.015, w: 0.21, h: 0.21, fill: { type: "none" }, line: { color: a.outer, width: 2.25 } });
    if (a.inner) s.addShape("ellipse", { x: PANEL_X + 0.27, y: ly + 0.065, w: 0.11, h: 0.11, fill: { color: a.inner }, line: { color: a.inner, width: 0.5 } });
    s.addText(a.label, { x: PANEL_X + 0.56, y: ly, w: PANEL_W - 0.72, h: 0.26, fontFace: FONT, fontSize: 7.4, color: C.ink, margin: 0 });
    ly += 0.30;
  });
  extra.forEach(e => {
    if (e[0] === "assetdot") s.addShape("ellipse", { x: PANEL_X + 0.27, y: ly + 0.07, w: 0.1, h: 0.1, fill: { color: C.asset }, line: { color: C.asset, width: 0.5 } });
    if (e[0] === "ductind") s.addShape("line", { x: PANEL_X + 0.18, y: ly + 0.12, w: 0.3, h: 0.001, line: { color: "C9CDD2", width: 1, dashType: "dash" } });
    if (e[0] === "pit") s.addShape("rect", { x: PANEL_X + 0.2, y: ly + 0.03, w: 0.24, h: 0.16, fill: { type: "none" }, line: { color: C.magenta, width: 1.5 } });
    if (e[0] === "cross") s.addShape("line", { x: PANEL_X + 0.18, y: ly + 0.12, w: 0.3, h: 0.001, line: { color: C.magenta, width: 1.5, dashType: "dash" } });
    if (e[0] === "hull") s.addShape("line", { x: PANEL_X + 0.18, y: ly + 0.12, w: 0.3, h: 0.001, line: { color: C.red, width: 2.5 } });
    if (e[0] === "mkcl") s.addShape("line", { x: PANEL_X + 0.18, y: ly + 0.12, w: 0.3, h: 0.001, line: { color: C.clgold, width: 1.5, dashType: "dashDot" } });
    if (e[0] === "mksb") s.addShape("line", { x: PANEL_X + 0.18, y: ly + 0.12, w: 0.3, h: 0.001, line: { color: C.sbred, width: 2.25 } });
    if (e[0] === "mkedge") s.addShape("line", { x: PANEL_X + 0.18, y: ly + 0.12, w: 0.3, h: 0.001, line: { color: C.edgegrey, width: 1.0 } });
    s.addText(e[1], { x: PANEL_X + 0.56, y: ly, w: PANEL_W - 0.72, h: 0.26, fontFace: FONT, fontSize: 7.4, color: C.ink, margin: 0 });
    ly += 0.30;
  });
}

// ---------- scope table slide ----------
{
  const s = pres.addSlide();
  s.background = { color: C.white };
  s.addText("CONSOLIDATED FIELD-GOVERNED SCOPE — TWY E (E4–E6) · REV P05", { x: 0.5, y: 0.3, w: 15.5, h: 0.55, fontFace: FONT, fontSize: 20, bold: true, color: C.navy, margin: 0 });
  const header = ["Loc", "Asset", "Works Action", "Route", "Remarks"].map(t => ({ text: t, options: { bold: true, color: C.white, fill: { color: C.navy }, fontSize: 9 } }));
  const rows = [header];
  const remark = { CORE_DUCT: "Core out shallow base + full cable replacement", CORE_SAW: "Core out shallow base + full cable replacement", CABLE_DUCT: "Full manhole-to-light cable replacement", CABLE_SAW: "Full manhole-to-light cable replacement", NOT_AFF: "Field verified — no works", RRM: "Remove / protect before sawcut, re-fix after paving" };
  const actName = { CORE_DUCT: "CORE OUT + NEW CABLE", CORE_SAW: "CORE OUT + NEW CABLE", CABLE_DUCT: "NEW CABLE ONLY", CABLE_SAW: "NEW CABLE ONLY", NOT_AFF: "NOT AFFECTED", RRM: "RRM REMOVE / PROTECT" };
  const route = { CORE_DUCT: "Duct", CORE_SAW: "Sawcut", CABLE_DUCT: "Duct", CABLE_SAW: "Sawcut", NOT_AFF: "—", RRM: "—" };
  for (const loc of ["LOC01", "LOC02", "LOC03"]) {
    for (const [act, items] of Object.entries(D[loc].scope)) {
      items.forEach(it => rows.push([
        { text: loc.replace("LOC0", "LOC-0"), options: { fontSize: 8 } },
        { text: it[0], options: { fontSize: 8, bold: true } },
        { text: actName[act], options: { fontSize: 8 } },
        { text: route[act], options: { fontSize: 8 } },
        { text: remark[act], options: { fontSize: 8 } },
      ]));
    }
  }
  s.addTable(rows, { x: 0.5, y: 1.05, w: 15.5, colW: [1.1, 2.3, 3.4, 1.2, 7.5], border: { pt: 0.5, color: "C8CDD3" }, fontFace: FONT, color: C.ink, valign: "middle", rowH: 0.24 });
  s.addText("Totals: 11 core-outs (Location 1 only — no coring at Locations 2/3) · 31 secondary cable runs · 3 RRMs · 1 field-verified not affected. Edit rows as required, then align the drawing sheets to match.", { x: 0.5, y: 11.05, w: 15.5, h: 0.4, fontFace: FONT, fontSize: 10, italic: true, color: C.greyDark, margin: 0 });
}

pres.writeFile({ fileName: "/home/user/awesome-claude-skills/projects/taxiway-e-agl-milling/drawings/TWY-E-AGL-SHOPDWG-EDITABLE_RevP05.pptx" })
  .then(() => console.log("WROTE pptx"));
