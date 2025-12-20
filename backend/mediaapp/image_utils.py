from PIL import Image


def create_thumbnail(
    source_path: str,
    target_path: str,
    size=(300, 300)
) -> None:
    """
    Создаёт thumbnail изображения.
    """
    with Image.open(source_path) as img:
        img.convert('RGB')
        img.thumbnail(size)
        img.save(target_path, format='JPEG', quality=85)
