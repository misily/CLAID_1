from django.db import models
from rest_framework import serializers
from article.models import Article
from article.models import Comment, NoticeComment
from article.models import VocalNotice
from user.models import User

class ArticleSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    
    def get_user(self, obj):
        return {"pk": obj.user.pk, "login_type": obj.user.login_type, "nickname": obj.user.nickname, "profile_image": str(obj.user.profile_image)} 
    
    class Meta:
        model = Article
        fields = '__all__'

class ArticleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ('voice', 'song_info', 'article_image', 'song')



class VocalNoticeSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    
    def get_user(self, obj):
        return {"pk": obj.user.pk, "login_type": obj.user.login_type, "nickname": obj.user.nickname, "profile_image": str(obj.user.profile_image)} 
    
    class Meta:
        model = VocalNotice
        fields = '__all__'


class VocalNoticeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VocalNotice
        fields = ('title', 'content', 'article_image')


# 작성자 : 김은수
# 내용 : 유저모델에서 가져올 필드들
# 작성일 : 2023.06.21
class CommentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'nickname', 'profile_image']



class CommentSerializer(serializers.ModelSerializer):
    user = CommentUserSerializer()
    good = serializers.SerializerMethodField()

    def get_good(self, comment):
        good_users = comment.good.all()
        good_user_data = CommentUserSerializer(good_users, many=True)
        return good_user_data
    
    class Meta:
        model = Comment
        fields = ['content', 'user', 'good']


class UserIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id']


class CommentCreateSerializer(serializers.ModelSerializer):
   
    class Meta:
            model = Comment
            fields= ("content",)


#NoticeArticleComment

class NoticeCommentSerializer(serializers.ModelSerializer):
    user = CommentUserSerializer()
    good = serializers.SerializerMethodField()

    def get_good(self, comment):
        good_users = comment.good.all()
        good_user_data = CommentUserSerializer(good_users, many=True)
        return good_user_data
    
    class Meta:
        model = NoticeComment
        fields = ['content', 'user', 'good']



class NoticeCommentCreateSerializer(serializers.ModelSerializer):
   
    class Meta:
            model = NoticeComment
            fields= ("content",)