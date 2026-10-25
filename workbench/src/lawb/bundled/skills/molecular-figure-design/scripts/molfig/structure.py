"""Protein structure to vector cartoon ribbon, in pure Python.

PyMOL is the usual tool here, but it is a heavy install and it rasterises; this
module instead fetches a PDB entry, extracts the C-alpha trace and any bound
ligands, assigns secondary structure, and emits a depth-shaded ribbon as real
matplotlib paths.  The result stays vector in the exported PDF/SVG and needs
nothing beyond numpy/scipy/matplotlib.

If PyMOL *is* available, `render_with_pymol()` writes an equivalent raster
instead; the layout code does not care which produced the asset.

Everything is drawn in the figure's own millimetre coordinate system, so a
structure is placed by giving it a box, exactly like any other panel.
"""
from __future__ import annotations

import pathlib
import warnings

import numpy as np
from matplotlib.patches import PathPatch
from matplotlib.path import Path

from . import style as S

RCSB = "https://files.rcsb.org/download/{pdb}.pdb"
CACHE = pathlib.Path(__file__).resolve().parent.parent / "cache"


# --------------------------------------------------------------------------- #
# Fetch and parse
# --------------------------------------------------------------------------- #
def fetch_pdb(pdb_id: str = "1CRN", cache_dir: pathlib.Path | None = None) -> pathlib.Path:
    """Download a PDB entry once and cache it next to the project."""
    cache_dir = pathlib.Path(cache_dir or CACHE)
    cache_dir.mkdir(parents=True, exist_ok=True)
    dest = cache_dir / f"{pdb_id.upper()}.pdb"
    if dest.exists() and dest.stat().st_size > 10_000:
        return dest
    import requests
    r = requests.get(RCSB.format(pdb=pdb_id.upper()), timeout=90)
    r.raise_for_status()
    dest.write_bytes(r.content)
    return dest


def parse_pdb(path: pathlib.Path, chain: str = "auto"):
    """Return (ca_xyz, residue_numbers, hetero_atoms, chain_id).

    hetero_atoms maps residue name -> (N,3) coordinates, for cofactor/ligand.
    Only the first model is read; altloc B+ is skipped.

    chain="auto" takes the chain with the most C-alpha atoms, because the
    polymer is not always chain A (1ZUA, for one, starts at B).
    """
    lines = []
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line[:6] == "ENDMDL":
                break
            lines.append(line)

    if chain == "auto":
        tally: dict[str, int] = {}
        for line in lines:
            if line[:6] == "ATOM  " and line[12:16].strip() == "CA":
                tally[line[21]] = tally.get(line[21], 0) + 1
        if not tally:
            raise ValueError(f"no CA atoms at all in {path}")
        chain = max(tally, key=tally.get)

    ca, resi = [], []
    het: dict[str, list] = {}
    for line in lines:
        rec = line[:6]
        if rec == "ATOM  ":
            if line[21] != chain or line[16] not in (" ", "A"):
                continue
            if line[12:16].strip() == "CA":
                ca.append((float(line[30:38]), float(line[38:46]), float(line[46:54])))
                resi.append(int(line[22:26]))
        elif rec == "HETATM":
            if line[21] not in (chain, " "):
                continue
            name = line[17:20].strip()
            if name in ("HOH", "DOD"):
                continue
            het.setdefault(name, []).append(
                (float(line[30:38]), float(line[38:46]), float(line[46:54])))
    if not ca:
        raise ValueError(f"no CA atoms for chain {chain} in {path}")
    return (np.asarray(ca, float), np.asarray(resi, int),
            {k: np.asarray(v, float) for k, v in het.items()}, chain)


# --------------------------------------------------------------------------- #
# Secondary structure, from geometry alone
# --------------------------------------------------------------------------- #
def assign_ss(ca: np.ndarray) -> np.ndarray:
    """Per-residue 'H' / 'E' / 'C' from CA-CA distances.

    A full DSSP run needs backbone N/O and hydrogen bonding; for a cartoon the
    i->i+3 and i->i+4 distance signature separates helix from strand well
    enough, and errors cost at most one ribbon segment of visual noise.
    """
    n = len(ca)
    ss = np.full(n, "C", dtype="<U1")
    d3 = np.full(n, np.nan)
    d4 = np.full(n, np.nan)
    d2 = np.full(n, np.nan)
    d3[:n - 3] = np.linalg.norm(ca[3:] - ca[:-3], axis=1)
    d4[:n - 4] = np.linalg.norm(ca[4:] - ca[:-4], axis=1)
    d2[:n - 2] = np.linalg.norm(ca[2:] - ca[:-2], axis=1)

    helix = (d3 > 4.6) & (d3 < 6.6) & (d4 > 5.4) & (d4 < 7.6)
    strand = (d2 > 6.2) & (d3 > 9.0) & (d4 > 11.5)

    def runs(mask, min_len, char):
        i = 0
        while i < n:
            if mask[i]:
                j = i
                while j < n and mask[j]:
                    j += 1
                if j - i >= min_len:
                    ss[i:min(j + 3, n)] = char
                i = j
            else:
                i += 1

    runs(helix, 4, "H")
    runs(strand & (ss == "C"), 2, "E")
    return ss


