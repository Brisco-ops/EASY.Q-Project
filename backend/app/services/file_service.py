import os
import secrets
from app.config import STORAGE_DIR


def ensure_dirs():
    os.makedirs(STORAGE_DIR, exist_ok=True)
    os.makedirs(os.path.join(STORAGE_DIR, "uploads"), exist_ok=True)
    os.makedirs(os.path.join(STORAGE_DIR, "qr"), exist_ok=True)


def save_pdf(content: bytes, original_filename: str) -> str:
    ensure_dirs()
    token = secrets.token_hex(8)
    safe_name = os.path.basename(original_filename).replace(" ", "_")
    if not safe_name.lower().endswith(".pdf"):
        safe_name += ".pdf"
    filename = f"{token}_{safe_name}"
    path = os.path.join(STORAGE_DIR, "uploads", filename)
    with open(path, "wb") as f:
        f.write(content)
    return path


def is_valid_pdf(content: bytes) -> bool:
    return len(content) >= 5 and content[:5] == b"%PDF-"
