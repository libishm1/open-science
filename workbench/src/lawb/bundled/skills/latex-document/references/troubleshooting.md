# LaTeX troubleshooting

Part of the latex-document skill. Find the first error line in the log, then match it here.

| Error text | Cause | Fix |
|---|---|---|
| `Undefined control sequence` | A command from a package that is not loaded, or a typo | Load the package, or fix the spelling |
| `File 'x.sty' not found` | Package missing | Tectonic fetches it automatically; with TeX Live run `tlmgr install x`; with MiKTeX allow on-the-fly install |
| `Missing $ inserted` | Maths character (`_`, `^`) in text mode | Wrap in `$...$`, or escape as `\_` |
| `Citation 'key' undefined` | BibTeX not run, or key misspelt | Run the full build (latexmk or tectonic does this); check the key in the `.bib` file |
| `Reference 'fig:x' undefined` | Label missing or one pass short | Check `\label` is after `\caption`; rebuild |
| `Overfull \hbox` | A line is too wide | Usually harmless; break long URLs with `\url{}` or rephrase |
| `Unicode character ... not set up` | Non-ASCII text with pdfLaTeX | Compile with XeLaTeX or LuaLaTeX and use `fontspec` |
| `Dimension too large` | A plotted value or coordinate overflowed | Scale the data, or use `pgfplots` with `compat` set |
| `Too many unprocessed floats` | Many figures in a row | Add `\clearpage`, or use the `placeins` package |

If the error makes no sense, comment out half the document and rebuild. Repeat on the failing half
until one line remains.
