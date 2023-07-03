from django.apps import AppConfig


class SeparatorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "separator"

    '''
    작성자 : 이준영
    내용 : Celery 앱 등록
    작성일 : 2023.07.02
    '''
    def ready(self):
        from separator.tasks import app as celery_app
        self.celery_app = celery_app