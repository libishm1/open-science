"""Compile every transcribed equation with pdflatex (amsmath/amssymb/bm) to catch LaTeX errors.

Input:  equations.json {"key": ..., "equations": [{"id": "1", "latex": "..."}, ...]} (Stage 2, Task C)
Output: one line per equation (OK / ERROR + first error line) and a summary; exit code 1 if any fail.
        The .tex/.log files go to workdir (default: a new temporary folder).
pdflatex runs with -no-shell-escape and a 90 s timeout per equation.

Example: python -P check_latex.py work/eqpipe/equations/Smith2024.json work/eqpipe/latexwork/Smith2024
Requires: a TeX distribution with pdflatex on PATH (TeX Live or MiKTeX); standard library only.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('equations', help='equations JSON')
ap.add_argument('workdir', nargs='?', help='folder for the .tex files (default: new temp folder)')
args = ap.parse_args()

eqs = json.load(open(args.equations, encoding='utf-8'))
work = args.workdir or tempfile.mkdtemp(prefix='eqcheck_')
os.makedirs(work, exist_ok=True)
PRE = (r'\documentclass{article}\usepackage{amsmath,amssymb,bm}\usepackage[T1]{fontenc}'
       r'\providecommand{\degree}{^\circ}\begin{document}' + '\n')
bad = 0
for e in eqs['equations']:
    tex = PRE + '\\begin{equation*}\n' + e['latex'].strip().strip('$') + '\n\\end{equation*}\n\\end{document}\n'
    name = 'eq_' + ''.join(c if c.isalnum() else '_' for c in str(e['id']))
    open(os.path.join(work, name + '.tex'), 'w', encoding='utf-8').write(tex)
    try:
        r = subprocess.run(['pdflatex', '-interaction=nonstopmode', '-halt-on-error', '-no-shell-escape', name + '.tex'],
                           cwd=work, capture_output=True, text=True, timeout=90, encoding='utf-8', errors='replace')
        ok = r.returncode == 0
        err = next((l for l in r.stdout.splitlines() if l.startswith('!')), '') if not ok else ''
    except subprocess.TimeoutExpired:
        ok, err = False, 'timeout'
    bad += (not ok)
    print(f"eq {e['id']}: {'OK' if ok else 'ERROR ' + err}")
print(f"SUMMARY {len(eqs['equations']) - bad}/{len(eqs['equations'])} equations compile")
sys.exit(1 if bad else 0)
