from rest_framework import serializers


class MediaUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
