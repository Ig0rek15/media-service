from django.db import transaction
from .models import MediaJob
from .exceptions import FatalMediaError


def lock_and_mark_processing(job_id: str) -> MediaJob:
    """
    Блокирует job в БД и помечает как processing.
    """
    with transaction.atomic():
        job = (
            MediaJob.objects
            .select_for_update()
            .get(id=job_id)
        )

        if job.attempts >= MediaJob.MAX_ATTEMPTS:
            raise FatalMediaError('Retry limit exceeded')

        job.attempts += 1
        job.status = MediaJob.STATUS_PROCESSING
        job.save(update_fields=['attempts', 'status'])

        return job


def finish_job_success(job: MediaJob, result: dict) -> None:
    """
    Завершает job успешно.
    """
    job.result = result
    job.status = MediaJob.STATUS_DONE
    job.error = None
    job.save(update_fields=['result', 'status', 'error'])


def fail_and_retry(task, job: MediaJob, exc: Exception) -> None:
    """
    Помечает job как failed и инициирует retry в Celery.
    """
    job.status = MediaJob.STATUS_FAILED
    job.error = str(exc)
    job.save(update_fields=['status', 'error'])

    raise task.retry(exc=exc, countdown=5)


def fail_job(
    job: MediaJob,
    exc: Exception,
    unexpected: bool = False,
) -> None:
    """
    Финально завершает job с ошибкой.
    """
    job.status = MediaJob.STATUS_FAILED

    if unexpected:
        job.error = f'Unexpected error: {exc}'
    else:
        job.error = str(exc)

    job.save(update_fields=['status', 'error'])
