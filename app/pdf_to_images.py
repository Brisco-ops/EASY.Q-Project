from __future__ import annotations

import os
import secrets
from pdf2image import convert_from_path
from .files import ensure_dirs
from .settings import settings


def pdf_to_png_paths(pdf_path: str, dpi: int = 200, max_pages: int = 8) -> list[str]:
    ensure_dirs()
    token = secrets.token_hex(6)
    out_dir = os.path.join(settings.uploads_dir, f"pages_{token}")
    os.makedirs(out_dir, exist_ok=True)

    images = convert_from_path(pdf_path, dpi=dpi, fmt="png")
    paths: list[str] = []

    for i, img in enumerate(images[:max_pages], start=1):
        p = os.path.join(out_dir, f"page_{i}.png")
        img.save(p, "PNG")
        paths.append(p)

    return paths
