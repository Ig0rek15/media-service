from rest_framework.exceptions import APIException
from rest_framework import status


class MediaAPIException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Media API error'
    default_code = 'media_error'

    def __init__(self, detail=None, status_code=None):
        if status_code is not None:
            self.status_code = status_code
        super().__init__(detail or self.default_detail)


class MediaProcessingError(Exception):
    """
    Базовая ошибка обработки медиа.
    """
    pass


class RetryableMediaError(MediaProcessingError):
    """
    Ошибка, при которой задачу можно повторить.
    """
    pass


class FatalMediaError(MediaProcessingError):
    """
    Ошибка, при которой повторять задачу бессмысленно.
    """
    pass
