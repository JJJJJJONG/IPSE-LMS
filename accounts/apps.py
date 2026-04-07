from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        """
        Django 앱 레지스트리가 완전히 로드된 후 실행되는 초기화 메서드.
        여기서 signals 모듈을 임포트해야 안전하게 옵저버 패턴이 등록됩니다.
        """
        import accounts.signals