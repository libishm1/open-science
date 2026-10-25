"""PDF text extraction to markdown with page markers. Uses PyMuPDF if installed, else pypdf."""

from pathlib import Path


def extract(pdf: Path, out: Path | None = None) -> str:
    try:
        import fitz  # PyMuPDF
    except ImportError:
        fitz = None
    if fitz is not None:
        doc = fitz.open(pdf)
        pages = [page.get_text() for page in doc]
        engine = "pymupdf"
    else:
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError("install PyMuPDF (pip install pymupdf) or pypdf to parse PDFs") from exc
        pages = [p.extract_text() or "" for p in PdfReader(str(pdf)).pages]
        engine = "pypdf"
    body = "\n".join(f"\n<!-- page {i} -->\n{text}" for i, text in enumerate(pages, 1))
    md = f"# {pdf.stem}\n\nSource: {pdf.name}; pages: {len(pages)}; engine: {engine}\n{body}\n"
    if out:
        out.write_text(md, encoding="utf-8")
    return md


def sections(md: str) -> list[str]:
    """Split extracted text at lines that look like headings (short, title-cased or numbered)."""
    out, current = [], []
    for line in md.splitlines():
        stripped = line.strip()
        is_heading = (0 < len(stripped) <= 80 and not stripped.endswith((".", ",", ";"))
                      and (stripped[:1].isdigit() or stripped.isupper()))
        if is_heading and current:
            out.append("\n".join(current))
            current = []
        current.append(line)
    if current:
        out.append("\n".join(current))
    return out
