"""Check that a PDB entry contains what you think it does, before you cite it.

A PDB ID is a claim about a molecule, and a figure caption repeats that claim to
every reader. IDs get copied between papers, entries get superseded, and titles
and deposited ligands do not always agree. This fetches each entry and prints
what the file itself says: the molecule name from COMPND, the chain with the
most residues, and every ligand with the chemical name from its own HETNAM
record.

    py -3.11 verify_pdb.py 1CRN 4HHB
    py -3.11 verify_pdb.py --expect "1CRN=CRAMBIN" "4HHB=HEMOGLOBIN"

With --expect, exits non-zero if any entry's COMPND does not contain the
expected substring (case-insensitive), so it can gate a build.

A real example of why this matters: an entry whose title described a complex
with a reduced steroid product turned out to have the unreduced substrate as
its deposited ligand. The figure caption had to state what the coordinates
contained, not what the title said.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

CACHE = pathlib.Path("pdb_cache")
RCSB = "https://files.rcsb.org/download/{pdb}.pdb"
SOLVENT = {"HOH", "DOD", "GOL", "EDO", "SO4", "PO4", "ACT", "DMS", "MPD",
           "PEG", "CL", "NA", "K", "MG", "CA", "ZN", "BME", "TRS", "IMD"}


def fetch(pdb_id: str, cache: pathlib.Path) -> str:
    cache.mkdir(parents=True, exist_ok=True)
    dest = cache / f"{pdb_id.upper()}.pdb"
    if dest.exists() and dest.stat().st_size > 5000:
        return dest.read_text(encoding="utf-8", errors="replace")
    import requests
    r = requests.get(RCSB.format(pdb=pdb_id.upper()), timeout=90)
    r.raise_for_status()
    dest.write_bytes(r.content)
    return r.text


def describe(pdb_id: str, text: str) -> dict:
    mol = re.search(r"COMPND   \d MOLECULE: (.+?);", text)
    title = " ".join(l[10:].strip() for l in text.splitlines()
                     if l.startswith("TITLE "))
    hetnam: dict[str, str] = {}
    for line in text.splitlines():
        if line.startswith("HETNAM"):
            code = line[11:14].strip()
            hetnam[code] = (hetnam.get(code, "") + " " + line[15:].strip()).strip()
    chains: dict[str, set] = {}
    ligands: dict[str, int] = {}
    for line in text.splitlines():
        if line.startswith("ENDMDL"):
            break
        if line.startswith("ATOM  ") and line[12:16].strip() == "CA":
            chains.setdefault(line[21], set()).add(line[22:27])
        elif line.startswith("HETATM"):
            name = line[17:20].strip()
            if name not in SOLVENT:
                ligands[name] = ligands.get(name, 0) + 1
    best = max(chains, key=lambda c: len(chains[c])) if chains else "?"
    return {
        "id": pdb_id.upper(),
        "molecule": mol.group(1) if mol else "(no COMPND MOLECULE record)",
        "title": title,
        "chain": best,
        "residues": len(chains.get(best, ())),
        "ligands": {k: (hetnam.get(k, "(no HETNAM record)"), v)
                    for k, v in sorted(ligands.items())},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ids", nargs="*", help="PDB IDs")
    ap.add_argument("--expect", nargs="*", default=[],
                    help='pairs like "1CRN=CRAMBIN"')
    ap.add_argument("--cache", default=str(CACHE))
    args = ap.parse_args()

    expect = {}
    for pair in args.expect:
        if "=" not in pair:
            raise SystemExit(f"--expect needs ID=SUBSTRING, got {pair!r}")
        k, v = pair.split("=", 1)
        expect[k.upper()] = v
    ids = [i.upper() for i in args.ids] or list(expect)
    if not ids:
        raise SystemExit("give at least one PDB ID")

    failures = 0
    for pdb_id in ids:
        try:
            info = describe(pdb_id, fetch(pdb_id, pathlib.Path(args.cache)))
        except Exception as exc:
            print(f"{pdb_id}  FETCH FAILED: {exc}")
            failures += 1
            continue
        print(f"\n{info['id']}  chain {info['chain']}, {info['residues']} residues")
        print(f"  molecule : {info['molecule']}")
        print(f"  title    : {info['title'][:150]}")
        if info["ligands"]:
            print("  ligands  :")
            for code, (name, n) in info["ligands"].items():
                print(f"      {code:4s} {n:4d} atoms  {name[:60]}")
        else:
            print("  ligands  : none (apo, or all filtered as solvent)")
        want = expect.get(info["id"])
        if want and want.lower() not in info["molecule"].lower():
            print(f"  MISMATCH : expected {want!r} in the molecule name")
            failures += 1
    print()
    if failures:
        print(f"{failures} problem(s)")
        return 1
    print("all entries match" if expect else "done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
