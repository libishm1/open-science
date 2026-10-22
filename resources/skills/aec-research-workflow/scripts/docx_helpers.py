"""Small python-docx helpers for the synthesis report (Arial, A4, numbered captions, hyperlinks).

Import it from a build script; it has no command line of its own.
Text passed to para/bullet/table/caption supports **bold**, *italic* and X_{sub} subscript markers.
Set SUBSCRIPT_RE to a regex with two groups to turn plain "X_y" symbols into subscripts as well.

Example:
    import sys; sys.path.insert(0, 'scripts')
    from docx_helpers import new_document, para, bullet, table, figure
    doc = new_document()
    doc.add_heading('Synthesis', 1)
    para(doc, 'Mean **UDI** rose by *12 %* (T_{in} fixed).')
    table(doc, ['Paper', 'Finding'], [['A2024', '...']], [4, 12])
    doc.save('synthesis.docx')
Requires: python-docx.
"""
import re

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

NAVY = RGBColor(0x1F, 0x38, 0x64)
GREY = RGBColor(0x59, 0x59, 0x59)
# Optional: plain symbols to subscript automatically, e.g. re.compile(r'\b(T|Q)_(in|out|max|min)\b')
SUBSCRIPT_RE = None


def new_document():
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    for side in ('left_margin', 'right_margin'):
        setattr(sec, side, Cm(2.2))
    sec.top_margin, sec.bottom_margin = Cm(2.0), Cm(2.0)
    st = doc.styles['Normal']
    st.font.name, st.font.size = 'Arial', Pt(10.5)
    st.element.rPr.rFonts.set(qn('w:eastAsia'), 'Arial')
    st.paragraph_format.space_after = Pt(6)
    st.paragraph_format.line_spacing = 1.15
    for lvl, size in ((1, 15), (2, 12.5), (3, 11)):
        h = doc.styles[f'Heading {lvl}']
        h.font.name, h.font.size, h.font.bold, h.font.color.rgb = 'Arial', Pt(size), True, NAVY
        rf = h.element.rPr.rFonts
        for att in ('w:asciiTheme', 'w:hAnsiTheme', 'w:eastAsiaTheme', 'w:cstheme'):
            if rf.get(qn(att)) is not None:
                del rf.attrib[qn(att)]
        for att in ('w:ascii', 'w:hAnsi', 'w:eastAsia', 'w:cs'):
            rf.set(qn(att), 'Arial')
        h.paragraph_format.space_before = Pt(14 if lvl == 1 else 10)
        h.paragraph_format.space_after = Pt(6)
        h.paragraph_format.keep_with_next = True
    for name in ('List Bullet', 'List Number'):
        doc.styles[name].font.name = 'Arial'
        doc.styles[name].font.size = Pt(10.5)
    add_page_number_footer(doc)
    return doc


def add_page_number_footer(doc):
    p = doc.sections[0].footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    for tag, text in (('begin', None), (None, 'PAGE'), ('end', None)):
        if tag:
            el = OxmlElement('w:fldChar'); el.set(qn('w:fldCharType'), tag); run._r.append(el)
        else:
            el = OxmlElement('w:instrText'); el.set(qn('xml:space'), 'preserve'); el.text = text; run._r.append(el)
    run.font.size, run.font.name = Pt(9), 'Arial'


