"""Menu Item Merging and Deduplication Module.

Aggregates extracted items across all chunks, normalizes spacing and capitalization,
and deduplicates based on (food_item, category, variations).
"""

import re
from typing import Any, Dict, List, Tuple
from utils import logger

def normalize_string(text: str) -> str:
    """Normalize string by stripping leading/trailing spaces and collapsing multiple internal spaces.

    Args:
        text (str): Input text string.

    Returns:
        str: Cleaned string.
    """
    if not text:
        return ""
    cleaned = re.sub(r'\s+', ' ', text.strip())
    return cleaned

def normalize_item_fields(item: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize fields of a menu item for consistent presentation and comparison.

    Args:
        item (Dict[str, Any]): Input menu item dictionary.

    Returns:
        Dict[str, Any]: Item with normalized food_item, category, variations, and prices.
    """
    food_item = normalize_string(item.get("food_item", "")).title()
    category = normalize_string(item.get("category", "")).title()
    variations = [normalize_string(v).title() for v in item.get("variations", []) if v]
    prices = [normalize_string(p) for p in item.get("prices", []) if p]

    return {
        "food_item": food_item,
        "category": category if category else "Main Course",
        "variations": variations,
        "prices": prices
    }

def generate_dedup_key(item: Dict[str, Any]) -> Tuple[str, str, Tuple[str, ...]]:
    """Generate composite lookup key for deduplication.

    Key consists of case-folded (lowercase) tuple: (food_item, category, variations_tuple).

    Args:
        item (Dict[str, Any]): Normalized item dictionary.

    Returns:
        Tuple[str, str, Tuple[str, ...]]: Comparison key tuple.
    """
    food_key = item["food_item"].lower()
    cat_key = item["category"].lower()
    var_key = tuple(v.lower() for v in item.get("variations", []))
    return (food_key, cat_key, var_key)

def merge_and_deduplicate_chunks(chunk_results: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """Merge extracted item lists from multiple chunks and eliminate duplicates.

    Args:
        chunk_results (List[List[Dict[str, Any]]]): List of chunk outputs.

    Returns:
        List[Dict[str, Any]]: Consolidated, normalized, and deduplicated menu items list.
    """
    total_raw_items = sum(len(c) for c in chunk_results)
    logger.info(f"Merging {total_raw_items} total item(s) from {len(chunk_results)} chunk(s)...")

    seen_keys = set()
    merged_items: List[Dict[str, Any]] = []

    for chunk in chunk_results:
        for raw_item in chunk:
            norm_item = normalize_item_fields(raw_item)
            if not norm_item["food_item"]:
                continue

            dedup_key = generate_dedup_key(norm_item)
            if dedup_key in seen_keys:
                logger.debug(f"Duplicate item skipped: {norm_item['food_item']} ({norm_item['category']})")
                continue

            seen_keys.add(dedup_key)
            merged_items.append(norm_item)

    logger.info(f"Deduplication complete: Reduced {total_raw_items} raw items to {len(merged_items)} unique items.")
    return merged_items
