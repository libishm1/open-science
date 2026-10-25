# Local Agent Workbench (VS Code)

A thin wrapper that runs the workbench commands in a terminal. It needs the workbench folder, set in `lawb.repoPath`.

Install for local development: open this folder in VS Code and press F5 (Run Extension). Commands are in the Command Palette under "LAWB".

The extension has no logic of its own: each command runs `python -m lawb ...` with `PYTHONPATH` set to the workbench `src` folder.

## Commands

| Command | What it does |
|---|---|
| LAWB: Doctor | checks Python, the skills, PDF support, the local model server, and cloud status |
| LAWB: Setup | sets up the bundled skills (no network) |
| LAWB: List skills | lists every skill and where it comes from |
| LAWB: Extract text from the active PDF | writes a markdown file next to the PDF, with page markers |
| LAWB: Build diagram from the active JSON spec | writes Mermaid text, and an SVG when rendering is available |
| LAWB: PRISMA counts from the active CSV | writes counts next to the CSV, derived from its rows |
| LAWB: Run error loop on the active project folder | runs the routed fix loop on a project with a pipeline.json |

Settings: `lawb.repoPath` (the workbench folder, required), `lawb.pythonPath` (for example `py -3`),
and `lawb.model` (the model for the loop).

## How it is built

- The commands run the workbench CLI with an argument array and no shell. Paths with spaces,
  brackets, ampersands, or non-ASCII characters are passed through unchanged.
- Output is forced to UTF-8, so Tamil and other non-ASCII text prints correctly on Windows.
- Each run has a time limit and can be cancelled from the progress notification. Cancelling
  stops the child process.
- Bad input is refused before anything runs: a missing repository, a wrong file type, a folder
  without `pipeline.json`, or a Python that cannot be found each give a message that names the fix.

## Tests

```bash
LAWB_REPO=/path/to/local-agent-workbench LAWB_REAL_PDF=/path/to/a/paper.pdf npm test
```

- `test/cli.test.js`: unit tests for the argument building, validation, and environment (no Python needed).
- `test/extension.test.js`: wiring tests with a fake `vscode` module. They check that the commands
  are registered and that bad input is refused before any run.
- `test/challenge.test.js`: challenge tests against the real workbench: a 150-page PDF with Tamil text
  in a folder with awkward characters, a 40-node diagram with quotes and pipes, a messy 500-row
  screening CSV with case and spacing errors, a run that hangs (time limit), a cancelled run, UTF-8
  output on the pipe, a missing input, a loop with no pipeline file, and optionally a real PDF.

Without `LAWB_REPO`, the integration tests are skipped and the unit tests still run. Nothing in the
tests points at a personal folder.

What is not tested here: the extension has not been run inside the VS Code window. Its wiring is tested
with a fake `vscode` module. The error loop is not run from the extension, because it needs a local model server.

## Installing in Antigravity and other VS Code forks

Antigravity is a VS Code fork and, per public third-party reports, installs extensions from the
Open VSX registry rather than the Microsoft Marketplace. Publish this extension to Open VSX
(`npx ovsx publish`) with your own publisher name, or install the packaged `.vsix` file with the
Extensions view's "Install from VSIX" command. Google's official Antigravity documentation was not
checked for this, so verify the install path there first.

## Packaging

```bash
npx @vscode/vsce package     # creates local-agent-workbench-0.1.0.vsix
```
