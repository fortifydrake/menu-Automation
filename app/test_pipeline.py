"""Standalone test script to verify end-to-end execution of the OCR to AI pipeline."""

import os
import sys
import json
from pathlib import Path

# Add app directory to sys.path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

from pipeline import run_menu_pipeline
from utils import logger

def test_pipeline_on_pdf(pdf_path: str):
    logger.info(f"--- STARTING TEST FOR {pdf_path} ---")
    if not os.path.exists(pdf_path):
        logger.error(f"Test PDF not found at {pdf_path}")
        return

    def status_callback(msg: str, progress: float):
        print(f"[{int(progress*100):3d}%] {msg}")

    try:
        results = run_menu_pipeline(pdf_path, progress_callback=status_callback)
        print("\n" + "="*50)
        print(f"TEST COMPLETE: Extracted {len(results)} items")
        print("="*50)
        if results:
            print("Sample item 1:")
            print(json.dumps(results[0], indent=2))
        else:
            print("WARNING: Pipeline returned 0 items.")
    except Exception as e:
        print(f"TEST FAILED WITH EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    menu_pdf = os.path.join(app_dir.parent, "menu.pdf")
    test_pipeline_on_pdf(menu_pdf)
