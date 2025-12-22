import requests

from celery import shared_task

from .models import MediaJob


@shared_task(bind=True, max_retries=5, queue='media.default')
def send_webhook(self, job_id: str):
    job = MediaJob.objects.get(id=job_id)

    if not job.callback_url:
        return

    payload = {
        'job_id': str(job.id),
        'status': job.status,
        'result': job.result,
        'error': job.error,
    }

    try:
        response = requests.post(
            job.callback_url,
            json=payload,
            timeout=5,
        )
        response.raise_for_status()

    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)
