"""PDF page renderer and word coordinates for the StudySpace read-along."""
from __future__ import annotations
import base64
import re
import fitz


def page_visual_and_segments(data: bytes, page_index: int) -> dict:
    """Return sharp PDF page image + word positions grouped into speech-sized chunks.

    Word coordinates come from the actual PDF page, so synchronized visual
    highlighting can be drawn over the page, not just an extracted transcript.
    """
    with fitz.open(stream=data, filetype="pdf") as doc:
        page = doc[page_index]
        width, height = page.rect.width, page.rect.height
        # 2x render makes printed text easier to read at enlarged screen sizes.
        pix = page.get_pixmap(matrix=fitz.Matrix(2.2, 2.2), alpha=False, annots=True)
        png_data = pix.tobytes("png")
        raw_words = page.get_text("words", sort=True)

    lines = []
    last_key = None
    for record in raw_words:
        x0, y0, x1, y1, word, block, line, word_number = record[:8]
        if not str(word).strip():
            continue
        key = (block, line)
        if key != last_key:
            lines.append([])
            last_key = key
        lines[-1].append({
            "text": str(word),
            "x": round(max(0, x0 / width * 100), 4),
            "y": round(max(0, y0 / height * 100), 4),
            "w": round(max(0, (x1 - x0) / width * 100), 4),
            "h": round(max(0, (y1 - y0) / height * 100), 4),
        })

    # Pauses between small groups make pause/resume and spoken-position tracking
    # more reliable than feeding the entire PDF into one browser utterance.
    segments = []
    batch = []
    batch_text = ""
    for line in lines:
        candidate = " ".join(w["text"] for w in line)
        # Avoid a huge utterance; a completed sentence is a natural chunk.
        if batch and len(batch_text) + len(candidate) > 185:
            segments.append(_segment(batch))
            batch, batch_text = [], ""
        batch.extend(line)
        batch_text += (" " if batch_text else "") + candidate
        if len(batch_text) >= 75 and re.search(r'[.!?][”"\']?$', candidate):
            segments.append(_segment(batch))
            batch, batch_text = [], ""
    if batch:
        segments.append(_segment(batch))

    return {
        "image": "data:image/png;base64," + base64.b64encode(png_data).decode("ascii"),
        "width": width,
        "height": height,
        "segments": segments,
        "word_count": sum(len(segment["words"]) for segment in segments),
    }


def _segment(words: list[dict]) -> dict:
    offset = 0
    result_words = []
    text_words = []
    for item in words:
        if text_words:
            offset += 1
        result_words.append({**item, "start": offset, "end": offset + len(item["text"])})
        text_words.append(item["text"])
        offset += len(item["text"])
    return {"text": " ".join(text_words), "words": result_words}


