import tempfile
from django.core.files.storage import default_storage


def download_file(storage_path: str) -> str:
    """
    Скачивает файл из object storage во временный файл.
    Возвращает путь к локальному файлу.
    """
    tmp = tempfile.NamedTemporaryFile(delete=False)
    with default_storage.open(storage_path, 'rb') as source:
        tmp.write(source.read())
    tmp.close()
    return tmp.name


def upload_file(local_path: str, storage_path: str) -> None:
    """
    Загружает локальный файл в object storage.
    """
    with open(local_path, 'rb') as f:
        default_storage.save(storage_path, f)
