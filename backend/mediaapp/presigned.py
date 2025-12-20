import boto3
from django.conf import settings


def generate_presigned_url(
    key: str,
    expires_in: int = 300,
) -> str:
    """
    Генерирует временный публичный URL для скачивания файла из MinIO (S3 API)
    """

    client = boto3.client(
        's3',
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )

    url = client.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
            'Key': key,
        },
        ExpiresIn=expires_in,
    )

    return url.replace(
        settings.AWS_S3_ENDPOINT_URL,
        settings.MINIO_PUBLIC_ENDPOINT,
    )
