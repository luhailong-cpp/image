from pathlib import Path
import hashlib, io, json
import numpy as np
from PIL import Image
CORE,HALO,PATCH,OVERLAP,EXTENDED,FINAL=1024,115,1254,230,4326,4096

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))

def require(condition, message):
    if not condition:
        raise ValueError(message)

def load_rgb(path, expected_hash, expected_size):
    data = Path(path).read_bytes()
    require(hashlib.sha256(data).hexdigest() == expected_hash, f"SHA mismatch: {path}")
    with Image.open(io.BytesIO(data)) as image:
        image.load()
        require(image.size == expected_size and image.mode in ("RGB", "RGBA"), f"Invalid native image: {path}")
        if image.mode == "RGBA":
            require(image.getchannel("A").getextrema() == (255, 255), f"Non-opaque image: {path}")
        return np.asarray(image.convert("RGB")).copy()

def blend(existing, incoming, alpha):
    require(existing.shape == incoming.shape and existing.shape[:2] == alpha.shape, "Blend orientation/dimensions mismatch")
    weight = alpha.astype(np.uint32)[..., None]
    return ((existing.astype(np.uint32) * (255 - weight) + incoming.astype(np.uint32) * weight + 127) // 255).astype(np.uint8)

def append_with_mask(base, incoming, alpha, label, orientation, overlap_transform=None):
    """Return combined pixels and optional transform evidence; never resample."""
    if orientation == "vertical":
        existing, new = base[:, -OVERLAP:], incoming[:, :OVERLAP]
    else:
        existing, new = base[-OVERLAP:, :], incoming[:OVERLAP, :]
    detail = {"id": label, "orientation": orientation, "colorAdjustment": False}
    if overlap_transform is not None:
        original_shape = existing.shape
        existing, new, transform_info = overlap_transform(existing.copy(), new.copy(), alpha.copy(), label, orientation)
        require(existing.shape == new.shape == original_shape and existing.dtype == new.dtype == np.uint8, "Overlap transform changed dimensions/dtype")
        detail.update(colorAdjustment=True, transform=transform_info)
    mixed = blend(existing, new, alpha)
    if orientation == "vertical":
        result = np.concatenate((base[:, :-OVERLAP], mixed, incoming[:, OVERLAP:]), axis=1)
    else:
        result = np.concatenate((base[:-OVERLAP, :], mixed, incoming[OVERLAP:, :]), axis=0)
    return result, detail

def assemble(arrays, masks, overlap_transform=None):
    rows, operations = [], []
    for row in range(1, 5):
        combined = arrays[row, 1]
        for column in range(2, 5):
            label = f"vertical_r{row:02}_c{column-1:02}_c{column:02}"
            combined, info = append_with_mask(combined, arrays[row, column], masks[label], label, "vertical", overlap_transform)
            operations.append(info)
        require(combined.shape == (PATCH, EXTENDED, 3), "Wrong row assembly dimensions")
        rows.append(combined)
    combined = rows[0]
    for row in range(2, 5):
        label = f"horizontal_r{row-1:02}_r{row:02}"
        combined, info = append_with_mask(combined, rows[row-1], masks[label], label, "horizontal", overlap_transform)
        operations.append(info)
    require(combined.shape == (EXTENDED, EXTENDED, 3), "Incomplete extended canvas")
    return combined, operations
