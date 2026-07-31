const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType,
  AlignmentType, ShadingType, BorderStyle, ImageRun, VerticalAlign, LevelFormat,
} = require("docx");

const DXA = 1440;                       // 1 inch
const PAGE_W = 12240, PAGE_H = 15840;   // US Letter, matching the source IR
const MARGIN = 1080;                    // 0.75"
const CONTENT = PAGE_W - 2 * MARGIN;    // 10080

const GREY = "D9D9D9";
const thin = { style: BorderStyle.SINGLE, size: 4, color: "000000" };
const BORDERS = { top: thin, bottom: thin, left: thin, right: thin };

const t = (text, o = {}) => new TextRun({ text, font: "Calibri", size: o.size || 20, ...o });
const p = (runs, o = {}) => new Paragraph({ children: runs, ...o });

function cell(children, o = {}) {
  return new TableCell({
    children,
    width: { size: o.width, type: WidthType.DXA },
    shading: o.shade ? { type: ShadingType.CLEAR, fill: o.shade, color: "auto" } : undefined,
    verticalAlign: VerticalAlign.CENTER,
    borders: BORDERS,
    margins: { top: 60, bottom: 60, left: 90, right: 90 },
  });
}

// ---------------------------------------------------------------- header logos
const HDR_W = [4400, CONTENT - 4400];
const header = new Table({
  columnWidths: HDR_W,
  width: { size: CONTENT, type: WidthType.DXA },
  borders: {
    top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE },
    left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE },
    insideHorizontal: { style: BorderStyle.NONE }, insideVertical: { style: BorderStyle.NONE },
  },
  rows: [new TableRow({
    children: [
      new TableCell({
        children: [p([new ImageRun({
          type: "png", data: fs.readFileSync("adb-logo.png"),
          transformation: { width: 165, height: 57 },
        })])],
        width: { size: HDR_W[0], type: WidthType.DXA },
        borders: { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE },
                   left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE } },
        verticalAlign: VerticalAlign.CENTER,
      }),
      new TableCell({
        children: [p([new ImageRun({
          type: "png", data: fs.readFileSync("ada-logo.png"),
          transformation: { width: 108, height: 70 },
        })], { alignment: AlignmentType.RIGHT })],
        width: { size: HDR_W[1], type: WidthType.DXA },
        borders: { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE },
                   left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE } },
        verticalAlign: VerticalAlign.CENTER,
      }),
    ],
  })],
});

// ---------------------------------------------------------------- items table
const COLS = [520, 1240, 3400, 1080, 1000, 1120, 1720];
const HEADS = ["S/N", "ERP No.", "DESCRIPTION", "REQUIRED QTY", "UNIT\nPRICE",
               "TOTAL\nCOST", "REMARKS"];

const headRow = new TableRow({
  tableHeader: true,
  children: HEADS.map((h, i) => cell(
    h.split("\n").map((line) => p([t(line, { size: 16 })], { alignment: AlignmentType.CENTER })),
    { width: COLS[i], shade: GREY },
  )),
});

const ITEMS = [
  {
    erp: "10016966",
    desc: "BASE, MOUNTING;TYP:HIGH PRESSURE INJECTION SHALLOW, DMNSN:DIA 8IN; "
        + "MFR:ADB SAFEGATE,P/N:MSBC122V0003,P/N:M10;HS:85309000, W/EARTHING CONNECTION, "
        + "FIXING SCREW SET, ONE SIDE CABLE (POLE QTY: 2)",
    qty: "7 EA",
    unit: "323.80\nAED",
    total: "2,266.60\nAED",
    rem: "10 pcs available at ADA-D02 Warehouse",
  },
  {
    erp: "10020584",
    desc: "CABLE, ELECTRICAL;CNDCTR DIA:4MM2, CNDCTR QTY:2C, VOLT RTNG:2750.1KV "
        + "(1 rol/2000m)",
    qty: "350 M",
    unit: "7.57\nAED / M",
    total: "2,649.50\nAED",
    rem: "1 RoL (2000 m) available at ADA-D03 Warehouse. 350 m required; balance to remain "
       + "on the roll",
  },
];

const itemRows = ITEMS.map((it, n) => new TableRow({
  children: [
    cell([p([t(String(n + 1), { size: 18 })], { alignment: AlignmentType.CENTER })],
         { width: COLS[0] }),
    cell([p([t(it.erp, { size: 18 })], { alignment: AlignmentType.CENTER })], { width: COLS[1] }),
    cell([p([t(it.desc, { size: 18 })])], { width: COLS[2] }),
    cell([p([t(it.qty, { size: 18 })], { alignment: AlignmentType.CENTER })], { width: COLS[3] }),
    cell(it.unit.split("\n").map((l) =>
      p([t(l, { size: 18 })], { alignment: AlignmentType.CENTER })), { width: COLS[4] }),
    cell(it.total.split("\n").map((l) =>
      p([t(l, { size: 18 })], { alignment: AlignmentType.CENTER })), { width: COLS[5] }),
    cell([p([t(it.rem, { size: 18 })], { alignment: AlignmentType.CENTER })], { width: COLS[6] }),
  ],
}));

