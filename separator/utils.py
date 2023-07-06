from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from spleeter.separator import Separator
import os

'''
작성자 : 이준영
내용 : 비동기 처리를 위한 노래 업로드, 쓰이진 않았지만 만약을 위해 남겨둠.
수정일 : 2023.07.02
'''
def handle_uploaded_file(f):
    file_name = f.name.replace(' ', '').replace('.mp3', '')
    file_path = os.path.join(settings.MEDIA_ROOT, file_name + '.mp3')
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return file_name

'''
작성자 : 이준영
내용 : 비동기 처리를 위한 오디오 분리
수정일 : 2023.07.02
'''
def separate_audio(file_name):
    domain = os.environ.get('domain')
    if domain == '127.0.0.1':
        domain += ':8000'
        
    separator = Separator('spleeter:2stems')
    file_path = os.path.join(settings.MEDIA_ROOT, file_name + '.mp3')
    output_path = os.path.join(settings.MEDIA_ROOT, 'output')
    separator.separate_to_file(file_path, output_path, codec="mp3", bitrate="128k")
    
    vocals_path = os.path.join(output_path, f'{file_name}/vocals.mp3')
    accompaniment_path = os.path.join(output_path, f'{file_name}/accompaniment.mp3')
    
    vocals_path = vocals_path.replace(settings.MEDIA_ROOT, domain + '/media').replace("\\", "/")
    accompaniment_path = accompaniment_path.replace(settings.MEDIA_ROOT, domain + '/media').replace("\\", "/")
    
    os.remove(file_path)
    
    return {
        'vocals': vocals_path,
        'accompaniment': accompaniment_path
    }
