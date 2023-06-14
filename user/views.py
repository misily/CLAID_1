from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from my_settings import GOOGLE_API_KEY
from user.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from user.serializers import CustomTokenObtainPairSerializer

import requests



'''
작성자 :김은수
내용 : 소셜 로그인
최초 작성일 : 2023.06.13
업데이트 일자 : 2023.06.13
'''  
def SocialLogin(** kwargs):
    data = {k: v for k, v in kwargs.items() if v is not None}
    email = data.get('email')
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        new_user = User.objects.create(**data)
        # pw는 사용불가로 지정
        new_user.set_unusable_password()
        new_user.save()
        # 이후 토큰 발급해서 프론트로
        refresh = RefreshToken.for_user(new_user)
        access_token = CustomTokenObtainPairSerializer.get_token(new_user)
        return Response(
            {"refresh": str(refresh), "access": str(access_token.access_token)},
            status=status.HTTP_200_OK,
        )

'''
작성자 :김은수
내용 : 구글 로그인
최초 작성일 : 2023.06.12
업데이트 일자 : 2023.06.13
'''  
class GoogleLogin(APIView):

    def get(self, request):
        return Response(GOOGLE_API_KEY, status=status.HTTP_200_OK)
    
    def post(self, request):
        access_token = request.data["access_token"]
        user_data = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_data = user_data.json()
        data = {
            "email": user_data.get("email"),
            "login_type": "google",
        }
        print(user_data)
        return SocialLogin(**data)
    
# class GoogleCallback(APIView):
