import json
from google import genai
from .settings import settings


def chat_about_menu(menu_payload: dict, lang: str, messages: list[dict]) -> str:
    client = genai.Client(api_key=settings.google_api_key)

    system = f"""
Tu es un serveur/maître d'hôtel d'un restaurant. Tu réponds en langue: {lang}.

Règles strictes:
- Tu ne proposes QUE des plats et vins présents dans le JSON fourni.
- Si le client demande un plat qui n'existe pas, propose 2 alternatives proches.
- Réponses courtes, chaleureuses, concrètes.
- Si on te demande "que recommandes-tu", demande d'abord 1 question: préférence (viande/poisson/végé) + budget.
""".strip()

    context = {
        "menu": {
            "restaurant_name": menu_payload.get("restaurant_name"),
            "currency": menu_payload.get("currency"),
            "sections": menu_payload.get("sections", []),
            "wines": menu_payload.get("wines", []),
            "pairings": menu_payload.get("pairings", []),
        }
    }

    # On convertit l'historique minimal en texte
    history = []
    for m in messages[-8:]:
        role = m.get("role")
        content = m.get("content", "")
        if role in ("user", "assistant"):
            history.append({"role": role, "parts": [{"text": content}]})

    resp = client.models.generate_content(
        model=settings.gemini_model,
        contents=[
            {"role": "user", "parts": [{"text": system}]},
            {"role": "user", "parts": [{"text": "Voici le menu JSON (source de vérité):"}]},
            {"role": "user", "parts": [{"text": json.dumps(context, ensure_ascii=False)}]},
            *history,
        ],
    )

    return getattr(resp, "text", "") or ""
