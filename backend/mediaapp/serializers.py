from rest_framework import serializers, status

from .models import MediaJob
from .exceptions import MediaAPIException


class MediaUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class MediaJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaJob
        fields = (
            'id',
            'status',
            'result',
            'error',
            'created_at',
            'updated_at',
        )


class MediaRetrySerializer(serializers.Serializer):
    job_id = serializers.UUIDField()

    def validate(self, attrs):
        job_id = attrs['job_id']

        try:
            job = MediaJob.objects.get(pk=job_id)
        except MediaJob.DoesNotExist:
            raise MediaAPIException(
                'Job not found',
                status_code=status.HTTP_404_NOT_FOUND
            )

        if job.status != MediaJob.STATUS_FAILED:
            raise MediaAPIException(
                'Retry allowed only for failed jobs'
            )

        if job.attempts >= MediaJob.MAX_ATTEMPTS:
            raise MediaAPIException(
                'Retry limit exceeded'
            )

        attrs['job'] = job
        return attrs
