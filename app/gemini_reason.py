from __future__ import annotations

import json
from google import genai
from .settings import settings


def _client() -> genai.Client:
    return genai.Client(api_key=settings.google_api_key)


def enrich_pairing_reasons(pairings: list[dict], max_items: int = 25) -> list[dict]:
    if not pairings:
        return pairings

    client = _client()
    payload = pairings[:max_items]

    schema = {
        "type": "object",
        "properties": {
            "reasons": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "dish_name": {"type": "string"},
                        "wine_name": {"type": "string"},
                        "reason": {"type": "string"},
                    },
                    "required": ["dish_name", "wine_name", "reason"],
                },
            }
        },
        "required": ["reasons"],
    }

    prompt = """
Tu écris des raisons d'accord mets-vins courtes, factuelles et prudentes.
Règles:
- 1 phrase max, 90 caractères idéalement.
- Tu te bases uniquement sur: dish_tags, wine_type, wine_region, wine_grape.
- Ne cite pas de cuissons/ingrédients non présents.
- Si tu es incertain: raison générique (ex: "Accord équilibré avec les saveurs du plat.").
Retourne uniquement un JSON conforme au schéma.
""".strip()

    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=[{"role": "user", "parts": [{"text": prompt}, {"text": json.dumps(payload, ensure_ascii=False)}]}],
        config={"response_mime_type": "application/json", "response_schema": schema},
    )

    data = json.loads(getattr(response, "text", "") or "{}")
    reasons = {(r["dish_name"], r["wine_name"]): r["reason"] for r in data.get("reasons", [])}

    for p in pairings:
        key = (p.get("dish_name"), p.get("wine_name"))
        if key in reasons:
            p["reason"] = reasons[key]

    return pairings
