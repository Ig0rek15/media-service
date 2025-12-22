import os


IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}


def detect_media_type(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()

    if ext in IMAGE_EXTENSIONS:
        return 'image'

    if ext in VIDEO_EXTENSIONS:
        return 'video'

    return 'unknown'
