from django.apps import AppConfig


class ProblemsConfig(AppConfig):
    name = "problems"

    def ready(self):
        import problems.signals  # noqa: F401
