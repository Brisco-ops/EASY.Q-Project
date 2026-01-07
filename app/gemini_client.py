import json
import re
from google import genai
from .settings import settings


def _client() -> genai.Client:
    return genai.Client(api_key=settings.google_api_key)


def _extract_json(text: str) -> dict:
    text = (text or "").strip()
    if not text:
        raise ValueError("Réponse Gemini vide")

    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text).strip()

    if not text.startswith("{"):
        m = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if m:
            text = m.group(0)

    return json.loads(text)


def _prompt(languages: list[str]) -> str:
    langs = ", ".join(sorted(set([l.strip().lower() for l in languages if l.strip()]))) or "fr"
    return f"""
Tu es un expert en menus de restaurant.

Retourne UNIQUEMENT un JSON strict (pas de markdown, pas de texte autour).

Format:
{{
  "restaurant_name": "string",
  "currency": "EUR|null",
  "sections": [
    {{
      "title": "string",
      "items": [
        {{
          "name": "string",
          "marketing_name": "string|null",
          "description": "string|null",
          "price": 12.5|null,
          "tags": ["beef","fish","spicy","creamy","vegetarian","dessert","grilled"]
        }}
      ]
    }}
  ],
  "wines": [
    {{
      "name": "string",
      "type": "red|white|rose|sparkling|dessert|other|null",
      "region": "string|null",
      "grape": "string|null",
      "price": 9.0|null
    }}
  ],
  "translations": {{
    "fr": {{"sections": [...], "wines": [...]}},
    "en": {{"sections": [...], "wines": [...]}},
    ...
  }}
}}

Règles:
- N'invente pas plats/vins/prix.
- Ajoute "marketing_name" si le nom est banal/peu vendeur (sans mentir).
- Ajoute des tags simples.
- Traductions pour: {langs} (titres, noms, descriptions, vins). Prix inchangés.
- Si une info manque: null.
- JSON strict: guillemets doubles, pas de trailing commas.
""".strip()


def extract_menu_from_pdf(pdf_path: str, languages: list[str]) -> dict:
    client = _client()
    prompt = _prompt(languages)

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=[
            {"role": "user", "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "application/pdf", "data": pdf_bytes}},
            ]}
        ],
        config={"response_mime_type": "application/json"},
    )

    return _extract_json(getattr(response, "text", "") or "")


def extract_menu_from_images(image_paths: list[str], languages: list[str]) -> dict:
    client = _client()
    prompt = _prompt(languages)

    parts = [{"text": prompt}]
    for p in image_paths:
        with open(p, "rb") as f:
            parts.append({"inline_data": {"mime_type": "image/png", "data": f.read()}})

    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=[{"role": "user", "parts": parts}],
        config={"response_mime_type": "application/json"},
    )

    return _extract_json(getattr(response, "text", "") or "")
