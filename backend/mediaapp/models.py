import uuid

from django.db import models
from django.conf import settings


class MediaJob(models.Model):
    MAX_ATTEMPTS = 3

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

    original_file = models.CharField(
        max_length=1024,
        help_text='Path or key in object storage'
    )

    file_name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=100)
    size = models.BigIntegerField()
    preset = models.CharField(
        max_length=50,
        default='default'
    )
    file_hash = models.CharField(
        max_length=64,
        db_index=True,
        help_text='SHA256 hash of original file'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_QUEUED
    )

    attempts = models.PositiveSmallIntegerField(
        default=0,
        help_text='How many times the job was executed'
    )

    result = models.JSONField(
        null=True,
        blank=True,
        help_text='Generated artifacts, e.g. {thumb: url, medium: url}'
    )

    callback_url = models.URLField(
        null=True,
        blank=True,
        help_text='Webhook URL to notify on completion'
    )

    error = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        constraints = [
            models.UniqueConstraint(
                fields=['file_hash', 'preset'],
                name='unique_file_hash_preset'
            )
        ]

    def __str__(self) -> str:
        return f'{self.id} ({self.status})'
