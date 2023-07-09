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
수정자 : 이준영
내용 : 도메인 더 싱크
수정일 : 2023.07.08
'''
domain = os.environ.get('domain')
if domain == '127.0.0.1':
    domain = 'http://127.0.0.1:8000'

'''
작성자 : 이준영
내용 : 노래 업로드 함수와 연결
최초 작성일 : 2023.06.20
수정자 : 이준영
내용 : 비동기 수정
수정일 : 2023.07.02
수정자 : 이준영
내용 : 중복 자료 예외 처리
수정일 : 2023.07.03
수정자 : 이준영
내용 : 중복 자료 예외 폴더로
수정일 : 2023.07.08
'''
class UploadFileView(APIView):
    permission_classes = [IsAuthenticated]  
    
    def post(self, request, format=None):
        audio_file = request.FILES.get("file")
        if not audio_file:
            return Response({'message': '파일이 업로드되지 않았습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        file_name = audio_file.name

        if SeparationResult.objects.filter(Q(file_name=file_name) & ~Q(state='error')).exists():
            return Response({'message': '중복된 자료입니다.'}, status=status.HTTP_409_CONFLICT)
        
        result = SeparationResult.objects.create(
            user=request.user,
            file_name=file_name,
            audio_file=audio_file,
            state='waiting',
        )
        
        separate_audio_task.delay(result.id)
        
        return Response({'result_id': result.id}, status=status.HTTP_201_CREATED)

'''
작성자 : 이준영
내용 : 유동적 url을 위해 커스텀 페이지네이션 추가
작성일 : 2023.07.09
'''
class CustomPageNumberPagination(PageNumberPagination):
    def get_next_link(self):
        if not self.page.has_next():
            return None
        return domain + '/separator/converted-files/?page=' + str(self.page.next_page_number())

    def get_previous_link(self):
        if not self.page.has_previous():
            return None
        return domain + '/separator/converted-files/?page=' + str(self.page.previous_page_number())

    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'results': data
        })

'''
작성자 : 이준영
내용 : 결과 확인
최초 작성일 : 2023.06.30
수정자 : 이준영
수정 내용 : 비동기 처리, 상세보기 추가, 페이지네이션, 삭제
수정일 : 2023.07.03
수정자 : 이준영
수정 내용 : 유동적 url을 위해 커스텀 페이지네이션 사용,
            삭제 오류 시 오류 출력 후 다음 삭제 독립적 시행
수정일 : 2023.07.09
'''
class ConvertedFilesView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination()

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
        
        paths = []
        if hasattr(file, 'audio_file') and file.audio_file:
            paths.append(file.audio_file.path)
        if hasattr(file, 'vocals_path') and file.vocals_path:
            paths.append(file.vocals_path)
        if hasattr(file, 'accompaniment_path') and file.accompaniment_path:
            paths.append(file.accompaniment_path)

        for path in paths:
            try:
                if os.path.isfile(path):
                    os.remove(path)
            except Exception as e:
                print(f"Failed to delete {path}: {str(e)}")
                
        file.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
