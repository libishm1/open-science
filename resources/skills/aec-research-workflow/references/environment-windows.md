# Environment: a locked-down Windows research workstation

For a university-managed Windows 11 PC with no administrator rights, endpoint antivirus, and Documents and Desktop redirected into OneDrive. **Probe the environment before trusting old notes**; tool availability drifts.

## Python

- The default `python` may be a newer version than some wheels support (Open3D needed Python 3.11). Use the launcher: `py -3.11 -m venv .venv`.
- Use a per-project `.venv`, created outside OneDrive.
- `python -I` (isolated) breaks imports of packages in user site-packages (for example lxml). Use `-P` for your own scripts; keep `-I` for code that touches downloaded files.
- Set `PYTHONIOENCODING=utf-8`; the console code page may be cp1252.
- Non-ASCII paths (accented or Arabic folder names) can break when passed through PowerShell argv. Resolve them with `glob` inside Python.
- conda: use Miniforge, not Miniconda (its terms prompt blocks non-interactive `conda create`). `conda init powershell` can stall when `$PROFILE` lives in OneDrive.

## Shell

- Write patch scripts with a file-writing tool, **never as shell heredocs**: backslash escapes and backticks get mangled (`\b`, `\1`, `\\ref` turning into control bytes). Scan generated `.tex` for stray `\r`.
- `cmd | tail` hides the exit code. Redirect to a file and check the status.
- Git Bash `curl` can hang; use PowerShell `Invoke-WebRequest`. Use `tar.exe` for large archives rather than `Expand-Archive`.
- PowerShell: `& "path\npm.cmd" run dev -- --host … --port …`; set `$env:PATH`, not `set "PATH=…"`; a process-scoped execution-policy bypass needs no admin.
- Port already in use (WinError 10048): stop the old server or choose another port.

## Node

- Install Node portably under `%LOCALAPPDATA%` and call `node.exe` or `npm.cmd` by full path when PATH is unreliable.
- Endpoint antivirus may silently delete unsigned native binaries in `node_modules` (esbuild, rollup, sharp). Use npm `overrides` to `esbuild-wasm` and `@rollup/wasm-node` and remove the locked entries.
- Write launch commands into the README; they are easy to forget.

## OneDrive

- Never put secrets, `.env`, `node_modules`, Lean or Mathlib caches, or build staging inside OneDrive.
- OneDrive locks folders mid-delete (`shutil.rmtree` → WinError 5). Stage builds and packages outside it.
- Moving a file over a synced shared document breaks its share link. Write in place.

## Documents

- Check for pandoc, LibreOffice and poppler before assuming them. MiKTeX ships `pdftoppm`.
- PDF → Markdown: `pymupdf4llm`; page renders for visual checks: PyMuPDF. Edit docx with python-docx.
- Word and Excel through COM from PowerShell: `SaveAs2` format 16 (docx) or 17 (pdf); Excel `CalculateFull` to recalculate formulas. Kill windowless WINWORD after each render, force-embed images (`BreakLink`), and test COM on a trivial document first because it can hang.
- pandoc moves `\begin{abstract}` into the title block, so affiliations can land after the abstract; post-process the docx.

## LaTeX and Lean

- MiKTeX may be installed off PATH: call it by full path with `pdflatex -interaction=nonstopmode --enable-installer`, then bibtex, then pdflatex twice. tectonic is a portable alternative.
- Lean 4 + Mathlib: keep the Lake project outside OneDrive and compile with `lake env lean <file>`.

## Java and large tools

Use a portable JRE (for example Temurin) for Java tools such as the Future Weather Generator.

## Secrets

- Never ask for keys or tokens to be pasted into chat. Keys go into the app's own settings or an owner-only `.env` outside OneDrive.
- Never create, print, commit or store API keys, tokens, SSH keys or passwords in files, code or git history.
- If a secret has been pasted into a chat or a log, tell the researcher to revoke and rotate it.

## Connectors

Email connectors may be unauthorised. Draft emails for the researcher to send.
