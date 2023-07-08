from celery import shared_task
from celery.utils.log import get_task_logger
from .utils import separate_audio
from celery import Celery

'''
작성자 : 이준영
내용 : 오디오 분리 비동기 작업
수정일 : 2023.07.02
수정자 : 이준영
내용 : docs 추가
    file_name으로 중복될 수 있어 result_id로 바꿈
    utils.py로 통합
수정일 : 2023.07.08
'''
app = Celery('tasks')
logger = get_task_logger(__name__)
# app.config_from_object('celeryconfig')

@shared_task
def separate_audio_task(result_id):
    try:
        logger.info(f"Audio separation started: {result_id}")
        separate_audio(result_id)
        logger.info(f"Audio separation completed: {result_id}")
    except Exception as e:
        logger.error(f"Audio separation task failed: {e}")
