from django.urls import path
from . import views

urlpatterns = [   
    path('', views.ArticleView.as_view(), name='article_view'),
    path('<int:user_id>/', views.ArticleDetailView.as_view(), name='article_detail_view'),
]