# -*- coding: utf-8 -*-
"""Run a matplotlib figure script with every savefig forced to one resolution (default 600 dpi, as many
journals ask for). Only the raster resolution changes: sizes are in inches and fonts in points, so the
layout is identical.

Inputs:  a figure script (run as __main__ from its own folder) and optional arguments for it after --
Output:  whatever the script saves, at --dpi

Example: python render_600dpi.py figures/make_fig3.py
         python render_600dpi.py --dpi 1200 figures/make_fig3.py -- --variant b
Requires: matplotlib.
"""
import argparse, os, runpy, sys
import matplotlib
matplotlib.use("Agg")
from matplotlib.figure import Figure

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--dpi", type=int, default=600, help="resolution for every savefig (default: 600)")
ap.add_argument("script", help="figure script to run")
ap.add_argument("script_args", nargs=argparse.REMAINDER, help="arguments passed to the script (after --)")
args = ap.parse_args()

_orig = Figure.savefig


def _savefig(self, *a, **kwargs):
    kwargs["dpi"] = args.dpi
    return _orig(self, *a, **kwargs)


Figure.savefig = _savefig
script = os.path.abspath(args.script)
os.chdir(os.path.dirname(script))
sys.path.insert(0, os.path.dirname(script))
sys.argv = [script] + [x for x in args.script_args if x != "--"]
runpy.run_path(script, run_name="__main__")
