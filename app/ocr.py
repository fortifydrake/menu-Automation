"""OCR Module for PDF menu text extraction and cleaning.

Converts PDF pages into images, extracts raw text using pytesseract (--oem 3 --psm 6),
and performs comprehensive text normalization and cleaning.
"""

import os
import re
from typing import List, Optional
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

from config import config
from utils import logger, save_ocr_output, Timer

# Ensure tesseract path is registered in pytesseract
if config.TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH

def convert_pdf_to_images(pdf_path: str, dpi: int = 350) -> List[Image.Image]:
    """Convert a PDF document into a list of PIL Images.

    Args:
        pdf_path (str): Path to the PDF file.
        dpi (int, optional): Image resolution in DPI. Defaults to 350.

    Returns:
        List[Image.Image]: Converted PIL Image objects per page.

    Raises:
        FileNotFoundError: If PDF file does not exist.
        RuntimeError: If PDF conversion fails (e.g., Poppler not installed).
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at path: {pdf_path}")

    logger.info(f"Converting PDF '{pdf_path}' to images at {dpi} DPI...")
    try:
        pages = convert_from_path(pdf_path, dpi=dpi)
        logger.info(f"Successfully converted {len(pages)} page(s) from PDF.")
        return pages
    except Exception as e:
        logger.error(f"PDF conversion failed: {e}")
        raise RuntimeError(
            f"Failed to convert PDF to images: {e}. "
            "Please ensure Poppler is installed and added to PATH."
        ) from e

def clean_ocr_text(raw_text: str) -> str:
    """Clean and sanitize raw OCR text.

    Removes:
    - Invalid unicode / non-printable characters
    - Page numbers (e.g., 'Page 1 of 5', standalone page counters)
    - Page headers and footers
    - Duplicate horizontal whitespace and empty lines

    Args:
        raw_text (str): Raw string returned from Tesseract OCR.

    Returns:
        str: Sanitized, clean text line-by-line.
    """
    if not raw_text:
        return ""

    # 1. Remove non-printable / control characters except newlines & tabs
    cleaned = re.sub(r'[^\x09\x0A\x0D\x20-\x7E\u00A0-\u024F\u0400-\u04FF]', ' ', raw_text)

    # 2. Process line by line
    lines = cleaned.splitlines()
    cleaned_lines: List[str] = []

    # Regex patterns for page numbers, headers, and footers
    page_num_pattern = re.compile(
        r'^\s*(?:page\s*\d+(?:\s*of\s*\d+)?|\d+\s*/\s*\d+|\b\d+\b)\s*$',
        re.IGNORECASE
    )
    header_footer_pattern = re.compile(
        r'^\s*(?:www\.[a-z0-9-]+\.[a-z]+|http[s]?://\S+|all rights reserved|powered by \S+)\s*$',
        re.IGNORECASE
    )

    for line in lines:
        # Collapse multiple spaces / tabs within the line
        line = re.sub(r'[ \t]+', ' ', line).strip()

        # Filter out empty lines
        if not line:
            continue

        # Filter out page number artifacts
        if page_num_pattern.match(line):
            logger.debug(f"Skipping detected page number line: '{line}'")
            continue

        # Filter out obvious header/footer metadata
        if header_footer_pattern.match(line):
            logger.debug(f"Skipping header/footer line: '{line}'")
            continue

        cleaned_lines.append(line)

    # Rejoin lines with single newlines
    final_text = "\n".join(cleaned_lines)
    return final_text

def extract_text_from_pdf(pdf_path: str) -> str:
    """Run full OCR process on a PDF file: convert -> Tesseract (--oem 3 --psm 6) -> clean.

    Args:
        pdf_path (str): Path to the target PDF menu file.

    Returns:
        str: Merged and cleaned OCR text across all pages.
    """
    config.validate()

    with Timer(f"OCR Extraction for {os.path.basename(pdf_path)}"):
        pages = convert_pdf_to_images(pdf_path)
        all_pages_text: List[str] = []

        for idx, page_img in enumerate(pages, start=1):
            logger.info(f"Processing OCR on page {idx}/{len(pages)}...")
            # Convert to grayscale for optimal Tesseract recognition
            gray_img = page_img.convert("L")
            # Tesseract config: OEM 3 (Default LSTM), PSM 6 (Assume a single uniform block of text)
            raw_page_text = pytesseract.image_to_string(
                gray_img,
                config="--oem 3 --psm 6"
            )
            cleaned_page = clean_ocr_text(raw_page_text)
            if cleaned_page:
                all_pages_text.append(cleaned_page)

        full_cleaned_text = "\n\n".join(all_pages_text)
        save_ocr_output(full_cleaned_text)
        logger.info(
            f"OCR complete. Extracted {len(full_cleaned_text)} characters across {len(pages)} pages."
        )
        return full_cleaned_text
