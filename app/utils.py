"""Utility module for logging, audit file management, and helper functions."""

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, Optional
from config import config

def ensure_log_dir() -> Path:
    """Ensure the logs directory exists.

    Returns:
        Path: Path object pointing to logs directory.
    """
    log_dir = config.LOG_DIR
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir

def setup_logger(name: str = "menu_pipeline") -> logging.Logger:
    """Configure and return a standard logger.

    Args:
        name (str): Logger name.

    Returns:
        logging.Logger: Configured logger.
    """
    log_dir = ensure_log_dir()
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # File handler
        file_handler = logging.FileHandler(log_dir / "pipeline.log", encoding="utf-8")
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - [%(levelname)s] - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Stream/Console handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            "%(levelname)s: %(message)s"
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger

logger = setup_logger()

def save_ocr_output(text: str, filename: str = "ocr_output.txt") -> Path:
    """Save cleaned OCR text output to logs directory.

    Args:
        text (str): Extracted and cleaned OCR text.
        filename (str): Output filename.

    Returns:
        Path: Path to saved file.
    """
    log_dir = ensure_log_dir()
    filepath = log_dir / filename
    filepath.write_text(text, encoding="utf-8")
    logger.info(f"Saved OCR text output to {filepath}")
    return filepath

def save_chunk_text(chunk_index: int, text: str) -> Path:
    """Save raw text chunk to logs.

    Args:
        chunk_index (int): Index of the chunk (0-indexed or 1-indexed).
        text (str): Chunk text content.

    Returns:
        Path: Path to saved file.
    """
    log_dir = ensure_log_dir()
    filepath = log_dir / f"chunk_{chunk_index}.txt"
    filepath.write_text(text, encoding="utf-8")
    logger.debug(f"Saved chunk {chunk_index} text to {filepath}")
    return filepath

def save_gemini_interaction(
    chunk_index: int, request_prompt: str, raw_response: str
) -> None:
    """Save Gemini request and response logs.

    Args:
        chunk_index (int): Index of chunk being processed.
        request_prompt (str): Prompt sent to Gemini.
        raw_response (str): Text response from Gemini.
    """
    log_dir = ensure_log_dir()
    req_file = log_dir / f"gemini_request_{chunk_index}.txt"
    resp_file = log_dir / f"gemini_response_{chunk_index}.json"

    req_file.write_text(request_prompt, encoding="utf-8")
    resp_file.write_text(raw_response, encoding="utf-8")

def save_failed_chunk(chunk_index: int, raw_response: str) -> Path:
    """Save failed JSON chunk response for debugging.

    Args:
        chunk_index (int): Chunk index that failed JSON parsing.
        raw_response (str): Raw string response from Gemini.

    Returns:
        Path: Path to saved failed chunk file.
    """
    log_dir = ensure_log_dir()
    filepath = log_dir / f"gemini_failed_chunk_{chunk_index}.json"
    filepath.write_text(raw_response, encoding="utf-8")
    logger.error(f"Saved unparseable Gemini response for chunk {chunk_index} to {filepath}")
    return filepath

class Timer:
    """Context manager and stopwatch helper to measure execution timing."""
    def __init__(self, description: str = "Operation"):
        self.description = description
        self.elapsed_time: float = 0.0

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed_time = time.perf_counter() - self.start_time
        logger.info(f"{self.description} completed in {self.elapsed_time:.2f} seconds.")
