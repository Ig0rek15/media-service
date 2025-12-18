import time

from django.core.files.storage import default_storage

from .models import MediaJob
from project.celery import app


@app.task(
    bind=True,
    queue='media.default',
    max_retries=3,
    retry_backoff=5,
    retry_jitter=True,
)
def process_media(self, job_id):
    job = MediaJob.objects.get(id=job_id)

    try:
        job.status = MediaJob.STATUS_PROCESSING
        job.save(update_fields=['status'])

        # Симуляция обработки
        time.sleep(3)

        with default_storage.open(job.original_file, 'rb') as f:
            f.read(1024)

        job.status = MediaJob.STATUS_DONE
        job.error = None
        job.save(update_fields=['status', 'error'])

    except Exception as exc:
        job.attempts += 1
        job.error = str(exc)

        if self.request.retries < self.max_retries:
            job.status = MediaJob.STATUS_QUEUED
            job.save(update_fields=['attempts', 'status', 'error'])
            raise self.retry(exc=exc)

        job.status = MediaJob.STATUS_FAILED
        job.save(update_fields=['attempts', 'status', 'error'])
        raise
