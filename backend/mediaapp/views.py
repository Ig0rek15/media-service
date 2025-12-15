from django.core.files.storage import default_storage
from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import MediaJob
from .serializers import MediaUploadSerializer
from .tasks import process_media


class MediaViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = MediaUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uploaded_file = serializer.validated_data['file']

        # сохранение в minio
        storage_path = default_storage.save(
            f'uploads/{uploaded_file.name}',
            uploaded_file
        )

        # сохранение пути до файла и его состояния
        job = MediaJob.objects.create(
            original_file=storage_path,
            file_name=uploaded_file.name,
            content_type=uploaded_file.content_type,
            size=uploaded_file.size,
            status=MediaJob.STATUS_QUEUED,
        )

        # отправка задачи в очередь
        process_media.delay(job.id)

        return Response(
            {
                'job_id': str(job.id),
                'status': job.status,
            },
            status=status.HTTP_201_CREATED
        )