# --------------------------------------------------------------------------- #
# Orientation and projection
# --------------------------------------------------------------------------- #
def project(ca: np.ndarray, *, roll: float = 0.0, tilt: float = 0.0,
            spin: float = 0.0, extra: dict | None = None):
    """PCA-align then rotate; return 2D coords plus depth.

    PCA puts the widest face of the TIM barrel in the picture plane, which is
    usually the view that most looks like the fold.  roll/tilt/spin are degrees
    for hand-tuning.
    """
    c = ca.mean(0)
    X = ca - c
    _, _, vt = np.linalg.svd(X, full_matrices=False)
    basis = vt[:3]
    if np.linalg.det(basis) < 0:
        basis[2] *= -1

    def rot(axis, deg):
        a = np.deg2rad(deg)
        ca_, sa = np.cos(a), np.sin(a)
        if axis == "x":
            return np.array([[1, 0, 0], [0, ca_, -sa], [0, sa, ca_]])
        if axis == "y":
            return np.array([[ca_, 0, sa], [0, 1, 0], [-sa, 0, ca_]])
        return np.array([[ca_, -sa, 0], [sa, ca_, 0], [0, 0, 1]])

    M = rot("z", spin) @ rot("x", tilt) @ rot("y", roll) @ basis
    out = X @ M.T
    extra_out = {k: (v - c) @ M.T for k, v in (extra or {}).items()}
    return out[:, :2], out[:, 2], extra_out


def fit_box(xy: np.ndarray, depth: np.ndarray, box, extra=None, pad: float = 0.0):
    """Scale/translate projected coords into a target (x, y, w, h) mm box."""
    bx, by, bw, bh = box
    x0, y0 = xy.min(0)
    x1, y1 = xy.max(0)
    s = min((bw - 2 * pad) / max(x1 - x0, 1e-9), (bh - 2 * pad) / max(y1 - y0, 1e-9))
    ox = bx + (bw - (x1 - x0) * s) / 2 - x0 * s
    oy = by + (bh - (y1 - y0) * s) / 2 - y0 * s
    f2 = lambda p: np.column_stack([p[:, 0] * s + ox, p[:, 1] * s + oy])
    f3 = lambda p: np.column_stack([p[:, 0] * s + ox, p[:, 1] * s + oy, p[:, 2] * s])
    out_extra = {k: f3(v) for k, v in (extra or {}).items()}
    return f2(xy), depth * s, s, out_extra


# --------------------------------------------------------------------------- #
# Ribbon geometry
# --------------------------------------------------------------------------- #
def _smooth_by_ss(ca2: np.ndarray, ss: np.ndarray) -> np.ndarray:
    """Collapse helical coils onto the helix axis; leave loops alone.

    Cartoon renderers draw the helix *axis*, not the CA spiral.  A 5-residue
    running mean cancels the 3.6-residue helical repeat, which is why the output
    reads as a ribbon rather than a corkscrew.
    """
    out = ca2.astype(float).copy()
    n = len(out)
    for win, char in ((2, "H"), (1, "E")):
        idx = np.flatnonzero(ss == char)
        for i in idx:
            lo, hi = max(0, i - win), min(n, i + win + 1)
            out[i] = ca2[lo:hi].mean(0)
    return out


def _resample(pts: np.ndarray, per_seg: int = 5):
    """Smooth spline through control points, `per_seg` samples per residue."""
    from scipy.interpolate import splprep, splev
    n = len(pts)
    if n < 2:
        return pts.copy()
    k = min(3, n - 1)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        tck, _ = splprep([pts[:, i] for i in range(pts.shape[1])], s=0, k=k)
        u = np.linspace(0, 1, max(n * per_seg, 6))
        out = splev(u, tck)
    return np.column_stack(out)


