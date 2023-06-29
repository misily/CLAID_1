from django.test import TestCase
from django.urls import reverse # url 가져올때
from rest_framework.test import APITestCase
from rest_framework import status
from user.models import User

from article.models import Article, VocalNotice, NoticeComment, Comment
from article.serializers import VocalNoticeSerializer, ArticleSerializer, CommentSerializer, NoticeCommentSerializer

from faker import Faker

# 회원가입
class UserRegistrationTest(APITestCase):
    def setUp(self):
        url = reverse("user:signup")
        user_data = {
            "email": "pretty981210@gmail.com",
            "nickname": "minyoung",
            "password": "Zz@19960806"
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)



# 노래자랑 게시판
class AiArticleCreateTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.article_data = {
            "voice": "목소리",
            "song_info": "제목-가수",
            "article_image": "/image.png",
            "song": "/song.mp4"
        }
        cls.user_data = {
            "email": "pretty981210@gmail.com",
            "nickname" : "minyoung",
            "password": "Zz@19960806"
        }
        cls.user = User.objects.create_user("pretty981210@gmail.com","minyoung","Zz@19960806")

    # 로그인 토큰 가져오기
    def setUp(self):
        self.access_token = self.client.post(reverse('user:token_obtain_pair'), self.user_data).data['access']

    # 로그인이 안된 유저가 post 시도할때 에러
    def test_fail_if_not_logged_in(self):
        url = reverse("article_view")
        response = self.client.post(url, self.article_data)
        self.assertEqual(response.status_code, 401)

    # 노래자랑 게시판 글 작성 테스트
    def test_create_notice_article(self):
        response = self.client.post(
            path=reverse("article_view"),
            data=self.article_data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        # self.assertEqual(response.status_code, 201)
        self.assertEqual(response.status_code, 400)

# 노래자랑 게시글 읽기 테스트
class AiArticleReadTest(APITestCase):
    @classmethod
    def setUpClass(cls):
        cls.faker = Faker()
        cls.articles=[]
        for i in range(10): # 10명의 유저가 각각 하나의 게시글을 작성하도록
            cls.user = User.objects.create_user(cls.faker.email(), cls.faker.name(), cls.faker.word())
            cls.articles.append(
                Article.objects.create(
                voice=cls.faker.sentence(), 
                song_info=cls.faker.text(),
                article_image=cls.faker.text(),
                song=cls.faker.text(),
                user=cls.user,
                ))

    def test_get_ai_article(self):
        for article in self.articles:
            url = reverse("article_detail_view", kwargs={"article_id": article.pk})
            response = self.client.get(url)
            serializer = ArticleSerializer(article).data

            # 조회수 증가를 확인하기 위해 게시물 수동 조회
            original_hits = article.hits
            article.refresh_from_db()  # 게시물 조회수 새로고침

            # 조회수가 1만큼 증가하는지 확인
            self.assertEqual(article.hits, original_hits + 1)

            # created 필드를 제외한 필드 목록 생성
            compare_fields = [field for field in serializer.keys() if field != "created_at" and field != "updated_at"]

             # compare_fields에 있는 필드만 비교
            for key in compare_fields:
                if key == 'hits':
                    # 조회수 필드의 경우, 값이 기존 조회수 + 1과 같아야 합니다.
                    self.assertEqual(response.data[key], original_hits + 1)
                else:
                    self.assertEqual(response.data[key], serializer[key])

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
    @classmethod
    def tearDownClass(cls):
        pass

# 노래자랑 게시글 수정 테스트
class NoticeArticlePatchTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {
            "email": "pretty981210@gmail.com",
            "nickname" : "minyoung",
            "password": "Zz@19960806"
        }
        cls.article_data = {
            "voice": "목소리",
            "song_info": "제목-가수",
            "article_image": "/image.png",
            "song": "/song.mp4"
        }
        cls.faker = Faker()
        cls.article = []
        cls.user = User.objects.create_user("pretty981210@gmail.com","minyoung","Zz@19960806")
        cls.article.append(
                VocalNotice.objects.create(
                title=cls.faker.sentence(), 
                content=cls.faker.text(), 
                user=cls.user,
                ))

    def setUp(self):
        self.access_token = self.client.post(reverse('user:token_obtain_pair'), self.user_data).data['access']

    # 노래자랑 게시글 수정
    def test_patch_notice(self):
        patch_url = reverse('article_detail_view', kwargs={"article_id":self.article[0].pk})
        response = self.client.patch(patch_url, HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        self.assertEqual(response.status_code, 200)


# 노래자랑 게시글 삭제 테스트
class NoticeArticlePatchTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {
            "email": "pretty981210@gmail.com",
            "nickname" : "minyoung",
            "password": "Zz@19960806"
        }
        cls.article_data = {
            "voice": "목소리",
            "song_info": "제목-가수",
            "article_image": "/image.png",
            "song": "/song.mp4"
        }
        cls.faker = Faker()
        cls.article = []
        cls.user = User.objects.create_user("pretty981210@gmail.com","minyoung","Zz@19960806")
        cls.article.append(
                VocalNotice.objects.create(
                title=cls.faker.sentence(), 
                content=cls.faker.text(), 
                user=cls.user,
                ))

    def setUp(self):
        self.access_token = self.client.post(reverse('user:token_obtain_pair'), self.user_data).data['access']

    # 노래자랑 게시글 삭제
    def test_delete_notice(self):
        delete_url = reverse('article_detail_view', kwargs={"article_id": self.article[0].pk})
        response = self.client.delete(delete_url, HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        self.assertEqual(response.status_code, 204)








# 방법공유 게시판
class NoticeArticleCreateTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.article_data = {
            "title": "제목",
            "content": "내용"
        }
        cls.user_data = {
            "email": "pretty981210@gmail.com",
            "nickname" : "minyoung",
            "password": "Zz@19960806"
        }
        cls.user = User.objects.create_user("pretty981210@gmail.com","minyoung","Zz@19960806")

    # 로그인 토큰 가져오기
    def setUp(self):
        self.access_token = self.client.post(reverse('user:token_obtain_pair'), self.user_data).data['access']

    #로그인이 안된 유저가 post 시도할때 에러
    def test_fail_if_not_logged_in(self):
        url = reverse("vocal_notice_view")
        response = self.client.post(url, self.article_data)
        self.assertEqual(response.status_code, 401)

    # 방법공유 게시판 글 작성 테스트
    def test_create_notice_article(self):
        response = self.client.post(
            path=reverse("vocal_notice_view"),
            data=self.article_data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, 201)

# 방법공유 게시글 읽기 테스트
class NoticeArticleReadTest(APITestCase):
    @classmethod
    def setUpClass(cls):
        cls.faker = Faker()
        cls.articles=[]
        for i in range(10): # 10명의 유저가 각각 하나의 게시글을 작성하도록
            cls.user = User.objects.create_user(cls.faker.email(), cls.faker.name(), cls.faker.word())
            cls.articles.append(
                VocalNotice.objects.create(
                title=cls.faker.sentence(), 
                content=cls.faker.text(), 
                user=cls.user,
                ))

    def test_get_notice_article(self):
        for article in self.articles:
            url = reverse("vocal_notice_detail_view", kwargs={"article_id": article.pk})
            response = self.client.get(url)
            serializer = VocalNoticeSerializer(article).data

            # 조회수 증가를 확인하기 위해 게시물 수동 조회
            original_hits = article.hits
            article.refresh_from_db()  # 게시물 조회수 새로고침

            # 조회수가 1만큼 증가하는지 확인
            self.assertEqual(article.hits, original_hits + 1)

            # created 필드를 제외한 필드 목록 생성
            compare_fields = [field for field in serializer.keys() if field != "created_at" and field != "updated_at"]

             # compare_fields에 있는 필드만 비교
            for key in compare_fields:
                if key == 'hits':
                    # 조회수 필드의 경우, 값이 기존 조회수 + 1과 같아야 합니다.
                    self.assertEqual(response.data[key], original_hits + 1)
                else:
                    self.assertEqual(response.data[key], serializer[key])

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
    @classmethod
    def tearDownClass(cls):
        pass

# 방법공유 게시글 수정 테스트
class NoticeArticlePatchTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {
            "email": "pretty981210@gmail.com",
            "nickname" : "minyoung",
            "password": "Zz@19960806"
        }
        cls.article_data = {
            "title": "제목",
            "content": "내용"
        }
        cls.faker = Faker()
        cls.article = []
        cls.user = User.objects.create_user("pretty981210@gmail.com","minyoung","Zz@19960806")
        cls.article.append(
                VocalNotice.objects.create(
                title=cls.faker.sentence(), 
                content=cls.faker.text(), 
                user=cls.user,
                ))

    def setUp(self):
        self.access_token = self.client.post(reverse('user:token_obtain_pair'), self.user_data).data['access']

    # 방법공유 게시글 수정
    def test_patch_notice(self):
        patch_url = reverse('vocal_notice_detail_view', kwargs={"article_id":self.article[0].pk})
        response = self.client.patch(patch_url, HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        self.assertEqual(response.status_code, 200)


# 방법공유 게시글 삭제 테스트
class NoticeArticlePatchTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {
            "email": "pretty981210@gmail.com",
            "nickname" : "minyoung",
            "password": "Zz@19960806"
        }
        cls.article_data = {
            "title": "제목",
            "content": "내용"
        }
        cls.faker = Faker()
        cls.article = []
        cls.user = User.objects.create_user("pretty981210@gmail.com","minyoung","Zz@19960806")
        cls.article.append(
                VocalNotice.objects.create(
                title=cls.faker.sentence(), 
                content=cls.faker.text(), 
                user=cls.user,
                ))

    def setUp(self):
        self.access_token = self.client.post(reverse('user:token_obtain_pair'), self.user_data).data['access']

    # 방법공유 게시글 삭제
    def test_delete_notice(self):
        delete_url = reverse('vocal_notice_detail_view', kwargs={"article_id": self.article[0].pk})
        response = self.client.delete(delete_url, HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        self.assertEqual(response.status_code, 204)





# 댓글======================================
# 노래자랑 게시판 댓글
class AiCommentCreateTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.article_data = {
            "voice": "목소리",
            "song_info": "제목-가수",
            "article_image": "/image.png",
            "song": "/song.mp4"
        }
        cls.user_data = {
            "email": "pretty981210@gmail.com",
            "nickname" : "minyoung",
            "password": "Zz@19960806"
        }
        cls.user = User.objects.create_user("pretty981210@gmail.com","minyoung","Zz@19960806")
        cls.article = Article.objects.create( # 댓글 테스트에서 사용되는 게시글
            user=cls.user,
            **cls.article_data
        )
        cls.comment_data = {
            "user": cls.user.pk,
            "article": cls.article.pk,
            "content": "댓글"
        }

    # 로그인 토큰 가져오기
    def setUp(self):
        self.access_token = self.client.post(reverse('user:token_obtain_pair'), self.user_data).data['access']

    #로그인이 안된 유저가 댓글 작성 시도할때 에러
    def test_fail_if_not_logged_in_ai_comment(self):
        url = reverse('Comment', kwargs={"article_id": self.article.pk})
        response = self.client.post(url, data=self.comment_data)
        self.assertEqual(response.status_code, 401)

    # 노래자랑 게시판 글 작성 테스트
    def test_create_ai_comment(self):
        response = self.client.post(
            path=reverse('Comment', kwargs={"article_id": self.article.pk}),
            data=self.comment_data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, 201)
      
# 노래자랑 게시글 읽기 테스트
class AiCommentReadTest(APITestCase):
    @classmethod
    def setUpClass(cls):
        cls.faker = Faker()
        cls.articles=[]
        cls.comments=[]
        for i in range(10): # 10명의 유저가 각각 하나의 게시글을 작성하도록
            cls.user = User.objects.create_user(cls.faker.email(), cls.faker.name(), cls.faker.word())
            cls.articles.append(
                Article.objects.create(
                voice=cls.faker.sentence(), 
                song_info=cls.faker.text(),
                article_image=cls.faker.text(),
                song=cls.faker.text(),
                user=cls.user,
                )
            )
            cls.comments.append(
                Comment.objects.create(
                    user=cls.user,
                    article=cls.articles[i],
                    content=cls.faker.text(),
                )
            )

    def test_get_ai_comment(self):
        for comment in self.comments:
            url = reverse("Comment", kwargs={"article_id": comment.article.pk})
            response = self.client.get(url)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(len(response.data) > 0, 'Response data is empty.')

            fetched_comments = response.data

            for c in fetched_comments:
                serializer = CommentSerializer(comment).data

                # created 필드를 제외한 필드 목록 생성
                compare_fields = [field for field in serializer.keys() if field != "created_at" and field != "updated_at"]

                # compare_fields에 있는 필드만 비교
                for key in compare_fields:
                    if key == 'good':
                        self.assertEqual(len(c[key]), len(CommentSerializer(comment.good, many=True).data))
                    else:
                        self.assertEqual(c[key], serializer[key])
            
    @classmethod
    def tearDownClass(cls):
        pass

# 노래자랑 게시글 수정 테스트
class AiCommentPatchTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {
            "email": "pretty981210@gmail.com",
            "nickname" : "minyoung",
            "password": "Zz@19960806"
        }
        cls.article_data = {
            "voice": "목소리",
            "song_info": "제목-가수",
            "article_image": "/image.png",
            "song": "/song.mp4"
        }
        cls.faker = Faker()
        cls.article = []
        cls.user = User.objects.create_user("pretty981210@gmail.com","minyoung","Zz@19960806")
        cls.article = Article.objects.create( # 댓글 테스트에서 사용되는 게시글
            user=cls.user,
            **cls.article_data
        )
        cls.comment_data = {
            "user": cls.user, # cls.user 객체를 할당하도록
            "article": cls.article,
            "content": "댓글"
        }

    def setUp(self):
        self.access_token = self.client.post(reverse('user:token_obtain_pair'), self.user_data).data['access']
        self.comment = Comment.objects.create(**self.comment_data)

    # 노래자랑 게시글 수정
    def test_patch_ai_comment(self):
        response = self.client.patch(
            path=reverse('CommentUD', kwargs={"article_id": self.article.pk, "pk": self.comment.pk}),
            data={
                "content": "댓글"
            },
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, 200)



# 노래자랑 게시글 삭제 테스트
class AiArticlePatchTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {
            "email": "pretty981210@gmail.com",
            "nickname" : "minyoung",
            "password": "Zz@19960806"
        }
        cls.article_data = {
            "voice": "목소리",
            "song_info": "제목-가수",
            "article_image": "/image.png",
            "song": "/song.mp4"
        }
        cls.user = User.objects.create_user("pretty981210@gmail.com","minyoung","Zz@19960806")
        cls.article = Article.objects.create( # 댓글 테스트에서 사용되는 게시글
            user=cls.user,
            **cls.article_data
        )
        cls.comment_data = {
            "user": cls.user,
            "article": cls.article,
            "content": "댓글"
        }
    def setUp(self):
        self.access_token = self.client.post(reverse('user:token_obtain_pair'), self.user_data).data['access']
        self.comment = Comment.objects.create(**self.comment_data)

    # 노래자랑 게시글 삭제
    def test_delete_ai_comment(self):
        response = self.client.delete(
            path=reverse('CommentUD', kwargs={"article_id": self.article.pk, "pk": self.comment.pk}),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, 204)





# 방법공유 게시판 댓글
class NoticeCommentCreateTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.article_data = {
            "title": "제목",
            "content": "내용"
        }
        cls.user_data = {
            "email": "pretty981210@gmail.com",
            "nickname" : "minyoung",
            "password": "Zz@19960806"
        }
        cls.user = User.objects.create_user("pretty981210@gmail.com","minyoung","Zz@19960806")
        cls.article = VocalNotice.objects.create( # 댓글 테스트에서 사용되는 게시글
            user=cls.user,
            **cls.article_data
        )
        cls.comment_data = {
            "user": cls.user.pk,
            "article": cls.article.pk,
            "content": "댓글"
        }

    # 로그인 토큰 가져오기
    def setUp(self):
        self.access_token = self.client.post(reverse('user:token_obtain_pair'), self.user_data).data['access']

    #로그인이 안된 유저가 댓글 작성 시도할때 에러
    def test_fail_if_not_logged_in_comment(self):
        url = reverse('NoticeComment', kwargs={"article_id": self.article.pk})
        response = self.client.post(url, data=self.comment_data)
        self.assertEqual(response.status_code, 401)

    # 방법공유 게시판 글 작성 테스트
    def test_create_comment(self):
        response = self.client.post(
            path=reverse('NoticeComment', kwargs={"article_id": self.article.pk}),
            data=self.comment_data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, 201)
      
# 방법공유 게시글 읽기 테스트
class NoticeCommentReadTest(APITestCase):
    @classmethod
    def setUpClass(cls):
        cls.faker = Faker()
        cls.articles=[]
        cls.comments=[]
        for i in range(10): # 10명의 유저가 각각 하나의 게시글을 작성하도록
            cls.user = User.objects.create_user(cls.faker.email(), cls.faker.name(), cls.faker.word())
            cls.articles.append(
                VocalNotice.objects.create(
                title=cls.faker.sentence(), 
                content=cls.faker.text(), 
                user=cls.user,
                )
            )
            cls.comments.append(
                NoticeComment.objects.create(
                    user=cls.user,
                    article=cls.articles[i],
                    content=cls.faker.text(),
                )
            )

    def test_get_notice_comment(self):
        for comment in self.comments:
            url = reverse("NoticeComment", kwargs={"article_id": comment.article.pk})
            response = self.client.get(url)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(len(response.data) > 0, 'Response data is empty.')

            fetched_comments = response.data

            for c in fetched_comments:
                serializer = NoticeCommentSerializer(comment).data

                # created 필드를 제외한 필드 목록 생성
                compare_fields = [field for field in serializer.keys() if field != "created_at" and field != "updated_at"]

                # compare_fields에 있는 필드만 비교
                for key in compare_fields:
                    if key == 'good':
                        self.assertEqual(len(c[key]), len(NoticeCommentSerializer(comment.good, many=True).data))
                    else:
                        self.assertEqual(c[key], serializer[key])
            
    @classmethod
    def tearDownClass(cls):
        pass      

# 방법공유 게시글 수정 테스트
class NoticeCommentPatchTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {
            "email": "pretty981210@gmail.com",
            "nickname" : "minyoung",
            "password": "Zz@19960806"
        }
        cls.article_data = {
            "title": "제목",
            "content": "내용"
        }
        cls.faker = Faker()
        cls.article = []
        cls.user = User.objects.create_user("pretty981210@gmail.com","minyoung","Zz@19960806")
        cls.article = VocalNotice.objects.create( # 댓글 테스트에서 사용되는 게시글
            user=cls.user,
            **cls.article_data
        )
        cls.comment_data = {
            "user": cls.user, # cls.user 객체를 할당하도록
            "article": cls.article,
            "content": "댓글"
        }

    def setUp(self):
        self.access_token = self.client.post(reverse('user:token_obtain_pair'), self.user_data).data['access']
        self.comment = NoticeComment.objects.create(**self.comment_data)

    # 방법공유 게시글 수정
    def test_patch_notice_comment(self):
        response = self.client.patch(
            path=reverse('NoticeCommentUD', kwargs={"article_id": self.article.pk, "pk": self.comment.pk}),
            data={
                "content": "댓글"
            },
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, 200)



# 방법공유 게시글 삭제 테스트
class NoticeArticlePatchTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {
            "email": "pretty981210@gmail.com",
            "nickname" : "minyoung",
            "password": "Zz@19960806"
        }
        cls.article_data = {
            "title": "제목",
            "content": "내용"
        }
        cls.user = User.objects.create_user("pretty981210@gmail.com","minyoung","Zz@19960806")
        cls.article = VocalNotice.objects.create( # 댓글 테스트에서 사용되는 게시글
            user=cls.user,
            **cls.article_data
        )
        cls.comment_data = {
            "user": cls.user,
            "article": cls.article,
            "content": "댓글"
        }
    def setUp(self):
        self.access_token = self.client.post(reverse('user:token_obtain_pair'), self.user_data).data['access']
        self.comment = NoticeComment.objects.create(**self.comment_data)

    # 방법공유 게시글 삭제
    def test_delete_notice_comment(self):
        response = self.client.delete(
            path=reverse('NoticeCommentUD', kwargs={"article_id": self.article.pk, "pk": self.comment.pk}),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, 204)

