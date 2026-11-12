"""Detection of image URLs in dynamic MyŠkoda API fields."""
from __future__ import annotations

from urllib.parse import urlsplit
from ipaddress import ip_address

_IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp")
_IMAGE_NAMES = ("image", "picture", "photo", "thumbnail", "render", "visual", "icon")


def is_image_field(path: str, value: object) -> bool:
    """Only route actual HTTPS image URLs, not arbitrary API strings."""
    if not isinstance(value, str) or not value.startswith("https://"):
        return False
    parsed = urlsplit(value)
    if not parsed.hostname or parsed.username or parsed.password:
        return False
    if parsed.hostname.lower() in ("localhost", "localhost.localdomain"):
        return False
    try:
        if not ip_address(parsed.hostname).is_global:
            return False
    except ValueError:
        pass
    leaf = path.lower().rsplit(".", 1)[-1]
    return parsed.path.lower().endswith(_IMAGE_SUFFIXES) or any(
        part in leaf for part in _IMAGE_NAMES
    )
