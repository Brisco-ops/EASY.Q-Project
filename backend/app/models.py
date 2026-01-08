from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db import Base


class Menu(Base):
    __tablename__ = "menus"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    pdf_path = Column(String(500), nullable=False)
    languages = Column(String(50), nullable=False, default="en,fr,es")
    menu_data = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    conversations = relationship(
        "Conversation", back_populates="menu", cascade="all, delete-orphan"
    )


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    menu_id = Column(Integer, ForeignKey("menus.id"), nullable=False)
    session_id = Column(String(100), nullable=False, index=True)  # Browser session ID
    messages = Column(Text, nullable=False, default="[]")  # JSON array of messages
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    menu = relationship("Menu", back_populates="conversations")
