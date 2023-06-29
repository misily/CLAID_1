from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from spleeter.separator import Separator
from django.conf import settings
import os

domain = os.environ.get('domain')

def handle_uploaded_file(f):
    file_name = f.name.replace(' ', '').replace('.mp3', '')
    file_path = os.path.join(settings.MEDIA_ROOT, file_name + '.mp3')
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return file_name

def separate_audio(file_name):
    separator = Separator('spleeter:2stems')
    file_path = os.path.join(settings.MEDIA_ROOT, file_name + '.mp3')
    output_path = os.path.join(settings.MEDIA_ROOT, 'output')
    separator.separate_to_file(file_path, output_path)
    
    vocals_path = os.path.join(output_path, f'{file_name}/vocals.wav')
    accompaniment_path = os.path.join(output_path, f'{file_name}/accompaniment.wav')
    
    # 개발 서버 주소에 맞게 경로 수정
    vocals_path = vocals_path.replace(settings.MEDIA_ROOT, 'http://'+domain+'/media').replace("\\", "/")
    accompaniment_path = accompaniment_path.replace(settings.MEDIA_ROOT, 'http://'+domain+'/media').replace("\\", "/")
    
    return {
        'vocals': vocals_path,
        'accompaniment': accompaniment_path
        }

class UploadFileView(APIView):
    permission_classes = [IsAuthenticated]  
    def post(self, request, format=None):
        file_name = handle_uploaded_file(request.FILES["file"])
        files = separate_audio(file_name)
        return Response({'files': files}, status=201)
    