from django.test import TestCase
from django.urls import reverse # url 가져올때
from rest_framework.test import APITestCase
from rest_framework import status
from user.models import User
from user.serializers import UserSerializer

# from .tokens import account_activation_token
# from django.utils.http import urlsafe_base64_encode, force_bytes, force_str, urlsafe_base64_decode
# from django.utils.encoding import force_bytes, force_text

# from django.core import mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token

from faker import Faker


#회원가입 테스트
class UserRegistrationTest(APITestCase):
    def setUp(self):
        url = reverse("user:signup")  # url에 name을 이용하여 해당 path를 가져옴 # user: 안쓰니까 에러남!!!
        self.faker = Faker()
        self.user_data = {
            "email": self.faker.unique.email(),
            "nickname": self.faker.name(),
            "password": self.faker.word(),
        }
        response = self.client.post(url, self.user_data)  # post에 url과 user_data 담아줌
        print(response.data['access'])
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["message"], "인증메일을 발송했습니다.") #응답 데이터의 "message" 키를 확인하여 "인증메일을 발송했습니다." 메시지가 있는지 확인

#회원가입 이메일 인증 테스트
class UserActivateTest(APITestCase):
    @classmethod
    def tearDown(cls):
        User.objects.all().delete()  # 테스트 전에 데이터베이스를 정리합니다.

    @classmethod
    def setUpTestData(cls):
        cls.faker = Faker()
        cls.user_data = {
            "email": cls.faker.unique.email(),
            "nickname": cls.faker.name(),
            "password": cls.faker.word(),
        }
        cls.user = User.objects.create_user(**cls.user_data)

    def test_user_signup(self):
        
        # 회원가입
        serializer = UserSerializer(data=self.user_data)
        if not serializer.is_valid():
            print(serializer.errors)
            self.fail("UserSerializer에서 유효하지 않은 데이터")

        # 액티베이션 링크를 클릭함
        user = serializer.save()  # 데이터 저장

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)

        response = self.client.get(f'/user/activate/{uid}/{token}')

        # 결과 확인, 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # 408(만료된 토큰)로 뜸
    # def test_user_activate(self):
    #     request = self.client
    #     force_authenticate(request, user=self.user)
    #     valid_token = "실제유효한 토큰 값 넣어주기(테스트용으로 토큰을 생성하는 것은 권장되지 않음)"
    #     # uid = "실제유효한 uid64 값 넣어주기"
    #     # url = reverse('user:activate', args=[uid, valid_token])
    #     url = reverse('user:activate', args=[self.user.email, valid_token])
    #     response = self.client.get(url)

    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data["message"], "이메일 인증이 완료되었습니다.")

# 로그인 테스트
class LoginUserTest(APITestCase):
    def setUp(self): # 모든 테스트 메소트 처음에 실행
        
        self.data = {"email":"test@test.com", "nickname": "test", "password":"1234"}
        self.user = User.objects.create_user("test@test.com","test","1234")  # create_user는 models.py에 설정해준 메소드
    
    # 일반 로그인 확인    
    def test_login(self):
        response = self.client.post(reverse('user:token_obtain_pair'), self.data)
        print("access: ",response.data['access'])
        self.assertEqual(response.status_code, 200)
    
    # 구글 로그인 확인    
    def google_login(self):
        response = self.client.post(reverse('user:googlelogin'), self.data)
        self.assertEqual(response.status_code, 200)

    # 카카오 로그인 확인    
    def kakao_login(self):
        response = self.client.post(reverse('user:kakaologin'), self.data)
        self.assertEqual(response.status_code, 200)

    # 일반 회원 정보 가져오기   
    def test_get_user_data(self):
        access_token = self.client.post(reverse('user:token_obtain_pair'), self.data).data['access']
        response = self.client.get(
            path=reverse('user:user_view'),
            HTTP_AUTHORIZATION = f"Bearer {access_token}"
        )
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.data['nickname'], self.data['nickname'])

    # 구글 회원 정보 가져오기   
    def google_get_user_data(self):
        access_token = self.client.post(reverse('user:googlelogin'), self.data).data['access']
        response = self.client.get(
            path=reverse('user:googlelogin'),
            HTTP_AUTHORIZATION = f"Bearer {access_token}"
        )
        self.assertEqual(response.status_code, 200)
    
    # 카카오 회원 정보 가져오기   
    def kakao_get_user_data(self):
        access_token = self.client.post(reverse('user:kakaologin'), self.data).data['access']
        response = self.client.get(
            path=reverse('user:kakaocallback'),
            HTTP_AUTHORIZATION = f"Bearer {access_token}"
        )
        print("response",response.data)
        self.assertEqual(response.status_code, 200)
        