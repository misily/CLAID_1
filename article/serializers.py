from django.db import models
from rest_framework import serializers
from article.models import Article
from article.models import Comment
from article.models import VocalArticle
from article.models import VocalNotice

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
        fields = ('title', 'content', 'article_image', 'song')


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class VocalArticleSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    
    def get_user(self, obj):
        return {"pk": obj.user.pk, "login_type": obj.user.login_type, "nickname": obj.user.nickname, "profile_image": str(obj.user.profile_image)} 
    
    class Meta:
        model = VocalArticle
        fields = '__all__'


class VocalArticleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VocalArticle
        fields = ('voice', 'song_info', 'song')
        


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