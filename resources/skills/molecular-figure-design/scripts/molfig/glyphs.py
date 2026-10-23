"""Vector biological and chemical glyphs, generated rather than imported.

Bioicons and SciDraw are excellent sources, but a downloaded icon set fixes the
line weight, palette and level of abstraction before the layout exists, and the
licences differ per icon.  Everything here is drawn from parameters instead, so
one call changes the stroke weight of the whole figure and the licence is the
project's own.

Chemistry is drawn as real skeletal structures (correct bond orders and
substituent positions), because a reviewer who knows the molecule will look.
"""
from __future__ import annotations

import numpy as np
from matplotlib.patches import PathPatch
from matplotlib.path import Path

from . import style as S

# --------------------------------------------------------------------------- #
# Skeletal chemistry
# --------------------------------------------------------------------------- #
def zigzag(x0: float, y0: float, n: int, L: float = 1.0, angle: float = 30.0,
           start_up: bool = True) -> np.ndarray:
    """n vertices of a standard skeletal zigzag chain."""
    a = np.deg2rad(angle)
    dx, dy = L * np.cos(a), L * np.sin(a)
    pts = [(x0, y0)]
    up = start_up
    for _ in range(n - 1):
        px, py = pts[-1]
        pts.append((px + dx, py + (dy if up else -dy)))
        up = not up
    return np.asarray(pts)


def draw_bonds(ax, pts: np.ndarray, bonds, *, color=None, lw: float = 0.45,
               zorder: int = 40, double_gap: float = 0.14, alpha: float = 1.0):
    """Draw bonds given (i, j, order) triples."""
    color = color or S.P["ink"]
    for i, j, order in bonds:
        p, q = pts[i], pts[j]
        d = q - p
        n = np.array([-d[1], d[0]])
        n /= (np.linalg.norm(n) + 1e-9)
        if order == 1:
            ax.plot(*np.column_stack([p, q]), color=color, lw=lw, zorder=zorder,
                    solid_capstyle="round", alpha=alpha)
        else:
            for s in (+1, -1):
                off = n * double_gap * s
                ax.plot(*np.column_stack([p + off, q + off]), color=color,
                        lw=lw, zorder=zorder, solid_capstyle="round", alpha=alpha)


def atom_label(ax, p, s, *, color=None, size=None, halo=True, zorder: int = 44,
               dx: float = 0.0, dy: float = 0.0):
    """Heteroatom label with a paper-coloured halo so bonds read behind it."""
    import matplotlib.patheffects as pe
    size = size or S.TYPE["micro"]
    t = ax.text(p[0] + dx, p[1] + dy, s, fontsize=size, color=color or S.P["ink"],
                ha="center", va="center", zorder=zorder, fontweight="medium")
    if halo:
        t.set_path_effects([pe.withStroke(linewidth=1.5, foreground=S.P["paper"])])
    return t


def hne(ax, x: float, y: float, *, L: float = 1.25, reduced: bool = False,
        color=None, accent=None, zorder: int = 40, lw: float = 0.45):
    """4-hydroxynonenal, or its reduced product 1,4-dihydroxynon-2-ene.

    HNE: OHC-CH=CH-CH(OH)-C5H11.  Carbonyl reductases reduce C1 to a primary
    alcohol and leave the C2=C3 alkene intact, so the only difference between
    the two glyphs is the C1 group: a true before/after pair.
    """
    color = color or S.P["ink"]
    accent = accent or S.P["ferro"]
    pts = zigzag(x, y, 9, L=L, start_up=True)
    bonds = [(i, i + 1, 1) for i in range(8)]
    bonds[1] = (1, 2, 2)                       # C2=C3
    draw_bonds(ax, pts, bonds, color=color, lw=lw, zorder=zorder)

    oh4 = pts[3] + np.array([0.0, -L * 0.82])  # C4 hydroxyl
    ax.plot(*np.column_stack([pts[3], oh4]), color=color, lw=lw, zorder=zorder,
            solid_capstyle="round")
    atom_label(ax, oh4, "OH", color=color, dy=-L * 0.16, zorder=zorder + 4)

    if reduced:
        o1 = pts[0] + np.array([-L * 0.80, L * 0.40])
        ax.plot(*np.column_stack([pts[0], o1]), color=accent, lw=lw,
                zorder=zorder, solid_capstyle="round")
        atom_label(ax, o1, "OH", color=accent, dx=-L * 0.16, zorder=zorder + 4)
    else:
        o1 = pts[0] + np.array([-L * 0.80, L * 0.40])
        draw_bonds(ax, np.array([pts[0], o1]), [(0, 1, 2)], color=accent,
                   lw=lw, zorder=zorder, double_gap=L * 0.10)
        atom_label(ax, o1, "O", color=accent, dx=-L * 0.20, dy=L * 0.10,
                   zorder=zorder + 4)
    return pts


