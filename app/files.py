import os
import secrets
from fastapi import UploadFile, HTTPException
from .settings import settings


def ensure_dirs() -> None:
    os.makedirs(settings.storage_dir, exist_ok=True)
    os.makedirs(settings.uploads_dir, exist_ok=True)
    os.makedirs(settings.qrs_dir, exist_ok=True)


def safe_pdf_filename(original: str) -> str:
    token = secrets.token_hex(8)
    base = os.path.basename(original).replace(" ", "_")
    if not base.lower().endswith(".pdf"):
        base = f"{base}.pdf"
    return f"{token}_{base}"


def _looks_like_pdf(data: bytes) -> bool:
    return len(data) >= 5 and data[:5] == b"%PDF-"


async def save_upload_pdf(file: UploadFile) -> str:
    ensure_dirs()
    content = await file.read()

    if not content or len(content) < 100:
        raise HTTPException(status_code=400, detail="Fichier PDF vide ou trop petit")

    if not _looks_like_pdf(content):
        raise HTTPException(status_code=400, detail="Le fichier envoyé ne ressemble pas à un PDF valide")

    filename = safe_pdf_filename(file.filename or "menu.pdf")
    path = os.path.join(settings.uploads_dir, filename)

    with open(path, "wb") as f:
        f.write(content)

    return path
