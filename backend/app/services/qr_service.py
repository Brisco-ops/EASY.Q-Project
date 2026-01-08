import os
import qrcode
from app.config import STORAGE_DIR, BASE_URL
from app.services.file_service import ensure_dirs


def generate_qr(slug: str) -> str:
    ensure_dirs()
    url = f"{BASE_URL}/menu/{slug}"
    filename = f"{slug}.png"
    path = os.path.join(STORAGE_DIR, "qr", filename)
    img = qrcode.make(url)
    img.save(path)
    return f"{BASE_URL}/storage/qr/{filename}"
