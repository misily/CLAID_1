from datetime import timezone
import datetime
from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from article.models import Article
from article.serializers import ArticleSerializer, ArticleCreateSerializer
from rest_framework import status
from pathlib import Path

import json
import os


BASE_DIR = Path(__file__).resolve().parent.parent
secret_file = os.path.join(BASE_DIR,'.env')

with open(secret_file) as f:
    secrets = json.loads(f.read())


def get_secret(setting, secrets=secrets):
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {} environment variable".format(setting)
        raise error_msg
    

class ArticleView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
# 작성자 : 공민영
# 내용 : 모든 게시글 가져오기
# 최초 작성일 : 2023.06.08
# 업데이트 일자 : 2023.06.08
    def get(self, request):
        article = Article.objects.all().order_by('-created_at')
        serializer = ArticleSerializer(article, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# 작성자 : 공민영
# 내용 : 게시글 작성하기
# 최초 작성일 : 2023.06.08
# 업데이트 일자 : 2023.06.08
    def post(self, request):
        serializer = ArticleCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    

  
class ArticleDetailView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
# 작성자 : 공민영
# 내용 : 게시글 상세보기
# 최초 작성일 : 2023.06.08
# 업데이트 일자 : 2023.06.08
    def get(self, request, user_id):
        article = Article.objects.get(id = user_id)
        serializer = ArticleSerializer(article)
        return Response(serializer.data, status=status.HTTP_200_OK)

'''
작성자 :왕규원
내용 : 조회수 중복방지 기능
최초 작성일 : 2023.06.13
업데이트 일자 : 2023.06.14
'''
def retreive(self,request,pk=None):

    instance = get_object_or_404(self.get_queryset(), pk=pk)
        #당일날 밤 12시에 쿠키 초기화
    tomorrow = datetime.datetime.replace(timezone.datetime.now(), hour=23, minute=59)
    expires = datetime.datetime.strftime(tomorrow, "%a, %d-%b-%Y %H:%M:%S GMT")
        
        # response를 미리 받고 쿠키를 만들어야 한다
    serializer = self.get_serializer(instance)
    response = Response(serializer.data, status=status.HTTP_200_OK)
        # 쿠키 읽기 & 생성
    if request.COOKIES.get('hits') is not None: # 쿠키에 hit 값이 이미 있을 경우
        cookies = request.COOKIES.get('hits')
        cookies_list = cookies.split('|')
        if str(pk) not in cookies_list:
            response.set_cookie('hits', cookies+f'|{pk}', expires=expires) # 쿠키 생성
            instance.hits += 1
            instance.save()
                    
    else: # 쿠키에 hit 값이 없을 경우(즉 현재 보는 게시글이 첫 게시글)
        response.set_cookie('hits', pk, expires=expires)
        instance.hits += 1
        instance.save()

    # hits가 추가되면 해당 instance를 serializer에 표시
    serializer = self.get_serializer(instance)

    return response

# 작성자 : 공민영
# 내용 : 게시글 수정하기
# 최초 작성일 : 2023.06.08
# 업데이트 일자 : 2023.06.08
def put(self, request, user_id):
    article = Article.objects.get(id = user_id)
        # 본인이 작성한 게시글이 맞다면
    if request.user == article.user:
        serializer = ArticleCreateSerializer(article, data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # 본인의 게시글이 아니라면
    else:
        return Response({'message':'로그인 후 이용해주세요.'}, status=status.HTTP_403_FORBIDDEN)
    
# 작성자 : 공민영
# 내용 : 게시글 삭제하기
# 최초 작성일 : 2023.06.08
# 업데이트 일자 : 2023.06.08
def delete(self, request, user_id):
    article = Article.objects.get(id=user_id)
        # 본인이 작성한 게시글이 맞다면
    if request.user == article.user:
        article.delete()
        return Response({'message':'게시글이 삭제되었습니다.'}, status=status.HTTP_204_NO_CONTENT)
        # 본인의 게시글이 아니라면
    else:
        return Response({'message':'본인 게시글만 삭제 가능합니다.'}, status=status.HTTP_403_FORBIDDEN)
