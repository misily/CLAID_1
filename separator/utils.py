from django.conf import settings
from django.shortcuts import get_object_or_404
from spleeter.separator import Separator
import os
from .models import SeparationResult
from celery.utils.log import get_task_logger

'''
작성자 : 이준영
내용 : 도메인 싱크
최초 작성일 : 2023.06.30
수정자 : 이준영
내용 : 도메인 더 싱크
수정일 : 2023.07.08
'''
domain = os.environ.get('domain')
if domain == '127.0.0.1':
    domain = 'http://127.0.0.1:8000'
    
'''
작성자 : 이준영
내용 : 오디오 분리 비동기 처리
작성일 : 2023.07.02
수정자 : 이준영
내용 : 효율적으로 분류 하기 위해 result_id를 씀,
    tasks.py에서 가져 와 통합, 예외 처리,
    경로가 맞지 않는 문제를 해결
수정일 : 2023.07.08
'''
logger = get_task_logger(__name__)

def separate_audio(result_id):
    result = get_object_or_404(SeparationResult, id=result_id)
    
    try:
        logger.info(f"Audio separation working: {result.file_name}")
        result.state = 'working'
        result.save()
        
        separator = Separator('spleeter:2stems')
        
        file_path = result.audio_file.path

        output_path = os.path.dirname(file_path)
        logger.info(f"output_path: {output_path}")
        separator.separate_to_file(file_path, output_path, codec="mp3", bitrate="128k")
        
        file_name = result.file_name.replace(' ', '_').replace('(', '').replace(')', '')
        vocals_path = os.path.join(output_path, f'{file_name}/vocals.mp3')
        logger.info(f"vocals_path: {vocals_path}")
        accompaniment_path = os.path.join(output_path, f'{file_name}/accompaniment.mp3')
        logger.info(f"accompaniment_path: {accompaniment_path}")
        
        vocals_url = domain + '/media' + vocals_path.replace(settings.MEDIA_ROOT, '').replace("\\", "/")
        logger.info(f"vocals_url: {vocals_url}")
        accompaniment_url = domain + '/media' + accompaniment_path.replace(settings.MEDIA_ROOT, '').replace("\\", "/")   
        logger.info(f"accompaniment_url: {accompaniment_url}")     
        
        logger.info(f"Original Audio file remove: {result.file_name}")
        os.remove(file_path)

        result.vocals_path = vocals_url
        result.accompaniment_path = accompaniment_url
        result.state = 'success'
        result.save()
        
        logger.info(f"Audio separation completed: {result.file_name}")
        
    except Exception as e:
        logger.error(f"Audio separation failed: {result.id}. {result.file_name}. Error: {e}")
        result.state = 'error'
        result.save()
        
        # 오류 발생 시 현재의 함수 실행은 멈추고, 이 함수를 호출한 celery로 예외가 전달
        raise e
