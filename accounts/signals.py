# accounts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Student

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_student_profile(sender, instance, created, **kwargs):
    """유저(User) 레코드가 새로 생성(created=True)될 때, 빈 Student 프로필을 함께 생성합니다."""
    if created:
        Student.objects.create(student=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_student_profile(sender, instance, **kwargs):
    """유저 정보가 업데이트될 때, 연결된 Student 정보도 안전하게 저장 상태를 동기화합니다."""
    if hasattr(instance, 'student'):
        instance.student.save()