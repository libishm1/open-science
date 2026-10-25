// Unit tests for lib/cli.js. They use a fake workbench folder, so no Python or workbench is needed.
const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("fs");
const os = require("os");
const path = require("path");
const cli = require("../lib/cli");

function tempDir() {
  return fs.mkdtempSync(path.join(os.tmpdir(), "lawb-plugin-"));
}

function fakeRepo(body = "print('ok')") {
  const root = tempDir();
  fs.mkdirSync(path.join(root, "src", "lawb"), { recursive: true });
  fs.writeFileSync(path.join(root, "src", "lawb", "__main__.py"), body, "utf8");
  return root;
}

test("validateRepo rejects an empty, missing, or wrong folder", () => {
  assert.equal(cli.validateRepo("").ok, false);
  assert.equal(cli.validateRepo("   ").ok, false);
  assert.match(cli.validateRepo(path.join(tempDir(), "nope")).message, /does not exist/);
  const plain = tempDir();
  assert.match(cli.validateRepo(plain).message, /missing src\/lawb\/__main__\.py/);
  assert.equal(cli.validateRepo(fakeRepo()).ok, true);
});

test("validateRepo rejects a file where a folder is expected", () => {
  const file = path.join(tempDir(), "f.txt");
  fs.writeFileSync(file, "x");
  assert.match(cli.validateRepo(file).message, /not a folder/);
});

test("validateInput checks presence and extension", () => {
  const dir = tempDir();
  const pdf = path.join(dir, "Report (final) v2.PDF");
  fs.writeFileSync(pdf, "x");
  assert.equal(cli.validateInput(pdf, ".pdf", "PDF").ok, true, "extension match is case-insensitive");
  assert.match(cli.validateInput(pdf, ".csv", "CSV").message, /must be a \.csv/);
  assert.match(cli.validateInput(path.join(dir, "missing.pdf"), ".pdf", "PDF").message, /not found/);
  assert.match(cli.validateInput("", ".pdf", "PDF").message, /No PDF selected/);
});

test("buildCommand produces argument arrays, not shell strings", () => {
  const file = "C:\\Docs\\Grant (draft) & notes.pdf";
  const { argv } = cli.buildCommand("pdf", { file, out: "C:\\Docs\\out.md" });
  assert.deepEqual(argv, ["pdf", file, "-o", "C:\\Docs\\out.md"]);
  const loop = cli.buildCommand("loop", { projectDir: "p", model: "qwen2.5-coder:7b" });
  assert.deepEqual(loop.argv, ["loop", "p", "--model", "qwen2.5-coder:7b"]);
  assert.deepEqual(cli.buildCommand("doctor", {}).argv, ["doctor"]);
  assert.throws(() => cli.buildCommand("nope", {}), /unknown command/);
});

test("siblingPath keeps the folder and changes the extension", () => {
  assert.equal(cli.siblingPath(path.join("a", "b c", "paper.pdf"), ".md"), path.join("a", "b c", "paper.md"));
  assert.equal(cli.siblingPath(path.join("a", "x.csv"), ".md", "_counts"), path.join("a", "x_counts.md"));
});

test("childEnv forces UTF-8 and prepends the workbench source folder", () => {
  const env = cli.childEnv("/repo", { PYTHONPATH: "/other" });
  assert.equal(env.PYTHONIOENCODING, "utf-8");
  assert.equal(env.PYTHONUTF8, "1");
  assert.ok(env.PYTHONPATH.startsWith(path.join("/repo", "src")));
  assert.ok(env.PYTHONPATH.includes("/other"));
  const again = cli.childEnv("/repo", { PYTHONPATH: path.join("/repo", "src") });
  assert.equal(again.PYTHONPATH.split(path.delimiter).filter((p) => p === path.join("/repo", "src")).length, 1);
});

test("interpreterCandidates splits launcher forms such as 'py -3'", () => {
  assert.deepEqual(cli.interpreterCandidates("py -3"), [{ cmd: "py", prefix: ["-3"] }]);
  assert.deepEqual(cli.interpreterCandidates(""), [{ cmd: "python", prefix: [] }]);
});

test("a missing interpreter gives a message that names the setting", async () => {
  const result = await cli.runCli({
    python: "definitely-not-a-python-binary-xyz",
    repoPath: fakeRepo(),
    argv: ["doctor"],
  });
  assert.match(result.error, /Python was not found/);
  assert.match(result.error, /lawb\.pythonPath/);
});

test("summarise gives the right level for each outcome", () => {
  assert.equal(cli.summarise("x", { code: 0 }).level, "info");
  assert.equal(cli.summarise("x", { code: 2, stderr: "boom\nlast line" }).level, "error");
  assert.match(cli.summarise("x", { code: 2, stderr: "a\nb\nlast" }).text, /last/);
  assert.equal(cli.summarise("x", { cancelled: true }).level, "warning");
  assert.match(cli.summarise("x", { timedOut: true }).text, /time limit/);
});
