from __future__ import annotations

from typing import Any
from .pairing_rules import preferred_styles_for_tags


def _wine_kind(wine: dict[str, Any]) -> str:
    kind = (wine.get("type") or "other").strip().lower()
    if kind in {"red", "white", "rose", "sparkling", "dessert"}:
        return kind
    return "other"


def _preferred_map(tags: list[str]) -> list[tuple[str, int]]:
    styles = preferred_styles_for_tags(tags)
    return [(s.kind, s.weight) for s in styles]


def _price_bonus(wine: dict[str, Any]) -> int:
    price = wine.get("price")
    if not isinstance(price, (int, float)):
        return 0
    if price <= 9:
        return 5
    if price <= 14:
        return 3
    return 1


def _wine_score(wine: dict[str, Any], preferred: list[tuple[str, int]]) -> int:
    kind = _wine_kind(wine)
    base = dict(preferred).get(kind, 0)
    return base + _price_bonus(wine)


def _score_to_confidence(best_score: int, best_base_weight: int) -> float:
    # best_base_weight ~ [0..95], best_score inclut bonus prix (+0..5)
    if best_base_weight <= 0:
        return 0.0

    raw = best_score / float(best_base_weight + 5)
    if raw < 0:
        return 0.0
    if raw > 1:
        return 1.0
    return round(raw, 2)


def _best_base_weight(preferred: list[tuple[str, int]]) -> int:
    return max([w for _, w in preferred], default=0)


def build_pairings(menu_payload: dict[str, Any], min_confidence: float = 0.55) -> list[dict[str, Any]]:
    wines = menu_payload.get("wines") or []
    if not wines:
        return []

    pairings: list[dict[str, Any]] = []
    cache: dict[str, list[tuple[str, int]]] = {}

    sections = menu_payload.get("sections") or []
    for s_idx, section in enumerate(sections):
        items = section.get("items") or []
        for i_idx, item in enumerate(items):
            dish_name = item.get("name")
            if not dish_name:
                continue

            tags = item.get("tags") or []
            key = "|".join(sorted([str(t).strip().lower() for t in tags if str(t).strip()]))

            if key not in cache:
                cache[key] = _preferred_map(tags)

            preferred = cache[key]
            base_weight = _best_base_weight(preferred)

            best_wine = None
            best_score = -1
            best_base = 0

            for w in wines:
                kind = _wine_kind(w)
                base = dict(preferred).get(kind, 0)
                score = base + _price_bonus(w)
                if score > best_score:
                    best_score = score
                    best_wine = w
                    best_base = base

            confidence = _score_to_confidence(best_score, max(best_base, base_weight))

            if not best_wine or confidence < float(min_confidence):
                continue

            pairings.append({
                "section_index": s_idx,
                "item_index": i_idx,
                "dish_name": dish_name,
                "wine_name": best_wine.get("name"),
                "reason": None,
                "confidence": confidence,
                "dish_tags": tags,
                "wine_type": best_wine.get("type"),
                "wine_region": best_wine.get("region"),
                "wine_grape": best_wine.get("grape"),
            })

    return pairings
