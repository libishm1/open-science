# Troubleshooting

Part of the pdf-to-markdown skill. Load only this file for this topic.

### "No module named pymupdf4llm" or venv doesn't exist
Recreate the skill's virtual environment:
```bash
# For fast mode:
cd ~/.claude/skills/pdf-to-markdown && rm -rf .venv && uv venv .venv && uv pip install --python .venv/bin/python pymupdf pymupdf4llm

# For docling mode:
cd ~/.claude/skills/pdf-to-markdown && rm -rf .venv && uv venv .venv && uv pip install --python .venv/bin/python pymupdf docling docling-core
```

### Poor extraction quality
- Try `--docling` for complex tables
- For scanned PDFs, ensure Tesseract OCR is installed: `brew install tesseract`

### Tables not formatting correctly
For complex tables, use `--docling` mode which uses IBM's TableFormer AI model.
