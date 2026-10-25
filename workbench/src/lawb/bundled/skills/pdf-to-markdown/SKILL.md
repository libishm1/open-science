---
name: pdf-to-markdown
description: Convert entire PDF documents to clean, structured Markdown for full context loading. Use this skill when the user wants to extract ALL text from a PDF into context (not grep/search), when discussing or analyzing PDF content in full, when the user mentions "load the whole PDF", "bring the PDF into context", "read the entire PDF", or when partial extraction/grepping would miss important context. This is the preferred method for PDF text extraction over page-by-page or grep approaches.
compatibility: Claude, Codex, local models, Herdr and Omarchy. Runs on Windows, macOS and Linux.
---

# PDF to Markdown Converter

Extract complete PDF content as structured Markdown, preserving:
- Headers (detected by font size, converted to # tags)
- Bold, italic, monospace formatting
- Tables (converted to Markdown tables)
- Lists (ordered and unordered)
- Multi-column layouts (correct reading order)
- Code blocks
- **Images** (extracted and copied next to output with relative paths)

## Quick start (for small local models)

1. Run python scripts/pdf_to_md.py <file.pdf> to write markdown next to the PDF.
2. Read the markdown in sections, not all at once.
3. For complex tables, use the accurate mode described in the usage reference.
4. Check the page count in the output against the PDF.

## Topics

| Section | File |
|---|---|
| When to Use This Skill | `references/when-to-use-this-skill.md` |
| Environment Setup | `references/environment-setup.md` |
| Quick Start | `references/quick-start.md` |
| Standard Workflow | `references/standard-workflow.md` |
| Caching | `references/caching.md` |
| Image Handling | `references/image-handling.md` |
| Output Format | `references/output-format.md` |
| Section Header | `references/section-header.md` |
| Extracted Images | `references/extracted-images.md` |
| Script Reference | `references/script-reference.md` |
| High-Accuracy Mode (Docling) | `references/high-accuracy-mode-docling.md` |
| Troubleshooting | `references/troubleshooting.md` |
| Comparison with Other Approaches | `references/comparison-with-other-approaches.md` |
