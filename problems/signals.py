# problems/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SolveRecord

@receiver(post_save, sender=SolveRecord)
def update_user_ranking_points(sender, instance, created, **kwargs):
    # 상태가 'SOLVED'로 변경되었을 때만 점수 가산
    if instance.status == 'SOLVED':
        profile = instance.user # User 모델에 점수 필드가 있다고 가정
        # 해당 유저가 푼 모든 문제의 포인트 합산 (또는 현재 포인트 + 문제 포인트)
        total = SolveRecord.objects.filter(user=instance.user, status='SOLVED').aggregate(
            total=models.Sum('problem__points')
        )['total']
        profile.total_points = total or 0
        profile.save()