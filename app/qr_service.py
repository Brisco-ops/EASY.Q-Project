import os
import qrcode
from .settings import settings
from .files import ensure_dirs


def generate_qr_png(url: str, filename: str) -> str:
    ensure_dirs()
    path = os.path.join(settings.qrs_dir, filename)
    img = qrcode.make(url)
    img.save(path)
    return path
