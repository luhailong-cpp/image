"""Replace only embedded PNG payloads in SVGs, preserving all other bytes.

The raster callback accepts PNG bytes and returns PNG bytes. An optional mapping
from *original PNG byte SHA-256* to graded bytes permits exact reuse of already
graded standalone assets. This module does not grade vector colors, follow
external references, serialize XML, or write files.
"""

from __future__ import annotations

import base64
import hashlib
import re
import struct
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from xml.parsers import expat

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
SVG_NAMESPACE = "http://www.w3.org/2000/svg"
XLINK_NAMESPACE = "http://www.w3.org/1999/xlink"
_ATTRIBUTE = re.compile(rb"([^\s=<>/'\"]+)\s*=\s*(['\"])(.*?)\2", re.DOTALL)
_PNG_URI = re.compile(rb"(data:image/png;base64,)(.*)\Z", re.DOTALL | re.IGNORECASE)


@dataclass(frozen=True)
class EmbeddedPng:
    """Location and decoded content of a real SVG image href attribute."""

    start: int
    end: int
    prefix: bytes
    data: bytes
    sha256: str


def _tag_end(data: bytes, start: int) -> int:
    quote = None
    for position in range(start, len(data)):
        value = data[position]
        if quote is not None:
            if value == quote:
                quote = None
        elif value in (34, 39):
            quote = value
        elif value == 62:
            return position + 1
    raise ValueError("Unterminated SVG start tag")


def _png_dimensions(data: bytes) -> tuple[int, int]:
    if len(data) < 33 or not data.startswith(PNG_SIGNATURE) or data[12:16] != b"IHDR":
        raise ValueError("Embedded raster or callback output is not a PNG")
    return struct.unpack(">II", data[16:24])


def inspect_svg_bytes(data: bytes) -> tuple[list[EmbeddedPng], dict]:
    """Parse SVG image references without changing the XML or decoding pixels.

    The repository uses UTF-8 SVG. UTF-16/32 is rejected rather than re-encoded.
    Entity declarations are rejected; ordinary XML character references work in
    text and vector attributes. PNG data URIs must contain literal base64 (with
    optional ASCII whitespace), as all current project assets do.
    """
    if b"\x00" in data[:256] or data.startswith((b"\xff\xfe", b"\xfe\xff")):
        raise ValueError("SVG grading requires an ASCII-compatible XML encoding")
    parser = expat.ParserCreate(namespace_separator="}")
    references: list[EmbeddedPng] = []
    stats = {
        "image_elements": 0,
        "embedded_png_references": 0,
        "unique_embedded_pngs": 0,
        "external_image_references": 0,
        "other_data_image_references": 0,
        "image_elements_without_href": 0,
        "text_elements": 0,
    }
    namespaces: dict[str, list[str]] = {}

    def start_namespace(prefix, uri):
        namespaces.setdefault(prefix or "", []).append(uri)

    def end_namespace(prefix):
        namespaces[prefix or ""].pop()

    def reject_entity(*_args):
        raise ValueError("SVG entity declarations/external entities are not supported")

    def is_svg_tag(name: str, local_name: str) -> bool:
        return name in (local_name, f"{SVG_NAMESPACE}}}{local_name}")

    def start_element(name, attributes):
        if is_svg_tag(name, "text"):
            stats["text_elements"] += 1
        if not is_svg_tag(name, "image"):
            return
        stats["image_elements"] += 1
        start = parser.CurrentByteIndex
        tag = data[start:_tag_end(data, start)]
        href_count = 0
        for match in _ATTRIBUTE.finditer(tag):
            raw_name = match.group(1).decode("ascii")
            parts = raw_name.split(":", 1)
            is_href = raw_name == "href"
            if len(parts) == 2 and parts[1] == "href":
                is_href = bool(namespaces.get(parts[0])) and namespaces[parts[0]][-1] == XLINK_NAMESPACE
            if not is_href:
                continue
            href_count += 1
            value = match.group(3)
            uri_match = _PNG_URI.fullmatch(value)
            if uri_match is None:
                key = "other_data_image_references" if value.lower().startswith(b"data:") else "external_image_references"
                stats[key] += 1
                continue
            payload = re.sub(rb"[\t\n\r ]", b"", uri_match.group(2))
            try:
                png = base64.b64decode(payload, validate=True)
            except ValueError as error:
                raise ValueError("Invalid base64 PNG in SVG image href") from error
            _png_dimensions(png)
            references.append(EmbeddedPng(
                start=start + match.start(3),
                end=start + match.end(3),
                prefix=uri_match.group(1),
                data=png,
                sha256=hashlib.sha256(png).hexdigest(),
            ))
            stats["embedded_png_references"] += 1
        if not href_count:
            stats["image_elements_without_href"] += 1

    parser.StartNamespaceDeclHandler = start_namespace
    parser.EndNamespaceDeclHandler = end_namespace
    parser.StartElementHandler = start_element
    parser.EntityDeclHandler = reject_entity
    parser.ExternalEntityRefHandler = reject_entity
    parser.SetParamEntityParsing(expat.XML_PARAM_ENTITY_PARSING_NEVER)
    parser.Parse(data, True)
    stats["unique_embedded_pngs"] = len({reference.sha256 for reference in references})
    if references:
        stats["classification"] = "embedded_raster"
    elif stats["image_elements"]:
        stats["classification"] = "external_or_other_images"
    elif stats["text_elements"]:
        stats["classification"] = "vector_with_text_no_raster"
    else:
        stats["classification"] = "vector_no_raster"
    return references, stats


