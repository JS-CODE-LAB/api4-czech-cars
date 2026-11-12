"""Render transparent vehicle images for Home Assistant light/dark themes."""
from __future__ import annotations

from io import BytesIO

from PIL import Image, ImageOps, UnidentifiedImageError

MAX_PIXELS = 20_000_000
OUTPUT_SIZE = (1200, 675)
PADDING = 56


def prepare_vehicle_image(data: bytes) -> tuple[bytes, dict[str, object]]:
    """Crop visible pixels, fit on neutral light canvas and return PNG + metadata.

    Only nontransparent pixels define the crop. If the source itself contains
    merely a thin silhouette, this cannot recreate missing vehicle details.
    """
    with Image.open(BytesIO(data)) as source:
        if source.width * source.height > MAX_PIXELS:
            raise ValueError("Image pixel limit exceeded")
        source.load()
        rgba = source.convert("RGBA")
        alpha = rgba.getchannel("A")
        bounds = alpha.getbbox()
        if bounds is None:
            bounds = (0, 0, source.width, source.height)
        cropped = rgba.crop(bounds)
        # Do not upscale very thin artifacts to fill the whole image.
        max_size = (OUTPUT_SIZE[0] - PADDING * 2, OUTPUT_SIZE[1] - PADDING * 2)
        cropped.thumbnail(max_size, Image.Resampling.LANCZOS)
        background = Image.new("RGB", OUTPUT_SIZE, "#f2f4f6")
        position = ((OUTPUT_SIZE[0] - cropped.width) // 2,
                    (OUTPUT_SIZE[1] - cropped.height) // 2)
        background.paste(cropped, position, cropped)
        out = BytesIO()
        background.save(out, format="PNG", optimize=True)
        return out.getvalue(), {
            "source_size": source.size,
            "visible_bounds": bounds,
            "visible_size": (bounds[2] - bounds[0], bounds[3] - bounds[1]),
            "output_size": OUTPUT_SIZE,
            "source_mode": source.mode,
        }
