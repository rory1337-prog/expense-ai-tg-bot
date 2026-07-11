from locales.en import TEXTS as EN_TEXTS
from locales.pl import TEXTS as PL_TEXTS
from locales.ru import TEXTS as RU_TEXTS

LOCALES = {"en": EN_TEXTS, "ru": RU_TEXTS, "pl": PL_TEXTS}


def t(key, lang="en"):
    return LOCALES.get(lang, EN_TEXTS).get(key, key)


def detect_language(language_code):
    if not language_code:
        return "en"

    language_code = language_code.lower()

    if language_code.startswith("ru"):
        return "ru"

    if language_code.startswith("pl"):
        return "pl"

    return "en"
