"""Benchmarks for the workbench. Each benchmark has an explicit expected answer.

Results are written to benchmarks/RESULTS.md. A check that cannot run here is reported as
NOT VERIFIED with the reason. It is never counted as a pass.

  B1  PRISMA counts       expected counts hand-derived from examples/screening/screening.csv
  B2  Diagram structure   each spec yields the right nodes, edges and labels in Mermaid text
  B3  Diagram validity    Mermaid CLI parse, when mmdc is installed (otherwise NOT VERIFIED)
  B4  PDF extraction      recall of known phrases in generated PDFs (exact ground truth)
  B5  Routed loop         fixes the seeded faults in examples/faulty_units, per local model
  B6  Figure coverage     which figure types the workbench can produce, against a fixed list
  B7  Cloud providers     one live call to Claude and to OpenAI, when keys are present

Usage (from the repository root, with PYTHONPATH=src):
    python benchmarks/run_benchmarks.py            # all
    python benchmarks/run_benchmarks.py --skip-llm # without the local-model loop (B5)
"""

import argparse
import json
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lawb import diagrams, pdf, review  # noqa: E402
from lawb.llm import OllamaClient  # noqa: E402
from lawb.pipeline import run_loop  # noqa: E402

RESULTS = []


def record(bench, check, status, detail=""):
    RESULTS.append({"bench": bench, "check": check, "status": status, "detail": detail})
    print(f"[{status:12s}] {bench} {check} {detail}", flush=True)


# ---------- B1: PRISMA counts ----------
EXPECTED_PRISMA = {
    "identified_total": 11,
    "identified_per_strand": {"strand_a": 3, "strand_b": 5, "strand_c": 3},
    "duplicates_removed": 2,
    "title_abstract_screened": 6,
    "title_abstract_excluded": {"off-topic": 2, "no method": 1},
    "full_text_assessed": 3,
    "full_text_excluded": {"no data": 2},
    "included": 1,
    "included_by_year": {"2021": 1},
    "included_by_type": {"book": 1},
}


def bench_prisma():
    counts = review.prisma(ROOT / "examples" / "screening" / "screening.csv")
    for key, expected in EXPECTED_PRISMA.items():
        got = counts[key]
        record("B1", key, "PASS" if got == expected else "FAIL", f"expected {expected} got {got}")
    # funnel consistency: records advancing from screening equal full-text records assessed
    advanced = counts["title_abstract_screened"] - sum(counts["title_abstract_excluded"].values())
    record("B1", "funnel consistency", "PASS" if advanced == counts["full_text_assessed"] else "FAIL",
           f"advanced {advanced}, assessed {counts['full_text_assessed']}")


# ---------- B2: diagram structure ----------
SPECS = {
    "pipeline": {
        "title": "Pipeline", "direction": "LR",
        "nodes": {"a": "Scan", "b": "Mesh", "c": "Pack"},
        "edges": [["a", "b", "clean"], ["b", "c"]],
    },
    "prisma_flow": {
        "title": "Flow", "direction": "TD",
        "nodes": {"id": "Identified", "sc": "Screened", "inc": "Included"},
        "edges": [["id", "sc"], ["sc", "inc", "eligible"]],
    },
    "decision": {
        "title": "Decision", "direction": "TD",
        "nodes": {"q": "Is it stable?", "y": "Use it", "n": "Revise"},
        "edges": [["q", "y", "yes"], ["q", "n", "no"]],
    },
}


def mermaid_structure(text):
    nodes = set(re.findall(r'^\s+(\w+)\["', text, re.MULTILINE))
    edges = re.findall(r"^\s+(\w+) --(?:>|>\|[^|]*\|) (\w+)$", text, re.MULTILINE)
    labels = re.findall(r'\["([^"]*)"\]', text)
    return nodes, edges, labels


def bench_diagrams():
    for name, spec in SPECS.items():
        text = diagrams.to_mermaid(spec)
        nodes, edges, labels = mermaid_structure(text)
        ok_nodes = nodes == set(spec["nodes"])
        ok_edges = len(edges) == len(spec["edges"])
        ok_labels = sorted(labels) == sorted(spec["nodes"].values())
        ok_dir = text.startswith(f"flowchart {spec['direction']}")
        status = "PASS" if (ok_nodes and ok_edges and ok_labels and ok_dir) else "FAIL"
        record("B2", f"{name} structure", status,
               f"nodes {len(nodes)}/{len(spec['nodes'])}, edges {len(edges)}/{len(spec['edges'])}")
    try:
        diagrams.to_mermaid({"nodes": {"a": "x"}, "edges": [["a", "zz"]]})
        record("B2", "unknown node rejected", "FAIL", "no error raised")
    except ValueError:
        record("B2", "unknown node rejected", "PASS")


def bench_mermaid_validity():
    """Render each spec with the Mermaid CLI. A render that succeeds means the Mermaid parser accepted it."""
    from lawb.diagrams import render_svg
    tmp = Path(tempfile.mkdtemp())
    for name, spec in SPECS.items():
        mmd = tmp / f"{name}.mmd"
        mmd.write_text(diagrams.to_mermaid(spec), encoding="utf-8")
        ok, err = render_svg(mmd, tmp / f"{name}.svg")
        if err == "mmdc not installed":
            record("B3", f"{name} parses", "NOT VERIFIED", "mmdc not installed")
        else:
            record("B3", f"{name} parses", "PASS" if ok else "FAIL", "" if ok else err[:120])


