"""Design system for a programmatic scientific figure.

Everything is drawn in millimetres on one matplotlib axes, so panel placement is
arithmetic rather than guesswork.  Output stays vector (PDF/SVG); only the soft
shadow and gradient layers are resampled raster, which is what lets shapes read
as illustration instead of flat clip art.

Conventions
-----------
zorder bands:  0-9 background | 10-19 cell body | 20-29 cards and organelles
               30-39 detail art | 40-49 protein | 50-59 arrows | 70+ type
"""
from __future__ import annotations

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, to_rgb, to_rgba
from matplotlib.patches import PathPatch
from matplotlib.path import Path
from scipy.ndimage import gaussian_filter

# --------------------------------------------------------------------------- #
# Canvas
# --------------------------------------------------------------------------- #
CANVAS_W = 180.0          # mm, double-column
CANVAS_H = 132.0          # mm

# Resolution of the raster layers (gradients, shadows, glows) in pixels per
# millimetre.  They are smooth by construction, so this can drop a long way
# before it shows; it is the dominant term in exported PDF size.
PX_PER_MM = 6.0

# --------------------------------------------------------------------------- #
# Palette.  One hero hue for the subject of the figure, three accent hues for
# upstream causes, three for downstream effects, and a desaturated slate.  Large
# areas use tints; saturation is reserved for small accents.
# --------------------------------------------------------------------------- #
PALETTE = {
    "ink":        "#101D2B",
    "ink_soft":   "#44535F",
    "ink_faint":  "#8A96A0",
    "paper":      "#F8F6F2",
    "paper_warm": "#F1ECE4",
    "rule":       "#D8D1C6",
    # hero hue: the one saturated colour the figure is built around
    "hero":        "#0F7A72",
    "hero_deep":   "#07433F",
    "hero_light":  "#CFE4E0",
    # accent hues, checked pairwise for deuteranope separation (see
    # references/debugging-and-readability.md for the check)
    "oxid":       "#C9941F",   # electrophilic / oxidative stress
    "hypox":      "#5A5796",   # hypoxia, HIF-1a
    "chemo":      "#A33E5D",   # therapeutic drug stress
    # convergent phenotypes
    "ferro":      "#B04A2C",   # iron / lipid peroxidation
    "metab":      "#5C6E2E",   # carbonyl and lipid metabolism
    # gap
    "slate":      "#7F8A93",
    "slate_pale": "#BFC6CB",
    "cofactor":   "#C9A227",   # NADPH
    "warn":       "#A33E5D",
}
P = PALETTE

# --------------------------------------------------------------------------- #
# Type scale (points).  One family, five sizes, no exceptions.
# --------------------------------------------------------------------------- #
TYPE = {
    "title":   10.5,
    "zone":     6.6,
    "label":    5.6,
    "micro":    4.8,
    "tick":     4.4,
}

FONT_STACK = ["Arial", "Helvetica", "Helvetica Neue", "Liberation Sans", "DejaVu Sans"]


def use_style() -> None:
    """Set global rcParams.  Fonts stay as text in SVG and as Type-42 in PDF."""
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": FONT_STACK,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "axes.linewidth": 0.4,
        "xtick.major.width": 0.4,
        "ytick.major.width": 0.4,
        "xtick.major.size": 1.4,
        "ytick.major.size": 1.4,
        "xtick.labelsize": TYPE["tick"],
        "ytick.labelsize": TYPE["tick"],
        "text.color": P["ink"],
        "axes.labelcolor": P["ink"],
        "xtick.color": P["ink_soft"],
        "ytick.color": P["ink_soft"],
        "figure.dpi": 150,
        "savefig.dpi": 600,
    })


def canvas(w: float = CANVAS_W, h: float = CANVAS_H):
    """Return (fig, ax) whose data coordinates are millimetres."""
    fig = plt.figure(figsize=(w / 25.4, h / 25.4))
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_facecolor(P["paper"])
    fig.patch.set_facecolor(P["paper"])
    return fig, ax


def chart_axes(fig, x: float, y: float, w: float, h: float, zorder: int = 60):
    """Inset axes positioned in millimetres on the main canvas."""
    ax = fig.add_axes((x / CANVAS_W, y / CANVAS_H, w / CANVAS_W, h / CANVAS_H))
    ax.set_zorder(zorder)
    ax.patch.set_alpha(0.0)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(P["ink_faint"])
        ax.spines[side].set_linewidth(0.35)
    ax.tick_params(length=1.2, width=0.35, pad=1.2, labelsize=TYPE["tick"])
    return ax


