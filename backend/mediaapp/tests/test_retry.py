import pytest

from mediaapp.models import MediaJob


@pytest.mark.django_db
def test_retry_job(
    api_client,
    image_file,
    upload_url,
    preset,
    mock_storage_save,
    mock_celery_delay,
):

    create_resp = api_client.post(
        upload_url,
        data={
            'file': image_file,
            'preset': preset,
        },
        format='multipart',
    )

    job = MediaJob.objects.get(id=create_resp.data['job_id'])
    job.status = MediaJob.STATUS_FAILED
    job.save()

    retry_resp = api_client.post(
        f'/api/media/{job.id}/retry/'
    )

    assert retry_resp.status_code == 200
    job.refresh_from_db()
    assert job.status == MediaJob.STATUS_QUEUED
