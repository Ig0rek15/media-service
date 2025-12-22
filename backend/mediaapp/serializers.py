from rest_framework import serializers, status

from .models import MediaJob
from .exceptions import MediaAPIException
from .presets import IMAGE_PRESETS
from .presigned import generate_presigned_url


class MediaUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    preset = serializers.CharField(
        required=False,
        default='default'
    )
    callback_url = serializers.URLField(
        required=False,
        allow_null=True,
        allow_blank=True,
    )

    def validate_preset(self, value):
        if value not in IMAGE_PRESETS:
            raise serializers.ValidationError('Unknown preset')
        return value


class MediaJobSerializer(serializers.ModelSerializer):
    result_urls = serializers.SerializerMethodField()

    class Meta:
        model = MediaJob
        fields = (
            'id',
            'status',
            'error',
            'result_urls',
            'created_at',
            'updated_at',
        )

    def get_result_urls(self, obj):
        if not obj.result:
            return None

        urls = {}

        for name, value in obj.result.items():
            if isinstance(value, str) and '/' in value:
                urls[name] = generate_presigned_url(value)

        return urls


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
