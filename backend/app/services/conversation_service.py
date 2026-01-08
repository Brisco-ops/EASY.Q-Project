import json
from sqlalchemy.orm import Session
from app.models import Conversation, Menu


def get_or_create_conversation(
    db: Session, menu_id: int, session_id: str
) -> Conversation:
    """Get existing conversation or create new one"""
    conv = (
        db.query(Conversation)
        .filter(Conversation.menu_id == menu_id, Conversation.session_id == session_id)
        .first()
    )

    if not conv:
        conv = Conversation(menu_id=menu_id, session_id=session_id, messages="[]")
        db.add(conv)
        db.commit()
        db.refresh(conv)

    return conv


def get_conversation_messages(db: Session, menu_id: int, session_id: str) -> list[dict]:
    """Get messages from a conversation"""
    conv = get_or_create_conversation(db, menu_id, session_id)
    return json.loads(conv.messages)


def save_conversation_messages(
    db: Session, menu_id: int, session_id: str, messages: list[dict]
):
    """Save messages to a conversation"""
    conv = get_or_create_conversation(db, menu_id, session_id)
    # Keep only last 20 messages
    conv.messages = json.dumps(messages[-20:], ensure_ascii=False)
    db.commit()


def clear_conversation(db: Session, menu_id: int, session_id: str):
    """Clear a conversation"""
    conv = (
        db.query(Conversation)
        .filter(Conversation.menu_id == menu_id, Conversation.session_id == session_id)
        .first()
    )

    if conv:
        conv.messages = "[]"
        db.commit()