# --------------------------------------------------------------------------- #
# Colour helpers
# --------------------------------------------------------------------------- #
def mix(c1, c2, t: float):
    """Linear blend of two colours, t=0 -> c1, t=1 -> c2."""
    a, b = np.array(to_rgb(c1)), np.array(to_rgb(c2))
    return tuple(a + (b - a) * float(t))


def tint(c, t: float):
    """Lighten toward paper."""
    return mix(c, P["paper"], t)


def shade(c, t: float):
    """Darken toward ink."""
    return mix(c, P["ink"], t)


# --------------------------------------------------------------------------- #
# Path construction
# --------------------------------------------------------------------------- #
def catmull_rom_closed(pts: np.ndarray) -> Path:
    """Closed cubic-Bezier path interpolating `pts` (N,2) smoothly."""
    pts = np.asarray(pts, dtype=float)
    n = len(pts)
    verts = [pts[0]]
    codes = [Path.MOVETO]
    for i in range(n):
        p0, p1 = pts[(i - 1) % n], pts[i]
        p2, p3 = pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = p1 + (p2 - p0) / 6.0
        c2 = p2 - (p3 - p1) / 6.0
        verts += [c1, c2, p2]
        codes += [Path.CURVE4] * 3
    verts.append(pts[0])
    codes.append(Path.CLOSEPOLY)
    return Path(np.asarray(verts), codes)


def catmull_rom_open(pts: np.ndarray) -> Path:
    """Open smooth cubic-Bezier path through `pts`."""
    pts = np.asarray(pts, dtype=float)
    n = len(pts)
    verts = [pts[0]]
    codes = [Path.MOVETO]
    for i in range(n - 1):
        p0 = pts[max(i - 1, 0)]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[min(i + 2, n - 1)]
        c1 = p1 + (p2 - p0) / 6.0
        c2 = p2 - (p3 - p1) / 6.0
        verts += [c1, c2, p2]
        codes += [Path.CURVE4] * 3
    return Path(np.asarray(verts), codes)


def blob(cx: float, cy: float, rx: float, ry: float, *,
         seed: int = 0, n: int = 11, jitter: float = 0.10,
         squash: float = 0.0) -> Path:
    """Organic closed shape.  Cells are not ellipses; this is what stops the
    figure looking like a slide template."""
    rng = np.random.default_rng(seed)
    ang = np.linspace(0, 2 * np.pi, n, endpoint=False)
    r = 1.0 + rng.uniform(-jitter, jitter, n)
    r = 0.5 * (r + np.roll(r, 1))              # smooth the radii a little
    x = cx + rx * r * np.cos(ang)
    y = cy + ry * r * np.sin(ang) * (1.0 - squash * np.cos(ang) ** 2)
    return catmull_rom_closed(np.column_stack([x, y]))


def organic_rect(cx: float, cy: float, rx: float, ry: float, *,
                 n: float = 3.4, seed: int = 3, jitter: float = 0.012,
                 pts: int = 96) -> Path:
    """Superellipse with a little noise: a cell outline with usable interior.

    A plain ellipse wastes the corners, and a rounded rectangle looks like a
    slide shape; the superellipse sits between the two.
    """
    rng = np.random.default_rng(seed)
    t = np.linspace(0, 2 * np.pi, pts, endpoint=False)
    c, s = np.cos(t), np.sin(t)
    x = np.sign(c) * np.abs(c) ** (2.0 / n)
    y = np.sign(s) * np.abs(s) ** (2.0 / n)
    wob = gaussian_filter(rng.normal(0, 1, pts), 6, mode="wrap")
    wob = 1.0 + jitter * wob / (np.abs(wob).max() + 1e-9)
    return catmull_rom_closed(
        np.column_stack([cx + rx * x * wob, cy + ry * y * wob])[::3])


def rounded_rect(x: float, y: float, w: float, h: float, r: float) -> Path:
    """Rounded rectangle as a Path (clippable, unlike FancyBboxPatch)."""
    r = min(r, w / 2, h / 2)
    k = r * 0.5523
    verts = [
        (x + r, y), (x + w - r, y),
        (x + w - r + k, y), (x + w, y + r - k), (x + w, y + r),
        (x + w, y + h - r),
        (x + w, y + h - r + k), (x + w - r + k, y + h), (x + w - r, y + h),
        (x + r, y + h),
        (x + r - k, y + h), (x, y + h - r + k), (x, y + h - r),
        (x, y + r),
        (x, y + r - k), (x + r - k, y), (x + r, y),
        (x + r, y),
    ]
    codes = [Path.MOVETO, Path.LINETO,
             Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.LINETO,
             Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.LINETO,
             Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.LINETO,
             Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.CLOSEPOLY]
    return Path(np.asarray(verts), codes)


