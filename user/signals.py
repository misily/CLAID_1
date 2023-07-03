from django.db.models.signals import post_save
from django.dispatch import receiver
from user.models import User, Point, PointHistory

@receiver(post_save, sender=User)
def create_user_points(sender, instance, created, **kwargs):
    if created:
        Point.objects.create(user=instance)
        PointHistory.objects.create(user=instance, point_change=+1000, reason="회원가입")