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
        logger.warning("OPENAI_API_KEY not found")
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
        logger.error("OpenAI error %s: %s", response.status_code, response.text)
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
            logger.warning("No output_text in OpenAI response")
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
    fallback = {
        "intent": "unknown",
        "period": "month",
        "language": "en",
        "category": None,
    }

    if not OPENAI_API_KEY:
        return fallback

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
                            "Parse the user's finance question into structured JSON.\n"
                            "The question can be in English, Russian, Polish, or mixed language.\n\n"
                            "Supported intents:\n"
                            "- biggest_expenses: asks for largest/biggest expenses or purchases\n"
                            "- average_daily_spending: asks for average daily spending\n"
                            "- total_spending: asks how much was spent in a period\n"
                            "- top_category: asks biggest/top spending category\n"
                            "- category_spending: asks how much was spent in a specific category\n"
                            "- unknown: not supported\n\n"
                            "Supported periods:\n"
                            "- today\n"
                            "- week\n"
                            "- month\n\n"
                            "Supported categories:\n"
                            "- food\n"
                            "- groceries\n"
                            "- transport\n"
                            "- shopping\n"
                            "- health\n"
                            "- entertainment\n"
                            "- bills\n"
                            "- services\n"
                            "- education\n"
                            "- other\n\n"
                            "Rules:\n"
                            "- If the question asks about a specific category, use category_spending.\n"
                            "- If no category is mentioned, category must be null.\n"
                            "- Detect the language of the question: en, ru, or pl.\n"
                            "- Return only structured JSON.\n\n"
                            "Examples:\n"
                            "сколько я потратил сегодня? -> total_spending, today, null, ru\n"
                            "ile wydałem w tym tygodniu? -> total_spending, week, null, pl\n"
                            "what is my top category this month? -> top_category, month, null, en\n"
                            "what is my average daily spending this month? -> average_daily_spending, month, null, en\n"
                            "what are my biggest expenses this month? -> biggest_expenses, month, null, en\n"
                            "how much did i spend on food this month? -> category_spending, month, food, en\n"
                            "сколько ушло на транспорт за неделю? -> category_spending, week, transport, ru\n\n"
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
                            "enum": [
                                "total_spending",
                                "top_category",
                                "category_spending",
                                "biggest_expenses",
                                "average_daily_spending",
                                "unknown",
                            ],
                        },
                        "period": {
                            "type": "string",
                            "enum": ["today", "week", "month"],
                        },
                        "language": {
                            "type": "string",
                            "enum": ["en", "ru", "pl"],
                        },
                        "category": {
                            "type": ["string", "null"],
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
                                "other",
                                None,
                            ],
                        },
                    },
                    "required": ["intent", "period", "language", "category"],
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
                json=payload,
            )

        if response.status_code != 200:
            logger.error(
                "OpenAI question parse error %s: %s",
                response.status_code,
                response.text,
            )
            return fallback

        data = response.json()
        output_text = data["output"][0]["content"][0]["text"]
        result = json.loads(output_text)

        return {
            "intent": result["intent"],
            "period": result["period"],
            "language": result["language"],
            "category": result["category"],
        }

    except Exception:
        logger.exception("AI question parsing failed")
        return fallback


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
        "on food",
        "on groceries",
        "on transport",
        "on shopping",
        "on health",
        "on entertainment",
        "on bills",
        "on services",
        "on education",
        "biggest expenses",
        "largest expenses",
        "biggest purchases",
        "largest purchases",
        "average daily spending",
        "average spending",

        "сколько",
        "потратил",
        "потратила",
        "расход",
        "расходы",
        "категория",
        "самая большая",
        "на еду",
        "на продукты",
        "на транспорт",
        "на покупки",
        "на здоровье",
        "на развлечения",
        "на счета",
        "на услуги",
        "на образование",
        "самые большие расходы",
        "крупные расходы",
        "самые дорогие покупки",
        "средние траты",
        "средний расход",   

        "ile",
        "wydałem",
        "wydałam",
        "wydatki",
        "kategoria",
        "na jedzenie",
        "na zakupy",
        "na transport",
        "na zdrowie",
        "na rozrywkę",
        "na rachunki",
        "na usługi",
        "na edukację",
        "największe wydatki",
        "najdroższe zakupy",
        "średnie wydatki",

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