def hexagon(cx: float, cy: float, r: float, *, pointy_top: bool = True):
    """Six vertices; pointy_top gives vertical left/right edges for fusion."""
    off = 90 if pointy_top else 60
    a = np.deg2rad(np.arange(6) * 60 + off)
    return np.column_stack([cx + r * np.cos(a), cy + r * np.sin(a)])


def anthracycline(ax, x: float, y: float, *, r: float = 1.05,
                  reduced: bool = False, color=None, accent=None,
                  zorder: int = 40, lw: float = 0.45):
    """Simplified anthracycline core: the linear tetracycle plus the C-13 group.

    Drawn as the recognisable ring system rather than full doxorubicin, and
    labelled as simplified in the caption.  The point of the glyph is the C-13
    carbonyl that carbonyl reductases turn into the far less active alcohol.
    """
    color = color or S.P["ink"]
    accent = accent or S.P["chemo"]
    dx = r * np.sqrt(3)
    rings = [hexagon(x + i * dx, y, r) for i in range(4)]
    for k, ring in enumerate(rings):
        ax.add_patch(PathPatch(Path(np.vstack([ring, ring[:1]])),
                               facecolor="none", edgecolor=color, lw=lw,
                               zorder=zorder, joinstyle="round"))
        if k in (1, 2):                        # quinone carbonyls
            for vi, sign in ((0, +1), (3, -1)):
                p = ring[vi]
                o = p + np.array([0.0, sign * r * 0.80])
                draw_bonds(ax, np.array([p, o]), [(0, 1, 2)], color=accent,
                           lw=lw, zorder=zorder, double_gap=r * 0.11)
                atom_label(ax, o, "O", color=accent, dy=sign * r * 0.18,
                           zorder=zorder + 4)
    # C-13 side chain on the right-hand ring
    anchor = rings[3][5]
    c13 = anchor + np.array([r * 0.86, -r * 0.50])
    me = c13 + np.array([r * 0.86, r * 0.50])
    ax.plot(*np.column_stack([anchor, c13]), color=color, lw=lw, zorder=zorder,
            solid_capstyle="round")
    ax.plot(*np.column_stack([c13, me]), color=color, lw=lw, zorder=zorder,
            solid_capstyle="round")
    o13 = c13 + np.array([0.0, -r * 0.85])
    if reduced:
        ax.plot(*np.column_stack([c13, o13]), color=accent, lw=lw,
                zorder=zorder, solid_capstyle="round")
        atom_label(ax, o13, "OH", color=accent, dy=-r * 0.18, zorder=zorder + 4)
    else:
        draw_bonds(ax, np.array([c13, o13]), [(0, 1, 2)], color=accent, lw=lw,
                   zorder=zorder, double_gap=r * 0.11)
        atom_label(ax, o13, "O", color=accent, dy=-r * 0.20, zorder=zorder + 4)
    return {"c13": c13, "right": me, "left": rings[0][3]}


def sugar_ring(ax, cx: float, cy: float, r: float, *, color=None,
               fill_color=None, label: str = "", zorder: int = 40,
               lw: float = 0.45, furanose: bool = False):
    """Pyranose (or furanose) ring glyph for glucose / sorbitol / fructose."""
    color = color or S.P["ink"]
    n = 5 if furanose else 6
    a = np.deg2rad(np.arange(n) * (360 / n) + 90)
    ring = np.column_stack([cx + r * np.cos(a), cy + r * np.sin(a)])
    if fill_color is not None:
        ax.add_patch(PathPatch(Path(np.vstack([ring, ring[:1]])),
                               facecolor=fill_color, edgecolor="none",
                               alpha=0.5, zorder=zorder - 1))
    ax.add_patch(PathPatch(Path(np.vstack([ring, ring[:1]])), facecolor="none",
                           edgecolor=color, lw=lw, zorder=zorder,
                           joinstyle="round"))
    if label:
        S.text(ax, cx, cy, label, size=S.TYPE["micro"], ha="center",
               va="center", color=color, zorder=zorder + 2)
    return ring


