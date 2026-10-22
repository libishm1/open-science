# -*- coding: utf-8 -*-
"""Version + backup helper for a manuscript.

  python snapshot.py --source paper.md save  "note"    snapshot the working source into versions/ with a note
  python snapshot.py bump  v3                          set the current version label (written into versions/VERSION)
  python snapshot.py list                              show every snapshot taken
  python snapshot.py backup <file> [<file> ...]        timestamped copy of any file into versions/backups/

--dir sets the versions folder (default: ./versions). Every snapshot is logged in versions/history.jsonl
with time, version, SHA-256 prefix, word count and note.

Build scripts can import backup() and call it on their outputs before overwriting them, so a build can
never destroy a previous deliverable (e.g. a DOCX someone has already commented on):
    import snapshot; snapshot.VER = "/path/to/versions"; snapshot.backup("Manuscript.docx")
(on import the folder defaults to ./versions relative to the current working directory)
Requires: standard library only.
"""
import argparse, os, sys, json, shutil, hashlib
from datetime import datetime

VER = os.path.abspath("versions")


def _paths():
    return os.path.join(VER, "backups"), os.path.join(VER, "history.jsonl"), os.path.join(VER, "VERSION")


def stamp(): return datetime.now().strftime("%Y-%m-%d_%H%M%S")
def version():
    vfile = _paths()[2]
    return open(vfile).read().strip() if os.path.exists(vfile) else "v0"
def digest(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:12]

def backup(path):
    """Timestamped copy of `path` into <versions>/backups/. Returns the backup path or None."""
    if not os.path.exists(path): return None
    bak = _paths()[0]
    os.makedirs(bak, exist_ok=True)
    b = os.path.basename(path)
    dst = os.path.join(bak, f"{stamp()}_{version()}_{b}")
    shutil.copy2(path, dst)
    return dst

def save(src, note=""):
    if not src or not os.path.exists(src):
        print("no working source found (give --source)"); return
    os.makedirs(VER, exist_ok=True)
    v = version()
    dst = os.path.join(VER, f"{v}_{stamp()}_{os.path.basename(src)}")
    shutil.copy2(src, dst)
    rec = dict(when=datetime.now().isoformat(timespec="seconds"), version=v,
               file=os.path.basename(dst), sha=digest(src),
               words=len(open(src, encoding="utf-8").read().split()), note=note)
    with open(_paths()[1], "a", encoding="utf-8") as fh: fh.write(json.dumps(rec) + "\n")
    print(f"snapshot {v}: {os.path.basename(dst)}  ({rec['words']} words, sha {rec['sha']})")
    if note: print(f"  note: {note}")

def show():
    log = _paths()[1]
    if not os.path.exists(log): print("no snapshots yet"); return
    print(f"{'when':20s} {'ver':5s} {'words':>6s} {'sha':12s} note")
    for line in open(log, encoding="utf-8"):
        r = json.loads(line)
        print(f"{r['when']:20s} {r['version']:5s} {r['words']:6d} {r['sha']:12s} {r.get('note','')}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", default="versions", help="versions folder (default: ./versions)")
    ap.add_argument("--source", help="working manuscript file (for save)")
    ap.add_argument("cmd", nargs="?", default="list", choices=["save", "bump", "list", "backup"])
    ap.add_argument("rest", nargs="*")
    args = ap.parse_args()
    VER = os.path.abspath(args.dir)
    if args.cmd == "save":   save(args.source, " ".join(args.rest))
    elif args.cmd == "bump":
        if not args.rest: sys.exit("bump needs a version label, e.g. v3")
        os.makedirs(VER, exist_ok=True)
        open(_paths()[2], "w").write(args.rest[0].strip())
        print("version is now", args.rest[0].strip())
    elif args.cmd == "backup":
        for f in args.rest:
            d = backup(f); print(("backed up -> " + os.path.basename(d)) if d else f"missing: {f}")
    else: show()
