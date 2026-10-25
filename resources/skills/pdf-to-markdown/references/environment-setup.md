# Environment Setup

Part of the pdf-to-markdown skill. Load only this file for this topic.

This skill uses a dedicated virtual environment at `~/.claude/skills/pdf-to-markdown/.venv/` to avoid polluting the user's working directory.

### First-Time Setup (if .venv doesn't exist)
```bash
# For fast mode only (PyMuPDF):
cd ~/.claude/skills/pdf-to-markdown && uv venv .venv && uv pip install --python .venv/bin/python pymupdf pymupdf4llm

# For --docling mode (high-accuracy tables):
cd ~/.claude/skills/pdf-to-markdown && uv venv .venv && uv pip install --python .venv/bin/python pymupdf docling docling-core

# Or install everything:
cd ~/.claude/skills/pdf-to-markdown && uv venv .venv && uv pip install --python .venv/bin/python pymupdf pymupdf4llm docling docling-core
```

### Verify Installation
```bash
# Verify fast mode:
~/.claude/skills/pdf-to-markdown/.venv/bin/python -c "import pymupdf; import pymupdf4llm; print('OK')"

# Verify docling mode:
~/.claude/skills/pdf-to-markdown/.venv/bin/python -c "import pymupdf; import docling; import docling_core; print('OK')"
```