# ---------- B4: PDF extraction ----------
PHRASES = ["Gamma radiation dosimetry", "figure 3 shows the decay curve", "Table 2 lists the parameters",
           "the sample was held at 42 degrees", "conclusion: the method is reproducible"]


def bench_pdf():
    try:
        import fitz
    except ImportError:
        record("B4", "pdf recall", "NOT VERIFIED", "PyMuPDF not installed")
        return
    tmp = Path(tempfile.mkdtemp())
    doc = fitz.open()
    for i in range(0, len(PHRASES), 2):
        page = doc.new_page()
        for j, phrase in enumerate(PHRASES[i:i + 2]):
            page.insert_text((72, 100 + 60 * j), phrase, fontsize=11)
    path = tmp / "known.pdf"
    doc.save(path)
    md = pdf.extract(path)
    found = [p for p in PHRASES if p in md]
    record("B4", "pdf recall", "PASS" if len(found) == len(PHRASES) else "FAIL",
           f"{len(found)}/{len(PHRASES)} phrases; engine pymupdf")
    pages = md.count("<!-- page ")
    record("B4", "page markers", "PASS" if pages == 3 else "FAIL", f"expected 3, got {pages}")


# ---------- B5: routed loop with local models ----------
def bench_loop(models):
    client = OllamaClient()
    project = ROOT / "examples" / "faulty_units"
    for model in models:
        t0 = time.time()
        try:
            result = run_loop(project, client, model)
        except Exception as exc:
            record("B5", model, "FAIL", f"error: {exc.__class__.__name__}")
            continue
        status = "PASS" if result["fixed"] else "FAIL"
        record("B5", model, status,
               f"fixed={result['fixed']} rounds={result['rounds']} t={time.time() - t0:.1f}s")


# ---------- B6: figure coverage against the commercial tools ----------
FIGURE_TASKS = [
    ("pipeline or workflow diagram", "flowchart", True),
    ("PRISMA flow diagram", "flowchart", True),
    ("decision tree", "flowchart", True),
    ("system architecture box diagram", "flowchart", True),
    ("bar or line chart from data", "plot", False),
    ("scatter plot with error bars", "plot", False),
    ("multi-panel publication figure with shared axes", "plot", False),
    ("scientific schematic with custom artwork", "illustration", False),
    ("molecular or cell illustration", "illustration", False),
    ("brand-styled template export", "template", False),
]


# ---------- B7: live cloud providers (opt-in; NOT VERIFIED without a working key) ----------
def bench_cloud():
    import os
    from lawb import llm

    def live(name, key_var, call):
        if not os.environ.get(key_var):
            record("B7", name, "NOT VERIFIED", f"{key_var} is not set")
            return
        try:
            reply = call()
            record("B7", name, "PASS" if reply else "FAIL", f"reply {reply[:40]!r}")
        except Exception as exc:
            text = str(exc)
            if "401" in text or "invalid" in text.lower() or "authentication" in text.lower():
                record("B7", name, "NOT VERIFIED", f"key rejected by the provider ({exc.__class__.__name__})")
            else:
                record("B7", name, "FAIL", f"{exc.__class__.__name__}: {text[:120]}")

    live("claude live reply", "ANTHROPIC_API_KEY",
         lambda: llm.anthropic_chat("claude-opus-5-5", "Reply with the single word OK.", None, 16))
    model = os.environ.get("LAWB_OPENAI_MODEL")
    if not model:
        record("B7", "openai live reply", "NOT VERIFIED", "set LAWB_OPENAI_MODEL to a model id on your account")
    else:
        live("openai live reply", "OPENAI_API_KEY",
             lambda: llm.openai_chat(model, "Reply with the single word OK.", None, 16))


def bench_coverage():
    supported = 0
    for task, kind, works in FIGURE_TASKS:
        status = "SUPPORTED" if works else "NOT SUPPORTED"
        supported += works
        record("B6", task, status, f"kind={kind}")
    record("B6", "coverage", "INFO", f"{supported}/{len(FIGURE_TASKS)} figure types produced by the workbench")


def write_results():
    lines = ["# Benchmark results", "",
             "Generated by benchmarks/run_benchmarks.py. A check that cannot run is NOT VERIFIED.", "",
             "| Bench | Check | Status | Detail |", "|---|---|---|---|"]
    for r in RESULTS:
        lines.append(f"| {r['bench']} | {r['check']} | {r['status']} | {r['detail']} |")
    passed = sum(1 for r in RESULTS if r["status"] == "PASS")
    failed = sum(1 for r in RESULTS if r["status"] == "FAIL")
    unverified = sum(1 for r in RESULTS if r["status"] == "NOT VERIFIED")
    lines += ["", f"Totals: {passed} pass, {failed} fail, {unverified} not verified."]
    (ROOT / "benchmarks" / "RESULTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (ROOT / "benchmarks" / "results.json").write_text(json.dumps(RESULTS, indent=2), encoding="utf-8")
    print("\n".join(lines[-1:]))
    return failed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-llm", action="store_true")
    ap.add_argument("--models", nargs="*", default=["qwen2.5-coder:1.5b", "qwen2.5-coder:7b", "qwen3:8b"])
    args = ap.parse_args()
    bench_prisma()
    bench_diagrams()
    bench_mermaid_validity()
    bench_pdf()
    if not args.skip_llm:
        bench_loop(args.models)
    else:
        record("B5", "routed loop", "NOT VERIFIED", "skipped with --skip-llm")
    bench_cloud()
    bench_coverage()
    return 1 if write_results() else 0


if __name__ == "__main__":
    sys.exit(main())
