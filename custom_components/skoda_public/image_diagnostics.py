"""Privacy-preserving image metadata inspection without image dependencies.

Never log image contents, source URLs, query strings, or authentication tokens.
"""
from __future__ import annotations

import struct


def inspect_image(data: bytes) -> dict[str, object]:
    """Inspect image header, dimensions and possible alpha transparency."""
    result: dict[str, object] = {
        "format": "unknown", "width": None, "height": None,
        "alpha": "unknown", "bytes": len(data),
    }
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 33:
        width, height, depth, color = struct.unpack_from(">IIBB", data, 16)
        result.update(format="PNG", width=width, height=height,
                      alpha="yes" if color in (4, 6) or b"tRNS" in data else "no")
    elif data[:6] in (b"GIF87a", b"GIF89a") and len(data) >= 10:
        width, height = struct.unpack_from("<HH", data, 6)
        result.update(format="GIF", width=width, height=height,
                      alpha="possible" if b"\x21\xf9\x04" in data else "unknown")
    elif data.startswith(b"RIFF") and data[8:12] == b"WEBP" and len(data) >= 30:
        chunk = data[12:16]
        result["format"] = "WebP"
        if chunk == b"VP8X":
            result.update(width=1 + int.from_bytes(data[24:27], "little"),
                          height=1 + int.from_bytes(data[27:30], "little"),
                          alpha="yes" if data[20] & 0x10 else "no")
        elif chunk == b"VP8 " and len(data) >= 30 and data[23:26] == b"\x9d\x01\x2a":
            result.update(width=struct.unpack_from("<H", data, 26)[0] & 0x3fff,
                          height=struct.unpack_from("<H", data, 28)[0] & 0x3fff,
                          alpha="no")
        elif chunk == b"VP8L" and len(data) >= 25 and data[20] == 0x2f:
            bits = int.from_bytes(data[21:25], "little")
            result.update(width=(bits & 0x3fff) + 1,
                          height=((bits >> 14) & 0x3fff) + 1,
                          alpha="possible")
    elif data.startswith(b"\xff\xd8"):
        result["format"] = "JPEG"
        result["alpha"] = "no"
        offset = 2
        while offset + 4 <= len(data):
            if data[offset] != 0xff:
                break
            marker = data[offset + 1]
            offset += 2
            if marker in (0xd8, 0xd9) or 0xd0 <= marker <= 0xd7:
                continue
            if marker == 0xda:
                break
            length = int.from_bytes(data[offset:offset + 2], "big")
            if length < 2 or offset + length > len(data):
                break
            if marker in (0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7,
                          0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf) and length >= 7:
                result["height"] = int.from_bytes(data[offset + 3:offset + 5], "big")
                result["width"] = int.from_bytes(data[offset + 5:offset + 7], "big")
                break
            offset += length
    return result
