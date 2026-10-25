# High-Accuracy Mode (Docling)

Part of the pdf-to-markdown skill. Load only this file for this topic.

For PDFs with complex tables that need high accuracy, use the `--docling` flag:

```bash
~/.claude/skills/pdf-to-markdown/.venv/bin/python \
    ~/.claude/skills/pdf-to-markdown/scripts/pdf_to_md.py \
    document.pdf --docling
```

**When to use `--docling`:**
- PDF has complex tables (borderless, merged cells, multi-column)
- Table accuracy is critical (medical data, financial reports)
- You're seeing garbled table output in default mode

**Trade-offs:**
- ~1 second per page (vs instant for fast mode)
- First run downloads AI models (~500MB one-time)
- Higher-resolution images (4x default)

**Note:** `--accurate` is an alias for `--docling`.
