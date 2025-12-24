import pytest

from mediaapp.models import MediaJob


@pytest.mark.django_db
def test_retrieve_job(
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

    job_id = create_resp.data['job_id']

    retrieve_resp = api_client.get(f'/api/media/{job_id}/')

    assert retrieve_resp.status_code == 200
    assert retrieve_resp.data['id'] == job_id
    assert retrieve_resp.data['status'] == 'queued'
