import time

from celery import shared_task
from django.core.files.storage import default_storage

from .models import MediaJob
from project.celery import app


@app.task(bind=True, queue='media.default')
def process_media(self, job_id):
    job = MediaJob.objects.get(id=job_id)

    job.status = MediaJob.STATUS_PROCESSING
    job.save(update_fields=['status'])

    time.sleep(3)

    with default_storage.open(job.original_file, 'rb') as f:
        f.read(1024)

    job.status = MediaJob.STATUS_DONE
    job.save(update_fields=['status'])
