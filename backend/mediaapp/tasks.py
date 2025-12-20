import os
import tempfile

from celery import shared_task
from django.db import transaction

from .models import MediaJob
from .storage import download_file, upload_file
from .image_utils import create_thumbnail
from .exceptions import RetryableMediaError, FatalMediaError


@shared_task(bind=True, max_retries=3, queue='media.default')
def process_media(self, job_id):
    try:
        with transaction.atomic():
            job = MediaJob.objects.select_for_update().get(id=job_id)

            if job.attempts >= MediaJob.MAX_ATTEMPTS:
                raise FatalMediaError('Retry limit exceeded')

            job.attempts += 1
            job.status = MediaJob.STATUS_PROCESSING
            job.save(update_fields=['attempts', 'status'])

        # === скачиваем оригинал ===
        source_path = download_file(job.original_file)

        # === делаем thumbnail ===
        tmp_thumb = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        create_thumbnail(source_path, tmp_thumb.name)

        # === загружаем результат ===
        thumb_storage_path = f'thumbnails/{job.id}/thumb.jpg'
        upload_file(tmp_thumb.name, thumb_storage_path)

        # === сохраняем результат ===
        job.result = {'thumb': thumb_storage_path}
        job.status = MediaJob.STATUS_DONE
        job.save(update_fields=['result', 'status'])

    except RetryableMediaError as exc:
        job.status = MediaJob.STATUS_FAILED
        job.error = str(exc)
        job.save(update_fields=['status', 'error'])
        raise self.retry(exc=exc, countdown=5)

    except FatalMediaError as exc:
        job.status = MediaJob.STATUS_FAILED
        job.error = str(exc)
        job.save(update_fields=['status', 'error'])

    except Exception as exc:
        job.status = MediaJob.STATUS_FAILED
        job.error = f'Unexpected error: {exc}'
        job.save(update_fields=['status', 'error'])
