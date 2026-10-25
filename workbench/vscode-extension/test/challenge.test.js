// Challenge tests: hard inputs of the kind used in past Claude and Codex sessions (long standards PDFs,
// Tamil text, awkward folder names, large diagrams, messy screening data, cancelled and slow runs).
//
// Runs against the real workbench. Set LAWB_REPO to its folder, or leave it unset to use the default
// location. Tests are skipped, not failed, when the workbench or Python is unavailable.
const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("fs");
const os = require("os");
const path = require("path");
const { spawnSync } = require("child_process");
const cli = require("../lib/cli");

// No default location: this repository is public, so the path comes only from the environment.
const REPO = process.env.LAWB_REPO || "";
const PYTHON = process.env.LAWB_PYTHON || "python";
const HAVE_WORKBENCH = cli.validateRepo(REPO).ok;
const HAVE_PYTHON = spawnSync(PYTHON, ["-c", "print(1)"], { encoding: "utf8" }).status === 0;
const HAVE_FITZ = HAVE_PYTHON && spawnSync(PYTHON, ["-c", "import fitz"], { encoding: "utf8" }).status === 0;
const SKIP = !HAVE_WORKBENCH || !HAVE_PYTHON;

// A folder with awkward characters: spaces, brackets, ampersand, and Tamil script.
function awkwardDir(name) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "lawb chall "));
  const dir = path.join(root, `Site (north) & ${name} பரிசோதனை`);
  fs.mkdirSync(dir, { recursive: true });
  return dir;
}

function runPython(code) {
  return spawnSync(PYTHON, ["-c", code], { encoding: "utf8", env: { ...process.env, PYTHONUTF8: "1" } });
}

test("C1: 150-page PDF with Tamil text in an awkward folder: text, page markers, and Unicode survive", { skip: SKIP || !HAVE_FITZ }, async () => {
  const dir = awkwardDir("pdf");
  const pdf = path.join(dir, "Standard (2023) draft & notes.pdf");
  const script = path.join(dir, "make_pdf.py");
  const fontPath = "C:/Windows/Fonts/Nirmala.ttf";
  const tamilLine = "இந்த ஆவணம் கல் வெட்டுதலுக்கான தரநிலையை விவரிக்கிறது";
  fs.writeFileSync(script, [
    "import fitz, os, sys",
    `pdf_path, font_path, line = sys.argv[1], sys.argv[2], sys.argv[3]`,
    "font = fitz.Font(fontfile=font_path) if os.path.exists(font_path) else None",
    "doc = fitz.open()",
    "for i in range(150):",
    "    page = doc.new_page()",
    "    if font:",
    "        page.insert_font(fontname='tam', fontbuffer=font.buffer)",
    "        page.insert_text((72, 72), 'Clause %d ' % (i + 1) + line, fontname='tam', fontsize=10)",
    "    else:",
    "        page.insert_text((72, 72), 'Clause %d standard text' % (i + 1), fontsize=10)",
    "    page.insert_text((72, 800), 'Page footer %d' % (i + 1), fontsize=8)",
    "doc.save(pdf_path)",
    "print('ok')",
  ].join("\n"), "utf8");
  const made = spawnSync(PYTHON, [script, pdf, fontPath, tamilLine], { encoding: "utf8", env: { ...process.env, PYTHONUTF8: "1" } });
  assert.equal(made.status, 0, made.stderr);
  const out = path.join(dir, "Standard (2023) draft & notes.md");
  const t0 = Date.now();
  const result = await cli.runCli({
    python: PYTHON,
    repoPath: REPO,
    cwd: dir,
    argv: cli.buildCommand("pdf", { file: pdf, out }).argv,
  });
  assert.equal(result.code, 0, result.stderr || result.error);
  const md = fs.readFileSync(out, "utf8");
  assert.equal((md.match(/<!-- page /g) || []).length, 150, "one marker per page");
  assert.match(md, /Clause 150/);
  if (fs.existsSync(fontPath)) assert.ok(md.includes("தரநிலை"), "Tamil characters must survive extraction");
  assert.ok(Date.now() - t0 < 120000, "150 pages should extract in under two minutes");
});

