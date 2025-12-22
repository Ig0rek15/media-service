import json
import subprocess


def get_video_metadata(path: str) -> dict:
    """
    Возвращает метаданные видео через ffprobe
    """
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height,codec_name',
        '-show_entries', 'format=duration',
        '-of', 'json',
        path,
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
    )

    data = json.loads(result.stdout)

    stream = data['streams'][0]
    format_data = data['format']

    return {
        'width': stream['width'],
        'height': stream['height'],
        'codec': stream['codec_name'],
        'duration': float(format_data['duration']),
    }


def extract_video_thumbnail(
    source_path: str,
    target_path: str,
    second: int = 1,
) -> None:
    """
    Извлекает кадр из видео (poster)
    """
    cmd = [
        'ffmpeg',
        '-y',
        '-ss', str(second),
        '-i', source_path,
        '-frames:v', '1',
        '-q:v', '2',
        target_path,
    ]

    subprocess.run(cmd, check=True)