// rebuild the merged left span properly
const totalRowFixed = new TableRow({
  children: [
    new TableCell({
      children: [p([t("TOTAL", { size: 18, bold: true })], { alignment: AlignmentType.RIGHT })],
      columnSpan: 5,
      width: { size: COLS[0] + COLS[1] + COLS[2] + COLS[3] + COLS[4], type: WidthType.DXA },
      borders: BORDERS,
      shading: { type: ShadingType.CLEAR, fill: "F2F2F2", color: "auto" },
      margins: { top: 60, bottom: 60, left: 90, right: 90 },
      verticalAlign: VerticalAlign.CENTER,
    }),
    cell([p([t("4,916.10", { size: 18, bold: true })], { alignment: AlignmentType.CENTER }),
          p([t("AED", { size: 18, bold: true })], { alignment: AlignmentType.CENTER })],
         { width: COLS[5], shade: "F2F2F2" }),
    cell([p([t("", { size: 18 })])], { width: COLS[6], shade: "F2F2F2" }),
  ],
});

const itemsTable = new Table({
  columnWidths: COLS,
  width: { size: CONTENT, type: WidthType.DXA },
  rows: [headRow, ...itemRows, totalRowFixed],
});

// ---------------------------------------------------------------- signatures
const SIG = [CONTENT / 2, CONTENT / 2];
const sigTable = new Table({
  columnWidths: SIG,
  width: { size: CONTENT, type: WidthType.DXA },
  rows: [
    new TableRow({ children: [
      cell([p([t("REQUESTED BY (ADB SAFEGATE)", { bold: true })])], { width: SIG[0], shade: GREY }),
      cell([p([t("APPROVED BY (ADA)", { bold: true })])], { width: SIG[1], shade: GREY }),
    ] }),
    new TableRow({ children: [
      cell([p([t("Name: Ragesh Menon", { bold: true })])], { width: SIG[0] }),
      cell([p([t("Name: Ahmad Al Saafin", { bold: true })])], { width: SIG[1] }),
    ] }),
    new TableRow({ children: [
      cell([p([t("Signature:", { bold: true })])], { width: SIG[0] }),
      cell([p([t("Signature:", { bold: true })])], { width: SIG[1] }),
    ] }),
    new TableRow({ children: [
      cell([p([t("Date:", { bold: true })])], { width: SIG[0] }),
      cell([p([t("Date:", { bold: true })])], { width: SIG[1] }),
    ] }),
  ],
});

// ---------------------------------------------------------------- meta lines
function metaLine(label, value, rightBold, rightPlain) {
  const W = [2200, 260, 3600, CONTENT - 6060];
  const parts = [
    p([t(label, { bold: true })]),
    p([t(":")]),
    p([t(value)]),
    p(rightBold ? [t(rightBold, { bold: true }), t(rightPlain || "")] : [t("")],
      { alignment: AlignmentType.RIGHT }),
  ];
  return new Table({
    columnWidths: W,
    width: { size: CONTENT, type: WidthType.DXA },
    borders: {
      top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE },
      left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE },
      insideHorizontal: { style: BorderStyle.NONE }, insideVertical: { style: BorderStyle.NONE },
    },
    rows: [new TableRow({
      children: parts.map((para, i) => new TableCell({
        children: [para],
        width: { size: W[i], type: WidthType.DXA },
        borders: { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE },
                   left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE } },
      })),
    })],
  });
}

const doc = new Document({
  numbering: {
    config: [{
      reference: "just",
      levels: [{
        level: 0, format: LevelFormat.BULLET, text: "•",
        alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } },
      }],
    }],
  },
  sections: [{
    properties: {
      page: {
        size: { width: PAGE_W, height: PAGE_H },
        margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN },
      },
    },
    children: [
      header,
      p([]),
      p([t("ADB SAFEGATE AGL SPARE PARTS REQUISITION", { bold: true, size: 28 })],
        { alignment: AlignmentType.CENTER }),
      p([t("‘Abu Dhabi Airports’", { bold: true, size: 22 })],
        { alignment: AlignmentType.CENTER }),
      p([]),
      metaLine("Requisition Type", "Internal"),
      metaLine("Date  Requested", "31-Jul- 2026", "Requisition No:", " ADB-IR 64"),
      p([]),
      itemsTable,
      p([t("(NOT PAYABLE)", { bold: true, size: 18 })], { alignment: AlignmentType.RIGHT }),
      p([]),
      p([]),
      p([t("JUSTIFICATION:", { bold: true, underline: {} })]),
      p([]),
      p([t("Please be informed that we are currently experiencing shortages of certain "
         + "materials, namely secondary cable and shallow bases. These materials are "
         + "available in the ADA store.")],
        { numbering: { reference: "just", level: 0 } }),
      p([t("To ensure timely completion of the works within the specified closure period and "
         + "to prevent any delay, we request approval to withdraw these materials through this "
         + "IR. Kindly arrange for the release of these materials at the earliest.")],
        { numbering: { reference: "just", level: 0 } }),
      p([t("The materials are required for the AGL rectification works on TWY E between E4 and "
         + "E6, per the final scope of work AUH-SK-AGL-TWYE-001 Rev P08.")],
        { numbering: { reference: "just", level: 0 } }),
      p([]),
      p([]),
      sigTable,
    ],
  }],
});

Packer.toBuffer(doc).then((b) => {
  fs.writeFileSync("ADB-IR 64 - Secondary Cable & Shallow Base - TWY E.docx", b);
  console.log("saved");
});
