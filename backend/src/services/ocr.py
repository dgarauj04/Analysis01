import pytesseract
from pdf2image import convert_from_path
import tempfile
import os
import logging

logger = logging.getLogger(__name__)

def ocr_pdf_images(pdf_path: str, lang="por") -> str:
    text_parts = []
    with tempfile.TemporaryDirectory() as tmpdir:
        images = convert_from_path(pdf_path, output_folder=tmpdir)
        for i, img in enumerate(images):
            try:
                txt = pytesseract.image_to_string(img, lang=lang)
                text_parts.append(txt)
            except Exception as e:
                logger.exception("Tesseract OCR failed on page %d: %s", i, e)
    return "\n".join(text_parts)
