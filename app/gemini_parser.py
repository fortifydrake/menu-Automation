"""Gemini API Interaction Module.

Provides persistent Gemini client management, chunk extraction with prompt enforcing schema,
and exponential backoff retry handling for API errors and JSON validation failures.
"""

import time
from typing import Any, Dict, List, Optional
from google import genai
from google.genai.types import GenerateContentConfig
from google.genai.errors import APIError

from config import config
from utils import logger, save_gemini_interaction, save_failed_chunk
from json_validator import validate_and_parse_chunk_json

# Global persistent Gemini client instance
_gemini_client: Optional[genai.Client] = None

def get_gemini_client() -> genai.Client:
    """Retrieve or initialize the singleton Gemini client instance.

    Returns:
        genai.Client: Configured Gemini client instance.

    Raises:
        ValueError: If GEMINI_API_KEY is missing.
    """
    global _gemini_client
    if _gemini_client is None:
        config.validate()
        logger.info("Initializing persistent Gemini client...")
        _gemini_client = genai.Client(api_key=config.GEMINI_API_KEY)
    return _gemini_client

EXTRACTION_PROMPT_TEMPLATE = """
You are an expert menu parser. Extract all restaurant food/beverage items from the provided OCR text.

STRICT INSTRUCTIONS:
- Perform EXTRACTION ONLY. Do NOT generate dish descriptions.
- Fix obvious OCR mistakes (e.g. "Vea" -> "Veg", merged words, missing spaces, bracket typos).
- Ignore headers, addresses, contact details, page numbers, taxes, allergy warnings, or section notes.
- Separate variations (e.g., Half/Full, Small/Large, Glass/Bottle) and corresponding prices into list arrays.
- Remove all currency symbols (£, $, €, ₹, Rs, INR, AED, etc.) and spaces from prices. Prices MUST be returned as strings.
- Return ONLY a valid JSON array matching the example structure.

JSON Schema:

[
    {{
        "food_item": "",
        "category": "",
        "variations": [],
        "prices": []
    }}
]

OCR TEXT:

__OCR_TEXT__
"""

def is_retryable_error(exc: Exception) -> bool:
    """Determine if an exception qualifies for automatic API retry.

    Retries on rate limits (429), server errors (503), timeouts, and transient connection issues.

    Args:
        exc (Exception): Caught exception.

    Returns:
        bool: True if retryable, False otherwise.
    """
    err_msg = str(exc).lower()
    if isinstance(exc, APIError):
        code = getattr(exc, "code", None) or getattr(exc, "status_code", None)
        if code in (429, 503):
            return True
    if any(keyword in err_msg for keyword in ["429", "503", "quota", "rate limit", "timeout", "connection"]):
        return True
    return False

def call_gemini_with_retry(prompt: str, chunk_index: int) -> str:
    """Call Gemini API with automatic exponential backoff retry.

    Args:
        prompt (str): Full prompt text.
        chunk_index (int): Index of chunk for logging.

    Returns:
        str: Raw text response from Gemini model.

    Raises:
        RuntimeError: If all retries fail.
    """
    client = get_gemini_client()
    gen_config = GenerateContentConfig(
        temperature=config.TEMPERATURE,
        response_mime_type="application/json"
    )

    delay = config.RETRY_INITIAL_DELAY
    last_exception = None

    for attempt in range(1, config.MAX_RETRIES + 1):
        try:
            logger.info(
                f"Calling Gemini API for chunk {chunk_index} (Attempt {attempt}/{config.MAX_RETRIES})..."
            )
            response = client.models.generate_content(
                model=config.GEMINI_MODEL,
                contents=prompt,
                config=gen_config
            )

            if response and response.text:
                save_gemini_interaction(chunk_index, prompt, response.text)
                return response.text
            else:
                raise ValueError("Gemini returned empty or null response text.")

        except Exception as e:
            last_exception = e
            if is_retryable_error(e) and attempt < config.MAX_RETRIES:
                logger.warning(
                    f"Retryable error on chunk {chunk_index} attempt {attempt}: {e}. Retrying in {delay}s..."
                )
                time.sleep(delay)
                delay *= config.RETRY_BACKOFF_FACTOR
            else:
                logger.error(f"Non-retryable or max attempts reached for chunk {chunk_index}: {e}")
                break

    raise RuntimeError(
        f"Failed to process chunk {chunk_index} after {config.MAX_RETRIES} attempts. Last error: {last_exception}"
    ) from last_exception

def process_chunk_extraction(
    chunk_text: str, chunk_index: int
) -> List[Dict[str, Any]]:
    """Process single OCR text chunk: query Gemini -> validate JSON -> retry once if invalid.

    Args:
        chunk_text (str): Sub-segment of OCR text.
        chunk_index (int): Index of chunk.

    Returns:
        List[Dict[str, Any]]: Validated list of extracted items for this chunk.
    """
    prompt = EXTRACTION_PROMPT_TEMPLATE.replace("__OCR_TEXT__", chunk_text)

    try:
        raw_response = call_gemini_with_retry(prompt, chunk_index)
    except Exception as e:
        logger.error(f"Failed to obtain Gemini response for chunk {chunk_index}: {e}")
        return []

    # First JSON validation attempt
    success, items = validate_and_parse_chunk_json(raw_response, chunk_index)
    if success:
        return items

    # Step 5 requirement: If JSON decoding fails, retry once
    logger.warning(
        f"JSON validation failed for chunk {chunk_index}. Executing single retry attempt with Gemini..."
    )
    try:
        raw_response_retry = call_gemini_with_retry(prompt, chunk_index)
        success_retry, items_retry = validate_and_parse_chunk_json(
            raw_response_retry, chunk_index
        )
        if success_retry:
            return items_retry
    except Exception as e:
        logger.error(f"JSON validation retry failed for chunk {chunk_index}: {e}")

    # If still invalid, save failed response and continue with empty result (no crash)
    save_failed_chunk(chunk_index, raw_response)
    return []
