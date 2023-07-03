import os
from urllib.parse import urlparse
from django.conf import settings
from django.db import models
from user.models import User
from django.utils import timezone
import shutil

class SeparationResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=255)
    vocals_path = models.CharField(max_length=255)
    accompaniment_path = models.CharField(max_length=255)
    state = models.CharField(max_length=255, default='waiting')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.file_name

    def delete(self, *args, **kwargs):
        vocals_path_relative = urlparse(self.vocals_path).path.lstrip('/media/')
        accompaniment_path_relative = urlparse(self.accompaniment_path).path.lstrip('/media/')

        # 파일 이름을 제외한 부모 디렉토리 경로를 찾습니다.
        vocals_parent_dir = os.path.dirname(os.path.join(settings.MEDIA_ROOT, vocals_path_relative))
        accompaniment_parent_dir = os.path.dirname(os.path.join(settings.MEDIA_ROOT, accompaniment_path_relative))

        # 해당 디렉토리가 있다면 삭제합니다.
        if os.path.isdir(vocals_parent_dir):
            shutil.rmtree(vocals_parent_dir)
        if os.path.isdir(accompaniment_parent_dir):
            shutil.rmtree(accompaniment_parent_dir)

        super().delete(*args, **kwargs)