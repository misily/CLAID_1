import os
from urllib.parse import urlparse
from django.conf import settings
from django.db import models
from user.models import User
from django.utils import timezone
from os.path import splitext
import shutil

'''
    작성자: 이준영
    내용: 음성분리관련 모델 정의
    작성일: 2023.07.03
    수정자: 이준영
    내용: 폴더별 유니크하게 적용
    수정일: 2023.07.08
'''
def user_directory_path(instance, filename):
    return f"separator/{instance.user.id}/{timezone.now().strftime('%Y%m%d_%H%M%S')}/{filename}"

class SeparationResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=255, blank=True)
    audio_file = models.FileField(upload_to=user_directory_path)
    vocals_path = models.CharField(max_length=255)
    accompaniment_path = models.CharField(max_length=255)
    state = models.CharField(max_length=255, default='waiting')
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        # 오직 처음 생성될 때만 실행
        if not self.id and self.audio_file:
            self.file_name = splitext(self.audio_file.name.split('/')[-1])[0]
        super().save(*args, **kwargs)
