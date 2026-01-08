from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas import (
    PublicMenuResponse,
    ChatRequest,
    ChatResponse,
    ConversationResponse,
)
from app.services.menu_service import (
    get_menu_by_slug,
    get_menu_data,
    get_full_menu_data,
)
from app.services.chat_service import chat_about_menu, chat_about_menu_stream
from app.services.conversation_service import (
    get_conversation_messages,
    save_conversation_messages,
    clear_conversation,
)

router = APIRouter(prefix="/api/public", tags=["public"])


@router.get("/menus/{slug}", response_model=PublicMenuResponse)
def get_public_menu(slug: str, lang: str = "en", db: Session = Depends(get_db)):
    menu = get_menu_by_slug(db, slug)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")

    data = get_menu_data(menu, lang)
    return PublicMenuResponse(**data)


@router.get("/menus/{slug}/conversation")
def get_conversation(slug: str, session_id: str, db: Session = Depends(get_db)):
    """Get conversation history for a session"""
    menu = get_menu_by_slug(db, slug)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")

    messages = get_conversation_messages(db, menu.id, session_id)
    return ConversationResponse(messages=messages)


@router.delete("/menus/{slug}/conversation")
def delete_conversation(slug: str, session_id: str, db: Session = Depends(get_db)):
    """Clear conversation history for a session"""
    menu = get_menu_by_slug(db, slug)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")

    clear_conversation(db, menu.id, session_id)
    return {"status": "cleared"}


@router.post("/menus/{slug}/chat", response_model=ChatResponse)
def chat_with_menu(slug: str, request: ChatRequest, db: Session = Depends(get_db)):
    menu = get_menu_by_slug(db, slug)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")

    full_data = get_full_menu_data(menu)

    lang = request.lang or "en"
    translations = full_data.get("translations", {})
    if lang in translations:
        full_data["sections"] = translations[lang].get(
            "sections", full_data.get("sections", [])
        )
        full_data["wines"] = translations[lang].get("wines", full_data.get("wines", []))

    answer = chat_about_menu(full_data, lang, request.messages)

    if request.session_id:
        messages_to_save = request.messages + [{"role": "assistant", "content": answer}]
        save_conversation_messages(db, menu.id, request.session_id, messages_to_save)

    return ChatResponse(answer=answer)


@router.post("/menus/{slug}/chat/stream")
def chat_with_menu_stream(
    slug: str, request: ChatRequest, db: Session = Depends(get_db)
):
    """Streaming chat endpoint using Server-Sent Events."""
    menu = get_menu_by_slug(db, slug)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")

    full_data = get_full_menu_data(menu)

    lang = request.lang or "en"
    translations = full_data.get("translations", {})
    if lang in translations:
        full_data["sections"] = translations[lang].get(
            "sections", full_data.get("sections", [])
        )
        full_data["wines"] = translations[lang].get("wines", full_data.get("wines", []))

    collected_response = []

    def generate():
        try:
            for chunk in chat_about_menu_stream(full_data, lang, request.messages):
                collected_response.append(chunk)
                yield f"data: {chunk}\n\n"

            if request.session_id:
                full_answer = "".join(collected_response)
                messages_to_save = request.messages + [
                    {"role": "assistant", "content": full_answer}
                ]
                save_conversation_messages(
                    db, menu.id, request.session_id, messages_to_save
                )

            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
