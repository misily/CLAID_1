from django.contrib import admin
from django.urls import path, include
from article import views

urlpatterns = [
    path('commentcr/', views.CommentView.as_view(), name='CommentforTest'),
    path('commentud/<int:pk>/', views.CommentView.as_view(), name='CommentforTest'),
]
