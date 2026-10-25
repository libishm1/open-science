"""Small data panels, and an honest way to show a gap in the data.

These take their numbers as arguments rather than importing a content module,
so they work for any figure.  The one rule they enforce: a panel must not be
able to disagree with the drawing beside it, so counts are derived from the same
structure the layout reads, never retyped.
"""
from __future__ import annotations

from matplotlib.patches import Rectangle

from . import style as S

# A reasonable default; override to match the source's own vocabulary.
GRADE_STYLE = {
    "established": dict(ls="solid", label="Established",
                        note="loss- and gain-of-function, phenotype in vivo"),
    "association": dict(ls="dashed", label="Association",
                        note="derived from expression cohorts"),
    "inference":   dict(ls="dotted", label="Inference",
                        note="not demonstrated causally in vivo"),
}

DASH = {"solid": (0, ()), "dashed": (0, (2.4, 1.5)), "dotted": (0, (0.7, 1.4))}


def grade_counts(items, key: str = "grade", grades=None) -> dict:
    """Census over any iterable of dicts carrying an evidence grade."""
    grades = grades or GRADE_STYLE
    out = {k: 0 for k in grades}
    for item in items:
        g = item.get(key)
        if g in out:
            out[g] += 1
    return out


def evidence_census(fig, rect, counts, *, title: str = "", grades=None,
                    hero=None):
    """Stacked bar of how well supported the figure's own claims are.

    rect is (x, y, w, h) in millimetres on the main canvas.
    """
    grades = grades or GRADE_STYLE
    hero = hero or S.P["hero"]
    x, y, w, h = rect
    order = [k for k in grades if counts.get(k)]
    cols = {}
    for i, k in enumerate(grades):
        t = i / max(len(grades) - 1, 1)
        cols[k] = S.mix(hero, S.P["ink_faint"], t)

    ax = S.chart_axes(fig, x, y, w, h)
    total = max(sum(counts.values()), 1)
    left = 0.0
    for k in order:
        v = counts[k]
        ax.barh([0], [v], left=[left], height=0.62, color=cols[k],
                edgecolor=S.P["paper"], linewidth=0.5, zorder=3)
        if v / total > 0.10:
            ax.text(left + v / 2, 0, str(v), ha="center", va="center",
                    fontsize=S.TYPE["micro"], color=S.P["paper"],
                    fontweight="bold", zorder=4)
        left += v
    ax.set_xlim(0, total)
    ax.set_ylim(-0.55, 0.55)
    ax.set_xticks([])
    ax.set_yticks([])
    for side in ("left", "bottom"):
        ax.spines[side].set_visible(False)

    main = fig.axes[0]
    if title:
        S.text(main, x, y + h + 1.0, title, size=S.TYPE["micro"],
               color=S.P["ink_soft"], va="bottom")
    caption = "   ·   ".join(
        f"{counts[k]} {grades[k]['label'].lower()}" for k in order)
    S.text(main, x, y - 1.9, caption, size=S.TYPE["micro"],
           color=S.P["ink_soft"], va="center")
    return ax


def grade_key(ax, x, y, *, gap: float = 3.1, length: float = 6.0, grades=None,
              notes: bool = True, extra=()):
    """Line-style key.  Without this the encoding is private to the author.

    `extra` takes (colour, linestyle_name, label) triples for figure-specific
    routes, for example a bypass drawn in an accent colour.
    """
    grades = grades or GRADE_STYLE
    rows = [(S.P["ink"], grades[k]["ls"], grades[k]["label"],
             grades[k]["note"]) for k in grades]
    rows += [(c, ls, lab, "") for c, ls, lab in extra]
    for i, (col, ls, lab, note) in enumerate(rows):
        yy = y - i * gap
        ax.plot([x, x + length], [yy, yy], color=col, lw=0.85,
                linestyle=DASH[ls], solid_capstyle="round", zorder=72)
        S.text(ax, x + length + 1.4, yy, lab, size=S.TYPE["micro"],
               weight="bold", color=col, va="center")
        if notes and note:
            S.text(ax, x + length + 1.4 + len(lab) * 1.18 + 1.4, yy, note,
                   size=S.TYPE["micro"], color=S.P["ink_soft"], va="center")


def missing_data_note(ax, rect, *, what: str, source: str):
    """Mark a gap the source cannot fill, instead of inventing a number.

    A placeholder naming what is absent is informative.  A fabricated value is
    a fabricated result.
    """
    x, y, w, h = rect
    p = S.rounded_rect(x, y, w, h, 1.2)
    S.fill(ax, p, S.P["paper_warm"], alpha=0.75, zorder=16)
    S.stroke(ax, p, color=S.P["rule"], lw=0.4, ls=(0, (2, 1.6)), zorder=17)
    S.text(ax, x + w / 2, y + h / 2 + 1.4, what, size=S.TYPE["micro"],
           weight="bold", ha="center", va="center", color=S.P["ink_soft"])
    S.text(ax, x + w / 2, y + h / 2 - 1.4, source, size=S.TYPE["micro"],
           ha="center", va="center", color=S.P["ink_faint"])
