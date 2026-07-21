"""Description Generator Module.

Generates professional 12-20 word restaurant descriptions for extracted menu items in batches of 20.
Generates descriptions separately after full extraction and deduplication.
"""

import json
from typing import Any, Dict, List
from google.genai.types import GenerateContentConfig

from config import config
from utils import logger, Timer
from gemini_parser import get_gemini_client, call_gemini_with_retry
from json_validator import clean_json_response_string

DESCRIPTION_PROMPT_TEMPLATE = """
You are a professional culinary writer. Generate a classic, elegant restaurant menu description for each dish listed below.

RULES FOR EACH DESCRIPTION:
- Length: strictly 12 to 20 words.
- Sentence count: exactly one sentence.
- Style: elegant, professional restaurant menu tone.
- Ingredients: mention traditional key ingredients or preparation methods appropriate for the dish name.
- Strict exclusions: DO NOT use promotional buzzwords (e.g. 'delicious', 'mouthwatering', 'best', 'tasty').
- DO NOT use quotation marks.

INPUT DISHES:
{dishes_json}

Return ONLY a valid JSON array of objects with keys "id" and "description".
Example format:
[
  {{
    "id": 1,
    "description": "Tender cottage cheese cubes simmered in a rich cream and tomato gravy infused with aromatic Indian spices."
  }}
]
"""

def generate_fallback_description(food_item: str, category: str) -> str:
    """Generate a clean fallback description if Gemini output is missing.

    Args:
        food_item (str): Food dish name.
        category (str): Food category name.

    Returns:
        str: 12-20 word generic restaurant style description.
    """
    return (
        f"Freshly prepared {food_item} crafted with classic culinary herbs and traditional spices for an authentic taste."
    )

def process_description_batch(
    batch_items: List[Dict[str, Any]], batch_index: int
) -> List[str]:
    """Send a batch of up to 20 items to Gemini to generate descriptions.

    Args:
        batch_items (List[Dict[str, Any]]): List of item dicts in current batch.
        batch_index (int): Batch number for logging.

    Returns:
        List[str]: List of generated description strings matching batch order.
    """
    input_list = [
        {"id": idx + 1, "food_item": item["food_item"], "category": item["category"]}
        for idx, item in enumerate(batch_items)
    ]
    prompt = DESCRIPTION_PROMPT_TEMPLATE.format(
        dishes_json=json.dumps(input_list, indent=2)
    )

    try:
        raw_response = call_gemini_with_retry(prompt, chunk_index=100 + batch_index)
        cleaned_json = clean_json_response_string(raw_response)
        parsed = json.loads(cleaned_json)

        # Map results by id
        desc_map: Dict[int, str] = {}
        if isinstance(parsed, list):
            for entry in parsed:
                if isinstance(entry, dict) and "id" in entry and "description" in entry:
                    try:
                        entry_id = int(entry["id"])
                        desc_text = str(entry["description"]).strip().replace('"', '')
                        desc_map[entry_id] = desc_text
                    except (ValueError, TypeError):
                        continue

        descriptions: List[str] = []
        for idx, item in enumerate(batch_items, start=1):
            desc = desc_map.get(idx)
            if not desc:
                logger.warning(
                    f"Batch {batch_index}: Missing description for item '{item['food_item']}'. Using fallback."
                )
                desc = generate_fallback_description(item['food_item'], item['category'])
            descriptions.append(desc)

        return descriptions

    except Exception as e:
        logger.error(f"Description batch {batch_index} failed: {e}. Applying fallback descriptions.")
        return [
            generate_fallback_description(item['food_item'], item['category'])
            for item in batch_items
        ]

def generate_descriptions_for_menu(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate descriptions for all menu items in batches of 20.

    Args:
        items (List[Dict[str, Any]]): List of extracted and deduplicated items.

    Returns:
        List[Dict[str, Any]]: Complete item dictionaries with added 'description' key.
    """
    if not items:
        return []

    batch_size = config.DESCRIPTION_BATCH_SIZE
    logger.info(f"Generating descriptions for {len(items)} items in batches of {batch_size}...")

    updated_items: List[Dict[str, Any]] = []

    with Timer(f"Description Generation ({len(items)} items)"):
        for i in range(0, len(items), batch_size):
            batch_items = items[i : i + batch_size]
            batch_num = (i // batch_size) + 1
            logger.info(
                f"Processing description batch {batch_num}/{(len(items) + batch_size - 1) // batch_size} ({len(batch_items)} items)..."
            )

            descriptions = process_description_batch(batch_items, batch_num)

            for item, desc in zip(batch_items, descriptions):
                item_copy = dict(item)
                item_copy["description"] = desc
                updated_items.append(item_copy)

    return updated_items
