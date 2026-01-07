from sqlalchemy import String, Integer, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    menus: Mapped[list["Menu"]] = relationship(back_populates="restaurant")


class Menu(Base):
    __tablename__ = "menus"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.id"), nullable=False)

    pdf_path: Mapped[str] = mapped_column(String(500), nullable=False)
    languages_csv: Mapped[str] = mapped_column(String(200), nullable=False, default="fr")

    menu_json: Mapped[str] = mapped_column(Text, nullable=False)
    public_slug: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())

    restaurant: Mapped["Restaurant"] = relationship(back_populates="menus")
