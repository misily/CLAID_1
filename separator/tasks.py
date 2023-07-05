from celery import shared_task
from celery.utils.log import get_task_logger
from .utils import handle_uploaded_file, separate_audio
from separator.models import SeparationResult
from celery import Celery

app = Celery('myapp')
logger = get_task_logger(__name__)
# app.config_from_object('celeryconfig')
@shared_task
def separate_audio_task(file_name):
    result = {}
    try:
        result = SeparationResult.objects.get(file_name=file_name)
        result.state = 'working'
        result.save()
        
        # 파일 처리 작업을 수행
        audio_files = separate_audio(file_name)
        
        # 분리된 음원 파일 경로를 업데이트
        result.vocals_path = audio_files['vocals']
        result.accompaniment_path = audio_files['accompaniment']
        result.state = 'success'
        result.save()

        logger.info(f"Audio separation completed: {file_name}")

    except Exception as e:
        result = SeparationResult.objects.get(file_name=file_name)
        result.state = 'error'
        result.save()
        logger.error(f"Audio separation error: {file_name}. Error: {e}")
