# Local agent workbench

> **Most people do not need this folder.** Everything here also works inside the Open-Science desktop app:
> install the app from the [releases page](https://github.com/libishm1/open-science/releases), attach your files, and
> ask in plain language. See the [documentation](https://libishm1.github.io/open-science/). This folder is the optional
> command-line version for scripting, other agents, and automation.

An offline, open-source workbench for research and engineering work with local language models.
It runs in a terminal and in VS Code, and it works without a network connection after setup.

What it does:

- **Skills:** pulls the public skill repositories and bundles a snapshot, so setup is fast and works offline.
- **Error loop:** a fixed pipeline runs the checks, and a local model proposes one exact edit per round.
- **Agent queue:** several models share a queue of jobs, and a failed job escalates to a larger model.
- **PDF text:** extracts text with page markers, using PyMuPDF or pypdf.
- **Diagrams:** writes Mermaid flowcharts from a small JSON spec, and renders SVG if the Mermaid CLI is installed.
- **Literature counts:** derives PRISMA-style counts from a screening CSV, so every number can be re-checked.
- **Optional cloud models:** Claude and OpenAI models can be used, but they are off by default.

## Quick start

```bash
python -m pip install pymupdf pypdf          # optional, for PDF parsing
ollama pull qwen2.5-coder:7b                 # one local model, optional but needed for the loop
python -m lawb setup                          # uses the bundled skills; no network needed
python -m lawb doctor                         # shows what is ready and the next command for each gap
```

`python -m lawb setup --pull` refreshes the skills from the public repositories. Skills you
own and keep privately can be imported with `python -m lawb setup --local-skills <folder>`;
they stay on your machine and are never added to the repository.

## Commands

| Command | Purpose |
|---|---|
| `python -m lawb skills list` | list the skills and where each one comes from |
| `python -m lawb skills find <words>` | rank skills by a query |
| `python -m lawb skills show <name> --section "Quick start (for small local models)"` | print one section |
| `python -m lawb pdf <file.pdf> -o out.md` | extract text with page markers |
| `python -m lawb diagram examples/diagram-spec.json -o out/` | Mermaid text, plus SVG when rendering is available |
| `python -m lawb review examples/screening/screening.csv -o counts.md` | PRISMA-style counts |
| `python -m lawb loop examples/faulty_units --model qwen2.5-coder:7b` | run the error loop on one project |
| `python -m lawb queue <folder-of-projects>` | run the agent queue with escalation |
| `python -m lawb queue <folder> --single qwen3:8b` | one model only, as a baseline |

## Local models and optional cloud models

Models are named `provider:model`. A bare name means a local Ollama model.

- `qwen3:8b` or `ollama:qwen3:8b`: local, always available.
- `anthropic:claude-opus-5-5`: Claude, through the official `anthropic` SDK.
- `openai:<model id>`: OpenAI, through the official `openai` SDK.

Cloud providers are **off by default**. Turning one on takes three commands:

```bash
python -m lawb keys set anthropic     # paste the key once; input is hidden
python -m lawb keys set openai        # same for OpenAI, if you want it
python -m lawb cloud-check            # one short test call per provider that has a key
```

Where things are kept:

- **The key** goes in the operating system's credential store (Windows Credential Manager,
  macOS Keychain, or the Linux Secret Service). It is not written to a file, the repository, or
  the config. `python -m lawb keys status` shows whether each key is set, never its value.
  `python -m lawb keys delete anthropic` removes it.
- **The environment** variables `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` also work, as a fallback.
  The stored key takes precedence over them.
- **Nothing is sent to a cloud provider** unless a command names one, such as `anthropic:<model>`.
  `python -m lawb keys disable` turns cloud off again.
- **Every cloud call is logged locally** with the provider, the model, and the time. The prompt and
  the answer are not logged. Read the log with `python -m lawb cloud-log`.

The config file is `$LAWB_HOME/config.json` (default `~/.lawb/config.json`). The default local
tiers are `qwen2.5-coder:1.5b`, `qwen2.5-coder:7b`, and `qwen3:8b`.

## Examples

- `examples/faulty_units`: a small project with four seeded bugs, each caught by a unit test. Run the loop on it.
- `examples/screening/screening.csv`: a screening file with a hand-checked count. The benchmarks check it.
- `examples/diagram-spec.json`: a three-step flow.

## Benchmarks and what they show

`python benchmarks/run_benchmarks.py` runs the checks and writes `benchmarks/RESULTS.md`. A check
that cannot run here is reported as NOT VERIFIED and is never counted as a pass.

Results from the last run on this machine are in `benchmarks/RESULTS.md`. In summary:

- **PRISMA counts:** all 10 expected counts match the hand-checked values. The benchmark found and
  fixed a bug where full-text rows were dropped when a record also appeared at title/abstract.
- **Diagrams:** the structure checks pass, and the Mermaid CLI parses and renders all three test specs.
- **PDF text:** all generated test phrases are recovered, with page markers.
- **Error loop:** the 7B and 8B local models fix all four seeded faults, each using all four rounds. The 1.5B model does not.
- **Cloud models:** NOT VERIFIED. The provider code is tested with fake clients, but no live call has
  been made, because the Claude key is not set and the OpenAI key is rejected.

### Figure types, compared with commercial tools

The workbench makes flowcharts and process diagrams. It does **not** replace Origin, LabStudio,
or BioRender. It does not make statistical plots, custom scientific illustrations, or
brand-styled templates, and it has no visual editor. For a flowchart that goes in a paper, it is
a free, scriptable alternative. For everything else, keep the commercial tool.

## Layout

```
src/lawb/          the package (cli, skills, pipeline, queue, llm, pdf, diagrams, review, doctor)
src/lawb/bundled/  snapshot of the owned skills, with the source commits in SNAPSHOT.json
examples/          small projects and data to try the commands on
benchmarks/        benchmark runner and results
tests/             unit tests (no network, no keys)
vscode-extension/  a thin VS Code extension that runs the commands above in a terminal
```

## Tests

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Licence

MIT for the workbench code. Each skill keeps the licence of the repository it comes from. Skills by
other contributors are not bundled.
