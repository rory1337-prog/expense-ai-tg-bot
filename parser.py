# ===== IMPORTS =====
from datetime import datetime

# ===== CATEGORY RULES =====
CATEGORY_KEYWORDS = {
    "food": [
        "coffee", "pizza", "burger", "sushi", "kfc", "mcdonalds",
        "restaurant", "cafe", "bar", "doner", "shawarma",
        "meal", "lunch", "dinner"
    ],

    "groceries": [
        "lidl", "kaufland", "biedronka", "zabka", "auchan",
        "carrefour", "tesco", "aldi", "grocery", "supermarket"
    ],

    "transport": [
        "taxi", "uber", "bolt", "bus", "train", "tram",
        "metro", "fuel", "gasoline", "petrol", "parking", "ticket"
    ],

    "shopping": [
        "spodnie", "shoes", "shirt", "jacket", "clothes",
        "zara", "hm", "h&m", "reserved", "allegro", "amazon",
        "nike", "adidas", "cosmetics"
    ],

    "health": [
        "pharmacy", "apteka", "doctor", "dentist",
        "medicine", "hospital", "clinic", "therapy", "vitamins"
    ],

    "entertainment": [
        "cinema", "movie", "netflix", "spotify",
        "steam", "game", "psn", "xbox", "concert"
    ],

    "bills": [
        "rent", "internet", "wifi", "phone",
        "electricity", "water", "gas", "utility",
        "utilities", "subscription"
    ],

    "services": [
        "barber", "haircut", "nails", "cleaning",
        "repair", "service", "mechanic", "washing", "laundry"
    ],

    "education": [
        "course", "udemy", "book", "lesson",
        "study", "education", "training", "school"
    ]
}

# ===== CATEGORY DETECTION =====
def detect_category(name):
    name = name.lower().strip().replace(',', '').replace('.', '')

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in name:
                return category

    return "other"

# ===== EXPENSE PARSING =====
def parse_expense(text):
    try:
        parts = text.split()
        
        if len(parts) < 2:
            return None
        
        amount = float(parts[-1])
        name = " ".join(parts[:-1]).strip()

        if not name:
            return None
        
        return {
            'name': name,
            'amount': amount,
            'category': detect_category(name),
            'type': 'expense',
            'created_at': datetime.now().replace(microsecond=0).isoformat()
        }
    except Exception:
        return None
    
# ===== INCOME PARSING =====
def parse_income(text):
    try:
        parts = text.split()

        if len(parts) < 3:
            return None
        
        amount = float(parts[-1])
        name = " ".join(parts[1:-1]).strip()

        if not name:
            return None
        
        return {
            "name": name,
            "amount": amount,
            "category": "income",
            "type": "income",
            "created_at": datetime.now().replace(microsecond=0).isoformat()
        }
    except Exception:
        return None