# --------------------------------------------------------------------------- #
# Cell architecture
# --------------------------------------------------------------------------- #
def cell(ax, path: Path, *, cyto_lo=None, cyto_hi=None, edge=None,
         zorder: int = 10):
    """Tumour cell body: gradient cytoplasm, occluded rim, double membrane."""
    cyto_lo = cyto_lo or S.tint(S.P["hero"], 0.93)
    cyto_hi = cyto_hi or S.P["paper_warm"]
    edge = edge or S.mix(S.P["hero_deep"], S.P["ink"], 0.4)
    S.soft_shadow(ax, path, blur=2.2, dx=0.7, dy=-1.0, color=S.P["ink"],
                  alpha=0.16, zorder=zorder - 4)
    S.gradient_fill(ax, path, cyto_hi, cyto_lo, kind="radial",
                    focus=(0.40, 0.70), spread=1.25, zorder=zorder)
    S.inner_shade(ax, path, blur=2.0, color=S.mix(S.P["hero_deep"], S.P["ink"], 0.5),
                  alpha=0.20, zorder=zorder + 2)
    S.stroke(ax, path, color=edge, lw=0.75, alpha=0.85, zorder=zorder + 4)
    inner = S.offset_path(path, -0.55)
    S.stroke(ax, inner, color=edge, lw=0.32, alpha=0.40, zorder=zorder + 4)
    return inner


def nucleus(ax, cx: float, cy: float, rx: float, ry: float, *, seed: int = 7,
            color=None, zorder: int = 24, pores: int = 15):
    """Nucleus with envelope, pores and a faint chromatin texture."""
    color = color or S.P["hypox"]
    p = S.blob(cx, cy, rx, ry, seed=seed, n=13, jitter=0.045)
    S.soft_shadow(ax, p, blur=1.3, dx=0.4, dy=-0.5, color=S.P["ink"],
                  alpha=0.20, zorder=zorder - 2)
    S.gradient_fill(ax, p, S.tint(color, 0.80), S.tint(color, 0.46),
                    kind="radial", focus=(0.40, 0.70), zorder=zorder)
    S.inner_shade(ax, p, blur=1.1, color=S.shade(color, 0.3), alpha=0.28,
                  zorder=zorder + 1)
    S.stroke(ax, p, color=S.shade(color, 0.35), lw=0.55, zorder=zorder + 3)

    poly = p.to_polygons(closed_only=False)[0]
    idx = np.linspace(0, len(poly) - 1, pores, endpoint=False).astype(int)
    ax.scatter(poly[idx, 0], poly[idx, 1], s=1.5, c=[S.shade(color, 0.45)],
               zorder=zorder + 4, linewidths=0)
    return p


def bilayer(ax, x0: float, x1: float, y: float, *, h: float = 2.3,
            period: float = 1.05, color=None, tail_color=None,
            zorder: int = 30, lw: float = 0.32, oxidised=(),
            curve: float = 0.0):
    """Phospholipid bilayer strip, with optional peroxidised tails.

    `oxidised` is a sequence of indices whose tails are drawn kinked and
    peroxide-capped, which is how lipid peroxidation actually presents.
    """
    color = color or S.mix(S.P["hero_deep"], S.P["ink"], 0.35)
    tail_color = tail_color or S.P["ink_faint"]
    n = max(int((x1 - x0) / period), 2)
    xs = np.linspace(x0, x1, n)
    yy = y + curve * np.sin(np.linspace(0, np.pi, n))
    r = period * 0.27
    for side in (+1, -1):
        for k, (xi, yi) in enumerate(zip(xs, yy)):
            head = (xi, yi + side * h / 2)
            ox = k in oxidised
            tcol = S.P["ferro"] if ox else tail_color
            for t_off in (-r * 0.45, r * 0.45):
                tip_y = yi + side * h * 0.07
                if ox:
                    mid = (xi + t_off * 0.4, (head[1] + tip_y) / 2 + side * 0.12)
                    ax.plot([head[0] + t_off, mid[0], xi + t_off * 0.2],
                            [head[1] - side * r, mid[1], tip_y],
                            color=tcol, lw=lw, zorder=zorder,
                            solid_capstyle="round")
                else:
                    ax.plot([head[0] + t_off, xi + t_off * 0.2],
                            [head[1] - side * r, tip_y], color=tcol, lw=lw,
                            zorder=zorder, solid_capstyle="round")
            hc = S.P["ferro"] if ox else color
            ax.scatter(*head, s=(r * 10) ** 2 * 0.30, c=[S.tint(hc, 0.25)],
                       edgecolors=S.shade(hc, 0.3), linewidths=lw * 0.6,
                       zorder=zorder + 1)
            if ox:
                ax.scatter(head[0] + r * 1.0, head[1] + side * r * 0.9, s=1.9,
                           c=[S.P["ferro"]], linewidths=0, zorder=zorder + 2)
    return xs, yy


