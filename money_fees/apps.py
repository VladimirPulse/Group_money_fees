from django.apps import AppConfig


class MoneyFeesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "money_fees"

    def ready(self):
        import money_fees.signals  # noqa
