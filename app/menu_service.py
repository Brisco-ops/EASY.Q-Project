import json
import re
import secrets
from sqlalchemy.orm import Session

from .models import Restaurant, Menu
from .gemini_client import extract_menu_from_pdf, extract_menu_from_images
from .pdf_to_images import pdf_to_png_paths
from .pairing_service import build_pairings
from .gemini_reason import enrich_pairing_reasons


_slug_re = re.compile(r"[^a-z0-9]+")


def _slugify(name: str) -> str:
    s = (name or "menu").strip().lower()
    s = _slug_re.sub("-", s).strip("-")
    suffix = secrets.token_hex(3)
    return f"{s[:50]}-{suffix}" if s else f"menu-{suffix}"


def _extract_with_fallback(pdf_path: str, languages: list[str]) -> dict:
    try:
        return extract_menu_from_pdf(pdf_path, languages)
    except Exception as e:
        msg = str(e).lower()
        if "document has no pages" in msg or "no pages" in msg or "0 page" in msg:
            image_paths = pdf_to_png_paths(pdf_path, dpi=200, max_pages=8)
            return extract_menu_from_images(image_paths, languages)
        raise


def _build_pairings_payload(extracted: dict) -> list[dict]:
    pairings = build_pairings(extracted, min_confidence=0.55)
    pairings = enrich_pairing_reasons(pairings, max_items=25)

    return [
        {
            "section_index": p.get("section_index"),
            "item_index": p.get("item_index"),
            "dish_name": p.get("dish_name"),
            "wine_name": p.get("wine_name"),
            "reason": p.get("reason"),
            "confidence": p.get("confidence"),
        }
        for p in pairings
        if p.get("wine_name") is not None
    ]



def create_menu(db: Session, restaurant_name: str, pdf_path: str, languages: list[str]) -> Menu:
    restaurant = Restaurant(name=restaurant_name.strip())
    db.add(restaurant)
    db.flush()

    extracted = _extract_with_fallback(pdf_path, languages)
    extracted.setdefault("restaurant_name", restaurant.name)

    extracted["pairings"] = _build_pairings_payload(extracted)

    slug = _slugify(restaurant.name)
    menu = Menu(
        restaurant_id=restaurant.id,
        pdf_path=pdf_path,
        languages_csv=",".join(languages),
        menu_json=json.dumps(extracted, ensure_ascii=False),
        public_slug=slug,
    )
    db.add(menu)
    db.commit()
    db.refresh(menu)
    return menu


def get_public_menu(db: Session, slug: str) -> Menu | None:
    return db.query(Menu).filter(Menu.public_slug == slug).first()
