from celery import shared_task

from .task_helpers import (
    lock_and_mark_processing,
    finish_job_success,
    fail_and_retry,
    fail_job,
)
from .storage import download_file
from .preset_handlers import process_image_preset
from .exceptions import RetryableMediaError, FatalMediaError


@shared_task(bind=True, max_retries=3, queue='media.default')
def process_media(self, job_id):
    job = None

    try:
        job = lock_and_mark_processing(job_id)

        source_path = download_file(job.original_file)
        result = process_image_preset(job, source_path)

        finish_job_success(job, result)

    except RetryableMediaError as exc:
        fail_and_retry(self, job, exc)

    except FatalMediaError as exc:
        fail_job(job, exc)

    except Exception as exc:
        fail_job(job, exc, unexpected=True)
