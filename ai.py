# ===== IMPORTS =====
import logging
import json
import base64
import requests
from datetime import datetime

from config import OPENAI_API_KEY
from parser import detect_category

logger = logging.getLogger(__name__)
# ===== AI RECEIPT PARSING =====
def ai_parse_photo(image_path):
    if not OPENAI_API_KEY:
        print('OPENAI_API_KEY not found')
        return None
    

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    # ===== OPENAI REQUEST =====
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "gpt-4.1-mini",
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Extract one expense from this receipt image. "
                            "Return only the structured result."
                        ),
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{image_base64}",
                    },
                ],
            }
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "expense_receipt",
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "name": {"type": "string"},
                        "amount": {"type": "number"},
                        "category": {
                            "type": "string",
                            "enum": [
                                "food",
                                "groceries",
                                "transport",
                                "shopping",
                                "health",
                                "entertainment",
                                "bills",
                                "services",
                                "education",
                                "other"
                            ],
                        },
                    },
                    "required": ["name", "amount", "category"],
                },
                "strict": True,
            }
        },
    }

    response = requests.post(
        "https://api.openai.com/v1/responses",
        headers=headers,
        json=payload,
        timeout=30,
    )

    if response.status_code != 200:
        print("OPENAI ERROR:", response.status_code, response.text)
        return None

    # ===== RESPONSE PARSING =====
    data = response.json()

    try:
        output_items = data.get("output", [])
        text_output = None

        for item in output_items:
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    text_output = content.get("text")
                    break
            if text_output:
                break

        if not text_output:
            print("No output_text in OpenAI response")
            return None

        expense = json.loads(text_output)

        expense["name"] = str(expense["name"]).strip()
        expense["amount"] = float(expense["amount"])
        expense["category"] = detect_category(expense["name"])

        allowed = {
            "food",
            "groceries",
            "transport",
            "shopping",
            "health",
            "entertainment",
            "bills",
            "services",
            "education",
            "other"
        }
        if expense["category"] not in allowed:
            expense["category"] = "other"
        expense['type'] = 'expense'
        expense['created_at'] = datetime.now().replace(microsecond=0).isoformat()

        return expense

    except Exception:
        logger.exception("AI receipt parsing failed")
        return None