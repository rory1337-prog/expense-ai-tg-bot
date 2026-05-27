# ===== IMPORTS =====
import logging
import json
import base64
import httpx
from datetime import datetime

from config import OPENAI_API_KEY
from parser import detect_category

logger = logging.getLogger(__name__)
# ===== AI RECEIPT PARSING =====
async def ai_parse_photo(image_path):
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

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            "https://api.openai.com/v1/responses",
            headers=headers,
            json=payload
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
        expense["category"] = str(expense["category"]).strip().lower()

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
        if (
            expense["category"] not in allowed
            or expense["category"] == "other"
        ):
            expense["category"] = detect_category(expense['name'])
        
        expense['type'] = 'expense'
        expense['created_at'] = datetime.now().replace(microsecond=0).isoformat()

        return expense

    except Exception:
        logger.exception("AI receipt parsing failed")
        return None
    
async def ai_parse_question(question):
    if not OPENAI_API_KEY:
        return {"intent": "unknown", "period": "month"}

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
                            "Parse the user's finance question into intent and period.\n"
                            "The question can be in English, Russian, Polish, or mixed language.\n\n"
                            "Supported intents:\n"
                            "- total_spending: asks how much was spent\n"
                            "- top_category: asks biggest/top spending category\n"
                            "- unknown: not supported\n\n"
                            "Supported periods:\n"
                            "- today\n"
                            "- week\n"
                            "- month\n\n"
                            "Detect the language of the question.\n"
                            "Examples:\n"
                            "сколько я потратил сегодня? -> total_spending, today\n"
                            "ile wydałem w tym tygodniu? -> total_spending, week\n"
                            "what is my top category this month? -> top_category, month\n\n"
                            "Return only structured JSON.\n\n"
                            f"Question: {question}"
                        ),
                    }
                ],
            }
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "finance_question_parser",
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "intent": {
                            "type": "string",
                            "enum": ["total_spending", "top_category", "unknown"],
                        },
                        "period": {
                            "type": "string",
                            "enum": ["today", "week", "month"],
                        },
                        "language": {
                            "type": "string",
                            "enum": ["en", "ru", "pl"]
                        }
                    },
                    "required": ["intent", "period", "language"],
                },
                "strict": True,
            }
        },
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                "https://api.openai.com/v1/responses",
                headers=headers,
                json=payload
            )

        if response.status_code != 200:
            print("OPENAI QUESTION PARSE ERROR:", response.status_code, response.text)
            return {"intent": "unknown", "period": "month"}

        data = response.json()
        output_text = data["output"][0]["content"][0]["text"]
        result = json.loads(output_text)

        return {
            "intent": result["intent"],
            "period": result["period"],
            "language": result["language"]
        }

    except Exception:
        logger.exception("AI question parsing failed")
        return {"intent": "unknown", "period": "month"}


def classify_message(text):
    text = text.lower().strip()

    question_keywords = [
        "how much",
        "spent",
        "spend",
        "biggest",
        "category",
        "this week",
        "this month",
        "last week",
        "last month",

        "сколько",
        "потратил",
        "потратила",
        "расход",
        "расходы",
        "категория",
        "самая большая",

        "ile",
        "wydałem",
        "wydałam",
        "wydatki",
        "kategoria",
    ]

    if text.endswith("?"):
        return "question"

    for keyword in question_keywords:
        if keyword in text:
            return "question"

    return "transaction"

async def ai_classify_message(text):

    if not OPENAI_API_KEY:
        return "transaction"
    
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
                            "Classify the user finance message into one of these types:\n"
                            "- expense: user wants to add an expense, e.g. coffee 15, кофе 15, kawa 15\n"
                            "- income: user wants to add income, e.g. salary 3000, зарплата 3000, pensja 3000\n"
                            "- question: user asks about stored financial data, totals, categories, reports, analytics, spending, balance\n"
                            "- unknown: message is not related to finance tracking\n\n"
                            "The message may be in English, Russian, Polish, or mixed language.\n"
                            "Return only structured JSON.\n\n"
                            f"Message: {text}"
                        )
                    }
                ]
            }
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "message_classifier",
                "schema": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": [
                                "expense",
                                "income",
                                "question",
                                "unknown"
                            ]
                        }
                    },
                    "required": ["type"],
                    "additionalProperties": False
                },
                "strict": True
            }
        }
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                "https://api.openai.com/v1/responses",
                headers=headers,
                json=payload
            )

        if response.status_code != 200:
            return "unknown"
        
        data = response.json()

        output_text = (
            data["output"][0]["content"][0]["text"]
        )

        result = json.loads(output_text)

        return result["type"]
    
    except Exception:
        logger.exception("AI message classification failed")
        return "unknown"