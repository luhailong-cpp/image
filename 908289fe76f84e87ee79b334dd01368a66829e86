"""Grade GIF palette RGB bytes without re-encoding any animation blocks.

The callback receives an N x 3 uint8 NumPy array and must return the same shape
and dtype. All indices used for transparency by a palette's frames are restored
to their original RGB. No image indices, LZW data, timing, disposal, or extension
bytes are changed. This module does not read or write files.
"""

from __future__ import annotations

import hashlib
import struct
from collections.abc import Callable
from dataclasses import dataclass, field

import numpy as np


@dataclass
class GifPalette:
    name: str
    start: int
    entries: int
    transparent_indices: set[int] = field(default_factory=set)

    @property
    def end(self) -> int:
        return self.start + self.entries * 3


def inspect_gif_bytes(data: bytes) -> tuple[list[GifPalette], dict]:
    """Parse the GIF block stream and determine every palette's protected RGB.

    GIF87a/89a, global/local palettes, comments, application extensions, and plain
    text extensions are supported. Malformed/truncated streams and image frames
    without a color table raise ValueError. Bytes following the trailer are
    preserved. This parser deliberately does not decompress or rewrite pixels.
    """
    if len(data) < 14 or data[:6] not in (b"GIF87a", b"GIF89a"):
        raise ValueError("Not a GIF87a/89a stream")
    width, height = struct.unpack_from("<HH", data, 6)
    if not width or not height:
        raise ValueError("GIF logical screen dimensions cannot be zero")
    palettes: list[GifPalette] = []
    global_palette = None
    position = 13

    def require(end: int):
        if end > len(data):
            raise ValueError(f"Truncated GIF near byte {position}")

    def new_palette(name: str, packed: int) -> GifPalette:
        nonlocal position
        palette = GifPalette(name, position, 1 << ((packed & 7) + 1))
        require(palette.end)
        palettes.append(palette)
        position = palette.end
        return palette

    def subblocks() -> list[bytes]:
        nonlocal position
        blocks = []
        while True:
            require(position + 1)
            length = data[position]
            position += 1
            if not length:
                return blocks
            require(position + length)
            blocks.append(data[position:position + length])
            position += length

    if data[10] & 0x80:
        global_palette = new_palette("global", data[10])
    frames = []
    pending_control = {"transparent_index": None, "delay_cs": 0, "disposal": 0, "user_input": False}
    extensions = []
    plain_text_blocks = 0
    loop_count = None

    def consume_control(palette: GifPalette | None):
        nonlocal pending_control
        control = pending_control
        index = control["transparent_index"]
        if index is not None:
            if palette is None or index >= palette.entries:
                raise ValueError("GIF transparency index is outside its color table")
            palette.transparent_indices.add(index)
        pending_control = {"transparent_index": None, "delay_cs": 0, "disposal": 0, "user_input": False}
        return control

    while True:
        require(position + 1)
        block_start = position
        marker = data[position]
        position += 1
        if marker == 0x3B:
            trailer_position = block_start
            break
        if marker == 0x21:
            require(position + 1)
            label = data[position]
            position += 1
            blocks = subblocks()
            extensions.append({"label": label, "start": block_start, "end": position})
            if label == 0xF9:
                if len(blocks) != 1 or len(blocks[0]) != 4:
                    raise ValueError("GIF graphic control extension must contain four bytes")
                control = blocks[0]
                pending_control = {
                    "transparent_index": control[3] if control[0] & 1 else None,
                    "delay_cs": struct.unpack_from("<H", control, 1)[0],
                    "disposal": (control[0] >> 2) & 7,
                    "user_input": bool(control[0] & 2),
                }
            elif label == 0x01:
                if not blocks or len(blocks[0]) != 12:
                    raise ValueError("GIF plain text extension must start with a 12-byte header")
                if global_palette is None:
                    raise ValueError("GIF plain text extension requires a global color table")
                consume_control(global_palette)
                plain_text_blocks += 1
            elif label == 0xFF and blocks and blocks[0] in (b"NETSCAPE2.0", b"ANIMEXTS1.0"):
                if len(blocks) > 1 and len(blocks[1]) == 3 and blocks[1][0] == 1:
                    loop_count = struct.unpack_from("<H", blocks[1], 1)[0]
            continue
        if marker == 0x2C:
            require(position + 9)
            left, top, frame_width, frame_height, packed = struct.unpack_from("<HHHHB", data, position)
            position += 9
            if not frame_width or not frame_height:
                raise ValueError("GIF image dimensions cannot be zero")
            palette = new_palette(f"frame_{len(frames)}_local", packed) if packed & 0x80 else global_palette
            if palette is None:
                raise ValueError("GIF image frame does not have a local or global color table")
            control = consume_control(palette)
            require(position + 1)
            lzw_start = position
            lzw_min_code_size = data[position]
            position += 1
            subblocks()
            frames.append({
                "index": len(frames), "left": left, "top": top,
                "width": frame_width, "height": frame_height,
                "interlaced": bool(packed & 0x40), "palette": palette.name,
                "lzw_min_code_size": lzw_min_code_size,
                "lzw_sha256": hashlib.sha256(data[lzw_start:position]).hexdigest(),
                **control,
            })
            continue
        raise ValueError(f"Unsupported/malformed GIF block 0x{marker:02x} at byte {block_start}")
    return palettes, {
        "version": data[:6].decode("ascii"),
        "width": width, "height": height,
        "frame_count": len(frames), "frames": frames,
        "loop_count": loop_count,
        "global_palette_count": int(global_palette is not None),
        "local_palette_count": len(palettes) - int(global_palette is not None),
        "palette_count": len(palettes),
        "palette_entries": sum(palette.entries for palette in palettes),
        "protected_transparency_entries": sum(len(palette.transparent_indices) for palette in palettes),
        "palettes": [{"name": p.name, "start": p.start, "entries": p.entries, "transparent_indices": sorted(p.transparent_indices)} for p in palettes],
        "plain_text_blocks": plain_text_blocks,
        "extensions": extensions,
        "trailer_position": trailer_position,
        "trailing_bytes": len(data) - position,
    }