test("C2: 40-node diagram with quotes, brackets, pipes, and Tamil labels builds valid Mermaid", { skip: SKIP }, async () => {
  const dir = awkwardDir("diagram");
  const nodes = {};
  const edges = [];
  for (let i = 0; i < 40; i++) {
    nodes[`n${i}`] = `Step ${i}: "check" [site | ${i % 3}] தேர்வு`;
    if (i > 0) edges.push([`n${i - 1}`, `n${i}`, i % 4 === 0 ? "decision | yes/no" : ""]);
  }
  const spec = path.join(dir, "flow spec.json");
  fs.writeFileSync(spec, JSON.stringify({ title: "Long flow", direction: "LR", nodes, edges }), "utf8");
  const result = await cli.runCli({
    python: PYTHON,
    repoPath: REPO,
    cwd: dir,
    argv: cli.buildCommand("diagram", { file: spec, outDir: path.join(dir, "out dir") }).argv,
  });
  assert.equal(result.code, 0, result.stderr || result.error);
  const mmd = fs.readFileSync(path.join(dir, "out dir", "flow spec.mmd"), "utf8");
  assert.match(mmd, /^flowchart LR/);
  assert.equal((mmd.match(/-->/g) || []).length, 39, "every edge is written once");
  assert.ok(mmd.includes("தேர்வு"), "Tamil labels are written in UTF-8");
  // Quotes inside labels must not break the Mermaid syntax (they are replaced, not escaped).
  assert.ok(!/\["[^"\]]*"[^\]]*"/.test(mmd), "no raw double quote inside a node label");
});

test("C3: messy screening CSV (500 rows, mixed case, stray spaces, blank reasons) counts correctly", { skip: SKIP }, async () => {
  const dir = awkwardDir("prisma");
  const rows = ["record_id,strand,year,type,duplicate,stage,decision,reason"];
  // Build a known answer: 500 records at title/abstract, every 5th excluded (off-topic),
  // and every 10th of the rest is also a duplicate row that must be ignored.
  let expIncluded = 0, expExcluded = 0, expDup = 0, expIdentified = 0;
  for (let i = 1; i <= 500; i++) {
    const excluded = i % 5 === 0;
    const decision = excluded ? "  EXCLUDE " : " Include";
    const reason = excluded ? "" : "";
    rows.push(`R${i}, strand_a ,${2000 + (i % 20)}, Journal ,no,Title_Abstract,${decision},${reason}`);
    expIdentified++;
    if (excluded) expExcluded++; else expIncluded++;
    if (i % 10 === 0) {
      rows.push(`R${i},strand_b,${2000 + (i % 20)},Journal,YES,title_abstract,include,`);
      expIdentified++;
      expDup++;
    }
  }
  // Full-text stage for the first 20 included records; decide 5 of them.
  let fullIncluded = 0;
  for (let i = 1; i <= 20; i++) {
    if (i % 5 === 0) continue;
    const decision = i % 4 === 0 ? "exclude" : "INCLUDE";
    if (decision.toLowerCase() === "include") fullIncluded++;
    rows.push(`R${i},strand_c,2001,book,no,full_text,${decision},no data`);
    expIdentified++;
  }
  const csv = path.join(dir, "screen data.csv");
  fs.writeFileSync(csv, rows.join("\n") + "\n", "utf8");
  const out = path.join(dir, "counts out.md");
  const result = await cli.runCli({
    python: PYTHON,
    repoPath: REPO,
    cwd: dir,
    argv: cli.buildCommand("review", { file: csv, out }).argv,
  });
  assert.equal(result.code, 0, result.stderr || result.error);
  const md = fs.readFileSync(out, "utf8");
  assert.match(md, new RegExp(`Identified: ${expIdentified}\\.`), "every row is counted as identified");
  assert.match(md, new RegExp(`Duplicates removed: ${expDup}\\.`), "case-insensitive duplicate flags are removed");
  assert.match(md, new RegExp(`\\(unique\\): ${expIncluded + expExcluded}\\.`), "unique title/abstract records");
  assert.match(md, new RegExp(`Full text assessed: ${20 - 4}\\.`) , "full text rows are kept, not dropped");
  assert.match(md, new RegExp(`Included: ${fullIncluded}\\.`), "included count is case-insensitive");
});

