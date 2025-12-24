import pytest

from mediaapp.models import MediaJob


@pytest.mark.django_db
def test_idempotent_upload_returns_existing_job(
    api_client,
    image_file_factory,
    upload_url,
    preset,
    mock_storage_save,
    mock_celery_delay,
):

    first = api_client.post(
        upload_url,
        data={
            'file': image_file_factory(),
            'preset': preset,
        },
        format='multipart',
    )

    second = api_client.post(
        upload_url,
        data={
            'file': image_file_factory(),
            'preset': preset,
        },
        format='multipart',
    )

    assert first.data['job_id'] == second.data['job_id']
    assert MediaJob.objects.count() == 1