def offset_path(path: Path, d: float, samples: int = 400) -> Path:
    """Approximate inward/outward offset of a closed path by `d` mm."""
    pts = path.to_polygons(closed_only=False)[0]
    # resample uniformly
    seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]
    t = np.linspace(0, seg[-1], samples, endpoint=False)
    xs = np.interp(t, seg, pts[:, 0])
    ys = np.interp(t, seg, pts[:, 1])
    cx, cy = xs.mean(), ys.mean()
    vx, vy = xs - cx, ys - cy
    norm = np.hypot(vx, vy)
    xs2 = xs + d * vx / norm
    ys2 = ys + d * vy / norm
    return catmull_rom_closed(np.column_stack([xs2, ys2])[::8])


# --------------------------------------------------------------------------- #
# Fills, shadows, rim light
# --------------------------------------------------------------------------- #
def _clip_to(ax, im, path):
    patch = PathPatch(path, facecolor="none", edgecolor="none")
    patch.set_transform(ax.transData)
    im.set_clip_path(patch)


def gradient_fill(ax, path: Path, c_lo, c_hi, *, kind: str = "linear",
                  angle: float = 90.0, focus=(0.42, 0.72), spread: float = 1.0,
                  alpha: float = 1.0, zorder: int = 10, res: int = 320):
    """Fill a path with a true gradient (not a flat colour)."""
    x0, y0, x1, y1 = path.get_extents().extents
    gx, gy = np.meshgrid(np.linspace(0, 1, res), np.linspace(0, 1, res))
    if kind == "linear":
        a = np.deg2rad(angle)
        t = gx * np.cos(a) + gy * np.sin(a)
        t = (t - t.min()) / max(np.ptp(t), 1e-9)
    else:  # radial
        t = np.hypot((gx - focus[0]), (gy - focus[1])) / (0.72 * spread)
        t = np.clip(t, 0, 1)
    cmap = LinearSegmentedColormap.from_list("g", [c_lo, c_hi])
    rgba = cmap(t)
    rgba[..., 3] *= alpha
    im = ax.imshow(rgba, extent=(x0, x1, y0, y1), origin="lower",
                   zorder=zorder, interpolation="bilinear")
    _clip_to(ax, im, path)
    return im


def _mask(path: Path, x0, y0, x1, y1, px_per_mm=None):
    px_per_mm = px_per_mm or PX_PER_MM
    nx = max(int((x1 - x0) * px_per_mm), 8)
    ny = max(int((y1 - y0) * px_per_mm), 8)
    gx, gy = np.meshgrid(np.linspace(x0, x1, nx), np.linspace(y0, y1, ny))
    pts = np.column_stack([gx.ravel(), gy.ravel()])
    return path.contains_points(pts).reshape(ny, nx).astype(float)


def soft_shadow(ax, path: Path, *, blur: float = 1.6, dx: float = 0.5,
                dy: float = -0.7, color=None, alpha: float = 0.26,
                zorder: int = 5, px_per_mm: float | None = None):
    """Blurred contact shadow.  This, not a thick outline, is what gives depth."""
    px_per_mm = px_per_mm or PX_PER_MM
    color = color or P["ink"]
    x0, y0, x1, y1 = path.get_extents().extents
    pad = 4 * blur + 2
    x0, y0, x1, y1 = x0 - pad, y0 - pad, x1 + pad, y1 + pad
    m = _mask(path, x0, y0, x1, y1, px_per_mm)
    m = gaussian_filter(m, sigma=blur * px_per_mm)
    rgba = np.zeros(m.shape + (4,))
    rgba[..., :3] = to_rgb(color)
    rgba[..., 3] = np.clip(m, 0, 1) * alpha
    ax.imshow(rgba, extent=(x0 + dx, x1 + dx, y0 + dy, y1 + dy),
              origin="lower", zorder=zorder, interpolation="bilinear")


