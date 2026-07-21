"""Legacy compatibility module for Pdf_text_extraction.

Delegates extraction and parsing tasks to the modular pipeline in pipeline.py.
"""

import json
from typing import Any, Dict, List, Union
from pipeline import run_menu_pipeline
from utils import logger

def extract_text_from_pdf_menu(pdf_path: str) -> Union[str, List[Dict[str, Any]]]:
    """Backward-compatible extraction function.

    Args:
        pdf_path (str): Path to the menu PDF file.

    Returns:
        Union[str, List[Dict[str, Any]]]: JSON string representation of extracted menu items.
    """
    logger.info(f"extract_text_from_pdf_menu called for '{pdf_path}'")
    try:
        items = run_menu_pipeline(pdf_path)
        return json.dumps(items, indent=2)
    except Exception as e:
        logger.error(f"Error in extract_text_from_pdf_menu: {e}")
        return json.dumps([])