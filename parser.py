# ===== IMPORTS =====
from datetime import datetime

# ===== CATEGORY RULES =====
CATEGORY_KEYWORDS = {
    "food": [
        "coffee", "pizza", "burger", "sushi", "kfc", "mcdonalds",
        "restaurant", "cafe", "bar", "doner", "shawarma",
        "meal", "lunch", "dinner",
        "кофе", "пицца", "бургер", "суши", "кафе", "ресторан",
        "бар", "донер", "шаверма", "шаурма", "обед", "ужин",
        "kawa", "kawiarnia", "restauracja", "obiad", "kolacja"
    ],

    "groceries": [
        "lidl", "kaufland", "biedronka", "zabka", "żabka", "auchan",
        "carrefour", "tesco", "aldi", "grocery", "supermarket",
        "продукты", "магазин", "супермаркет", "ашан", "бедронка",
        "жабка", "лидл",
        "produkty", "sklep", "spożywczy"
    ],

    "transport": [
        "taxi", "uber", "bolt", "bus", "train", "tram",
        "metro", "fuel", "gasoline", "petrol", "parking", "ticket",
        "такси", "автобус", "поезд", "трамвай", "метро",
        "бензин", "топливо", "парковка", "билет",
        "taksowka", "taksówka", "autobus", "pociag", "pociąg",
        "tramwaj", "paliwo", "parking", "bilet"
    ],

    "shopping": [
        "spodnie", "shoes", "shirt", "jacket", "clothes",
        "zara", "hm", "h&m", "reserved", "allegro", "amazon",
        "nike", "adidas", "cosmetics",
        "одежда", "обувь", "штаны", "футболка", "куртка",
        "косметика", "покупки",
        "ubrania", "buty", "koszulka", "kurtka", "kosmetyki", "zakupy"
    ],

    "health": [
        "pharmacy", "apteka", "doctor", "dentist",
        "medicine", "hospital", "clinic", "therapy", "vitamins",
        "аптека", "врач", "доктор", "стоматолог", "зубной",
        "лекарство", "лекарства", "больница", "клиника", "витамины",
        "lekarz", "dentysta", "lek", "leki", "szpital", "klinika", "witaminy"
    ],

    "entertainment": [
        "cinema", "movie", "netflix", "spotify",
        "steam", "game", "psn", "xbox", "concert",
        "кино", "кинотеатр", "фильм", "нетфликс", "спотифай",
        "игра", "игры", "концерт",
        "kino", "film", "gra", "gry", "koncert"
    ],

    "bills": [
        "rent", "internet", "wifi", "phone",
        "electricity", "water", "gas", "utility",
        "utilities", "subscription",
        "аренда", "квартира", "интернет", "телефон",
        "электричество", "вода", "газ", "коммуналка", "подписка",
        "czynsz", "mieszkanie", "prad", "prąd", "woda",
        "gaz", "rachunek", "abonament"
    ],

    "services": [
        "barber", "haircut", "nails", "cleaning",
        "repair", "service", "mechanic", "washing", "laundry",
        "барбер", "стрижка", "парикмахер", "ногти", "уборка",
        "ремонт", "сервис", "механик", "стирка", "прачечная",
        "fryzjer", "paznokcie", "sprzatanie", "sprzątanie",
        "naprawa", "mechanik", "pranie"
    ],

    "education": [
        "course", "udemy", "book", "lesson",
        "study", "education", "training", "school",
        "курс", "книга", "урок", "учеба", "учёба",
        "обучение", "школа",
        "kurs", "ksiazka", "książka", "lekcja", "nauka", "szkola", "szkoła"
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
        
        amount = None
        name_parts = None

        try:
            amount = float(parts[-1])
            name_parts = parts[:-1]
        except ValueError:
            try:
                amount = float(parts[0])
                name_parts = parts[1:]
            except ValueError:
                return None
            
        if amount <= 0:
            return None
        
        name = " ".join(name_parts).strip()

        if not name:
            return None
        
        return {
            'name': name,
            'amount': amount,
            'category': detect_category(name),
            'type': 'expense',
            'created_at': datetime.now().replace(microsecond=0).isoformat()
        }
    except (ValueError, IndexError):
        return None
    
# ===== INCOME PARSING =====
def parse_income(text):
    try:
        parts = text.split()

        if len(parts) < 2:
            return None

        amount = float(parts[-1])

        if amount <= 0:
            return None

        first_word = parts[0].lower()

        income_prefixes = [
            "income",
            "salary",
            "зарплата",
            "зп",
            "доход",
            "pensja",
            "przychod",
            "przychód",
        ]

        if first_word not in income_prefixes:
            return None

        if len(parts) == 2:
            name = first_word
        else:
            name = " ".join(parts[1:-1]).strip()

        return {
            "name": name,
            "amount": amount,
            "category": "income",
            "type": "income",
            "created_at": datetime.now().replace(microsecond=0).isoformat()
        }
    except (ValueError, IndexError):
        return None