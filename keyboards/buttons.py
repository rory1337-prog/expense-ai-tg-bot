BUTTONS = {
    "add_expense": {
        "en": "➕ Add expense",
        "ru": "➕ Добавить расход",
        "pl": "➕ Dodaj wydatek",
    },

    "reports": {
        "en": "📊 Reports",
        "ru": "📊 Отчёты",
        "pl": "📊 Raporty",
    },

    "edit": {
        "en": "✏️ Edit",
        "ru": "✏️ Изменить",
        "pl": "✏️ Edytuj",
    },

    "settings": {
        "en": "⚙️ Settings",
        "ru": "⚙️ Настройки",
        "pl": "⚙️ Ustawienia",
    },

    "help": {
        "en": "ℹ️ Help",
        "ru": "ℹ️ Помощь",
        "pl": "ℹ️ Pomoc",
    },
}


def b(key, lang="en"):
    return BUTTONS.get(key, {}).get(lang, key)