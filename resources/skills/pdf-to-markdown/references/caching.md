# Caching

Part of the pdf-to-markdown skill. Load only this file for this topic.

PDFs are **aggressively cached** to avoid re-processing. First extraction is slow, every subsequent request is instant.

### How It Works
- **Cache location**: `~/.cache/pdf-to-markdown/<cache_key>/`
- **Cache key**: Based on file content hash + extraction mode
- **Invalidation**: Cache is invalidated when:
  - Source PDF is modified (size or mtime changes)
  - Extractor version changes (automatic re-extraction)
  - Explicitly cleared with `--clear-cache` or `--clear-all-cache`

### Cache Commands
```bash
# Clear cache for a specific PDF
~/.claude/skills/pdf-to-markdown/.venv/bin/python ~/.claude/skills/pdf-to-markdown/scripts/pdf_to_md.py document.pdf --clear-cache

# Clear entire cache
~/.claude/skills/pdf-to-markdown/.venv/bin/python ~/.claude/skills/pdf-to-markdown/scripts/pdf_to_md.py --clear-all-cache

# Show cache statistics
~/.claude/skills/pdf-to-markdown/.venv/bin/python ~/.claude/skills/pdf-to-markdown/scripts/pdf_to_md.py --cache-stats
```

### Cache Contents
```
~/.cache/pdf-to-markdown/<cache_key>/
├── metadata.json    # source path, mtime, size, total_pages
├── full_output.md   # cached full markdown
└── images/          # extracted images
```
