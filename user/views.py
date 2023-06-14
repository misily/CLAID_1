from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from my_settings import GOOGLE_API_KEY
from user.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status, permissions
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from user.serializers import UserSerializer, MyTokenObtainPairSerializer, CustomTokenObtainPairSerializer
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from user.tokens import account_activation_token
import traceback
from django.shortcuts import redirect, render
from .models import User
from article.models import Article

from django.core.mail import send_mail

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


class UserSignupView(APIView):
# 작성자 : 공민영
# 내용 : 회원가입
# 최초 작성일 : 2023.06.08
# 업데이트 일자 : 2023.06.08
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "인증메일을 발송했습니다."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message":f"${serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
# 작성자 : 공민영
# 내용 : 로그인
# 최초 작성일 : 2023.06.08
# 업데이트 일자 : 2023.06.08
    serializer_class = MyTokenObtainPairSerializer


class UserActivate(APIView):
    permission_classes = [AllowAny]
# 작성자 : 공민영
# 내용 : 이메일 인증
# 최초 작성일 : 2023.06.08
# 업데이트 일자 : 2023.06.08
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(User, pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user=None

        try:
            if user is not None and account_activation_token.check_token(user, token):
                user.is_active = True
                user.save()
                return redirect('user:success')
            else:
                return Response({"message":"만료된 토큰"}, status=status.HTTP_408_REQUEST_TIMEOUT)
        
        except Exception as e:
            print(traceback.format_exc())

# 작성자 : 공민영
# 내용 : 이메일 성공시
# 최초 작성일 : 2023.06.08
# 업데이트 일자 : 2023.06.08
def active_success(request):
    return render(request, "email_active.html")



class UserLogoutView(APIView):
# 작성자 : 공민영
# 내용 : 로그아웃
# 최초 작성일 : 2023.06.08
# 업데이트 일자 : 2023.06.08
    def post(self, request):
        response = Response({"message": "로그아웃 완료"}, status=status.HTTP_200_OK)
        response.delete_cookie("access")
        response.delete_cookie("refresh")

