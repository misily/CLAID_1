from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from spleeter.separator import Separator
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status
import os

from .models import SeparationResult
from .tasks import separate_audio_task
from django.db.models import Q

from .serializers import SeparationResultSerializer
from rest_framework.pagination import PageNumberPagination

'''
작성자 : 이준영
내용 : 도메인 싱크
최초 작성일 : 2023.06.30
'''
domain = os.environ.get('domain')
if domain == '127.0.0.1':
    domain += ':8000'

'''
작성자 : 이준영
내용 : 노래 분리
최초 작성일 : 2023.06.20
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
내용 : 노래 업로드
최초 작성일 : 2023.06.20
수정자 : 이준영
내용 : 비동기 수정
수정일 : 2023.07.02
수정자 : 이준영
내용 : 중복 자료 예외 처리
수정일 : 2023.07.03
'''
class UploadFileView(APIView):
    permission_classes = [IsAuthenticated]  

    def post(self, request, format=None):
        file_name = handle_uploaded_file(request.FILES["file"])
        
        if SeparationResult.objects.filter(Q(file_name=file_name) & ~Q(state='error')).exists():
            return Response({'message': '중복된 자료입니다.'}, status=status.HTTP_409_CONFLICT)
        
        separate_audio_task.delay(file_name)
        result = SeparationResult.objects.create(
            user=request.user,
            file_name=file_name,
            vocals_path = 'waiting',
            accompaniment_path = 'waiting',
            state='waiting',
        )
        return Response({'result_id': result.id}, status=status.HTTP_201_CREATED)

'''
작성자 : 이준영
내용 : 결과 확인
최초 작성일 : 2023.06.30
수정자 : 이준영
수정 내용 : 비동기 처리, 상세보기 추가, 페이지네이션, 삭제
수정일 : 2023.07.03
'''
from rest_framework.renderers import JSONRenderer

class ConvertedFilesView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination()

    def get_user_converted_files(self, user):
        files = SeparationResult.objects.filter(user=user).order_by('-created_at')
        page = self.pagination_class.paginate_queryset(files, self.request)
        if page is not None:
            serializer = SeparationResultSerializer(page, many=True)
            return self.pagination_class.get_paginated_response(serializer.data)
        serializer = SeparationResultSerializer(files, many=True)
        return serializer.data

    def get(self, request, pk=None):
        if pk is None:
            response = self.get_user_converted_files(request.user)
            return response
        else:
            file = get_object_or_404(SeparationResult, id=pk)
            serializer = SeparationResultSerializer(file)
            return Response(serializer.data, status=status.HTTP_200_OK)


    def delete(self, request, pk):
        file = get_object_or_404(SeparationResult, pk=pk)
        if file.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        file.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)