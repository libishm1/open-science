# Standard Workflow

Part of the pdf-to-markdown skill. Load only this file for this topic.

When user provides a PDF and wants full content in context:

### Step 1: Ensure the skill venv exists
```bash
test -d ~/.claude/skills/pdf-to-markdown/.venv || (cd ~/.claude/skills/pdf-to-markdown && uv venv .venv && uv pip install --python .venv/bin/python pymupdf pymupdf4llm)
```

### Step 2: Convert PDF to Markdown
```bash
~/.claude/skills/pdf-to-markdown/.venv/bin/python ~/.claude/skills/pdf-to-markdown/scripts/pdf_to_md.py "/path/to/document.pdf"
```

### Step 3: Read the output
```bash
# Output is written to document.md in the same directory as the PDF
cat /path/to/document.md
```
