// VS Code wiring for the Local Agent Workbench. The logic lives in lib/cli.js (tested without VS Code).
const vscode = require("vscode");
const path = require("path");
const cli = require("./lib/cli");

let output;

function channel() {
  if (!output) output = vscode.window.createOutputChannel("Local Agent Workbench");
  return output;
}

function settings() {
  const cfg = vscode.workspace.getConfiguration("lawb");
  return {
    repoPath: (cfg.get("repoPath") || "").trim(),
    python: cfg.get("pythonPath") || "python",
    model: cfg.get("model") || "",
  };
}

function workspaceCwd(repoPath) {
  const folders = vscode.workspace.workspaceFolders;
  return folders && folders.length ? folders[0].uri.fsPath : repoPath;
}

function notify(level, text) {
  if (level === "error") return vscode.window.showErrorMessage(text);
  if (level === "warning") return vscode.window.showWarningMessage(text);
  return vscode.window.showInformationMessage(text);
}

// Run one CLI command with a progress indicator, cancel support, and a result message.
async function runCommand(name, input, label, { needsModel = false } = {}) {
  const s = settings();
  const repo = cli.validateRepo(s.repoPath);
  if (!repo.ok) {
    const choice = await vscode.window.showErrorMessage(repo.message, "Open Settings");
    if (choice === "Open Settings") vscode.commands.executeCommand("workbench.action.openSettings", "lawb.repoPath");
    return;
  }
  if (needsModel && !s.model) {
    vscode.window.showErrorMessage("Set lawb.model (for example qwen2.5-coder:7b) before running the loop.");
    return;
  }
  const { argv } = cli.buildCommand(name, { ...input, model: s.model });
  const out = channel();
  out.show(true);
  out.appendLine(`\n> lawb ${argv.join(" ")}`);

  await vscode.window.withProgress(
    { location: vscode.ProgressLocation.Notification, title: `LAWB: ${label}`, cancellable: true },
    async (progress, token) => {
      const controller = new AbortController();
      token.onCancellationRequested(() => controller.abort());
      const result = await cli.runCli({
        python: s.python,
        repoPath: s.repoPath,
        cwd: workspaceCwd(s.repoPath),
        argv,
        signal: controller.signal,
        onOutput: (chunk) => out.append(chunk),
      });
      const summary = cli.summarise(label, result);
      out.appendLine(`\n${summary.text}`);
      notify(summary.level, summary.text);
    }
  );
}

function activeFile(ext, what) {
  const editor = vscode.window.activeTextEditor;
  const file = editor ? editor.document.uri.fsPath : "";
  const check = cli.validateInput(file, ext, what);
  if (!check.ok) {
    vscode.window.showErrorMessage(check.message);
    return null;
  }
  return file;
}

// Ask for a folder when the loop is started from the palette without an open file.
async function pickProjectFolder() {
  const editor = vscode.window.activeTextEditor;
  if (editor) return path.dirname(editor.document.uri.fsPath);
  const picked = await vscode.window.showOpenDialog({
    canSelectFolders: true,
    canSelectFiles: false,
    canSelectMany: false,
    openLabel: "Use this project folder",
  });
  return picked && picked.length ? picked[0].fsPath : null;
}

function activate(context) {
  const reg = (id, fn) => context.subscriptions.push(vscode.commands.registerCommand(id, fn));

  reg("lawb.doctor", () => runCommand("doctor", {}, "doctor"));
  reg("lawb.setup", () => runCommand("setup", {}, "setup"));
  reg("lawb.skillsList", () => runCommand("skillsList", {}, "skills list"));

  reg("lawb.pdfExtract", () => {
    const file = activeFile(".pdf", "PDF");
    if (file) runCommand("pdf", { file, out: cli.siblingPath(file, ".md") }, "PDF text");
  });

  reg("lawb.diagramBuild", () => {
    const file = activeFile(".json", "diagram spec (JSON)");
    if (file) runCommand("diagram", { file, outDir: path.join(path.dirname(file), "diagrams") }, "diagram");
  });

  reg("lawb.prismaCounts", () => {
    const file = activeFile(".csv", "screening CSV");
    if (file) runCommand("review", { file, out: cli.siblingPath(file, ".md", "_counts") }, "PRISMA counts");
  });

  reg("lawb.loopRun", async () => {
    const projectDir = await pickProjectFolder();
    if (!projectDir) return;
    const hasPipeline = require("fs").existsSync(path.join(projectDir, "pipeline.json"));
    if (!hasPipeline) {
      vscode.window.showErrorMessage(`No pipeline.json in ${projectDir}. The loop needs one.`);
      return;
    }
    runCommand("loop", { projectDir }, "error loop", { needsModel: true });
  });
}

function deactivate() {
  if (output) output.dispose();
}

module.exports = { activate, deactivate };
