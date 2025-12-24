import pytest

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def image_file():
    return SimpleUploadedFile(
        name='test.jpg',
        content=b'\x47\x49\x46\x38\x39\x61',
        content_type='image/jpeg',
    )


@pytest.fixture
def image_file_factory():
    def factory():
        return SimpleUploadedFile(
            'test.jpg',
            b'fake image content',
            content_type='image/jpeg',
        )
    return factory


@pytest.fixture
def upload_url():
    return '/api/media/'


@pytest.fixture
def preset():
    return 'default'


@pytest.fixture
def mock_storage_save(mocker):
    '''
    Мокаем сохранение файла в object storage
    '''
    return mocker.patch(
        'mediaapp.views.default_storage.save',
        return_value='uploads/test.jpg',
    )


@pytest.fixture
def mock_celery_delay(mocker):
    '''
    Мокаем отправку Celery-задачи, чтобы pytest
    не пытался подключаться к Redis / broker.
    '''
    return mocker.patch(
        'mediaapp.views.process_media.delay',
        autospec=True,
        return_value=None,
    )
