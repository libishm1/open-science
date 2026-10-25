# Reproducibility packages and publisher submission packages

Two different artefacts with two different audiences. Do not conflate them.

- **Reviewer code/data package**: lets a referee check any reported number without rerunning
  anything expensive.
- **Publisher submission package**: the exact set of files the portal wants, named as it wants them.

---

## 1. The reviewer package

### Contents

```
Code_and_Data/
  README.md          the map: which script produces which table or figure
  code/              model, campaign runners, post-processing, figure generation
  data/              the result files every reported number comes from
```

Include **the result files**. A package that only contains code requires the referee to run a
campaign lasting many hours to check a percentage. Project B shipped a few hundred kilobytes of JSONL
that reproduces every table.

**Exclude:**
- document-generation scripts (the paper is not the deliverable here)
- raw simulation output directories (tens of gigabytes; the reduced files carry everything used)
- third-party weather files you cannot redistribute: ship the script that regenerates them and say
  where the inputs come from

### The README is the deliverable

A file listing is not a map. State:
- **what was run**, as a table of sub-campaign → count → output file → where it is reported
- **which script produces which table and figure**
- **how to reproduce the headline results without rerunning the simulation**
- **the traps** a reader would otherwise hit

That last one matters more than it sounds. Project B's README states three things a referee or future
maintainer would get wrong: energy comes from `eplusout.mtr` not `.csv`; the PCM layer's node set is
fixed by geometry, and inferring it from the output drops one node; cycles are counted from the
solver's discrete phase state, not a derived liquid fraction. Each was a real error that cost rework.

### Assert the package matches the paper

```python
assert wc_l("results.jsonl")        == N_MAIN
assert wc_l("detail_metrics.jsonl") == N_DETAIL
assert wc_l("melt_sweep.jsonl")     == N_SWEEP
assert wc_l("inert_control.jsonl")  == N_CONTROL
assert N_MAIN + N_DETAIL + N_SWEEP + N_CONTROL == N_STATED   # the total the manuscript states
```

If the package and the manuscript disagree about how many runs there were, a referee will find it.

---

## 2. The publisher package

### Example structure (an Editorial Manager portal, as used by Elsevier)

| Editorial Manager item | File |
|---|---|
| Cover Letter | `Cover_Letter.docx` |
| Manuscript | `Manuscript.docx` (or PDF / LaTeX source zip) |
| Highlights | `Highlights.docx`: separate file, not only in the manuscript |
| Declaration of Interest | `Declaration_of_Interest.docx` |
| Figure | `Fig1.png` … `FigN.png`, **uploaded individually** |
| Supplementary Material | `Supplementary_Material.pdf` (+ editable form) |
| Data/Code | `Code_and_Data.zip` |

Figures upload **individually, named by figure number**. Embedded-only figures are a common desk
rejection. Generate them by mapping caption number → source file, and **hash-verify** each copy against
its source; this is where the wrong-artwork bug reappears.

```python
MAIN_FIGS = {1: "lit_network", 2: "framework_pipeline", ...}
for n, stem in MAIN_FIGS.items():
    shutil.copy2(f"figures/{stem}.png", f"package/Figures/Fig{n}.png")
    assert md5(f"figures/{stem}.png") == md5(f"package/Figures/Fig{n}.png")
```

### Figure resolution is a compliance test, not an aesthetic one

Publishers such as Elsevier require **≥ 300 dpi** for halftone/combination art. Judge by
**effective** DPI:

```
effective_dpi = pixel_width / print_width_inches      # 190 mm double column = 7.48 in
```

Metadata DPI is irrelevant and misleading: Project B had figures tagged at a low DPI that were fine
and figures tagged higher that were not. About a third were effectively well below 300 dpi.

Matplotlib figures **re-render losslessly** at higher resolution. The scripts called `savefig()`
without a dpi argument, so forcing the rcParam re-renders the identical figure at more pixels;
figsize in inches is unchanged, so layout, fonts and content are untouched:

```python
import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["savefig.dpi"] = 300
runpy.run_path("make_figure.py", run_name="__main__")
```

**Never** upscale a raster: it adds pixels, not resolution, and reviewers can tell.

Watch for figures produced by a *different* script than the rest, and for scripts that write to the
repo root while the document reads from `figures/`; both leave stale low-resolution copies in the
shipped package.

### Ship a manifest

File, size, and a SHA-256 prefix for everything in the package. It costs ten lines and settles every
later "which version did we send?" question.

---

## 3. The submission checklist as a deliverable

Write the checklist into the package, and record **what is non-compliant** rather than hiding it.
Project B's checklist states plainly, in this form:

> Word count against the journal's limit: **over**.
> Figures + tables against the journal's display-item cap: **over**.

and then, for each, names the least-damaging way to resolve it. That is more useful to the author
than a green tick, and it is the honest position: those were decisions for the author to make, not
for the person assembling the package.

**Checklist contents**
- every journal limit, with the measured value beside it
- item-type mapping for the portal
- the verification run: guards passed, page count, overfull boxes, undefined references
- open risks, each with a recommended resolution and its cost

---

## 4. Rules

1. **Two packages, two audiences.** Never ship document-generation scripts to a referee, and never
   ship a bare code repository as "data availability."
2. **Result files first.** They are the package; code without them is not reproducible in practice.
3. **Hashes on every copy.** Copying is where artefacts silently diverge.
4. **Effective DPI, not metadata DPI.**
5. **Matching counts.** Assert the package's counts against the manuscript's stated counts.
6. **Non-compliance in writing.** Record it and hand the decision to the author.
