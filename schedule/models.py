from django.db import models
from django.conf import settings

PLATFORM_CHOICES = [
    ('zoom', 'Zoom'),
    ('teams', 'Microsoft Teams'),
    ('meet', 'Google Meet'),
    ('slack', 'Slack'),
    ('in_person', 'In Person'),
]

class Meeting(models.Model):
    title        = models.CharField(max_length=200)
    description  = models.TextField(blank=True)
    platform     = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='teams')
    meeting_link = models.URLField(blank=True)
    date_time    = models.DateTimeField()
    created_by   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='meetings')
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date_time']

    def __str__(self):
        return f"{self.title} - {self.date_time.strftime('%d %b %Y %H:%M')}"