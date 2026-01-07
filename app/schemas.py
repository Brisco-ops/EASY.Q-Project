from pydantic import BaseModel, Field
from typing import Optional, Literal


class MenuCreateResponse(BaseModel):
    menu_id: int
    public_url: str
    qr_url: str


class PublicMenuResponse(BaseModel):
    restaurant_name: str
    lang: str
    available_languages: list[str] = Field(default_factory=list)
    currency: Optional[str] = None
    sections: list[dict] = Field(default_factory=list)
    wines: list[dict] = Field(default_factory=list)
    pairings: list[dict] = Field(default_factory=list)


