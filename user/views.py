import requests, traceback

from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.core.mail import send_mail

from user.models import User
from user.tokens import account_activation_token
from user.serializers import UserSerializer, MyTokenObtainPairSerializer, CustomTokenObtainPairSerializer

from CLAID.settings import SOCIAL_OUTH_CONFIG

from article.models import Article

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status, permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.generics import get_object_or_404


GOOGLE_API_KEY = SOCIAL_OUTH_CONFIG['GOOGLE_API_KEY']


def SocialLogin(** kwargs):
    '''
    작성자 :김은수
    내용 : 소셜 로그인
    최초 작성일 : 2023.06.13
    업데이트 일자 : 2023.06.13
    '''  
    data = {k: v for k, v in kwargs.items() if v is not None}
    email = data.get('email')
    try:
        user = User.objects.get(email=email)
        return Response(
            {"refresh": str(refresh), "access": str(access_token.access_token)},
            status=status.HTTP_200_OK,
        )
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


class GoogleLogin(APIView):
    permission_classes = [AllowAny]
    '''
    작성자 :김은수
    내용 : 구글 로그인
    최초 작성일 : 2023.06.12
    업데이트 일자 : 2023.06.13
    '''  
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

        return SocialLogin(**data)
    

'''
작성자 : 이준영
내용 : KAKAO_KEYS
최초 작성일 : 2023.06.14
'''
KAKAO_REST_API_KEY = SOCIAL_OUTH_CONFIG['KAKAO_REST_API_KEY']
KAKAO_REDIRECT_URL = SOCIAL_OUTH_CONFIG['KAKAO_REDIRECT_URL']
KAKAO_SECRET_KEY = SOCIAL_OUTH_CONFIG['KAKAO_SECRET_KEY']
KAKAO_ADMIN_KEY = SOCIAL_OUTH_CONFIG['KAKAO_ADMIN_KEY']
KAKAO_LOGOUT_REDIRECT_URL = SOCIAL_OUTH_CONFIG['KAKAO_LOGOUT_REDIRECT_URL']

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
        return response
    
    
class KakaoCallBackView(APIView):
    '''
    작성자 : 이준영
    내용 : 프론트에서 받은 카카오 code를 받아 최종으로 JWT 토큰을 받으며 로그인
    최초 작성일 : 2023.06.14
    '''
    permission_classes = [AllowAny]
    
    def get(self, request):
        '''
        작성자 : 이준영
        내용 : 카카오 code를 받아 카카오 Token을 받는다.
        최초 작성일 : 2023.06.14
        '''
        code = request.GET.get('code')
        
        kakao_token_api = 'https://kauth.kakao.com/oauth/token'
        data = {
            'grant_type' : 'authorization_code',
            'client_id' : KAKAO_REST_API_KEY,
            'redirection_url' : KAKAO_REDIRECT_URL,
            'code' : code,
            'client_secret' : KAKAO_SECRET_KEY,
        }
        headers = {'Content-type': 'application/x-www-form-urlencoded;charset=utf-8'}        
        token_response = requests.post(kakao_token_api, data=data, headers=headers)        
        
        access_token = token_response.json().get('access_token')
        expires_in = token_response.json().get('expires_in')
        refresh_token = token_response.json().get('refresh_token')
        refresh_token_expires_in = token_response.json().get('refresh_token_expires_in')
        
        '''
        작성자 : 이준영
        내용 : 카카오 Token으로 사용자 정보를 받고,
        신규, 기존 사용자를 식별하여
        카카오 Token과 정보를 DB에 저장
        최초 작성일 : 2023.06.14
        '''
        user_data = requests.post(
            "https://kapi.kakao.com/v2/user/me",
            headers={
                    "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
                    "Authorization": f"Bearer {access_token}",
                    # "Access-Control-Allow-Origin": "http://127.0.0.1:5500/kakao.html",
            },
        )
        
        user_data = user_data.json()

        email = user_data.get("kakao_account").get("email")
        sns_id = user_data.get('id')
        nickname = user_data.get('properties').get('nickname')
        profile_image = user_data.get('properties').get('profile_image')
        
        kakao_data  = {
            "email" : email,
            "login_type": "kakao",
            "sns_id" : sns_id,
            "nickname" : nickname,
            "profile_image" : profile_image,
            "access_token" : access_token,
            "expires_in" : expires_in,
            "refresh_token" : refresh_token,
            "refresh_token_expires_in" : refresh_token_expires_in,
        }
        
        try:
            kakao_user, created = User.objects.get_or_create(email=email, defaults=kakao_data)
            if created:
                message = "신규 유저 정보 생성!"
                response_status = status.HTTP_200_OK
            else:
                serializer = UserSerializer(kakao_user, data=kakao_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    message = "기존 유저 정보 업데이트!"
                    response_status = status.HTTP_200_OK
                else:
                    return Response({"message": {serializer.errors}}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": "DB 저장 오류입니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        '''
        작성자 : 이준영
        내용 : 사용자 정보로 JWT Token을 만들어 커스텀해서 보내줌.
        최초 작성일 : 2023.06.14
        '''
        kakao_user = User.objects.get(email=email)
        
        token = MyTokenObtainPairSerializer.get_token(kakao_user)
        
        # JWT 토큰을 문자열로 변환
        access_token = str(token.access_token)        
        refresh_token = str(token)

        # OpenID connect 사용해요?

        # 오류 등을 try 로 나누고 return이나 response도 나누기
        
        # response에 답기
        response_data = {'message': message, 'access_token': access_token, 'refresh_token': refresh_token}
        return Response(response_data, status=response_status)
