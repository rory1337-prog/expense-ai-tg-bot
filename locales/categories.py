CATEGORY_TRANSLATIONS = {
    "food": {
        "en": "Food",
        "ru": "Еда",
        "pl": "Jedzenie",
    },

    "groceries": {
        "en": "Groceries",
        "ru": "Продукты",
        "pl": "Produkty",
    },

    "transport": {
        "en": "Transport",
        "ru": "Транспорт",
        "pl": "Transport",
    },

    "shopping": {
        "en": "Shopping",
        "ru": "Шопинг",
        "pl": "Zakupy",
    },

    "health": {
        "en": "Health",
        "ru": "Здоровье",
        "pl": "Zdrowie",
    },

    "entertainment": {
        "en": "Entertainment",
        "ru": "Развлечения",
        "pl": "Rozrywka",
    },

    "bills": {
        "en": "Bills",
        "ru": "Счета",
        "pl": "Rachunki",
    },

    "services": {
        "en": "Services",
        "ru": "Сервисы",
        "pl": "Usługi",
    },

    "education": {
        "en": "Education",
        "ru": "Образование",
        "pl": "Edukacja",
    },

    "other": {
        "en": "Other",
        "ru": "Другое",
        "pl": "Inne",
    },
}

def localize_category(category_key, lang="en"):
    category = CATEGORY_TRANSLATIONS.get(category_key)

    if not category:
        return category_key

    return category.get(lang, category_key)