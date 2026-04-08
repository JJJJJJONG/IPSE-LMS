# problems/signals.py
from django.db.models.signals import post_save
from django.db.models import Sum
from django.dispatch import receiver
from .models import SolveRecord

@receiver(post_save, sender=SolveRecord)
def update_user_ranking_points(sender, instance, created, **kwargs):
    # 상태가 'SOLVED'로 변경되었을 때만 점수 가산
    if instance.status == 'SOLVED':
        profile = instance.user
        total = SolveRecord.objects.filter(
            user=instance.user,
            status='SOLVED',
        ).aggregate(total=Sum('problem__points'))['total']
        profile.total_points = total or 0
        profile.save(update_fields=['total_points'])