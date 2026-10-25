"""Fail loudly on overlapping or out-of-canvas text.

A figure that compiles is not a figure that is readable.  Matplotlib will
happily draw two labels on top of each other and report success.

Rotated text is the reason this does real geometry rather than comparing
bounding boxes.  `get_window_extent` returns the axis-aligned box of a rotated
label, which for text at 60 degrees is roughly twice the area the glyphs
actually occupy, so an AABB test reports collisions that are not there.  Each
label is therefore measured unrotated, rotated about its own anchor, and the
resulting quadrilaterals are clipped against each other for a true overlap area.

    py -3.11 check_overlaps.py my_figure:build [--pad 0.25]

The argument is "module:function"; the function must return (fig, anything) and
the figure's first axes must be the millimetre canvas.

Exit status is 1 if anything is reported, so it can gate a build.
"""
from __future__ import annotations

import argparse
import itertools
import pathlib
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")

sys.path.insert(0, str(pathlib.Path.cwd()))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HA_OFF = {"left": 0.0, "center": -0.5, "right": -1.0}
VA_OFF = {"baseline": 0.0, "bottom": 0.0, "center": -0.5,
          "center_baseline": -0.5, "top": -1.0}


def text_quads_mm(fig, ax):
    """Every visible Text artist as (label, 4x2 array of mm corners)."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    inv = ax.transData.inverted()
    out = []
    for a in fig.findobj(matplotlib.text.Text):
        if not a.get_visible():
            continue
        s = a.get_text()
        if not s or not s.strip():
            continue
        rot = float(a.get_rotation())
        try:
            a.set_rotation(0)
            bb = a.get_window_extent(renderer=renderer)
            a.set_rotation(rot)
        except Exception:
            a.set_rotation(rot)
            continue
        w, h = bb.width, bb.height
        if w <= 0 or h <= 0:
            continue
        try:
            ax_, ay_ = a.get_transform().transform(a.get_position())
        except Exception:
            continue
        dx = HA_OFF.get(a.get_ha(), -0.5) * w
        dy = VA_OFF.get(a.get_va(), -0.5) * h
        corners = np.array([[dx, dy], [dx + w, dy], [dx + w, dy + h], [dx, dy + h]])
        th = np.deg2rad(rot)
        R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
        disp = corners @ R.T + np.array([ax_, ay_])
        out.append((s.replace("\n", " / ")[:44], inv.transform(disp)))
    return out


def _inflate(q, pad):
    c = q.mean(axis=0)
    v = q - c
    n = np.linalg.norm(v, axis=1, keepdims=True)
    return c + v * (1.0 + pad / np.maximum(n, 1e-9))


def _clip(subject, clipper):
    """Sutherland-Hodgman: both quads are convex, so this is exact."""
    out = list(subject)
    cc = clipper.mean(axis=0)
    for i in range(len(clipper)):
        a, b = clipper[i], clipper[(i + 1) % len(clipper)]
        e = b - a
        normal = np.array([-e[1], e[0]])
        if np.dot(normal, cc - a) < 0:
            normal = -normal
        inside = lambda p: np.dot(normal, p - a) >= -1e-12
        src, out = out, []
        for j in range(len(src)):
            p, q = src[j], src[(j + 1) % len(src)]
            pin, qin = inside(p), inside(q)
            if pin:
                out.append(p)
            if pin != qin:
                d = np.dot(normal, q - p)
                if abs(d) > 1e-12:
                    t = np.dot(normal, a - p) / d
                    out.append(p + t * (q - p))
        if not out:
            return []
    return out


def _area(poly):
    if len(poly) < 3:
        return 0.0
    p = np.asarray(poly)
    return abs(np.dot(p[:, 0], np.roll(p[:, 1], -1))
               - np.dot(p[:, 1], np.roll(p[:, 0], -1))) / 2.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pad", type=float, default=0.25)
    ap.add_argument("--min-area", type=float, default=0.40)
    ap.add_argument("target", help='module:function, e.g. my_figure:build')
    args = ap.parse_args()

    mod_name, _, fn_name = args.target.partition(":")
    import importlib
    mod = importlib.import_module(mod_name)
    build = getattr(mod, fn_name or "build")

    result = build()
    fig = result[0] if isinstance(result, tuple) else result
    ax = fig.axes[0]
    cw, ch = (v * 25.4 for v in fig.get_size_inches())
    quads = text_quads_mm(fig, ax)

    problems = []
    for (sa, qa), (sb, qb) in itertools.combinations(quads, 2):
        area = _area(_clip(_inflate(qa, args.pad), qb))
        if area >= args.min_area:
            problems.append(f"OVERLAP {area:6.1f} mm^2  '{sa}'  x  '{sb}'")

    for s, q in quads:
        if q[:, 0].min() < -0.5 or q[:, 1].min() < -0.5 \
                or q[:, 0].max() > cw + 0.5 or q[:, 1].max() > ch + 0.5:
            problems.append(
                f"OFF-CANVAS      '{s}'  "
                f"[{q[:, 0].min():.1f},{q[:, 1].min():.1f} to "
                f"{q[:, 0].max():.1f},{q[:, 1].max():.1f}]")

    print(f"{len(quads)} text objects checked, canvas {cw:.0f} x {ch:.0f} mm")
    if problems:
        print(f"{len(problems)} problem(s):")
        for p in sorted(problems):
            print("  " + p)
        return 1
    print("no overlapping or off-canvas text")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
