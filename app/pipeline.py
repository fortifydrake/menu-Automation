"""Master Orchestrator for Menu Automation OCR -> AI Parsing Pipeline.

Executes end-to-end processing:
PDF -> OCR -> Clean -> Chunk -> Gemini Extract -> Validate -> Merge & Dedup -> Batched Descriptions -> Clean Final JSON.
"""

import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from config import config
from utils import logger, ensure_log_dir, save_ocr_output, Timer
from ocr import extract_text_from_pdf
from chunker import chunk_text
from gemini_parser import process_chunk_extraction
from menu_merger import merge_and_deduplicate_chunks
from description_generator import generate_descriptions_for_menu

ProgressCallback = Callable[[str, float], None]

def run_menu_pipeline(
    pdf_path: str,
    progress_callback: Optional[ProgressCallback] = None
) -> List[Dict[str, Any]]:
    """Execute the full menu extraction and parsing pipeline.

    Args:
        pdf_path (str): File path to input PDF menu.
        progress_callback (Optional[ProgressCallback]): Optional callback function for status updates.
            Signature: progress_callback(status_message: str, progress_ratio: float)

    Returns:
        List[Dict[str, Any]]: Final list of clean menu items matching required schema.

    Raises:
        ValueError: If PDF file is invalid or environment configuration fails.
        RuntimeError: If critical unrecoverable step failure occurs.
    """
    def report_progress(msg: str, ratio: float) -> None:
        logger.info(f"[Pipeline Progress {int(ratio*100)}%] {msg}")
        if progress_callback:
            try:
                progress_callback(msg, ratio)
            except Exception as cb_err:
                logger.warning(f"Progress callback error: {cb_err}")

    report_progress("Validating environment and inputs...", 0.05)
    config.validate()

    with Timer(f"Full Menu Pipeline for '{pdf_path}'"):
        # Step 1: PDF to Image & OCR Extraction
        report_progress("Running Tesseract OCR on PDF pages...", 0.15)
        try:
            full_ocr_text = extract_text_from_pdf(pdf_path)
        except Exception as ocr_err:
            logger.error(f"OCR Extraction failed: {ocr_err}")
            raise RuntimeError(f"OCR failed: {ocr_err}") from ocr_err

        if not full_ocr_text or not full_ocr_text.strip():
            logger.error("OCR extracted no text from the provided PDF.")
            return []

        # Step 2: Chunking OCR Text
        report_progress("Splitting text into intelligent chunks...", 0.30)
        chunks = chunk_text(full_ocr_text)
        if not chunks:
            logger.error("Chunker returned no valid chunks.")
            return []

        # Step 3, 4, 5: Gemini Extraction & JSON Validation per Chunk
        report_progress(f"Extracting menu items across {len(chunks)} chunk(s)...", 0.45)
        raw_chunk_outputs: List[List[Dict[str, Any]]] = []

        for idx, chunk in enumerate(chunks, start=1):
            chunk_ratio = 0.45 + (0.25 * (idx / len(chunks)))
            report_progress(f"Processing Gemini extraction chunk {idx}/{len(chunks)}...", chunk_ratio)
            extracted_items = process_chunk_extraction(chunk, chunk_index=idx)
            raw_chunk_outputs.append(extracted_items)

        # Step 6: Merge & Deduplicate
        report_progress("Merging item lists and removing duplicates...", 0.75)
        unique_items = merge_and_deduplicate_chunks(raw_chunk_outputs)

        if not unique_items:
            logger.warning("No items were successfully extracted or deduplicated.")
            return []

        # Step 7 & 8: Batched Description Generation & Schema Enforcement
        report_progress(f"Generating descriptions for {len(unique_items)} items...", 0.85)
        final_menu_items = generate_descriptions_for_menu(unique_items)

        # Ensure schema strictness
        formatted_final_output: List[Dict[str, Any]] = []
        for item in final_menu_items:
            formatted_final_output.append({
                "food_item": str(item.get("food_item", "")),
                "category": str(item.get("category", "")),
                "description": str(item.get("description", "")),
                "variations": [str(v) for v in item.get("variations", [])],
                "prices": [str(p) for p in item.get("prices", [])]
            })

        # Step 10: Save final clean output log
        log_dir = ensure_log_dir()
        final_output_file = log_dir / "final_menu_output.json"
        final_output_file.write_text(
            json.dumps(formatted_final_output, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        logger.info(f"Saved final clean menu JSON ({len(formatted_final_output)} items) to {final_output_file}")

        report_progress(f"Pipeline complete! Extracted {len(formatted_final_output)} items.", 1.0)
        return formatted_final_output
