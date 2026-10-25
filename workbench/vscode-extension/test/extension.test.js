// Wiring tests for extension.js. The vscode module is replaced with a small fake, so these run in plain Node.
// They check that every command is registered, that bad input is refused before anything runs, and that
// valid input reaches the CLI with the right arguments.
const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("fs");
const os = require("os");
const path = require("path");

// No default location: this repository is public, so the path comes only from the environment.
const REPO = process.env.LAWB_REPO || "";

function makeVscode({ settings = {}, activeFile = null, messages = [] } = {}) {
  const commands = {};
  const lines = [];
  const vscode = {
    ProgressLocation: { Notification: 15 },
    commands: {
      registerCommand: (id, fn) => { commands[id] = fn; return { dispose() {} }; },
      executeCommand: async () => {},
    },
    workspace: {
      workspaceFolders: undefined,
      getConfiguration: () => ({ get: (k) => settings[k] }),
    },
    window: {
      activeTextEditor: activeFile ? { document: { uri: { fsPath: activeFile } } } : undefined,
      createOutputChannel: () => ({ appendLine: (l) => lines.push(l), append: (l) => lines.push(l), show() {}, dispose() {} }),
      withProgress: async (opts, task) => task({ report() {} }, { onCancellationRequested() {} }),
      showErrorMessage: async (m) => { messages.push(["error", m]); return undefined; },
      showWarningMessage: async (m) => { messages.push(["warning", m]); },
      showInformationMessage: async (m) => { messages.push(["info", m]); },
      showOpenDialog: async () => undefined,
    },
    ConfigurationTarget: {},
  };
  return { vscode, commands, lines, messages };
}

function loadExtension(fake) {
  const modPath = require.resolve("../extension.js");
  delete require.cache[modPath];
  const Module = require("module");
  const originalLoad = Module._load;
  Module._load = function (request, parent, isMain) {
    if (request === "vscode") return fake.vscode;
    return originalLoad.apply(this, arguments);
  };
  try {
    return require("../extension.js");
  } finally {
    Module._load = originalLoad;
  }
}

test("all seven commands are registered", () => {
  const fake = makeVscode();
  const ext = loadExtension(fake);
  const ctx = { subscriptions: [] };
  ext.activate(ctx);
  for (const id of ["lawb.doctor", "lawb.setup", "lawb.skillsList", "lawb.pdfExtract",
                    "lawb.diagramBuild", "lawb.prismaCounts", "lawb.loopRun"]) {
    assert.equal(typeof fake.commands[id], "function", `${id} must be registered`);
  }
});

test("a missing repoPath shows an error and runs nothing", async () => {
  const fake = makeVscode({ settings: { repoPath: "" } });
  const ext = loadExtension(fake);
  ext.activate({ subscriptions: [] });
  await fake.commands["lawb.doctor"]();
  assert.ok(fake.messages.some(([lvl, m]) => lvl === "error" && /lawb\.repoPath/.test(m)));
  assert.equal(fake.lines.length, 0, "no command line is written when the workbench is not set");
});

test("PDF command refuses a non-PDF active file", async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "lawb-ext-"));
  const txt = path.join(dir, "notes.txt");
  fs.writeFileSync(txt, "x");
  const fake = makeVscode({ settings: { repoPath: REPO }, activeFile: txt });
  const ext = loadExtension(fake);
  ext.activate({ subscriptions: [] });
  await fake.commands["lawb.pdfExtract"]();
  assert.ok(fake.messages.some(([lvl, m]) => lvl === "error" && /must be a \.pdf/.test(m)));
});

test("loop command refuses a folder without pipeline.json", async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "lawb-ext-loop-"));
  const file = path.join(dir, "units.py");
  fs.writeFileSync(file, "x");
  const fake = makeVscode({ settings: { repoPath: REPO, model: "qwen2.5-coder:7b" }, activeFile: file });
  const ext = loadExtension(fake);
  ext.activate({ subscriptions: [] });
  await fake.commands["lawb.loopRun"]();
  assert.ok(fake.messages.some(([lvl, m]) => lvl === "error" && /pipeline\.json/.test(m)));
});

test("doctor runs the real CLI and writes its output to the channel", { skip: !REPO || !fs.existsSync(path.join(REPO, "src", "lawb", "__main__.py")) }, async () => {
  const fake = makeVscode({ settings: { repoPath: REPO, pythonPath: "python" } });
  const ext = loadExtension(fake);
  ext.activate({ subscriptions: [] });
  await fake.commands["lawb.doctor"]();
  const text = fake.lines.join("\n");
  assert.match(text, /> lawb doctor/);
  assert.match(text, /python 3\.10\+/, "the doctor report is shown in the output channel");
});
