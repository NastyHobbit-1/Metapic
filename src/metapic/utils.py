from __future__ import annotations
from pathlib import Path
from typing import Iterable

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp", ".heic"}

def iter_images(paths: Iterable[str]):
    for p in paths:
        pth = Path(p)
        if pth.is_dir():
            for f in pth.rglob("*"):
                if f.suffix.lower() in IMAGE_EXTS:
                    yield f
        elif pth.suffix.lower() in IMAGE_EXTS:
            yield pth
