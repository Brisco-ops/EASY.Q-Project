from pydantic import BaseModel
from typing import Optional


class MenuCreateResponse(BaseModel):
    id: int
    slug: str
    public_url: str
    qr_url: str


class MenuItem(BaseModel):
    name: str
    description: Optional[str] = None
    price: Optional[float] = None
    tags: list[str] = []


class MenuSection(BaseModel):
    title: str
    items: list[MenuItem] = []


class Wine(BaseModel):
    name: str
    type: Optional[str] = None
    region: Optional[str] = None
    grape: Optional[str] = None
    price: Optional[float] = None
    pairing_tags: list[str] = []


class MenuData(BaseModel):
    restaurant_name: str
    currency: Optional[str] = "EUR"
    sections: list[MenuSection] = []
    wines: list[Wine] = []


class PublicMenuResponse(BaseModel):
    restaurant_name: str
    lang: str
    available_languages: list[str]
    currency: Optional[str] = None
    sections: list[dict] = []
    wines: list[dict] = []


class ChatRequest(BaseModel):
    messages: list[dict]
    lang: str = "en"
    session_id: str | None = None  # For conversation memory


class ChatResponse(BaseModel):
    answer: str


class ConversationResponse(BaseModel):
    messages: list[dict]
