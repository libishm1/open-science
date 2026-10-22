"""Dimensional-consistency check of every equation extracted from the literature.

Reads a JSONL of paper records (templates/SCHEMA.md). For each equation with a
`sympy` string of the form "lhs = rhs" (or "lhs <= rhs" / ">=" / "<" / ">") and a
`variables` map {symbol: unit-string}, substitutes SI units and checks that both
sides (and every additive term) share the same dimension.

Output: CSV with status PASS / EMPIRICAL / FAIL / SKIP (+ reason).
SKIP = not machine-checkable (no units, unparseable, operator notation). SKIP is not
an error, but equations used in a simulation must be PASS or have their coefficient
units added by hand.

Example: python -P check_equations.py data/papers.jsonl data/equations_checked.csv
Requires: sympy.
"""
import argparse, csv, json, re, sys
from pathlib import Path
import sympy as sp
from sympy.physics import units as u
from sympy.physics.units.systems.si import dimsys_SI

UNIT = {
    "": 1, "-": 1, "1": 1, "dimensionless": 1, "%": 1, "rad": 1, "deg": 1,
    "Pa": u.pascal, "kPa": u.pascal, "MPa": u.pascal, "GPa": u.pascal, "N": u.newton,
    "m": u.meter, "mm": u.meter, "cm": u.meter, "um": u.meter, "µm": u.meter,
    "s": u.second, "min": u.second, "h": u.second, "d": u.second,
    "kg": u.kilogram, "g": u.kilogram, "K": u.kelvin, "°C": u.kelvin, "C": u.kelvin,
    "J": u.joule, "W": u.watt, "mol": u.mole, "L": u.meter**3,
}
CLEAN = str.maketrans({"·": "*", "⋅": "*", "²": "^2", "³": "^3", "⁻": "^-", "¹": "1", "√": "sqrt"})


def parse_unit(s):
    """Unit string -> sympy expression of SI base units. None if unparseable."""
    if s is None:
        return None
    s = str(s).strip().translate(CLEAN)
    s = re.sub(r"[\[\]]", "", s).strip()
    if s.lower() in ("", "-", "dimensionless", "1", "%", "none", "rad", "deg", "n/a"):
        return sp.Integer(1)
    loc = {}
    def rep(m):
        t = m.group(0)
        if t not in UNIT:
            raise KeyError(t)
        name = "U_" + str(abs(hash(t)))
        loc[name] = UNIT[t]
        return name
    try:
        s2 = re.sub(r"[A-Za-z°µ]+", rep, s)
    except KeyError:
        return None
    s2 = re.sub(r"(?<=[\w\)])\s+(?=[\w\(])", "*", s2).replace("^", "**")
    try:
        return sp.sympify(s2, locals=loc)
    except Exception:
        return None


def dims(expr):
    from sympy.physics.units import Dimension
    from sympy.physics.units.systems import SI
    _, d = SI._collect_factor_and_dimension(expr)
    return dimsys_SI.get_dimensional_dependencies(d)


PRIMES = [37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83]


def check(eq):
    """PASS: all additive terms share one dimension.
    EMPIRICAL: mismatch only because numeric coefficients carry implicit units
               (e.g. E = 0.920*v_p - 62.018 with E in kPa, v_p in m/s): usable,
               but ONLY in the stated units.
    FAIL: genuine inconsistency with the units as recorded (check source).
    SKIP: not machine-checkable."""
    s = eq.get("sympy") or ""
    vars_ = eq.get("variables") or {}
    if not s or not vars_:
        return "SKIP", "no sympy string or variable units"
    if re.search(r"(?<![A-Za-z_])(grad|div|nabla|Sum|Integral|Derivative|diff|Function)\(", s):
        return "SKIP", "differential/summation operator notation - check by hand"
    m = re.split(r"<=|>=|==|=|<|>", s, maxsplit=1)
    if len(m) != 2:
        return "SKIP", "not an (in)equation"
    # dimensionless variables -> distinct test rationals (so phi/phi_m != 1)
    dimless = {k: sp.Rational(PRIMES[i % len(PRIMES)], 100)
               for i, k in enumerate(kk for kk, v in vars_.items() if parse_unit(v) == 1)}
    loc = {"exp": sp.exp, "log": sp.log, "ln": sp.log, "sqrt": sp.sqrt, "pi": sp.pi,
           "tanh": sp.tanh, "sin": sp.sin, "cos": sp.cos, "Abs": sp.Abs, "Rational": sp.Rational}
    subs = {}
    for k, v in vars_.items():
        sym = sp.Symbol(k, positive=True)
        loc[k] = sym
        if k in dimless:
            subs[sym] = dimless[k]
            continue
        vv = str(v)
        for dk, dv in dimless.items():
            vv = re.sub(r"\^\(?(-?)%s\)?" % re.escape(dk),
                        lambda mm: "^(%s%s)" % (mm.group(1), dv), vv)
        un = parse_unit(vv)
        if un is None:
            return "SKIP", f"unparsed unit '{v}' for {k}"
        subs[sym] = sp.Symbol(k + "_mag", positive=True) * un
    try:
        lhs = sp.sympify(m[0].replace("^", "**"), locals=loc)
        rhs = sp.sympify(m[1].replace("^", "**"), locals=loc)
    except Exception as e:
        return "SKIP", f"parse error: {e.__class__.__name__}"
    free = (lhs.free_symbols | rhs.free_symbols) - set(subs)
    if free:
        return "SKIP", "symbols without units: " + ",".join(sorted(map(str, free)))
    try:
        terms = []
        for side in (lhs, rhs):
            terms += list(sp.Add.make_args(sp.expand(side.subs(subs))))
        ds = []
        for t in terms:
            if t == 0:
                continue
            ds.append(dims(t))
        nonzero = [d for d in ds]
        if all(d == nonzero[0] for d in nonzero):
            return "PASS", str(nonzero[0])
        has_float = bool(re.search(r"\d\.\d|\de[-+]?\d", s))
        if has_float:
            return "EMPIRICAL", "numeric coefficients carry implicit units - use only in the units recorded"
        return "FAIL", f"term dimensions differ: {[str(x) for x in ds]}"
    except Exception as e:
        return "SKIP", f"dimension eval error: {e.__class__.__name__}: {e}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("papers", nargs="?", default="data/papers.jsonl", help="paper records, one JSON per line (default: data/papers.jsonl)")
    ap.add_argument("out", nargs="?", default="data/equations_checked.csv", help="output CSV (default: data/equations_checked.csv)")
    args = ap.parse_args()
    src, out = Path(args.papers), Path(args.out)
    rows = []
    for line in src.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        p = json.loads(line)
        for eq in p.get("equations") or []:
            st, why = check(eq)
            rows.append({"paper_id": p.get("id"), "doi": p.get("doi"), "name": eq.get("name"),
                         "latex": eq.get("latex"), "sympy": eq.get("sympy"),
                         "variables": json.dumps(eq.get("variables"), ensure_ascii=False),
                         "status": st, "detail": why})
    if not rows:
        sys.exit(f"no equations found in {src}")
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    from collections import Counter
    print(Counter(r["status"] for r in rows), "->", out)


if __name__ == "__main__":
    main()
