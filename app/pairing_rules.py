from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class WineStyle:
    kind: str  # "red" | "white" | "rose" | "sparkling" | "dessert" | "other"
    weight: int


def _norm_tags(tags: Iterable[str]) -> set[str]:
    return {str(t).strip().lower() for t in (tags or []) if str(t).strip()}


def preferred_styles_for_tags(tags: list[str]) -> list[WineStyle]:
    t = _norm_tags(tags)

    styles: list[WineStyle] = []

    def add(kind: str, weight: int) -> None:
        styles.append(WineStyle(kind=kind, weight=weight))

    # protéines / types
    if {"beef", "steak", "lamb", "duck"} & t:
        add("red", 90)
    if {"pork"} & t:
        add("red", 55)
        add("white", 45)
    if {"fish", "seafood", "shellfish"} & t:
        add("white", 85)
        add("sparkling", 55)
    if {"chicken", "turkey"} & t:
        add("white", 60)
        add("red", 45)
    if {"vegetarian", "vegan"} & t:
        add("white", 55)
        add("rose", 55)
        add("sparkling", 40)

    # styles culinaires
    if {"spicy", "chili"} & t:
        add("rose", 75)
        add("white", 60)
    if {"creamy", "buttery"} & t:
        add("white", 75)
    if {"tomato"} & t:
        add("red", 65)
    if {"fried", "crispy"} & t:
        add("sparkling", 70)
        add("white", 55)
    if {"grilled", "smoked"} & t:
        add("red", 60)

    # desserts
    if {"dessert", "sweet"} & t:
        add("dessert", 95)
        add("sparkling", 55)

    # fallback
    if not styles:
        add("white", 50)
        add("red", 45)

    # agrège en gardant le meilleur poids par type
    best: dict[str, int] = {}
    for s in styles:
        best[s.kind] = max(best.get(s.kind, 0), s.weight)

    return [WineStyle(kind=k, weight=w) for k, w in sorted(best.items(), key=lambda x: -x[1])]
