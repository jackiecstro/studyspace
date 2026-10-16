"""Read PDF pages; export real, colorful page highlights and positioned sticky notes."""
from __future__ import annotations
import fitz
import textwrap

PALETTE = {
    "Butter": (0.94, 0.80, 0.44),
    "Sage": (0.64, 0.76, 0.59),
    "Clay": (0.84, 0.57, 0.43),
    "Oat": (0.85, 0.75, 0.58),
}
NOTE_COLORS = {
    "Butter": (0.97, 0.90, 0.65),
    "Sage": (0.84, 0.88, 0.76),
    "Clay": (0.94, 0.79, 0.69),
    "Oat": (0.92, 0.86, 0.74),
}


def pdf_info(data: bytes) -> tuple[int, list[str]]:
    with fitz.open(stream=data, filetype="pdf") as doc:
        if doc.needs_pass:
            raise ValueError("This PDF is password-protected. Upload an unlocked copy.")
        if not len(doc):
            raise ValueError("This PDF has no pages.")
        return len(doc), [page.get_text("text", sort=True).strip() for page in doc]


def count_matches(data: bytes, phrase: str, pages: list[int]) -> dict[int,int]:
    with fitz.open(stream=data, filetype="pdf") as doc:
        return {i: len(doc[i].search_for(phrase.strip())) for i in pages if 0 <= i < len(doc) and phrase.strip()}


def _pdf_safe(s: str) -> str:
    # Built-in PDF fonts cannot draw every emoji: fall back to readable text.
    return str(s).encode("latin-1", errors="replace").decode("latin-1")


def _draw_sticky(page: fitz.Page, note: dict):
    """Flatten the movable web sticky at a proportional position on its PDF page."""
    bounds = page.rect
    w = bounds.width * .24
    h = w * 1.03
    x_pct = min(100, max(0, float(note.get('x', 10))))
    y_pct = min(100, max(0, float(note.get('y', 10))))
    x = bounds.x0 + min(bounds.width - w, (x_pct / 100) * bounds.width)
    y = bounds.y0 + min(bounds.height - h, (y_pct / 100) * bounds.height)
    rect = fitz.Rect(x, y, x + w, y + h)
    fill = NOTE_COLORS.get(note.get('color'), NOTE_COLORS['Butter'])
    shape = page.new_shape()
    shape.draw_rect(rect)
    shape.finish(fill=fill, color=(.49, .44, .36), width=.65)
    shape.commit(overlay=True)
    # Colored 'tape' accent makes the exported note feel like stationery.
    tape = fitz.Rect(x + w * .35, y - 3, x + w * .65, y + 7)
    shape = page.new_shape()
    shape.draw_rect(tape)
    shape.finish(fill=(.97, .94, .86), color=(.79, .73, .63), width=.4)
    shape.commit(overlay=True)
    title = _pdf_safe(note.get('title') or 'Study note')[:60]
    body = _pdf_safe(note.get('body') or '')[:1000]
    page.insert_textbox(fitz.Rect(x + 9, y + 14, x + w - 9, y + 40), title,
                        fontname='hebo', fontsize=10, color=(.25, .27, .22), overlay=True)
    # Reduce font size for long notes and fit the note content in its box.
    textbox = fitz.Rect(x + 9, y + 43, x + w - 9, y + h - 9)
    for fontsize in (9.3, 8.3, 7.2, 6.5):
        # insert_textbox returns negative when text cannot fit; drawing on failure
        # is not committed, so safe to retry at a smaller size.
        result = page.insert_textbox(textbox, body, fontname='helv', fontsize=fontsize,
                                     lineheight=1.2, color=(.31,.29,.24), overlay=True)
        if result >= 0:
            break
    # Add an actual PDF comment annotation as well, preserving full text.
    annot = page.add_text_annot(fitz.Point(x + w - 10, y + 10), body, icon='Note')
    annot.set_info(title=title, subject='StudySpace sticky note (also printed on page)')
    annot.update()


def annotated_pdf(data: bytes, highlights: list[dict], notes: list[dict]) -> bytes:
    """Copy the source and burn visible notes onto pages when downloading."""
    with fitz.open(stream=data, filetype="pdf") as doc:
        for item in highlights:
            index = int(item.get('page', -1))
            if not 0 <= index < len(doc) or item.get('color') not in PALETTE:
                continue
            page = doc[index]
            for region in page.search_for(item.get('phrase','')):
                annot = page.add_highlight_annot(region)
                annot.set_colors(stroke=PALETTE[item['color']])
                annot.set_opacity(.44)
                annot.update()
        for note in notes:
            index = int(note.get('page', -1))
            if 0 <= index < len(doc):
                _draw_sticky(doc[index], note)
        return doc.tobytes(garbage=3, deflate=True)


def render_page(data: bytes, page_index: int, scale: float = 1.5) -> bytes:
    with fitz.open(stream=data, filetype='pdf') as doc:
        pix = doc[page_index].get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False, annots=True)
        return pix.tobytes('png')