def _curvature_limit(xy: np.ndarray, hw: np.ndarray, factor: float = 0.72):
    """Clamp ribbon half-width to the local radius of curvature.

    Without this, a turn tighter than the ribbon is wide folds the offset edge
    through itself and renders as a triangular fan.
    """
    p0, p1, p2 = xy[:-2], xy[1:-1], xy[2:]
    a = np.linalg.norm(p1 - p0, axis=1)
    b = np.linalg.norm(p2 - p1, axis=1)
    c = np.linalg.norm(p2 - p0, axis=1)
    area = np.abs(np.cross(p1 - p0, p2 - p0)) / 2
    R = np.where(area > 1e-12, a * b * c / (4 * area + 1e-12), 1e6)
    R = np.r_[R[0], R, R[-1]]
    return np.minimum(hw, factor * R)


# relative half-widths, in Angstrom, before the mm scale factor
HALF_WIDTH = {"H": 1.15, "E": 1.00, "C": 0.30}


def ss_elements(ss: np.ndarray):
    """Contiguous runs of secondary structure, each overlapping its neighbour
    by one residue so the ribbon has no gaps at the joins."""
    runs, i, n = [], 0, len(ss)
    while i < n:
        j = i
        while j < n and ss[j] == ss[i]:
            j += 1
        runs.append((max(i - 1, 0), min(j + 1, n), ss[i]))
        i = j
    return runs


def ribbon_elements(xy: np.ndarray, depth: np.ndarray, ss: np.ndarray, *,
                    scale: float, per_seg: int = 5):
    """Build one closed polygon per secondary-structure element.

    Returns (polygon_or_polyline, mean_depth, ss_char, half_width) depth-sorted
    far-to-near, so near loops correctly occlude the barrel behind them.
    """
    xyz = np.column_stack([_smooth_by_ss(xy, ss), depth])
    out = []
    for i0, i1, char in ss_elements(ss):
        chunk = xyz[i0:i1]
        if len(chunk) < 2:
            continue
        dense = _resample(chunk, per_seg)
        pts, dep = dense[:, :2], dense[:, 2]

        if char == "C":                      # loops stay as tubes, not ribbons
            out.append((pts, float(dep.mean()), char, HALF_WIDTH["C"] * scale))
            continue

        hw = np.full(len(pts), HALF_WIDTH[char] * scale)
        if char == "E":                      # arrowhead on the last ~2 residues
            k = max(len(pts) - 2 * per_seg, 1)
            hw[k:] = np.linspace(HALF_WIDTH["E"] * 1.55 * scale, 0.04 * scale,
                                 len(pts) - k)
        hw = _curvature_limit(pts, hw)

        tang = np.gradient(pts, axis=0)
        tang /= (np.linalg.norm(tang, axis=1)[:, None] + 1e-9)
        nrm = np.column_stack([-tang[:, 1], tang[:, 0]])
        left = pts + nrm * hw[:, None]
        right = pts - nrm * hw[:, None]
        poly = np.vstack([left, right[::-1]])
        out.append((poly, float(dep.mean()), char, float(hw.mean())))

    out.sort(key=lambda t: t[1])
    return out


def draw_ribbon(ax, elems, *, hue=None, deep=None, light=None,
                zorder: int = 40, lw: float = 0.10):
    """Paint elements back to front with depth-mapped colour.

    One polygon per element, stroked once, so there are no quad seams.
    """
    hue = hue or S.P["hero"]
    deep = deep or S.P["hero_deep"]
    light = light or S.P["hero_light"]
    d = np.array([e[1] for e in elems])
    lo, hi = d.min(), d.max()
    for k, (geom, dep, char, hw) in enumerate(elems):
        t = (dep - lo) / max(hi - lo, 1e-9)                 # 0 far, 1 near
        base = S.mix(deep, hue, 0.25 + 0.75 * t)
        if char == "C":
            col = S.mix(base, light, 0.10 + 0.25 * t)
            ax.plot(geom[:, 0], geom[:, 1], color=col, lw=max(hw * 5.1, 0.35),
                    solid_capstyle="round", solid_joinstyle="round",
                    zorder=zorder + k * 0.01, alpha=0.98)
        else:
            col = S.mix(base, light, (0.45 if char == "H" else 0.30) * t)
            ax.add_patch(PathPatch(Path(geom), facecolor=col,
                                   edgecolor=S.shade(col, 0.42), linewidth=lw,
                                   zorder=zorder + k * 0.01,
                                   joinstyle="round"))