def grade_svg_bytes(
    data: bytes,
    grade_raster_bytes: Callable[[bytes], bytes],
    *,
    png_sha256_index: Mapping[str, bytes] | None = None,
) -> tuple[bytes, dict]:
    """Grade each distinct embedded PNG once; return SVG bytes and statistics.

    Only exact byte-hash index hits are reused. A differently encoded PNG with
    identical pixels is passed to the callback, whose own pixel cache may reuse
    an output safely. External image paths remain unchanged. Calls are always
    made against original input bytes, so duplicate href/xlink:href attributes
    cannot be graded twice. Across separate calls, the caller must use original
    files or a manifest; no hidden marker is inserted into the SVG.
    """
    references, stats = inspect_svg_bytes(data)
    stats.update({
        "callback_calls": 0,
        "sha_index_reuses": 0,
        "duplicate_reuses": 0,
        "modified_embedded_references": 0,
        "modified_unique_embedded_pngs": 0,
        "modified": False,
    })
    cache: dict[str, bytes] = {}
    replacements: list[tuple[int, int, bytes]] = []
    changed_hashes = set()
    for reference in references:
        if reference.sha256 in cache:
            output = cache[reference.sha256]
            stats["duplicate_reuses"] += 1
        else:
            if png_sha256_index is not None and reference.sha256 in png_sha256_index:
                output = png_sha256_index[reference.sha256]
                stats["sha_index_reuses"] += 1
            else:
                output = grade_raster_bytes(reference.data)
                stats["callback_calls"] += 1
            if not isinstance(output, bytes):
                raise TypeError("Raster callback and PNG SHA index values must be bytes")
            if _png_dimensions(output) != _png_dimensions(reference.data):
                raise ValueError("SVG raster grading changed embedded PNG dimensions")
            cache[reference.sha256] = output
        if output != reference.data:
            replacements.append((reference.start, reference.end, reference.prefix + base64.b64encode(output)))
            stats["modified_embedded_references"] += 1
            changed_hashes.add(reference.sha256)
    if not replacements:
        return data, stats
    result = bytearray()
    cursor = 0
    for start, end, replacement in replacements:
        result.extend(data[cursor:start])
        result.extend(replacement)
        cursor = end
    result.extend(data[cursor:])
    stats["modified_unique_embedded_pngs"] = len(changed_hashes)
    stats["modified"] = True
    return bytes(result), stats


def svg_structure_bytes(data: bytes) -> bytes:
    """Mask embedded PNG href values for exact preservation verification."""
    references, _ = inspect_svg_bytes(data)
    result = bytearray()
    cursor = 0
    for reference in references:
        result.extend(data[cursor:reference.start])
        result.extend(b"<EMBEDDED_PNG>")
        cursor = reference.end
    result.extend(data[cursor:])
    return bytes(result)
