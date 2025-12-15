import uuid

from django.db import models
from django.conf import settings


class MediaJob(models.Model):
    STATUS_QUEUED = 'queued'
    STATUS_PROCESSING = 'processing'
    STATUS_DONE = 'done'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = (
        (STATUS_QUEUED, 'Queued'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_DONE, 'Done'),
        (STATUS_FAILED, 'Failed'),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    # путь: uploads/2025/12/11/photo.jpg
    original_file = models.CharField(
        max_length=1024,
        help_text='Path or key in object storage'
    )

    file_name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=100)
    size = models.BigIntegerField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_QUEUED
    )

    attempts = models.PositiveSmallIntegerField(default=0)

    result = models.JSONField(
        null=True,
        blank=True,
        help_text='Generated artifacts, e.g. {thumb: url, medium: url}'
    )

    error = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return f'{self.id} ({self.status})'
