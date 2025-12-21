import tempfile

from .image_utils import create_thumbnail
from .storage import upload_file
from .presets import IMAGE_PRESETS


def process_image_preset(job, source_path):
    preset = IMAGE_PRESETS[job.preset]
    results = {}

    for name, size in preset.items():
        tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        create_thumbnail(source_path, tmp.name, size)

        storage_path = f'thumbnails/{job.id}/{name}.jpg'
        upload_file(tmp.name, storage_path)

        results[name] = storage_path

    return results
