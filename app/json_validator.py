"""JSON Validation and Sanitization Module.

Validates Gemini JSON responses against expected extraction schema and formats prices into string arrays.
Saves unparseable responses to audit logs.
"""

import json
import re
from typing import Any, Dict, List, Tuple
from utils import logger, save_failed_chunk

def clean_json_response_string(raw_response: str) -> str:
    """Strip markdown backticks or extra text surrounding JSON string.

    Args:
        raw_response (str): Gemini raw string output.

    Returns:
        str: Extracted JSON substring.
    """
    if not raw_response:
        return ""

    cleaned = raw_response.strip()
    # Remove markdown ```json ... ``` wrappers
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    # Locate first '[' and last ']' if present
    start_idx = cleaned.find("[")
    end_idx = cleaned.rfind("]")
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        cleaned = cleaned[start_idx : end_idx + 1]

    return cleaned

def sanitize_price(price_val: Any) -> str:
    """Sanitize individual price value to clean string without currency symbols or commas.

    Args:
        price_val (Any): Price input (e.g. 180, "$180", "Rs. 180.00", "₹180").

    Returns:
        str: Clean string digit representation.
    """
    val_str = str(price_val).strip()
    # Remove common currency symbols and labels
    val_str = re.sub(r'[£$€₹,\s]', '', val_str)
    val_str = re.sub(r'^(?:rs|inr|aed|usd|gbp)\.?', '', val_str, flags=re.IGNORECASE).strip()

    # Extract digits or floating number string if any remain
    match = re.search(r'\d+(?:\.\d+)?', val_str)
    if match:
        return match.group(0)
    return val_str

def sanitize_prices(prices: Any) -> List[str]:
    """Ensure prices are returned strictly as List[str].

    Args:
        prices (Any): Prices list or single value.

    Returns:
        List[str]: Clean list of price strings.
    """
    if not prices:
        return []

    if isinstance(prices, (list, tuple)):
        result = []
        for p in prices:
            sanitized = sanitize_price(p)
            if sanitized:
                result.append(sanitized)
        return result
    else:
        sanitized = sanitize_price(prices)
        return [sanitized] if sanitized else []

def sanitize_variations(variations: Any) -> List[str]:
    """Ensure variations are returned strictly as List[str]."""
    if not variations:
        return []
    if isinstance(variations, (list, tuple)):
        return [str(v).strip() for v in variations if str(v).strip()]
    return [str(variations).strip()]

def validate_and_parse_chunk_json(
    raw_response: str, chunk_index: int
) -> Tuple[bool, List[Dict[str, Any]]]:
    """Parse Gemini chunk response into list of valid item dictionaries.

    Args:
        raw_response (str): Raw string output from Gemini.
        chunk_index (int): Index of current chunk.

    Returns:
        Tuple[bool, List[Dict[str, Any]]]: (is_success, list of items)
    """
    cleaned_str = clean_json_response_string(raw_response)
    if not cleaned_str:
        logger.warning(f"Chunk {chunk_index} returned empty string response.")
        save_failed_chunk(chunk_index, raw_response)
        return False, []

    try:
        data = json.loads(cleaned_str)
    except json.JSONDecodeError as exc:
        logger.error(f"JSONDecodeError on chunk {chunk_index}: {exc}")
        save_failed_chunk(chunk_index, raw_response)
        return False, []

    if not isinstance(data, list):
        logger.error(f"Chunk {chunk_index} JSON root is not a list. Got: {type(data)}")
        save_failed_chunk(chunk_index, raw_response)
        return False, []

    valid_items: List[Dict[str, Any]] = []

    for item in data:
        if not isinstance(item, dict):
            continue

        food_item = str(item.get("food_item", "")).strip()
        category = str(item.get("category", "")).strip()

        # Discard invalid/empty food items
        if not food_item:
            continue

        variations = sanitize_variations(item.get("variations", []))
        prices = sanitize_prices(item.get("prices", []))

        valid_items.append({
            "food_item": food_item,
            "category": category if category else "Uncategorized",
            "variations": variations,
            "prices": prices
        })

    logger.info(f"Chunk {chunk_index}: Successfully validated {len(valid_items)} menu items.")
    return True, valid_items