def add_hyperlink(paragraph, url, text, size=None):
    part = paragraph.part
    r_id = part.relate_to(url, 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink', is_external=True)
    h = OxmlElement('w:hyperlink'); h.set(qn('r:id'), r_id)
    r = OxmlElement('w:r'); rPr = OxmlElement('w:rPr')
    c = OxmlElement('w:color'); c.set(qn('w:val'), '0563C1'); rPr.append(c)
    u = OxmlElement('w:u'); u.set(qn('w:val'), 'single'); rPr.append(u)
    if size:
        sz = OxmlElement('w:sz'); sz.set(qn('w:val'), str(int(size * 2))); rPr.append(sz)
    r.append(rPr); t = OxmlElement('w:t'); t.text = text; t.set(qn('xml:space'), 'preserve'); r.append(t)
    h.append(r); paragraph._p.append(h)
    return h


def para(doc, text='', style=None, bold=False, italic=False, size=None, color=None, align=None, after=None):
    p = doc.add_paragraph(style=style)
    if text:
        add_rich(p, text, bold=bold, italic=italic, size=size, color=color)
    if align == 'center':
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if after is not None:
        p.paragraph_format.space_after = Pt(after)
    return p


def add_rich(p, text, bold=False, italic=False, size=None, color=None):
    """Supports **bold**, *italic* and X_{sub} inline markers."""
    if SUBSCRIPT_RE is not None:
        text = re.sub(SUBSCRIPT_RE, r'\1_{\2}', text)
    parts = re.split(r'(\*\*[^*]+\*\*|\*[^*]+\*|_\{[^}]+\})', text)
    for part in parts:
        if not part:
            continue
        b, i, t, sub = bold, italic, part, False
        if part.startswith('**') and part.endswith('**'):
            b, t = True, part[2:-2]
        elif part.startswith('*') and part.endswith('*') and len(part) > 2:
            i, t = True, part[1:-1]
        elif part.startswith('_{') and part.endswith('}'):
            t, sub = part[2:-1], True
        run = p.add_run(t)
        run.bold, run.italic = b, i
        if sub:
            run.font.subscript = True
        if size:
            run.font.size = Pt(size)
        if color:
            run.font.color.rgb = color
    return p


def bullet(doc, text, level=0):
    p = doc.add_paragraph(style='List Bullet')
    add_rich(p, text)
    p.paragraph_format.left_indent = Cm(0.63 + 0.6 * level)
    p.paragraph_format.space_after = Pt(3)
    return p


def shade(cell, hex_fill):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement('w:shd'); sh.set(qn('w:val'), 'clear'); sh.set(qn('w:color'), 'auto'); sh.set(qn('w:fill'), hex_fill)
    tcPr.append(sh)


def table(doc, headers, rows, widths_cm, font_size=8.5, header_fill='1F3864', zebra='F2F2F2'):
    t = doc.add_table(rows=1, cols=len(headers))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.style = 'Table Grid'
    t.autofit = False
    for j, h in enumerate(headers):
        c = t.rows[0].cells[j]
        c.text = ''
        r = c.paragraphs[0].add_run(h); r.bold = True; r.font.size = Pt(font_size); r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        shade(c, header_fill)
    for i, row in enumerate(rows):
        cells = t.add_row().cells
        for j, v in enumerate(row):
            c = cells[j]; c.text = ''
            add_rich(c.paragraphs[0], str(v), size=font_size)
            c.paragraphs[0].paragraph_format.space_after = Pt(0)
            if zebra and i % 2 == 1:
                shade(c, zebra)
    for row in t.rows:
        for j, w in enumerate(widths_cm):
            row.cells[j].width = Cm(w)
    # repeat header row on each page
    trPr = t.rows[0]._tr.get_or_add_trPr(); th = OxmlElement('w:tblHeader'); th.set(qn('w:val'), 'true'); trPr.append(th)
    # never split a row across pages; keep the header with the first data row
    for row in t.rows:
        cs = OxmlElement('w:cantSplit'); cs.set(qn('w:val'), 'true'); row._tr.get_or_add_trPr().append(cs)
    for c in t.rows[0].cells:
        c.paragraphs[0].paragraph_format.keep_with_next = True
    return t


def caption(doc, text):
    p = doc.add_paragraph()
    add_rich(p, text, size=9, color=GREY)
    p.paragraph_format.space_after = Pt(10)
    return p


def figure(doc, path, width_cm, cap):
    doc.add_picture(path, width=Cm(width_cm))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption(doc, cap)


def landscape_section(doc):
    from docx.enum.section import WD_SECTION
    sec = doc.add_section(WD_SECTION.NEW_PAGE)
    sec.orientation = WD_ORIENT.LANDSCAPE
    sec.page_width, sec.page_height = Cm(29.7), Cm(21.0)
    return sec


def portrait_section(doc):
    from docx.enum.section import WD_SECTION
    sec = doc.add_section(WD_SECTION.NEW_PAGE)
    sec.orientation = WD_ORIENT.PORTRAIT
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    return sec
