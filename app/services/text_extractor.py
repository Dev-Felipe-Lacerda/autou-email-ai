# app/services/text_extractor.py
from typing import IO

import pdfplumber
from pdfminer.high_level import extract_text as pdfminer_extract_text


def extract_text_from_txt(file_obj: IO[bytes]) -> str:
    """Extract plain text content from a .txt upload."""
    try:
        file_obj.seek(0)
    except Exception:
        pass

    raw = file_obj.read()

    if isinstance(raw, bytes):
        for enc in ("utf-8", "latin-1"):
            try:
                return raw.decode(enc)
            except Exception:
                continue
        return raw.decode("utf-8", errors="ignore")

    return str(raw or "")


def extract_text_from_pdf(file_obj: IO[bytes]) -> str:
    """Extract text content from a PDF upload using pdfplumber and pdfminer as fallback."""
    try:
        file_obj.seek(0)
    except Exception:
        pass

    texts: list[str] = []

    # First try: pdfplumber, page by page
    with pdfplumber.open(file_obj) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                texts.append(page_text)

    merged = "\n\n".join(texts).strip()
    if merged:
        return merged

    # Second try: pdfminer (sometimes handles tricky PDFs better)
    try:
        file_obj.seek(0)
    except Exception:
        pass

    try:
        fallback_text = pdfminer_extract_text(file_obj) or ""
        return fallback_text.strip()
    except Exception:
        return ""
