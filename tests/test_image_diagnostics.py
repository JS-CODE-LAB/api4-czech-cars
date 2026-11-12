"""Verify image metadata detection without third-party packages."""
import importlib.util
import struct
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "custom_components/skoda_public/image_diagnostics.py"
spec = importlib.util.spec_from_file_location("image_diagnostics", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_png_rgba():
    header = b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR"
    data = header + struct.pack(">IIBBBBB", 640, 360, 8, 6, 0, 0, 0) + b"\x00\x00\x00\x00"
    result = module.inspect_image(data)
    assert result["format"] == "PNG"
    assert result["width"] == 640 and result["height"] == 360
    assert result["alpha"] == "yes"


def test_gif():
    result = module.inspect_image(b"GIF89a" + struct.pack("<HH", 320, 240))
    assert (result["width"], result["height"]) == (320, 240)


def test_unknown():
    result = module.inspect_image(b"not an image")
    assert result["format"] == "unknown"
    assert result["bytes"] == 12