def inner_shade(ax, path: Path, *, blur: float = 1.4, color=None,
                alpha: float = 0.30, zorder: int = 14, px_per_mm: float | None = None):
    """Ambient occlusion just inside an edge: cheap, and reads as volume."""
    px_per_mm = px_per_mm or PX_PER_MM
    color = color or P["ink"]
    x0, y0, x1, y1 = path.get_extents().extents
    pad = 4 * blur + 2
    x0, y0, x1, y1 = x0 - pad, y0 - pad, x1 + pad, y1 + pad
    m = _mask(path, x0, y0, x1, y1, px_per_mm)
    halo = np.clip(gaussian_filter(1.0 - m, sigma=blur * px_per_mm), 0, 1)
    rgba = np.zeros(m.shape + (4,))
    rgba[..., :3] = to_rgb(color)
    rgba[..., 3] = halo * m * alpha
    im = ax.imshow(rgba, extent=(x0, x1, y0, y1), origin="lower",
                   zorder=zorder, interpolation="bilinear")
    _clip_to(ax, im, path)


def glow(ax, path: Path, *, blur: float = 2.2, color=None, alpha: float = 0.5,
         zorder: int = 8, px_per_mm: float | None = None):
    """Outer halo, used sparingly to make the enzyme the focal point."""
    px_per_mm = px_per_mm or PX_PER_MM
    color = color or P["hero"]
    x0, y0, x1, y1 = path.get_extents().extents
    pad = 4 * blur + 2
    x0, y0, x1, y1 = x0 - pad, y0 - pad, x1 + pad, y1 + pad
    m = _mask(path, x0, y0, x1, y1, px_per_mm)
    h = gaussian_filter(m, sigma=blur * px_per_mm)
    h = np.clip(h - m, 0, 1)
    rgba = np.zeros(m.shape + (4,))
    rgba[..., :3] = to_rgb(color)
    rgba[..., 3] = h * alpha
    ax.imshow(rgba, extent=(x0, x1, y0, y1), origin="lower",
              zorder=zorder, interpolation="bilinear")


def blur_layer(ax, mask: np.ndarray, extent, *, blur_px: float, color,
               alpha: float = 0.3, zorder: int = 5, subtract=None, dx=0.0, dy=0.0):
    """Paint a blurred mask as a coloured layer.  Used for shadows and glows
    built from an arbitrary silhouette rather than a single path."""
    h = gaussian_filter(np.clip(mask, 0, 1), sigma=blur_px)
    if subtract is not None:
        h = np.clip(h - subtract, 0, 1)
    rgba = np.zeros(h.shape + (4,))
    rgba[..., :3] = to_rgb(color)
    rgba[..., 3] = h * alpha
    x0, x1, y0, y1 = extent
    ax.imshow(rgba, extent=(x0 + dx, x1 + dx, y0 + dy, y1 + dy),
              origin="lower", zorder=zorder, interpolation="bilinear")


def polygon_union_mask(polys, extent, px_per_mm: float | None = None):
    """Rasterised union of many polygons, for silhouette effects."""
    px_per_mm = px_per_mm or PX_PER_MM
    x0, x1, y0, y1 = extent
    nx = max(int((x1 - x0) * px_per_mm), 8)
    ny = max(int((y1 - y0) * px_per_mm), 8)
    gx, gy = np.meshgrid(np.linspace(x0, x1, nx), np.linspace(y0, y1, ny))
    pts = np.column_stack([gx.ravel(), gy.ravel()])
    acc = np.zeros(nx * ny, dtype=bool)
    for p in polys:
        acc |= Path(np.asarray(p)).contains_points(pts)
    return acc.reshape(ny, nx).astype(float)


def stroke(ax, path: Path, color=None, lw: float = 0.5, alpha: float = 1.0,
           zorder: int = 20, ls: str = "-", cap: str = "round"):
    pp = PathPatch(path, facecolor="none", edgecolor=color or P["ink"],
                   linewidth=lw, alpha=alpha, zorder=zorder, linestyle=ls,
                   capstyle=cap, joinstyle="round")
    ax.add_patch(pp)
    return pp


def fill(ax, path: Path, color, alpha: float = 1.0, zorder: int = 10,
         ec="none", lw: float = 0.0):
    pp = PathPatch(path, facecolor=color, edgecolor=ec, linewidth=lw,
                   alpha=alpha, zorder=zorder, joinstyle="round")
    ax.add_patch(pp)
    return pp


# --------------------------------------------------------------------------- #
# Arrows
# --------------------------------------------------------------------------- #
def _bezier(p0, p1, p2, n=120):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2 = map(np.asarray, (p0, p1, p2))
    return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2


