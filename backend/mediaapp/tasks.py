from celery import shared_task
from django.db import transaction

from .models import MediaJob
from .exceptions import RetryableMediaError, FatalMediaError


@shared_task(
    bind=True,
    max_retries=3,
    queue='media.default'
)
def process_media(self, job_id):
    try:
        with transaction.atomic():
            job = MediaJob.objects.select_for_update().get(id=job_id)

            if job.attempts >= MediaJob.MAX_ATTEMPTS:
                raise FatalMediaError('Retry limit exceeded')

            job.attempts += 1
            job.status = MediaJob.STATUS_PROCESSING
            job.save(update_fields=['attempts', 'status'])

        # ==== здесь будет реальная обработка ====
        # пока симулируем
        raise RetryableMediaError('Temporary processing failure')

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
        # неизвестная ошибка = fatal
        job.status = MediaJob.STATUS_FAILED
        job.error = f'Unexpected error: {exc}'
        job.save(update_fields=['status', 'error'])