def grade_gif_bytes(
    data: bytes,
    grade_rgb_callback: Callable[[np.ndarray], np.ndarray],
) -> tuple[bytes, dict]:
    """Return palette-graded GIF bytes and stats, with exact animation layout."""
    palettes, stats = inspect_gif_bytes(data)
    stats.update({"callback_calls": 0, "modified_palette_count": 0, "modified_color_entries": 0, "modified": False})
    result = None
    for palette in palettes:
        original = np.frombuffer(data[palette.start:palette.end], dtype=np.uint8).reshape(palette.entries, 3)
        output = grade_rgb_callback(original.copy())
        stats["callback_calls"] += 1
        if not isinstance(output, np.ndarray) or output.dtype != np.uint8 or output.shape != original.shape:
            raise TypeError("GIF grading callback must return a matching N x 3 uint8 NumPy array")
        output = output.copy()
        if palette.transparent_indices:
            protected = sorted(palette.transparent_indices)
            output[protected] = original[protected]
        changed = int(np.count_nonzero(np.any(output != original, axis=1)))
        if changed:
            if result is None:
                result = bytearray(data)
            result[palette.start:palette.end] = output.tobytes()
            stats["modified_palette_count"] += 1
            stats["modified_color_entries"] += changed
    stats["modified"] = result is not None
    return (bytes(result) if result is not None else data), stats


def gif_structure_bytes(data: bytes) -> bytes:
    """Mask all palette payloads for byte-exact animation-block verification."""
    palettes, _ = inspect_gif_bytes(data)
    result = bytearray(data)
    for palette in palettes:
        result[palette.start:palette.end] = b"\x00" * (palette.entries * 3)
    return bytes(result)