def ros(ax, cx: float, cy: float, r: float, *, color=None, n: int = 8,
        zorder: int = 34, lw: float = 0.34):
    """Radiating burst for ROS / reactive carbonyl stress."""
    color = color or S.P["ferro"]
    a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    for ai in a:
        ax.plot([cx + r * 0.52 * np.cos(ai), cx + r * np.cos(ai)],
                [cy + r * 0.52 * np.sin(ai), cy + r * np.sin(ai)],
                color=color, lw=lw, zorder=zorder, solid_capstyle="round")
    ax.scatter(cx, cy, s=(r * 9) ** 2 * 0.09, c=[S.tint(color, 0.25)],
               edgecolors=color, linewidths=lw, zorder=zorder + 1)


def immune_cell(ax, cx: float, cy: float, r: float, *, color=None,
                zorder: int = 22, seed: int = 11, label: str = ""):
    """Lymphocyte-style cell: ruffled outline, large nucleus."""
    color = color or S.P["metab"]
    p = S.blob(cx, cy, r, r, seed=seed, n=15, jitter=0.16)
    S.soft_shadow(ax, p, blur=0.9, dx=0.25, dy=-0.4, alpha=0.18,
                  zorder=zorder - 1)
    S.gradient_fill(ax, p, S.tint(color, 0.70), S.tint(color, 0.35),
                    kind="radial", focus=(0.4, 0.68), zorder=zorder)
    S.stroke(ax, p, color=S.shade(color, 0.35), lw=0.42, zorder=zorder + 2)
    nuc = S.blob(cx - r * 0.12, cy + r * 0.05, r * 0.52, r * 0.46,
                 seed=seed + 1, n=11, jitter=0.10)
    S.fill(ax, nuc, S.shade(color, 0.30), alpha=0.85, zorder=zorder + 3)
    if label:
        S.text(ax, cx, cy - r - 0.9, label, size=S.TYPE["micro"],
               ha="center", va="top", color=S.shade(color, 0.3))
    return p


def cofactor_cycle(ax, cx: float, cy: float, r: float, *, color=None,
                   zorder: int = 46, lw: float = 0.5,
                   left: str = "NADPH", right: str = "NADP$^+$"):
    """Circular cofactor arrow: the shared reducing-equivalent pool."""
    color = color or S.P["cofactor"]
    a = np.linspace(np.deg2rad(205), np.deg2rad(-25), 90)
    pts = np.column_stack([cx + r * np.cos(a), cy + r * np.sin(a)])
    ax.plot(pts[:, 0], pts[:, 1], color=S.shade(color, 0.15), lw=lw,
            zorder=zorder, solid_capstyle="round")
    d = pts[-1] - pts[-4]
    d /= (np.linalg.norm(d) + 1e-9)
    nvec = np.array([-d[1], d[0]])
    head = np.array([pts[-1] + d * 0.55,
                     pts[-1] - d * 0.30 + nvec * 0.38,
                     pts[-1] - d * 0.30 - nvec * 0.38])
    ax.add_patch(PathPatch(Path(head), facecolor=S.shade(color, 0.15),
                           edgecolor="none", zorder=zorder))
    S.text(ax, cx - r * 1.02, cy - r * 0.44, left, size=S.TYPE["micro"],
           ha="right", va="center", color=S.shade(color, 0.25))
    S.text(ax, cx + r * 1.02, cy - r * 0.44, right, size=S.TYPE["micro"],
           ha="left", va="center", color=S.shade(color, 0.25))


def zoom_callout(ax, src, dst_rect, *, color=None, lw: float = 0.3,
                 alpha: float = 0.55, zorder: int = 18, r: float = 1.4):
    """Marker on the source plus two leader lines to a detail panel."""
    color = color or S.P["ink_faint"]
    x, y, w, h = dst_rect
    cx, cy = src
    circ = S.blob(cx, cy, r, r, seed=2, n=18, jitter=0.0)
    S.stroke(ax, circ, color=color, lw=lw, alpha=alpha + 0.2, zorder=zorder)
    corners = [(x, y + h), (x, y)] if x > cx else [(x + w, y + h), (x + w, y)]
    for c in corners:
        v = np.array(c) - np.array(src)
        v = v / (np.linalg.norm(v) + 1e-9)
        ax.plot([cx + v[0] * r, c[0]], [cy + v[1] * r, c[1]], color=color,
                lw=lw, alpha=alpha, zorder=zorder, solid_capstyle="round")


def card(ax, x: float, y: float, w: float, h: float, *, accent=None,
         r: float = 1.6, zorder: int = 16, alpha: float = 0.52,
         edge_alpha: float = 0.5, lw: float = 0.35):
    """Soft tinted zone behind a functional group of glyphs."""
    accent = accent or S.P["hero"]
    p = S.rounded_rect(x, y, w, h, r)
    S.fill(ax, p, S.tint(accent, 0.90), alpha=alpha, zorder=zorder)
    S.stroke(ax, p, color=S.tint(accent, 0.45), lw=lw, alpha=edge_alpha,
             zorder=zorder + 1)
    return p
