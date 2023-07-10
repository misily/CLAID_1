from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers
from user.models import User, Profile, Point, PointHistory

from article.models import Article
from django.core.mail import EmailMessage
from CLAID import settings
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from article.serializers import ArticleSerializer
from user.tokens import account_activation_token
import os

from threading import Thread
    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["login_type"] = user.login_type
        return token


class SNSUserSerializer(serializers.ModelSerializer):
    '''
    작성자 : 이준영
    내용 : 일반 로그인 기능 구현 전 sns 로그인
    최초 작성일 : 2023.06.14
    '''
    class Meta:
        model = User
        fields = "__all__"
    
    def create(self, validated_data):        
        user = super().create(validated_data)
        user.save()        
        return user
    
    def update(self, instance, validated_data):
        user = super().update(instance, validated_data)
        user.save()
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
    '''
    작성자 : 공민영
    내용 : 회원가입
    최초 작성일 : 2023.06.08
    내용 : 이메일 전송 비동기 처리함
    업데이트 일자 : 2023.06.29
    수정자 : 이준영
    내용 : domain이 동적이지 않아서 핫픽스
    업데이트 일자 : 2023.07.10
    '''
    def send_email(self, user):
        message = (
                "안녕하세요, {nickname}님!\n\n"
                "회원가입 인증을 완료하려면 다음 링크를 클릭해주세요:\n"
                "{domain}/user/activate/{uid}/{token}\n\n"
                "---\n"
                "감사합니다!"
                ).format(
                    nickname=user.nickname,
                    domain= os.environ.get("domain"),
                    uid=urlsafe_base64_encode(force_bytes(user.pk)),
                    token=account_activation_token.make_token(user),
                )

        subject = "회원가입 인증 메일입니다."
        to = [user.email]
        from_email = settings.DEFAULT_FROM_EMAIL
        EmailMessage(subject=subject, body=message, to=to, from_email=from_email).send()

    def create(self, validated_data):
        user = super().create(validated_data)
        user.is_active = False
        password = user.password
        # 비밀번호 암호화
        user.set_password(password)
        user.save()

        # 이메일 발송 작업을 새로운 스레드에서 실행
        email_thread = Thread(target=self.send_email, args=(user,))
        email_thread.start()
        
        return user

    
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    '''
    작성자 : 공민영
    내용 : 토큰
    최초 작성일 : 2023.06.08
    수정자 : 이준영
    내용 : 커스텀 토큰 페이로드 추가
    업데이트 일자 : 2023.06.14
    '''
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["id"] = user.id
        token["email"] = user.email
        token["login_type"] = user.login_type
        token["sns_id"] = user.sns_id
        token["nickname"] = user.nickname
        token["profile_image"] = str(user.profile_image)
        token["is_active"] = user.is_active
        token["is_admin"] = user.is_admin
        return token
    
    def get_user(self, validated_data):
        user = self.user
        return user
    
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['nickname', 'profile_image']

class PointSerializer(serializers.ModelSerializer):
    '''
    작성자 : 공민영
    내용 : 포인트 지급, 차감
    최초 작성일 : 2023.07.02
    '''
    user_email = serializers.SerializerMethodField()

    def get_user_email(self, obj):
        return obj.user.email
    
    class Meta:
        model = Point
        fields = ['user_email', 'user', 'points']

class PointHistorySerializer(serializers.ModelSerializer):
    '''
    작성자 : 공민영
    내용 : 일반계정 포인트 지급, 차감 관련된 히스토리
    최초 작성일 : 2023.07.02
    '''
    class Meta:
        model = PointHistory
        fields = ['point_change', 'reason', 'created_at']

class SuperPointHistorySerializer(serializers.ModelSerializer):
    '''
    작성자 : 공민영
    내용 : 슈퍼계정 포인트 지급, 차감 관련된 히스토리
    최초 작성일 : 2023.07.02
    '''
    user_email = serializers.SerializerMethodField()

    def get_user_email(self, obj):
        return obj.user.email
    
    class Meta:
        model = PointHistory
        fields = ['user_email', 'user', 'point_change', 'reason', 'created_at']