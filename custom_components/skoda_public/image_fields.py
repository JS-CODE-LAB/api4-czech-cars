"""Detection of image URLs in dynamic MyŠkoda API fields."""
from __future__ import annotations

from urllib.parse import urlsplit

_IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".svg")
_IMAGE_NAMES = ("image", "picture", "photo", "thumbnail", "render", "visual", "icon")


def is_image_field(path: str, value: object) -> bool:
    """Only route actual HTTPS image URLs, not arbitrary API strings."""
    if not isinstance(value, str) or not value.startswith("https://"):
        return False
    parsed = urlsplit(value)
    if not parsed.hostname or parsed.username or parsed.password:
        return False
    leaf = path.lower().rsplit(".", 1)[-1]
    return parsed.path.lower().endswith(_IMAGE_SUFFIXES) or any(
        part in leaf for part in _IMAGE_NAMES
    )