def taper_arrow(ax, p0, p2, *, bow: float = 0.0, w0: float = 0.5,
                w1: float = 1.1, head_l: float = 2.6, head_w: float = 2.6,
                color=None, alpha: float = 1.0, zorder: int = 50,
                taper_from: float = 0.0):
    """Quadratic-bezier arrow whose shaft widens along its length.

    A tapered shaft carries direction even before the reader sees the head,
    which keeps the pathway legible when the figure is shrunk to column width.
    """
    color = color or P["ink"]
    p0, p2 = np.asarray(p0, float), np.asarray(p2, float)
    mid = (p0 + p2) / 2
    d = p2 - p0
    nvec = np.array([-d[1], d[0]])
    nvec = nvec / (np.linalg.norm(nvec) + 1e-9)
    p1 = mid + nvec * bow

    curve = _bezier(p0, p1, p2, 160)
    seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(curve, axis=0), axis=1))]
    total = seg[-1]
    if total <= head_l * 1.2:
        head_l = total * 0.5
    keep = seg <= (total - head_l)
    shaft = curve[keep]
    if len(shaft) < 3:
        shaft = curve[:3]
    s = seg[keep] / max(total - head_l, 1e-9)
    s = np.clip((s - taper_from) / max(1 - taper_from, 1e-9), 0, 1)
    halfw = (w0 + (w1 - w0) * s) / 2

    tang = np.gradient(shaft, axis=0)
    tang /= (np.linalg.norm(tang, axis=1)[:, None] + 1e-9)
    nrm = np.column_stack([-tang[:, 1], tang[:, 0]])
    left = shaft + nrm * halfw[:, None]
    right = shaft - nrm * halfw[:, None]

    tip = curve[-1]
    base = shaft[-1]
    bdir = tip - base
    bdir /= (np.linalg.norm(bdir) + 1e-9)
    bn = np.array([-bdir[1], bdir[0]])
    head = np.array([base + bn * head_w / 2, tip, base - bn * head_w / 2])

    poly = np.vstack([left, head, right[::-1]])
    ax.add_patch(PathPatch(Path(poly), facecolor=color, edgecolor="none",
                           alpha=alpha, zorder=zorder, joinstyle="round"))
    return curve


def inhibit_arrow(ax, p0, p2, *, bow: float = 0.0, w: float = 0.7,
                  bar: float = 2.4, color=None, alpha: float = 1.0,
                  zorder: int = 50):
    """Blunt-ended inhibition connector (the T-bar)."""
    color = color or P["warn"]
    p0, p2 = np.asarray(p0, float), np.asarray(p2, float)
    mid = (p0 + p2) / 2
    d = p2 - p0
    nvec = np.array([-d[1], d[0]])
    nvec /= (np.linalg.norm(nvec) + 1e-9)
    p1 = mid + nvec * bow
    curve = _bezier(p0, p1, p2, 80)
    ax.add_patch(PathPatch(Path(curve), facecolor="none", edgecolor=color,
                           linewidth=w, alpha=alpha, zorder=zorder,
                           capstyle="round"))
    tip = curve[-1]
    bdir = curve[-1] - curve[-6]
    bdir /= (np.linalg.norm(bdir) + 1e-9)
    bn = np.array([-bdir[1], bdir[0]])
    ax.plot(*np.column_stack([tip + bn * bar / 2, tip - bn * bar / 2]),
            color=color, lw=w * 1.5, alpha=alpha, zorder=zorder,
            solid_capstyle="round")


# --------------------------------------------------------------------------- #
# Type
# --------------------------------------------------------------------------- #
def text(ax, x, y, s, *, size="label", weight="normal", color=None,
         ha="left", va="center", zorder: int = 75, alpha: float = 1.0,
         style="normal", rotation: float = 0.0, linespacing: float = 1.25):
    return ax.text(x, y, s,
                   fontsize=TYPE.get(size, size) if isinstance(size, str) else size,
                   fontweight=weight, color=color or P["ink"], ha=ha, va=va,
                   zorder=zorder, alpha=alpha, style=style, rotation=rotation,
                   linespacing=linespacing)


def tracked(s: str, space: str = " ") -> str:
    """Poor-man's letterspacing for small-caps zone headings."""
    return space.join(s)


def panel_label(ax, x, y, letter, *, color=None):
    text(ax, x, y, letter, size=TYPE["zone"] + 1.2, weight="bold",
         color=color or P["ink"], ha="left", va="center", zorder=80)
