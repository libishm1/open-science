# Comparison with Other Approaches

Part of the pdf-to-markdown skill. Load only this file for this topic.

| Approach | Use Case | Limitations |
|----------|----------|-------------|
| **This skill (pymupdf4llm)** | Full document context with images | Large PDFs may exceed context |
| **--docling mode** | Complex tables, medical/financial PDFs | Slower (~1 sec/page), larger models |
| Grepping PDF | Find specific text | Loses structure, no images |
| Page-by-page extraction | Targeted pages | Manual, loses cross-page context |
| Read tool on PDF | Quick preview | Limited formatting preservation |
