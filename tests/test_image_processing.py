"""Vehicle image rendering and cropping tests."""
import importlib.util
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw

path = Path(__file__).resolve().parents[1] / "custom_components/skoda_public/image_processing.py"
spec = importlib.util.spec_from_file_location("image_processing", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_crop_alpha_and_light_background():
    source = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    ImageDraw.Draw(source).rectangle((400, 400, 1500, 700), fill=(80, 80, 80, 255))
    buffer = BytesIO()
    source.save(buffer, format="PNG")
    data, info = module.prepare_vehicle_image(buffer.getvalue())
    assert info["visible_bounds"] == (400, 400, 1501, 701)
    with Image.open(BytesIO(data)) as result:
        assert result.size == (1200, 675)
        assert result.mode == "RGB"
        assert result.getpixel((0, 0)) == (242, 244, 246)


def test_transparent_empty_image():
    source = Image.new("RGBA", (40, 30), (0, 0, 0, 0))
    buffer = BytesIO()
    source.save(buffer, format="PNG")
    data, info = module.prepare_vehicle_image(buffer.getvalue())
    assert info["visible_bounds"] == (0, 0, 40, 30)
    assert data.startswith(b"\x89PNG")
