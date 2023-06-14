from django.contrib import admin
from django.urls import path, include
from user import views

urlpatterns = [
    path('google/', views.GoogleLogin.as_view(), name='googlelogin'),
    path('google/callback/', views.GoogleLogin.as_view(), name='googlelogin'),
]