test("C4: a Python run that never finishes is killed after the time limit", { skip: SKIP }, async () => {
  const repo = fs.mkdtempSync(path.join(os.tmpdir(), "lawb-slow-"));
  fs.mkdirSync(path.join(repo, "src", "lawb"), { recursive: true });
  fs.writeFileSync(path.join(repo, "src", "lawb", "__main__.py"), "import time\ntime.sleep(60)\n", "utf8");
  const t0 = Date.now();
  const result = await cli.runCli({ python: PYTHON, repoPath: repo, argv: ["doctor"], timeoutMs: 800 });
  assert.equal(result.timedOut, true);
  assert.ok(Date.now() - t0 < 15000, "must not wait for the full sleep");
  assert.match(cli.summarise("doctor", result).text, /time limit/);
});

test("C5: cancellation from the UI kills the process and reports it as cancelled", { skip: SKIP }, async () => {
  const repo = fs.mkdtempSync(path.join(os.tmpdir(), "lawb-cancel-"));
  fs.mkdirSync(path.join(repo, "src", "lawb"), { recursive: true });
  fs.writeFileSync(path.join(repo, "src", "lawb", "__main__.py"), "import time\ntime.sleep(60)\n", "utf8");
  const controller = new AbortController();
  const pending = cli.runCli({ python: PYTHON, repoPath: repo, argv: ["doctor"], signal: controller.signal });
  setTimeout(() => controller.abort(), 700);
  const result = await pending;
  assert.equal(result.cancelled, true);
  assert.equal(cli.summarise("doctor", result).level, "warning");
});

test("C6: non-ASCII output from the CLI arrives intact on the pipe (Windows encoding check)", { skip: SKIP }, async () => {
  const repo = fs.mkdtempSync(path.join(os.tmpdir(), "lawb-utf8-"));
  fs.mkdirSync(path.join(repo, "src", "lawb"), { recursive: true });
  fs.writeFileSync(path.join(repo, "src", "lawb", "__main__.py"),
    "import sys\nprint('தமிழ் ✓ café')\nsys.stdout.flush()\n", "utf8");
  const result = await cli.runCli({ python: PYTHON, repoPath: repo, argv: ["doctor"] });
  assert.equal(result.code, 0, result.stderr || result.error);
  assert.ok(result.stdout.includes("தமிழ் ✓ café"), `got ${JSON.stringify(result.stdout)}`);
});

test("C7: a workbench command with a bad input reports the error instead of crashing", { skip: SKIP }, async () => {
  const dir = awkwardDir("bad");
  const missing = path.join(dir, "does not exist.pdf");
  const result = await cli.runCli({
    python: PYTHON, repoPath: REPO, cwd: dir,
    argv: cli.buildCommand("pdf", { file: missing }).argv,
  });
  assert.notEqual(result.code, 0);
  assert.equal(cli.summarise("PDF text", result).level, "error");
});

test("C8: the error loop refuses a project folder without pipeline.json", { skip: SKIP }, async () => {
  const dir = awkwardDir("loop");
  const result = await cli.runCli({
    python: PYTHON, repoPath: REPO, cwd: dir,
    argv: cli.buildCommand("loop", { projectDir: dir, model: "qwen2.5-coder:7b" }).argv,
  });
  assert.notEqual(result.code, 0, "the workbench must not run a loop without its pipeline file");
});

test("C9: a real local PDF (set LAWB_REAL_PDF) extracts substantial text with page markers", { skip: SKIP || !process.env.LAWB_REAL_PDF || !fs.existsSync(process.env.LAWB_REAL_PDF || "") }, async () => {
  const pdf = process.env.LAWB_REAL_PDF;
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "lawb real "));
  const out = path.join(dir, "real.md");
  const result = await cli.runCli({ python: PYTHON, repoPath: REPO, cwd: dir, argv: cli.buildCommand("pdf", { file: pdf, out }).argv });
  assert.equal(result.code, 0, result.stderr || result.error);
  const md = fs.readFileSync(out, "utf8");
  assert.ok(md.length > 2000, "a real paper should produce substantial text");
  assert.match(md, /<!-- page 1 -->/);
});
