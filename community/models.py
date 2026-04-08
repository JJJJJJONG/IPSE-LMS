from django.db import models
from django.conf import settings

POST = (
    ('News', 'News'),
    ('Event', 'Event'),
)

class NewsAndEventsManager(models.Manager):
    pass # 기존에 특별한 로직이 없었다면 이렇게 두면 돼!

class NewsAndEvents(models.Model):
    title = models.CharField(max_length=200, null=True, verbose_name="제목")
    summary = models.TextField(max_length=200, blank=True, null=True, verbose_name="내용 요약")
    posted_as = models.CharField(choices=POST, max_length=10, verbose_name="게시글 분류")
    updated_date = models.DateTimeField(auto_now=True, auto_now_add=False, null=True)
    upload_time = models.DateTimeField(auto_now=False, auto_now_add=True, null=True)
    event_date = models.DateField(null=True, blank=True, verbose_name="행사 진행 일자 (Event용)")
    thumbnail = models.ImageField(upload_to='activities/thumbnails/', null=True, blank=True, verbose_name="썸네일")
    objects = NewsAndEventsManager()

    def __str__(self):
        return self.title


class NewsAndEventsComment(models.Model):
    post = models.ForeignKey(
        NewsAndEvents,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(verbose_name="댓글 내용")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author} - {self.post}"