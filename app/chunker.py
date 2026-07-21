"""Chunking module for splitting large OCR text into manageable segments.

Ensures chunks stay strictly below character limits (8000-10000 chars),
breaks at line boundaries wherever possible, and never splits words mid-word.
"""

from typing import List
from config import config
from utils import logger, save_chunk_text

def chunk_text(text: str, max_chars: int = config.CHUNK_MAX_CHARS) -> List[str]:
    """Split OCR text into chunks respecting character limits and line boundaries.

    Args:
        text (str): Full clean OCR text string.
        max_chars (int): Maximum allowed character length per chunk. Defaults to config setting.

    Returns:
        List[str]: List of intelligent text chunks.
    """
    if not text or not text.strip():
        logger.warning("Chunker received empty text.")
        return []

    text = text.strip()
    if len(text) <= max_chars:
        logger.info(f"Text length ({len(text)} chars) fits within single chunk limit ({max_chars}).")
        save_chunk_text(1, text)
        return [text]

    lines = text.split("\n")
    chunks: List[str] = []
    current_lines: List[str] = []
    current_length = 0

    for line in lines:
        line_len = len(line) + 1  # +1 for newline character

        # Handle edge case where a single line exceeds max_chars
        if line_len > max_chars:
            # First flush existing chunk if any
            if current_lines:
                chunk_str = "\n".join(current_lines).strip()
                if chunk_str:
                    chunks.append(chunk_str)
                current_lines = []
                current_length = 0

            # Split oversized line on word boundaries
            words = line.split(" ")
            current_sub_words: List[str] = []
            sub_len = 0
            for word in words:
                word_len = len(word) + 1
                if sub_len + word_len > max_chars and current_sub_words:
                    chunks.append(" ".join(current_sub_words))
                    current_sub_words = [word]
                    sub_len = len(word)
                else:
                    current_sub_words.append(word)
                    sub_len += word_len
            if current_sub_words:
                current_lines = [" ".join(current_sub_words)]
                current_length = len(current_lines[0])
            continue

        # Check if adding this line exceeds the chunk size
        if current_length + line_len > max_chars:
            chunk_str = "\n".join(current_lines).strip()
            if chunk_str:
                chunks.append(chunk_str)
            current_lines = [line]
            current_length = len(line)
        else:
            current_lines.append(line)
            current_length += line_len

    # Append any remaining lines
    if current_lines:
        chunk_str = "\n".join(current_lines).strip()
        if chunk_str:
            chunks.append(chunk_str)

    logger.info(f"Split text into {len(chunks)} chunk(s) (max_chars={max_chars}).")
    for idx, chunk in enumerate(chunks, start=1):
        save_chunk_text(idx, chunk)

    return chunks