def draw_cofactor(ax, pts: np.ndarray, *, scale: float, color=None,
                  zorder: int = 48, alpha: float = 0.96,
                  bond_cut: float = 1.85):
    """Draw a bound cofactor/ligand as ball-and-stick.

    Bonds come from a 3D distance cutoff, not from atom order: PDB atom order
    zigzags across the molecule and drawing it as a polyline looks like noise.
    """
    color = color or S.P["cofactor"]
    if len(pts) < 2:
        return
    cut = bond_cut * scale
    d = np.linalg.norm(pts[:, None, :] - pts[None, :, :], axis=-1)
    i, j = np.where(np.triu(d, 1) < cut)
    # atom radius set in millimetres, then converted to the points matplotlib
    # wants, so the cofactor stays in scale whatever box the enzyme is drawn in
    r_pt = (0.50 * scale) * 72.0 / 25.4
    for a, b in zip(i, j):
        ax.plot(pts[[a, b], 0], pts[[a, b], 1], color=S.shade(color, 0.22),
                lw=max(0.22, r_pt * 0.52), alpha=0.85,
                zorder=zorder, solid_capstyle="round")
    ax.scatter(pts[:, 0], pts[:, 1], s=max(r_pt ** 2 * 3.1416, 0.9),
               c=[color], edgecolors=S.shade(color, 0.45), linewidths=0.14,
               zorder=zorder + 1, alpha=alpha)


# --------------------------------------------------------------------------- #
# One-call asset
# --------------------------------------------------------------------------- #
def place_enzyme(ax, box, *, pdb_id: str, chain: str = "auto",
                 roll: float = 0.0, tilt: float = 0.0, spin: float = 0.0,
                 ligands=("NAP", "NDP", "STR"), halo: bool = True,
                 zorder: int = 40, hue=None, lw: float = 0.10):
    """Fetch, orient, scale and draw the enzyme inside a (x, y, w, h) mm box.

    Returns a dict with the projected coordinates, so callers can anchor
    annotations (active site, cofactor) to real atom positions.
    """
    path = fetch_pdb(pdb_id)
    ca, resi, het, chain = parse_pdb(path, chain=chain)
    want = {k: v for k, v in het.items() if k in ligands}
    xy, depth, extra = project(ca, roll=roll, tilt=tilt, spin=spin, extra=want)
    xy, depth, scale, extra = fit_box(xy, depth, box, extra=extra, pad=0.6)

    ss = assign_ss(ca)
    elems = ribbon_elements(xy, depth, ss, scale=scale)

    hue = hue or S.P["hero"]
    if halo:
        polys = [g for g, _, c, _ in elems if c != "C"]
        pad = 5.0
        ext = (xy[:, 0].min() - pad, xy[:, 0].max() + pad,
               xy[:, 1].min() - pad, xy[:, 1].max() + pad)
        ppm = S.PX_PER_MM
        m = S.polygon_union_mask(polys, ext, ppm)
        S.blur_layer(ax, m, ext, blur_px=1.0 * ppm, color=S.P["ink"],
                     alpha=0.22, zorder=zorder - 5, dx=0.4, dy=-0.6)
        S.blur_layer(ax, m, ext, blur_px=2.0 * ppm, color=hue,
                     alpha=0.30, zorder=zorder - 4, subtract=m)

    draw_ribbon(ax, elems, hue=hue, deep=S.shade(hue, 0.55),
                light=S.tint(hue, 0.70), zorder=zorder, lw=lw)
    for name, pts in extra.items():
        col = S.P["cofactor"] if name in ("NAP", "NDP") else S.P["chemo"]
        draw_cofactor(ax, pts, scale=scale, color=col, zorder=zorder + 8)

    return {"xy": xy, "depth": depth, "ss": ss, "resi": resi,
            "ligands": extra, "scale": scale, "pdb": pdb_id,
            "elements": elems, "chain": chain, "n_res": len(ca)}


# --------------------------------------------------------------------------- #
# Optional PyMOL route (unused unless PyMOL is importable)
# --------------------------------------------------------------------------- #
def render_with_pymol(pdb_id: str, out: str = "cache/akr_pymol.png",
                      width: int = 2400, height: int = 2000):
    """Render the same entry with PyMOL if it is installed.

    Kept so the pipeline can upgrade to ray-traced cartoons on a machine with
    open-source PyMOL, without any layout change.
    """
    from pymol import cmd                                   # noqa: PLC0415
    cmd.reinitialize()
    cmd.fetch(pdb_id, async_=0)
    cmd.hide("everything")
    cmd.show("cartoon", "polymer")
    cmd.show("sticks", "resn NAP+NDP+HPR")
    cmd.set("cartoon_transparency", 0.0)
    cmd.set("ray_opaque_background", 0)
    cmd.set("antialias", 2)
    cmd.spectrum("b", "teal white", "polymer")
    cmd.orient("polymer")
    cmd.ray(width, height)
    cmd.png(out, dpi=600)
    return out
