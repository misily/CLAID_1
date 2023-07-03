from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.UploadFileView.as_view(), name='file-upload'),
    path('converted-files/', views.ConvertedFilesView.as_view(), name='converted-files'),
    path('converted-files/<int:pk>/', views.ConvertedFilesView.as_view(), name='converted-file'),
]
