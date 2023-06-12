from django.shortcuts import render
from rest_framework import generics
from rest_framework import mixins

from article.models import Comment
from article.serializers import CommentSerializer

# Create your views here.

'''
작성자 :김은수
내용 : 댓글의 생성과 조회가 가능함
최초 작성일 : 2023.06.08
업데이트 일자 : 2023.06.09
'''
class CommentView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    

'''
작성자 :김은수
내용 : 댓글의 수정과 삭제가 가능함
최초 작성일 : 2023.06.07
업데이트 일자 : 2023.06.09
'''  
class CommentViewByArticle(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

