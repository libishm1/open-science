// Core logic for the Local Agent Workbench extension. No dependency on the vscode module, so it
// can be tested with plain Node. The extension (extension.js) only wires these pieces to VS Code.
//
// Design rules:
//  - The CLI is started with an argument array and shell:false, so paths with spaces, quotes,
//    parentheses, or non-ASCII characters are passed through unchanged. Nothing is typed into a terminal.
//  - Python output is forced to UTF-8, so Tamil and other non-ASCII text prints correctly on Windows.
//  - Every run has a timeout and can be cancelled. The child process is killed on cancel.

const { spawn, spawnSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const DEFAULT_TIMEOUT_MS = 30 * 60 * 1000; // 30 minutes; a local model loop can be slow

// Turn a loose setting value into a list of candidate interpreters. Windows often has
// "py -3" rather than "python"; the launcher form needs its arguments split out.
function interpreterCandidates(setting) {
  const value = (setting || "python").trim();
  if (!value) return [{ cmd: "python", prefix: [] }];
  const parts = value.split(/\s+/);
  return [{ cmd: parts[0], prefix: parts.slice(1) }];
}

// Check the workbench folder before running anything. Returns { ok, message }.
function validateRepo(repoPath) {
  if (!repoPath || !repoPath.trim()) {
    return { ok: false, message: "Set lawb.repoPath to the workbench folder (the one that contains src/lawb)." };
  }
  if (!fs.existsSync(repoPath)) {
    return { ok: false, message: `lawb.repoPath does not exist: ${repoPath}` };
  }
  if (!fs.statSync(repoPath).isDirectory()) {
    return { ok: false, message: `lawb.repoPath is not a folder: ${repoPath}` };
  }
  const entry = path.join(repoPath, "src", "lawb", "__main__.py");
  if (!fs.existsSync(entry)) {
    return { ok: false, message: `No workbench found at ${repoPath} (missing src/lawb/__main__.py).` };
  }
  return { ok: true, message: "" };
}

// Check that an input path exists and has the expected extension. Returns { ok, message }.
function validateInput(filePath, expectedExt, what) {
  if (!filePath) return { ok: false, message: `No ${what} selected.` };
  if (!fs.existsSync(filePath)) return { ok: false, message: `${what} not found: ${filePath}` };
  if (expectedExt && path.extname(filePath).toLowerCase() !== expectedExt) {
    return { ok: false, message: `${what} must be a ${expectedExt} file: ${path.basename(filePath)}` };
  }
  return { ok: true, message: "" };
}

// Build the argument list for `python -m lawb ...`. Returns { argv, label }.
function buildCommand(name, input) {
  switch (name) {
    case "doctor":
      return { argv: ["doctor"], label: "doctor" };
    case "setup":
      return { argv: ["setup"], label: "setup" };
    case "skillsList":
      return { argv: ["skills", "list"], label: "skills list" };
    case "pdf":
      return withOptionalOut(["pdf", input.file], input.out, "pdf");
    case "diagram":
      return { argv: ["diagram", input.file, "-o", input.outDir], label: "diagram" };
    case "review":
      return withOptionalOut(["review", input.file], input.out, "review");
    case "loop": {
      const argv = ["loop", input.projectDir];
      if (input.model) argv.push("--model", input.model);
      return { argv, label: "loop" };
    }
    default:
      throw new Error(`unknown command: ${name}`);
  }
}

function withOptionalOut(argv, out, label) {
  if (out) argv.push("-o", out);
  return { argv, label };
}

// Output paths next to the input, with a suffix, e.g. "report.pdf" -> "report.md".
function siblingPath(filePath, newExt, suffix = "") {
  const dir = path.dirname(filePath);
  const base = path.basename(filePath, path.extname(filePath));
  return path.join(dir, base + suffix + newExt);
}

// Environment for the child process. Keeps the caller's environment and adds the workbench source
// folder to PYTHONPATH, with UTF-8 I/O so non-ASCII text survives on Windows.
function childEnv(repoPath, base = process.env) {
  const srcDir = path.join(repoPath, "src");
  const existing = base.PYTHONPATH ? base.PYTHONPATH.split(path.delimiter) : [];
  const pythonPath = [srcDir, ...existing.filter((p) => p && p !== srcDir)].join(path.delimiter);
  return {
    ...base,
    PYTHONPATH: pythonPath,
    PYTHONIOENCODING: "utf-8",
    PYTHONUTF8: "1",
    PYTHONUNBUFFERED: "1",
  };
}

// Run the CLI. Resolves with { code, stdout, stderr, timedOut, cancelled, error }.
// Never rejects: callers always get a result they can show to the user.
function runCli({ python, repoPath, cwd, argv, timeoutMs = DEFAULT_TIMEOUT_MS, signal, onOutput }) {
  const [candidate] = interpreterCandidates(python);
  const args = [...candidate.prefix, "-m", "lawb", ...argv];
  return new Promise((resolve) => {
    let stdout = "";
    let stderr = "";
    let timedOut = false;
    let cancelled = false;
    let child;
    try {
      child = spawn(candidate.cmd, args, {
        cwd: cwd || repoPath,
        env: childEnv(repoPath),
        shell: false,
        windowsHide: true,
      });
    } catch (err) {
      return resolve({ code: null, stdout, stderr, timedOut, cancelled, error: spawnMessage(err, candidate.cmd) });
    }
    const timer = setTimeout(() => {
      timedOut = true;
      child.kill();
    }, timeoutMs);
    const onAbort = () => {
      cancelled = true;
      child.kill();
    };
    if (signal) {
      if (signal.aborted) onAbort();
      else signal.addEventListener("abort", onAbort, { once: true });
    }
    child.stdout.setEncoding("utf8");
    child.stderr.setEncoding("utf8");
    child.stdout.on("data", (d) => {
      stdout += d;
      if (onOutput) onOutput(d);
    });
    child.stderr.on("data", (d) => {
      stderr += d;
      if (onOutput) onOutput(d);
    });
    child.on("error", (err) => {
      clearTimeout(timer);
      resolve({ code: null, stdout, stderr, timedOut, cancelled, error: spawnMessage(err, candidate.cmd) });
    });
    child.on("close", (code) => {
      clearTimeout(timer);
      resolve({ code, stdout, stderr, timedOut, cancelled, error: null });
    });
  });
}

function spawnMessage(err, cmd) {
  if (err && err.code === "ENOENT") {
    return `Python was not found ("${cmd}"). Set lawb.pythonPath to your Python 3.10+ interpreter.`;
  }
  return `Could not start Python: ${err && err.message ? err.message : err}`;
}

// Turn a finished run into a short user message and a severity.
function summarise(label, result) {
  if (result.cancelled) return { level: "warning", text: `${label} was cancelled.` };
  if (result.timedOut) return { level: "error", text: `${label} stopped after the time limit.` };
  if (result.error) return { level: "error", text: result.error };
  if (result.code === 0) return { level: "info", text: `${label} finished.` };
  const tail = (result.stderr || result.stdout || "").trim().split(/\r?\n/).slice(-3).join(" | ");
  return { level: "error", text: `${label} failed (exit ${result.code}). ${tail}`.trim() };
}

module.exports = {
  DEFAULT_TIMEOUT_MS,
  interpreterCandidates,
  validateRepo,
  validateInput,
  buildCommand,
  siblingPath,
  childEnv,
  runCli,
  summarise,
};
