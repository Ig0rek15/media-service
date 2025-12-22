import tempfile

from celery import shared_task

from .task_helpers import (
    lock_and_mark_processing,
    finish_job_success,
    fail_and_retry,
    fail_job,
)
from .storage import download_file, upload_file
from .media_type import detect_media_type
from .preset_handlers import process_image_preset
from .exceptions import RetryableMediaError, FatalMediaError
from .webhooks import send_webhook
from .video_utils import (
    get_video_metadata,
    extract_video_thumbnail,
)


def process_video(job):
    source_path = download_file(job.original_file)
    metadata = get_video_metadata(source_path)

    tmp_poster = tempfile.NamedTemporaryFile(
        suffix='.jpg',
        delete=False,
    )

    extract_video_thumbnail(
        source_path,
        tmp_poster.name,
        second=1,
    )

    poster_storage_path = f'thumbnails/{job.id}/poster.jpg'
    upload_file(tmp_poster.name, poster_storage_path)

    return {
        'poster': poster_storage_path,
        **metadata,
    }


@shared_task(bind=True, max_retries=3, queue='media.default')
def process_media(self, job_id):
    job = None

    try:
        job = lock_and_mark_processing(job_id)
        media_type = detect_media_type(job.file_name)

        if media_type == 'image':
            source_path = download_file(job.original_file)
            result = process_image_preset(job, source_path)

        elif media_type == 'video':
            result = process_video(job)
        else:
            raise FatalMediaError('Unsupported media type')

        finish_job_success(job, result)
        send_webhook(job.id)

    except RetryableMediaError as exc:
        fail_and_retry(self, job, exc)

    except FatalMediaError as exc:
        fail_job(job, exc)

    except Exception as exc:
        fail_job(job, exc, unexpected=True)
