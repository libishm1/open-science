---
name: latex-document
description: Procedure for writing and compiling LaTeX documents (papers, reports, letters, slides, posters) to PDF with a reproducible build, including a minimal paper template, bibliography with BibTeX or biblatex, figures and tables, and a troubleshooting table for common compile errors. Uses Tectonic (one executable, no admin install) or latexmk where a TeX distribution exists. Use when a user asks for a LaTeX document, a compiled PDF from LaTeX, or help fixing a LaTeX error.
compatibility: Claude, Codex, local models, Herdr and Omarchy. Tectonic and latexmk run on Windows, macOS and Linux.
license: see repository LICENSE
---

# LaTeX documents

## Quick start (for small local models)

1. Copy the template from `references/templates.md` into `main.tex`.
2. Fill the title, authors and sections. Keep one sentence per line, so diffs stay readable.
3. Compile with `tectonic main.tex` (or `latexmk -pdf main.tex`).
4. If it fails, read the first error line in the log and look it up in `references/troubleshooting.md`.
5. Open the PDF and check figures, references and page count.

## Build tools

| Tool | When to use | Command |
|---|---|---|
| Tectonic | No TeX installed, or no admin rights. Downloads packages on first use and caches them | `tectonic main.tex` |
| latexmk | A full TeX distribution exists (TeX Live, MiKTeX) | `latexmk -pdf main.tex` (or `-xelatex` for system fonts and non-Latin scripts) |

For non-Latin scripts such as Tamil, compile with XeLaTeX or LuaLaTeX and load a font that has the
script, for example `\usepackage{fontspec}` with `\setmainfont{Noto Serif Tamil}`.

## Rules

- Keep the build reproducible: one command, no manual steps. Commit the source and the bibliography,
  not the PDF, unless a PDF is the deliverable.
- Put figures in `figures/` and reference them with relative paths.
- Use `\label` and `\ref` for every figure, table and equation. Never type numbers by hand.
- Use `booktabs` rules for tables. Avoid vertical lines.
- Use `siunitx` for numbers with units.
- Cite only sources you have checked. Mark unknowns as `[citation needed]` in the text, not with a
  made-up key.

## Files

- `references/templates.md` - minimal article, report and letter skeletons.
- `references/troubleshooting.md` - common errors and fixes.
- `references/platform-compatibility.md` - where each step runs.
