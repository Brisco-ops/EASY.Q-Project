from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas import MenuCreateResponse
from app.services.file_service import save_pdf, is_valid_pdf
from app.services.menu_service import create_menu

router = APIRouter(prefix="/api/menus", tags=["menus"])


@router.post("", response_model=MenuCreateResponse)
async def upload_menu(
    restaurant_name: str = Form(...),
    languages: str = Form("en,fr,es"),
    pdf: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    content = await pdf.read()
    
    if not content or len(content) < 100:
        raise HTTPException(status_code=400, detail="PDF file is empty or too small")
    
    if not is_valid_pdf(content):
        raise HTTPException(status_code=400, detail="Invalid PDF file")
    
    pdf_path = save_pdf(content, pdf.filename or "menu.pdf")
    
    menu, qr_url = create_menu(db, restaurant_name, pdf_path, languages)
    
    from app.config import BASE_URL
    public_url = f"{BASE_URL}/menu/{menu.slug}"
    
    return MenuCreateResponse(
        id=menu.id,
        slug=menu.slug,
        public_url=public_url,
        qr_url=qr_url
    )
