from repositories.user_settings import UserSettingsRepository


class SettingsService:
    @staticmethod
    def get_user_settings(chat_id):
        settings = UserSettingsRepository.get_by_chat_id(str(chat_id))

        if not settings:
            settings = UserSettingsRepository.create(str(chat_id))

        return {
            "language": settings.language,
            "currency": settings.currency,
        }

    @staticmethod
    def set_user_language(chat_id, language):
        settings = UserSettingsRepository.get_by_chat_id(str(chat_id))

        if not settings:
            settings = UserSettingsRepository.create(str(chat_id))

        settings.language = language
        UserSettingsRepository.update(settings)

    @staticmethod
    def set_user_currency(chat_id, currency):
        settings = UserSettingsRepository.get_by_chat_id(str(chat_id))

        if not settings:
            settings = UserSettingsRepository.create(str(chat_id))

        settings.currency = currency
        UserSettingsRepository.update(settings)

    @staticmethod
    def ensure_user_settings(chat_id, language="en", currency="PLN"):
        settings = UserSettingsRepository.get_by_chat_id(str(chat_id))

        if not settings:
            UserSettingsRepository.create(
                str(chat_id),
                language=language,
                currency=currency,
            )
