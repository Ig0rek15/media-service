from rest_framework import viewsets, status
from  rest_framework.decorators import action
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.db import IntegrityError
from django.shortcuts import get_object_or_404

from .models import MediaJob
from .serializers import (
    MediaUploadSerializer,
    MediaJobSerializer,
    MediaRetrySerializer
)
from .hash_utils import compute_file_hash
from .tasks import process_media


class MediaViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = MediaUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uploaded_file = serializer.validated_data['file']
        preset = serializer.validated_data['preset']

        file_hash = compute_file_hash(uploaded_file)

        existing_job = MediaJob.objects.filter(
            file_hash=file_hash,
            preset=preset,
        ).first()

        if existing_job:
            return Response(
                {
                    'job_id': str(existing_job.id),
                    'status': existing_job.status,
                },
                status=status.HTTP_200_OK,
            )

        storage_path = default_storage.save(
            f'uploads/{uploaded_file.name}',
            uploaded_file
        )

        try:
            job = MediaJob.objects.create(
                original_file=storage_path,
                file_name=uploaded_file.name,
                content_type=uploaded_file.content_type,
                size=uploaded_file.size,
                preset=preset,
                file_hash=file_hash,
                status=MediaJob.STATUS_QUEUED,
            )
        except IntegrityError:
            job = MediaJob.objects.get(
                file_hash=file_hash,
                preset=preset,
            )

        process_media.delay(job.id)

        return Response(
            {
                'job_id': str(job.id),
                'status': job.status,
            },
            status=status.HTTP_201_CREATED
        )

    def retrieve(self, request, pk=None):
        job = get_object_or_404(MediaJob, pk=pk)
        serializer = MediaJobSerializer(job)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        serializer = MediaRetrySerializer(data={'job_id': pk})
        serializer.is_valid(raise_exception=True)

        job = serializer.validated_data['job']

        job.status = MediaJob.STATUS_QUEUED
        job.error = None
        job.save(update_fields=['status', 'error', 'updated_at'])

        process_media.delay(job.id)

        return Response(
            {
                'job_id': str(job.id),
                'status': job.status,
                'attempts': job.attempts,
            }
        )
