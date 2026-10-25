---
name: local-model-setup
description: Choose, install and check local AI models for a task (coding, math, literature review, general use) with Ollama, LM Studio, llama.cpp or vLLM, so work stays on the user's machine. Gives measured recommendations, hardware guidance, install commands for Windows, macOS and Linux, how to connect the model to the app, how to test it, and how to add an optional cloud key safely. Use when a user asks which local model to use, how to install one, why a model is slow or fails to load, or how to keep data off the internet.
compatibility: Claude, Codex, local models, Herdr and Omarchy. Ollama runs on Windows, macOS and Linux.
license: see repository LICENSE
---

# Local model setup

## Quick start (for small local models)

1. Ask the user's main task: coding, math, literature, or general.
2. Ask how much RAM and GPU memory the computer has.
3. Pick the model from the table below. Use the smaller model if RAM is 8 GB or less.
4. Most users do not use a terminal: tell them to install the Ollama desktop app, pick the model in its
   model menu and send one message (it downloads). Offer `ollama pull <model>` only if they ask for a command.
5. Tell the user to add an Ollama provider in the app (`http://localhost:11434`, no key needed).
6. Test with one short prompt. If it fails to load, see the troubleshooting table.

## Recommendations

Measured on one reference machine (Windows 11, 64 GB RAM, 8 GB GPU) with small exact-answer tests.
They are a starting point, not a ranking. Re-measure on the user's machine when it matters.

| Task | Model | Smaller option | Evidence |
|---|---|---|---|
| Coding | `qwen2.5-coder:7b` | `qwen2.5-coder:1.5b` | 3/3 coding tasks; fixed all faults in a multi-step error loop, where the 1.5B model failed |
| Math | `qwen3:14b` | `qwen2.5-coder:7b` | 6/6 math problems, about three times slower; the 7B model scored 5/6 |
| Literature review | `qwen3:8b` | `qwen2.5-coder:1.5b` | 3/3 on extraction, screening and refusing to invent a reference |
| General use | `qwen3:8b` | `qwen2.5-coder:1.5b` | Followed skills in 7/7 tasks; the 1.5B model followed 5/7 |

## Hardware guide

| Memory available | What fits |
|---|---|
| 8 GB RAM, no GPU | 1.5B models. Slow but usable for short tasks |
| 16 GB RAM, or a GPU with 8 GB | 7B and 8B models |
| 32 GB RAM or more, or a GPU with 12 GB or more | 14B models at a usable speed |

## Install

| System | Command |
|---|---|
| Windows | Install from ollama.com/download, or `winget install --id Ollama.Ollama -e` |
| macOS | Install from ollama.com/download |
| Linux | `curl -fsSL https://ollama.com/install.sh | sh` (read the script first if your policy requires it) |
| Any | `ollama pull qwen2.5-coder:7b` then `ollama list` to confirm |

The workbench does the same in one step: `python -m lawb models install --task coding`
(or `--task all`), and `python -m lawb models recommend` prints this table with what is installed.

## Connect and test

1. In the app's provider settings, add a custom provider with the Ollama preset (`http://localhost:11434`).
   Presets also exist for LM Studio, llama.cpp and vLLM.
2. Pick the model and send "Reply with the word OK."
3. For skills, keep each request small and point the model at one skill file. Small models do best with
   the skill's Quick start section.

## Optional cloud models

Cloud models are off unless the user adds a key. With the workbench:
`python -m lawb keys set anthropic` or `python -m lawb keys set openai` (hidden input; stored in the
operating system's credential store). Never use cloud models for patient data or unpublished data.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| "read GGUF metadata ... size overflows" | Old model file and newer Ollama do not match | `ollama rm <model>` then `ollama pull <model>` |
| Very slow replies | Model larger than GPU memory, running on CPU | Use the smaller option, or close other GPU programs |
| Connection refused | Ollama is not running | Start the Ollama app, or run `ollama serve` |
| Model ignores the skill | Prompt too long for a small model | Give it only the Quick start and one reference |

## Files

- `references/platform-compatibility.md` - where each step runs.
