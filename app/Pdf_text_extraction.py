import os
import pytesseract
from pdf2image import convert_from_path
from dotenv import load_dotenv
import time
import requests

load_dotenv()
tesseract_path = os.getenv('tesseract')
model = os.getenv('model')

if not tesseract_path:
    raise Exception(
        "TESSERACT_PATH not found in .env"
    )

if not os.path.exists(tesseract_path):
    raise Exception(
        f"Tesseract executable not found: {tesseract_path}"
    )
    
pytesseract.pytesseract.tesseract_cmd = tesseract_path


def extract_text_from_pdf_menu(pdf_path):
    if not os.path.exists(pdf_path):
        return f"Error: The file '{pdf_path}' was not found."

    print("Converting PDF pages to images...")
    try:
        pages = convert_from_path(pdf_path, dpi=350) 
    except Exception as e:
        return f"Failed to convert PDF: {e}\n(Make sure Poppler is installed and configured)"

    result_text = ""

    for i, page_image in enumerate(pages, start=1):
        print(f"Processing page {i}...")
        
        gray_image = page_image.convert('L')
        
        
        custom_config = r'--psm 3'
        page_text = pytesseract.image_to_string(gray_image, config=custom_config)
        
        if i==0 :
            result_text+= AIparser(page_text.strip())[:-4]+',\n'
            continue
    
        result_text+=AIparser(page_text.strip())[7:-4]+',\n'
        time.sleep(5)

    result_text = result_text[1:-2] + """
``` """
    
    return result_text

def AIparser(text):

    prompt = """
You are an expert menu parser and restaurant menu writer.

Extract all menu items from OCR text.

Fix OCR mistakes such as:
- ! instead of i
- Veg written as Vea, Vaq, Vegg etc.
- Chicken and Veg merged together
- Missing spaces
- Broken words
- Incorrect brackets such as [ ... ) or ( ... ]

You may see dish variations separated by:
- |
- /
- ,
- nothing at all

Use your own understanding to separate variations correctly.

Rules:
- Ignore page numbers
- Ignore restaurant information
- Ignore addresses
- Ignore contact details
- Ignore descriptions from OCR
- Ignore allergy warnings
- Ignore taxes
- Ignore section notes
- Extract only actual food items
- Detect category
- Detect variations
- Detect prices
- Generate a professional restaurant-style description for each item
- Remove all currency symbols (£, $, €, ₹, Rs, INR, AED, etc.)
- Remove commas and spaces
- return prices as array of strings
- Never return strings for prices

Examples:

£220 -> 220
₹349 -> 349
Rs. 199 -> 199
$12 -> 12

Description Rules:
- Generate the description yourself
- Do NOT use OCR descriptions
- 12-25 words
- One sentence only
- Professional restaurant menu style
- Mention key ingredients when obvious
- If ingredients are unknown, generate a reasonable generic description based on the dish name
- Do not start every description with 'Delicious'
- No marketing language
- No quotation marks

Return ONLY valid JSON.

Schema:

[
    {
        "food_item": "",
        "category": "",
        "description": "",
        "variations": [],
        "prices": []
    }
]

OCR TEXT:

""" + text

    response = requests.post(
        model,
        json={
            "model": "gemma3:4b",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False
        },
        timeout=300
    )

    response.raise_for_status()

    result = response.json()["message"]["content"]

    return result