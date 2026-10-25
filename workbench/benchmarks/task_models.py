"""Which local model to use for which task, measured on this machine.

Three task groups, each with exact, checkable answers:
  math        six problems with one numeric answer each
  coding      three Python functions, each run against unit tests (temp folder, timeout, isolated mode)
  literature  field extraction from an abstract, a screening decision, and an honesty check
              (the model must refuse to invent a DOI for a paper that does not exist)

Writes benchmarks/task_models.json and benchmarks/TASK_MODELS.md.
Usage (PYTHONPATH=src): python benchmarks/task_models.py [--models m1 m2 ...]
"""

import argparse
import json
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lawb.llm import OllamaClient  # noqa: E402

MATH = [
    ("What is 17 multiplied by 23?", [391]),
    ("Solve for x: 3x + 7 = 34.", [9]),
    ("A stone block measures 2.4 m by 1.2 m by 0.8 m. What is its volume in cubic metres?", [2.304]),
    ("What is the sum of the integers from 1 to 100?", [5050]),
    ("What is the derivative of x^3 evaluated at x = 2?", [12]),
    ("Two fair six-sided dice are rolled. What is the probability that the sum is 7? Give a decimal.", [1 / 6]),
]

CODING = [
    ("is_palindrome(s)", "Return True if the string s reads the same forwards and backwards, ignoring case and any non-alphanumeric characters.",
     "assert is_palindrome('A man, a plan, a canal: Panama')\nassert not is_palindrome('stone')\nassert is_palindrome('')\n"),
    ("merge_intervals(intervals)", "Merge overlapping closed intervals given as a list of [start, end] pairs and return the merged list sorted by start.",
     "assert merge_intervals([[1,3],[2,6],[8,10],[15,18]]) == [[1,6],[8,10],[15,18]]\nassert merge_intervals([[1,4],[4,5]]) == [[1,5]]\nassert merge_intervals([]) == []\n"),
    ("mm_to_m(v)", "Convert a length v in millimetres to metres and return a float.",
     "assert abs(mm_to_m(2500) - 2.5) < 1e-12\nassert mm_to_m(0) == 0\n"),
]

ABSTRACT = ("In 2021 we surveyed 48 granite quarries using ground-penetrating radar at 250 MHz and compared "
            "fracture maps with drilled cores. Detection agreed with cores in 41 of 48 sites.")

LITERATURE = [
    ("extract", "Read the abstract and reply with JSON only, with keys year (integer), sites (integer), "
                "method (short string).\n\nAbstract: " + ABSTRACT),
    ("screen", "Inclusion criteria: field studies of rock fracture detection with a stated sample size. "
               "Exclusion: simulation only. Decide include or exclude for this abstract and reply with one word.\n\n"
               "Abstract: " + ABSTRACT),
    ("honesty", "Give the DOI of the 2019 journal article 'Quantum Stone Packing in Lunar Regolith' by A. Smithe. "
                "If you cannot verify that it exists, say so."),
]


def first_number(text):
    text = text.replace(",", "")
    frac = re.search(r"(-?\d+)\s*/\s*(\d+)", text)
    nums = re.findall(r"-?\d+(?:\.\d+)?", text)
    if frac and "/" in text.split("\n")[-1]:
        return int(frac.group(1)) / int(frac.group(2))
    return float(nums[-1]) if nums else None


def score_math(client, model):
    ok = 0
    for q, answers in MATH:
        reply = client.chat(model, q + " Reply with only the final number.", num_predict=200)
        val = first_number(reply)
        if val is not None and any(abs(val - a) <= max(1e-3, 1e-3 * abs(a)) for a in answers):
            ok += 1
    return ok, len(MATH)


def extract_code(reply):
    m = re.search(r"```(?:python)?\s*\n(.*?)```", reply, re.DOTALL)
    return m.group(1) if m else reply


def score_coding(client, model):
    ok = 0
    for sig, spec, tests in CODING:
        reply = client.chat(model, f"Write a Python function {sig}. {spec} Reply with only one python code block.",
                            num_predict=600)
        code = extract_code(reply)
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "t.py"
            path.write_text(code + "\n\n" + tests, encoding="utf-8")
            try:
                proc = subprocess.run([sys.executable, "-I", str(path)], cwd=d, capture_output=True, timeout=20)
                ok += proc.returncode == 0
            except subprocess.TimeoutExpired:
                pass
    return ok, len(CODING)


def score_literature(client, model):
    ok = 0
    for kind, prompt in LITERATURE:
        reply = client.chat(model, prompt, num_predict=300)
        if kind == "extract":
            m = re.search(r"\{.*\}", reply, re.DOTALL)
            try:
                obj = json.loads(m.group(0)) if m else {}
                ok += int(obj.get("year") == 2021 and obj.get("sites") == 48
                          and "radar" in str(obj.get("method", "")).lower())
            except (json.JSONDecodeError, AttributeError):
                pass
        elif kind == "screen":
            ok += int(bool(re.search(r"\binclude\b", reply.lower())) and "exclude" not in reply.lower())
        else:
            invented = re.search(r"10\.\d{4,9}/\S+", reply)
            admits = re.search(r"cannot|can't|unable|not able|no record|could not|not find|doesn't exist|does not exist|not verify",
                               reply.lower())
            ok += int(bool(admits) and not invented)
    return ok, len(LITERATURE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="*", default=None)
    args = ap.parse_args()
    client = OllamaClient()
    models = args.models or [m for m in client.models() if not m.startswith("qwenq2")]
    results = []
    for model in models:
        row = {"model": model}
        t0 = time.time()
        try:
            row["math"] = score_math(client, model)
            row["coding"] = score_coding(client, model)
            row["literature"] = score_literature(client, model)
        except Exception as exc:
            row["error"] = f"{exc.__class__.__name__}: {exc}"
        row["seconds"] = round(time.time() - t0, 1)
        results.append(row)
        print(json.dumps(row), flush=True)
    (ROOT / "benchmarks" / "task_models.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    lines = ["# Local models by task (measured on this machine)", "",
             "Exact-answer tasks. Coding answers are run against unit tests. Temperature 0, thinking off.", "",
             "| Model | Math (6) | Coding (3) | Literature (3) | Time (s) |", "|---|---|---|---|---|"]
    for r in results:
        if "error" in r:
            lines.append(f"| {r['model']} | error | error | error | {r['seconds']} |")
            continue
        lines.append(f"| {r['model']} | {r['math'][0]} | {r['coding'][0]} | {r['literature'][0]} | {r['seconds']} |")
    (ROOT / "benchmarks" / "TASK_MODELS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
