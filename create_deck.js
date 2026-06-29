const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const { FaExclamationTriangle, FaCogs, FaLayerGroup, FaBrain, FaShieldAlt, FaTrophy, FaServer, FaLightbulb } = require("react-icons/fa");

function renderIconSvg(IconComponent, color, size = 256) {
  return ReactDOMServer.renderToStaticMarkup(
    React.createElement(IconComponent, { color, size: String(size) })
  );
}

async function iconToBase64Png(IconComponent, color, size = 256) {
  const svg = renderIconSvg(IconComponent, color, size);
  const pngBuffer = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + pngBuffer.toString("base64");
}

const makeShadow = () => ({ type: "outer", color: "000000", blur: 6, offset: 2, angle: 45, opacity: 0.12 });

// Color palette — Ocean Gradient
const C = {
  darkBg: "0B1D33",
  navy: "21295C",
  deepBlue: "065A82",
  teal: "1C7293",
  lightTeal: "E8F4F8",
  white: "FFFFFF",
  offWhite: "F7FAFC",
  text: "1E293B",
  muted: "64748B",
  accent: "0891B2",
};

async function main() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9";
  pres.author = "Ronak Dedhiya";
  pres.title = "AI Candidate Ranking System";

  // Pre-render icons
  const iconProblem = await iconToBase64Png(FaExclamationTriangle, "#" + C.white);
  const iconArch = await iconToBase64Png(FaCogs, "#" + C.teal);
  const iconScoring = await iconToBase64Png(FaLayerGroup, "#" + C.teal);
  const iconFeatures = await iconToBase64Png(FaBrain, "#" + C.teal);
  const iconHoneypot = await iconToBase64Png(FaShieldAlt, "#" + C.teal);
  const iconResults = await iconToBase64Png(FaTrophy, "#" + C.teal);
  const iconTech = await iconToBase64Png(FaServer, "#" + C.teal);
  const iconDecisions = await iconToBase64Png(FaLightbulb, "#" + C.white);

  // ---- SLIDE 1: Title ----
  let s1 = pres.addSlide();
  s1.background = { color: C.darkBg };
  // Decorative shape
  s1.addShape(pres.shapes.OVAL, { x: 7.5, y: -1.5, w: 5, h: 5, fill: { color: C.deepBlue, transparency: 40 } });
  s1.addShape(pres.shapes.OVAL, { x: -1.5, y: 3.5, w: 4, h: 4, fill: { color: C.navy, transparency: 50 } });
  s1.addText("AI Candidate Ranking System", {
    x: 0.8, y: 1.2, w: 8.4, h: 1.2, fontSize: 40, fontFace: "Calibri",
    color: C.white, bold: true, margin: 0,
  });
  s1.addText("Semantic understanding over keyword matching", {
    x: 0.8, y: 2.5, w: 8.4, h: 0.7, fontSize: 20, fontFace: "Calibri",
    color: C.accent, margin: 0,
  });
  s1.addText("Redrob AI Hackathon  |  2026", {
    x: 0.8, y: 3.5, w: 8.4, h: 0.5, fontSize: 14, fontFace: "Calibri",
    color: C.muted, margin: 0,
  });

  // ---- SLIDE 2: Problem ----
  let s2 = pres.addSlide();
  s2.background = { color: C.darkBg };
  s2.addImage({ data: iconProblem, x: 0.8, y: 0.5, w: 0.45, h: 0.45 });
  s2.addText("The Problem", {
    x: 1.4, y: 0.45, w: 5, h: 0.55, fontSize: 32, fontFace: "Calibri",
    color: C.white, bold: true, margin: 0,
  });

  const problems = [
    { title: "Missed Talent", desc: "Recruiters review hundreds of profiles, still miss the right person" },
    { title: "Keyword Trap", desc: "Marketing managers with AI buzzwords rank above real engineers" },
    { title: "Static Profiles", desc: "No behavioral signals — is the candidate actually available?" },
    { title: "Data Traps", desc: "~80 honeypot candidates with impossible profiles exist in the data" },
  ];
  problems.forEach((p, i) => {
    const y = 1.4 + i * 1.0;
    s2.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.8, y: y, w: 8.4, h: 0.8, fill: { color: C.navy, transparency: 30 }, rectRadius: 0.08,
    });
    s2.addText([
      { text: p.title, options: { bold: true, color: C.accent, fontSize: 15 } },
      { text: "  —  " + p.desc, options: { color: C.white, fontSize: 14 } },
    ], { x: 1.1, y: y + 0.1, w: 7.8, h: 0.6, fontFace: "Calibri", margin: 0, valign: "middle" });
  });

  // ---- SLIDE 3: Architecture ----
  let s3 = pres.addSlide();
  s3.background = { color: C.offWhite };
  s3.addImage({ data: iconArch, x: 0.8, y: 0.4, w: 0.45, h: 0.45 });
  s3.addText("Two-Phase Architecture", {
    x: 1.4, y: 0.35, w: 6, h: 0.55, fontSize: 32, fontFace: "Calibri",
    color: C.text, bold: true, margin: 0,
  });

  // Phase A card
  s3.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.6, y: 1.2, w: 4.3, h: 3.6, fill: { color: C.white }, rectRadius: 0.1, shadow: makeShadow(),
  });
  s3.addText("Phase A: Pre-computation", {
    x: 0.9, y: 1.35, w: 3.7, h: 0.45, fontSize: 16, fontFace: "Calibri",
    color: C.deepBlue, bold: true, margin: 0,
  });
  s3.addText("Run once, no time limit", {
    x: 0.9, y: 1.75, w: 3.7, h: 0.3, fontSize: 11, fontFace: "Calibri", color: C.muted, margin: 0,
  });
  s3.addText([
    { text: "Generate 384-dim text embeddings for 100K candidates using all-MiniLM-L6-v2", options: { bullet: true, breakLine: true, fontSize: 12 } },
    { text: "Detect ~64 honeypot candidates via 4 integrity checks", options: { bullet: true, breakLine: true, fontSize: 12 } },
    { text: "Artifacts: embeddings.npy (147MB), honeypots.json", options: { bullet: true, fontSize: 12 } },
  ], { x: 0.9, y: 2.2, w: 3.7, h: 2.2, fontFace: "Calibri", color: C.text, margin: 0, paraSpaceAfter: 8, valign: "top" });

  // Phase B card
  s3.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 5.1, y: 1.2, w: 4.3, h: 3.6, fill: { color: C.white }, rectRadius: 0.1, shadow: makeShadow(),
  });
  s3.addText("Phase B: Runtime Ranking", {
    x: 5.4, y: 1.35, w: 3.7, h: 0.45, fontSize: 16, fontFace: "Calibri",
    color: C.deepBlue, bold: true, margin: 0,
  });
  s3.addText("18 seconds, CPU only", {
    x: 5.4, y: 1.75, w: 3.7, h: 0.3, fontSize: 11, fontFace: "Calibri", color: C.muted, margin: 0,
  });
  s3.addText([
    { text: "Stream 100K candidates", options: { bullet: true, breakLine: true, fontSize: 12 } },
    { text: "Extract features per candidate", options: { bullet: true, breakLine: true, fontSize: 12 } },
    { text: "Hard filter (honeypots, consulting-only, non-tech)", options: { bullet: true, breakLine: true, fontSize: 12 } },
    { text: "Composite scoring with behavioral modifier", options: { bullet: true, breakLine: true, fontSize: 12 } },
    { text: "Output top 100 as CSV with reasoning", options: { bullet: true, fontSize: 12 } },
  ], { x: 5.4, y: 2.2, w: 3.7, h: 2.2, fontFace: "Calibri", color: C.text, margin: 0, paraSpaceAfter: 6, valign: "top" });

  // Arrow between phases
  s3.addText(">>>", { x: 4.5, y: 2.7, w: 0.8, h: 0.5, fontSize: 20, color: C.accent, align: "center", fontFace: "Calibri" });

  // ---- SLIDE 4: Scoring ----
  let s4 = pres.addSlide();
  s4.background = { color: C.offWhite };
  s4.addImage({ data: iconScoring, x: 0.8, y: 0.4, w: 0.45, h: 0.45 });
  s4.addText("3-Layer Scoring System", {
    x: 1.4, y: 0.35, w: 6, h: 0.55, fontSize: 32, fontFace: "Calibri",
    color: C.text, bold: true, margin: 0,
  });

  // Layer 1
  s4.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.6, y: 1.15, w: 2.8, h: 3.6, fill: { color: C.white }, rectRadius: 0.1, shadow: makeShadow(),
  });
  s4.addText("Layer 1", { x: 0.8, y: 1.25, w: 2.4, h: 0.35, fontSize: 13, color: C.deepBlue, bold: true, fontFace: "Calibri", margin: 0 });
  s4.addText("Hard Filters", { x: 0.8, y: 1.55, w: 2.4, h: 0.3, fontSize: 11, color: C.muted, fontFace: "Calibri", margin: 0 });
  s4.addText([
    { text: "Honeypot detected", options: { bullet: true, breakLine: true, fontSize: 11 } },
    { text: "Consulting-only career", options: { bullet: true, breakLine: true, fontSize: 11 } },
    { text: "Non-tech + no AI evidence", options: { bullet: true, fontSize: 11 } },
  ], { x: 0.8, y: 2.0, w: 2.4, h: 2.4, fontFace: "Calibri", color: C.text, margin: 0, paraSpaceAfter: 6 });

  // Layer 2
  s4.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 3.6, y: 1.15, w: 2.8, h: 3.6, fill: { color: C.white }, rectRadius: 0.1, shadow: makeShadow(),
  });
  s4.addText("Layer 2", { x: 3.8, y: 1.25, w: 2.4, h: 0.35, fontSize: 13, color: C.deepBlue, bold: true, fontFace: "Calibri", margin: 0 });
  s4.addText("Composite Fit (0–1)", { x: 3.8, y: 1.55, w: 2.4, h: 0.3, fontSize: 11, color: C.muted, fontFace: "Calibri", margin: 0 });
  s4.addText([
    { text: "Skills: 30%", options: { bullet: true, breakLine: true, fontSize: 11, bold: true } },
    { text: "Career: 25%", options: { bullet: true, breakLine: true, fontSize: 11, bold: true } },
    { text: "Title: 15%", options: { bullet: true, breakLine: true, fontSize: 11 } },
    { text: "Semantic: 10%", options: { bullet: true, breakLine: true, fontSize: 11 } },
    { text: "Experience: 10%", options: { bullet: true, breakLine: true, fontSize: 11 } },
    { text: "Location: 5%", options: { bullet: true, breakLine: true, fontSize: 11 } },
    { text: "Education: 5%", options: { bullet: true, fontSize: 11 } },
  ], { x: 3.8, y: 2.0, w: 2.4, h: 2.4, fontFace: "Calibri", color: C.text, margin: 0, paraSpaceAfter: 3 });

  // Layer 3
  s4.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 6.6, y: 1.15, w: 2.8, h: 3.6, fill: { color: C.white }, rectRadius: 0.1, shadow: makeShadow(),
  });
  s4.addText("Layer 3", { x: 6.8, y: 1.25, w: 2.4, h: 0.35, fontSize: 13, color: C.deepBlue, bold: true, fontFace: "Calibri", margin: 0 });
  s4.addText("Behavioral (0.5–1.2x)", { x: 6.8, y: 1.55, w: 2.4, h: 0.3, fontSize: 11, color: C.muted, fontFace: "Calibri", margin: 0 });
  s4.addText([
    { text: "Availability: 50%", options: { bullet: true, breakLine: true, fontSize: 11, bold: true } },
    { text: "(response rate, recency)", options: { breakLine: true, fontSize: 10, color: C.muted, indentLevel: 1 } },
    { text: "Quality: 30%", options: { bullet: true, breakLine: true, fontSize: 11 } },
    { text: "(GitHub, verifications)", options: { breakLine: true, fontSize: 10, color: C.muted, indentLevel: 1 } },
    { text: "Notice period: 20%", options: { bullet: true, fontSize: 11 } },
  ], { x: 6.8, y: 2.0, w: 2.4, h: 2.4, fontFace: "Calibri", color: C.text, margin: 0, paraSpaceAfter: 3 });

  // Formula at bottom
  s4.addText("Final Score  =  Fit Score  ×  Behavioral Modifier", {
    x: 0.6, y: 4.95, w: 8.8, h: 0.4, fontSize: 14, fontFace: "Calibri",
    color: C.deepBlue, bold: true, align: "center", margin: 0,
  });

  // ---- SLIDE 5: Features ----
  let s5 = pres.addSlide();
  s5.background = { color: C.offWhite };
  s5.addImage({ data: iconFeatures, x: 0.8, y: 0.4, w: 0.45, h: 0.45 });
  s5.addText("Beyond Keywords: Multi-Signal Features", {
    x: 1.4, y: 0.35, w: 7, h: 0.55, fontSize: 30, fontFace: "Calibri",
    color: C.text, bold: true, margin: 0,
  });

  const featureCards = [
    {
      title: "Skills Features",
      items: ["119 skills → MUST_HAVE / STRONG_SIGNAL / SUPPORTING", "Synonym groups (FAISS = Pinecone = Qdrant)", "Trust = proficiency × endorsements × duration"],
    },
    {
      title: "Career Text Analysis",
      items: ["Regex detection of retrieval, ML, production keywords", "Production evidence: deployed, scale, latency", "Consulting firm career detection"],
    },
    {
      title: "Semantic Understanding",
      items: ["Sentence-transformer embeddings (384-dim)", "Captures meaning beyond exact keywords", "\"RecSys engineer\" matches \"retrieval engineer\""],
    },
  ];

  featureCards.forEach((card, i) => {
    const x = 0.6 + i * 3.1;
    s5.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: x, y: 1.2, w: 2.9, h: 3.6, fill: { color: C.white }, rectRadius: 0.1, shadow: makeShadow(),
    });
    s5.addText(card.title, {
      x: x + 0.2, y: 1.35, w: 2.5, h: 0.4, fontSize: 14, fontFace: "Calibri",
      color: C.deepBlue, bold: true, margin: 0,
    });
    const textArr = card.items.map((item, j) => ({
      text: item,
      options: { bullet: true, breakLine: j < card.items.length - 1, fontSize: 11 },
    }));
    s5.addText(textArr, {
      x: x + 0.2, y: 1.9, w: 2.5, h: 2.6, fontFace: "Calibri", color: C.text, margin: 0, paraSpaceAfter: 8, valign: "top",
    });
  });

  // ---- SLIDE 6: Honeypot ----
  let s6 = pres.addSlide();
  s6.background = { color: C.offWhite };
  s6.addImage({ data: iconHoneypot, x: 0.8, y: 0.4, w: 0.45, h: 0.45 });
  s6.addText("Trap Detection Strategy", {
    x: 1.4, y: 0.35, w: 6, h: 0.55, fontSize: 32, fontFace: "Calibri",
    color: C.text, bold: true, margin: 0,
  });

  // Table
  const hpTableRows = [
    [
      { text: "Check", options: { bold: true, color: C.white, fill: { color: C.deepBlue }, fontSize: 12 } },
      { text: "What It Catches", options: { bold: true, color: C.white, fill: { color: C.deepBlue }, fontSize: 12 } },
      { text: "Count", options: { bold: true, color: C.white, fill: { color: C.deepBlue }, fontSize: 12, align: "center" } },
    ],
    [
      { text: "Duration Mismatch", options: { fontSize: 11, bold: true } },
      { text: "Claimed months > 2× actual date span", options: { fontSize: 11 } },
      { text: "18", options: { fontSize: 13, bold: true, color: C.accent, align: "center" } },
    ],
    [
      { text: "Expert Zero Duration", options: { fontSize: 11, bold: true } },
      { text: "Expert proficiency with 0 months on 2+ skills", options: { fontSize: 11 } },
      { text: "21", options: { fontSize: 13, bold: true, color: C.accent, align: "center" } },
    ],
    [
      { text: "YOE vs Career Span", options: { fontSize: 11, bold: true } },
      { text: "Claimed YOE > career span + 3 years", options: { fontSize: 11 } },
      { text: "25", options: { fontSize: 13, bold: true, color: C.accent, align: "center" } },
    ],
    [
      { text: "Start After End", options: { fontSize: 11, bold: true } },
      { text: "Career entry with start_date > end_date", options: { fontSize: 11 } },
      { text: "0", options: { fontSize: 13, align: "center" } },
    ],
  ];

  s6.addTable(hpTableRows, {
    x: 0.6, y: 1.2, w: 8.8, colW: [2.5, 4.8, 1.5],
    border: { pt: 0.5, color: "E2E8F0" },
    rowH: [0.45, 0.45, 0.45, 0.45, 0.45],
    fontFace: "Calibri",
    color: C.text,
  });

  // Result callout
  s6.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.6, y: 3.8, w: 8.8, h: 1.0, fill: { color: C.lightTeal }, rectRadius: 0.1,
  });
  s6.addText([
    { text: "64 honeypots detected", options: { bold: true, fontSize: 18, color: C.deepBlue } },
    { text: "   |   ", options: { fontSize: 18, color: C.muted } },
    { text: "0 in top 100", options: { bold: true, fontSize: 18, color: C.accent } },
  ], { x: 0.8, y: 3.85, w: 8.4, h: 0.9, fontFace: "Calibri", align: "center", valign: "middle", margin: 0 });

  // ---- SLIDE 7: Results ----
  let s7 = pres.addSlide();
  s7.background = { color: C.offWhite };
  s7.addImage({ data: iconResults, x: 0.8, y: 0.4, w: 0.45, h: 0.45 });
  s7.addText("Results", {
    x: 1.4, y: 0.35, w: 6, h: 0.55, fontSize: 32, fontFace: "Calibri",
    color: C.text, bold: true, margin: 0,
  });

  // Top 5 table
  const resultsTable = [
    [
      { text: "#", options: { bold: true, color: C.white, fill: { color: C.deepBlue }, fontSize: 11, align: "center" } },
      { text: "Candidate", options: { bold: true, color: C.white, fill: { color: C.deepBlue }, fontSize: 11 } },
      { text: "YOE", options: { bold: true, color: C.white, fill: { color: C.deepBlue }, fontSize: 11, align: "center" } },
      { text: "Core Skills", options: { bold: true, color: C.white, fill: { color: C.deepBlue }, fontSize: 11 } },
    ],
    [{ text: "1", options: { align: "center", fontSize: 11 } }, { text: "Lead AI Engineer @ Razorpay", options: { fontSize: 11, bold: true } }, { text: "6.7", options: { align: "center", fontSize: 11 } }, { text: "BM25, Elasticsearch, Embeddings, IR", options: { fontSize: 10 } }],
    [{ text: "2", options: { align: "center", fontSize: 11 } }, { text: "AI Engineer @ Microsoft", options: { fontSize: 11, bold: true } }, { text: "6.9", options: { align: "center", fontSize: 11 } }, { text: "BM25, L2R, OpenSearch, RecSys", options: { fontSize: 10 } }],
    [{ text: "3", options: { align: "center", fontSize: 11 } }, { text: "Staff ML Engineer @ Paytm", options: { fontSize: 11, bold: true } }, { text: "7.0", options: { align: "center", fontSize: 11 } }, { text: "BM25, IR, OpenSearch, Pinecone", options: { fontSize: 10 } }],
    [{ text: "4", options: { align: "center", fontSize: 11 } }, { text: "Senior ML Engineer @ Zomato", options: { fontSize: 11, bold: true } }, { text: "7.2", options: { align: "center", fontSize: 11 } }, { text: "BM25, Embeddings, IR, L2R", options: { fontSize: 10 } }],
    [{ text: "5", options: { align: "center", fontSize: 11 } }, { text: "Senior NLP Engineer @ Salesforce", options: { fontSize: 11, bold: true } }, { text: "8.9", options: { align: "center", fontSize: 11 } }, { text: "BM25, Elasticsearch, OpenSearch, Pinecone", options: { fontSize: 10 } }],
  ];
  s7.addTable(resultsTable, {
    x: 0.6, y: 1.1, w: 8.8, colW: [0.5, 3.3, 0.7, 4.3],
    border: { pt: 0.5, color: "E2E8F0" }, fontFace: "Calibri", color: C.text,
    rowH: [0.4, 0.4, 0.4, 0.4, 0.4, 0.4],
  });

  // Stats row
  const stats = [
    { num: "18.6s", label: "Execution Time" },
    { num: "14,640", label: "Filtered Out" },
    { num: "0", label: "Honeypots in Top 100" },
    { num: "100%", label: "Top-10 Product Co." },
  ];
  stats.forEach((stat, i) => {
    const x = 0.6 + i * 2.35;
    s7.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: x, y: 3.8, w: 2.15, h: 1.2, fill: { color: C.white }, rectRadius: 0.1, shadow: makeShadow(),
    });
    s7.addText(stat.num, {
      x: x, y: 3.9, w: 2.15, h: 0.6, fontSize: 22, fontFace: "Calibri",
      color: C.deepBlue, bold: true, align: "center", margin: 0,
    });
    s7.addText(stat.label, {
      x: x, y: 4.45, w: 2.15, h: 0.4, fontSize: 10, fontFace: "Calibri",
      color: C.muted, align: "center", margin: 0,
    });
  });

  // ---- SLIDE 8: Tech Stack ----
  let s8 = pres.addSlide();
  s8.background = { color: C.offWhite };
  s8.addImage({ data: iconTech, x: 0.8, y: 0.4, w: 0.45, h: 0.45 });
  s8.addText("Technology Stack", {
    x: 1.4, y: 0.35, w: 6, h: 0.55, fontSize: 32, fontFace: "Calibri",
    color: C.text, bold: true, margin: 0,
  });

  // Left column — stack
  s8.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.6, y: 1.15, w: 4.3, h: 3.8, fill: { color: C.white }, rectRadius: 0.1, shadow: makeShadow(),
  });
  s8.addText("Stack", { x: 0.9, y: 1.3, w: 3.7, h: 0.35, fontSize: 15, fontFace: "Calibri", color: C.deepBlue, bold: true, margin: 0 });

  const stackItems = [
    { label: "Core", value: "Python 3.11, NumPy, Pandas, orjson" },
    { label: "Embeddings", value: "sentence-transformers (all-MiniLM-L6-v2, 22M params)" },
    { label: "Scoring", value: "scikit-learn (cosine similarity)" },
    { label: "Sandbox", value: "Streamlit web app" },
  ];
  const stackText = stackItems.map((item, j) => [
    { text: item.label + ": ", options: { bold: true, fontSize: 12, breakLine: false } },
    { text: item.value, options: { fontSize: 12, breakLine: j < stackItems.length - 1 } },
  ]).flat();
  s8.addText(stackText, {
    x: 0.9, y: 1.8, w: 3.7, h: 2.8, fontFace: "Calibri", color: C.text, margin: 0, paraSpaceAfter: 10, valign: "top",
  });

  // Right column — constraints
  s8.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 5.1, y: 1.15, w: 4.3, h: 3.8, fill: { color: C.white }, rectRadius: 0.1, shadow: makeShadow(),
  });
  s8.addText("Constraints Met", { x: 5.4, y: 1.3, w: 3.7, h: 0.35, fontSize: 15, fontFace: "Calibri", color: C.deepBlue, bold: true, margin: 0 });

  const constraints = [
    { achieved: "18.6s execution", limit: "limit: 5 min" },
    { achieved: "~2GB RAM peak", limit: "limit: 16GB" },
    { achieved: "CPU only", limit: "no GPU" },
    { achieved: "No network calls", limit: "fully offline" },
    { achieved: "147MB precomputed", limit: "limit: 5GB" },
  ];
  const cText = constraints.map((c, j) => [
    { text: c.achieved, options: { bold: true, fontSize: 12, breakLine: false } },
    { text: "  (" + c.limit + ")", options: { fontSize: 11, color: C.muted, breakLine: j < constraints.length - 1 } },
  ]).flat();
  s8.addText(cText, {
    x: 5.4, y: 1.8, w: 3.7, h: 2.8, fontFace: "Calibri", color: C.text, margin: 0, paraSpaceAfter: 10, valign: "top",
  });

  // ---- SLIDE 9: Key Decisions ----
  let s9 = pres.addSlide();
  s9.background = { color: C.darkBg };
  s9.addShape(pres.shapes.OVAL, { x: 8, y: 3, w: 4, h: 4, fill: { color: C.navy, transparency: 40 } });
  s9.addImage({ data: iconDecisions, x: 0.8, y: 0.45, w: 0.45, h: 0.45 });
  s9.addText("Key Design Decisions", {
    x: 1.4, y: 0.4, w: 7, h: 0.55, fontSize: 32, fontFace: "Calibri",
    color: C.white, bold: true, margin: 0,
  });

  const decisions = [
    { title: "Rule-based + embeddings hybrid", desc: "No training labels — hand-crafted features encode JD knowledge, embeddings capture semantic meaning" },
    { title: "Behavioral modifier as multiplier", desc: "Inactive candidates can’t offset poor availability with good skills alone" },
    { title: "Career text (25%) > Title (15%)", desc: "JD explicitly warns against over-indexing on titles" },
    { title: "Skill trust scoring", desc: "Penalizes “expert” claims with 0 endorsements and 4 months duration" },
    { title: "Synonym groups", desc: "FAISS/Pinecone/Qdrant = \"vector DB experience\" — avoids penalizing equivalent tools" },
  ];
  decisions.forEach((d, i) => {
    const y = 1.3 + i * 0.82;
    s9.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.8, y: y, w: 8.4, h: 0.7, fill: { color: C.navy, transparency: 30 }, rectRadius: 0.08,
    });
    s9.addText([
      { text: d.title, options: { bold: true, color: C.accent, fontSize: 13 } },
      { text: "  —  " + d.desc, options: { color: C.white, fontSize: 12 } },
    ], { x: 1.1, y: y + 0.05, w: 7.8, h: 0.6, fontFace: "Calibri", margin: 0, valign: "middle" });
  });

  await pres.writeFile({ fileName: "/home/azureuser/Ronak/Other/ResumeParsing/approach_deck.pptx" });
  console.log("Presentation created successfully.");
}

main().catch(err => { console.error(err); process.exit(1); });
