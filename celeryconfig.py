import os
from celery import Celery
from django.conf import settings
import dotenv

# .env 파일 로드
dotenv.read_dotenv()

# Celery settings
'''
작성자 : 이준영
내용 : celery settings
작성일 : 2023.07.01
'''
BROKER_URL = 'amqp://guest:guest@localhost:5672//'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CLAID.settings')

app = Celery('config')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

CELERY_RESULT_BACKEND = 'django-db'

# Worker 설정
# app.conf.worker_prefetch_multiplier = 1
# app.conf.worker_max_tasks_per_child = 1

# ----------
# CELERY_BROKER_URL = 'amqp://guest:guest@localhost'

# #: Only add pickle to this list if your broker is secured
# #: from unwanted access (see userguide/security.html)
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_RESULT_BACKEND = 'db+sqlite:///results.sqlite'
# CELERY_TASK_SERIALIZER = 'json'


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')