"""Smallest figure that exercises the whole pipeline.

    py -3.11 example_figure.py
    py -3.11 ../scripts/check_overlaps.py example_figure:build

Shows the five things worth copying: a millimetre canvas, a real structure
rendered from deposited coordinates, depth from blurred masks rather than
outlines, connectors whose line style carries evidence grade, and a content
block that the drawing code reads instead of containing.

Replace CONTENT and the three zones; keep the structure.
"""
from __future__ import annotations

import os
import pathlib
import sys

import matplotlib
matplotlib.use("Agg")

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

from molfig import style as S          # noqa: E402
from molfig import structure as ST     # noqa: E402

# --------------------------------------------------------------------------- #
# Every fact lives here, never in the drawing code below.  That is what keeps a
# figure and its manuscript from drifting apart through a revision.
# --------------------------------------------------------------------------- #
CONTENT = {
    "title": "One structure, three consequences",
    "strapline": "replace this with the claim the figure is making",
    # EXAMPLE_PDB lets the smoke test run against a cached entry offline
    "pdb": os.environ.get("EXAMPLE_PDB", "1CRN"),
    "pdb_note": "replace with your own entry",
    "effects": [
        dict(label="Established effect", grade="established", hue="ferro",
             detail="loss- and gain-of-function,\nphenotype in vivo"),
        dict(label="Reported association", grade="association", hue="metab",
             detail="derived from expression\ncohorts"),
        dict(label="Plausible inference", grade="inference", hue="slate",
             detail="not demonstrated causally\nin vivo"),
    ],
}

GRADE_DASH = {"established": (0, ()), "association": (0, (2.4, 1.5)),
              "inference": (0, (0.7, 1.4))}

W, H = 180.0, 80.0


def build():
    S.use_style()
    fig, ax = S.canvas(W, H)

    S.text(ax, 3, H - 8, CONTENT["title"], size=S.TYPE["title"], weight="bold")
    S.text(ax, 3, H - 13, CONTENT["strapline"], size=S.TYPE["label"],
           color=S.P["ink_soft"])
    ax.plot([3, W - 3], [H - 17, H - 17], color=S.P["rule"], lw=0.5, zorder=70)

    # left: the structure, placed by giving it a box in millimetres
    info = ST.place_enzyme(ax, (4, 16, 44, 44), pdb_id=CONTENT["pdb"],
                           roll=35, tilt=20, halo=True, zorder=40)
    S.text(ax, 26, 13, f"PDB {CONTENT['pdb']}, {CONTENT['pdb_note']}",
           size=S.TYPE["micro"], ha="center", color=S.P["ink_soft"])
    S.text(ax, 26, 9.6, f"{info['n_res']} residues, chain {info['chain']}",
           size=S.TYPE["micro"], ha="center", color=S.P["ink_faint"])

    # right: three outcome cards, line style carrying the evidence grade
    x0, w, h = 86.0, 90.0, 14.0
    for i, eff in enumerate(CONTENT["effects"]):
        y = 46.0 - i * 18.0
        hue = S.P[eff["hue"]]
        card = S.rounded_rect(x0, y, w, h, 1.4)
        S.soft_shadow(ax, card, blur=0.9, dx=0.3, dy=-0.45, alpha=0.14,
                      zorder=18)
        S.gradient_fill(ax, card, S.tint(hue, 0.90), S.tint(hue, 0.74),
                        kind="linear", angle=260, zorder=20)
        S.stroke(ax, card, color=S.tint(hue, 0.38), lw=0.42, zorder=24)
        ax.plot([x0, x0], [y + 0.6, y + h - 0.6], color=hue, lw=1.4,
                solid_capstyle="round", zorder=26)
        S.text(ax, x0 + 2.4, y + h - 4.4, eff["label"], size=S.TYPE["label"],
               weight="bold", color=S.shade(hue, 0.28))
        S.text(ax, x0 + 2.4, y + 4.6, eff["detail"], size=S.TYPE["micro"],
               color=S.P["ink_soft"], va="center", linespacing=1.35)

        ax.plot([52, x0 - 1.4], [38, y + h / 2], color=S.mix(hue, S.P["ink"], 0.12),
                lw=0.6, linestyle=GRADE_DASH[eff["grade"]],
                solid_capstyle="round", zorder=52)

    return fig, info


if __name__ == "__main__":
    out = pathlib.Path("out")
    out.mkdir(exist_ok=True)
    fig, _ = build()
    for fmt in ("pdf", "svg", "png"):
        fig.savefig(out / f"example_figure.{fmt}", dpi=600,
                    facecolor=fig.get_facecolor())
    print("written to", out.resolve())
