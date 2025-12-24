import pytest

from mediaapp.models import MediaJob


@pytest.mark.django_db
def test_upload_creates_job(
    api_client,
    image_file,
    upload_url,
    preset,
    mock_storage_save,
    mock_celery_delay,
):
    response = api_client.post(
        upload_url,
        data={
            'file': image_file,
            'preset': preset,
        },
        format='multipart',
    )

    assert response.status_code == 201
    assert 'job_id' in response.data
    assert response.data['status'] == 'queued'

    job = MediaJob.objects.get(id=response.data['job_id'])
    assert job.preset == preset
    assert job.status == MediaJob.STATUS_QUEUED
