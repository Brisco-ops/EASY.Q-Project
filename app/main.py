import json
import os
import traceback
from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .settings import settings
from .db import Base, engine, get_db
from .files import ensure_dirs, save_upload_pdf
from .menu_service import create_menu, get_public_menu
from .qr_service import generate_qr_png
from .schemas import MenuCreateResponse, PublicMenuResponse
from .models import Menu
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel


ensure_dirs()
Base.metadata.create_all(bind=engine)



app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/storage", StaticFiles(directory=settings.storage_dir), name="storage")

@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "trace": traceback.format_exc()},
    )

@app.get("/health")
def health():
    return {"ok": True}


@app.get("/robots.txt", response_class=PlainTextResponse)
def robots():
    return f"User-agent: *\nAllow: /\nSitemap: {settings.base_url}/sitemap.xml\n"


@app.get("/sitemap.xml")
def sitemap(db: Session = Depends(get_db)):
    menus = db.query(Menu).order_by(Menu.created_at.desc()).all()
    urls = []
    for m in menus:
        lastmod = m.created_at.isoformat() if hasattr(m.created_at, "isoformat") else ""
        urls.append(
            f"""
  <url>
    <loc>{settings.base_url}/m/{m.public_slug}</loc>
    <lastmod>{lastmod}</lastmod>
  </url>"""
        )

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{''.join(urls)}
</urlset>"""
    return Response(content=xml.strip(), media_type="application/xml")


@app.post("/api/menus", response_model=MenuCreateResponse)
async def api_create_menu(
    restaurant_name: str = Form(...),
    languages: str = Form("fr"),
    pdf: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if pdf.content_type not in {"application/pdf", "application/octet-stream"}:
        raise HTTPException(status_code=400, detail="PDF requis")

    langs = [x.strip().lower() for x in languages.split(",") if x.strip()]
    if not langs:
        langs = ["fr"]

    pdf_path = await save_upload_pdf(pdf)
    menu = create_menu(db, restaurant_name, pdf_path, langs)

    public_url = f"{settings.base_url}/m/{menu.public_slug}?lang={langs[0]}"
    qr_filename = f"{menu.public_slug}.png"
    qr_path = generate_qr_png(public_url, qr_filename)
    qr_url = f"{settings.base_url}/storage/qrs/{os.path.basename(qr_path)}"

    return MenuCreateResponse(menu_id=menu.id, public_url=public_url, qr_url=qr_url)

class ChatRequest(BaseModel):
    lang: str = "fr"
    messages: list[dict]  # [{role:"user"/"assistant", content:"..."}]

@app.post("/api/public/menus/{slug}/chat")
def chat_menu(slug: str, body: ChatRequest, db: Session = Depends(get_db)):
    menu = get_public_menu(db, slug)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu introuvable")

    payload = json.loads(menu.menu_json)

    # IMPORTANT: utiliser la langue demandée si traduction dispo
    lang = (body.lang or "fr").lower()
    translations = payload.get("translations") or {}
    if lang in translations:
        payload = dict(payload)
        payload["sections"] = translations[lang].get("sections", payload.get("sections", []))
        payload["wines"] = translations[lang].get("wines", payload.get("wines", []))

    from .chat_service import chat_about_menu
    answer = chat_about_menu(payload, lang, body.messages or [])
    return {"answer": answer}

@app.get("/m/{slug}", response_class=HTMLResponse)
def public_menu_page(slug: str, lang: str = "fr"):
    safe_lang = (lang or "fr").lower()

    html = f"""
<!doctype html>
<html lang="{safe_lang}">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Menu</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f6f7fb;
      --card: #ffffff;
      --text: #111827;
      --muted: rgba(17,24,39,.65);
      --line: #e8e8ef;
      --shadow: 0 10px 28px rgba(0,0,0,.08);
      --radius: 16px;
    }}
    body {{
      margin: 0;
      font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
    }}
    .wrap {{
      max-width: 980px;
      margin: 0 auto;
      padding: 18px 14px 40px;
    }}
    .topbar {{
      display: flex;
      gap: 12px;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 12px;
    }}
    .brand {{
      display: grid;
      gap: 2px;
    }}
    h1 {{
      font-size: 22px;
      margin: 0;
      letter-spacing: -0.02em;
    }}
    .meta {{
      margin: 0;
      font-size: 13px;
      color: var(--muted);
    }}
    .controls {{
      display: flex;
      gap: 10px;
      align-items: center;
    }}
    select {{
      border: 1px solid var(--line);
      background: var(--card);
      border-radius: 12px;
      padding: 10px 12px;
      font-size: 14px;
    }}

    .card {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      padding: 14px;
    }}

    .section {{
      margin-top: 14px;
    }}
    .section-title {{
      font-size: 16px;
      margin: 0 0 10px;
      padding-top: 12px;
      border-top: 1px solid var(--line);
      letter-spacing: -0.01em;
    }}

    .item {{
      padding: 12px 0;
      border-bottom: 1px solid rgba(232,232,239,.8);
    }}
    .row {{
      display: flex;
      gap: 10px;
      align-items: baseline;
      justify-content: space-between;
    }}
    .name {{
      font-weight: 700;
      font-size: 15px;
      line-height: 1.25;
    }}
    .sub {{
      margin-top: 6px;
      font-size: 13px;
      color: var(--muted);
      line-height: 1.35;
    }}
    .pill {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;
      color: rgba(17,24,39,.75);
      background: rgba(17,24,39,.06);
      padding: 6px 10px;
      border-radius: 999px;
      margin-top: 8px;
    }}
    .price {{
      font-weight: 700;
      font-size: 14px;
      white-space: nowrap;
      margin-left: 10px;
    }}

    .grid {{
      display: grid;
      grid-template-columns: 1fr;
      gap: 12px;
    }}
    @media (min-width: 860px) {{
      .grid {{
        grid-template-columns: 1.6fr .9fr;
        align-items: start;
      }}
    }}

    .wines .item {{
      padding: 10px 0;
    }}

    .loading {{
      color: var(--muted);
      font-size: 14px;
      padding: 10px 0;
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="topbar">
      <div class="brand">
        <h1 id="title">Menu</h1>
        <p class="meta" id="meta">Chargement…</p>
      </div>
      <div class="controls">
        <select id="langSelect" aria-label="Langue"></select>
      </div>
    </div>

    <div class="grid">
      <div class="card" id="menuCard">
        <div class="loading" id="loading">Chargement du menu…</div>
      </div>

      <div class="card wines" id="winesCard" style="display:none">
        <h2 class="section-title" style="border-top:none;padding-top:0;margin-top:0">Vins</h2>
        <div id="winesList"></div>
      </div>
    </div>
  </div>

  <script>
    const SLUG = "{slug}";
    const LANG = "{safe_lang}";

    function setQueryLang(l) {{
      const url = new URL(window.location.href);
      url.searchParams.set("lang", l);
      window.location.href = url.toString();
    }}

    function money(v, currency) {{
      if (v == null) return "";
      if (typeof v === "number") {{
        try {{
          return new Intl.NumberFormat(undefined, {{ style: "currency", currency: currency || "EUR" }}).format(v);
        }} catch {{
          return String(v);
        }}
      }}
      return String(v);
    }}

    fetch("/api/public/menus/" + encodeURIComponent(SLUG) + "?lang=" + encodeURIComponent(LANG))
      .then(r => r.json())
      .then(data => {{
        document.getElementById("title").textContent = data.restaurant_name || "Menu";
        document.getElementById("meta").textContent =
          "Langue: " + (data.lang || "") + (data.currency ? " • Devise: " + data.currency : "");

        const sel = document.getElementById("langSelect");
        const langs = data.available_languages || [data.lang || "fr"];
        sel.innerHTML = "";
        langs.forEach(l => {{
          const opt = document.createElement("option");
          opt.value = l;
          opt.textContent = l.toUpperCase();
          if ((data.lang || "fr").toLowerCase() === l.toLowerCase()) opt.selected = true;
          sel.appendChild(opt);
        }});
        sel.addEventListener("change", (e) => setQueryLang(e.target.value));

        const pairings = data.pairings || [];
        const pairingMap = new Map();
        pairings.forEach(p => {{
          const key = String(p.section_index) + ":" + String(p.item_index);
          pairingMap.set(key, p);
        }});

        const menuCard = document.getElementById("menuCard");
        document.getElementById("loading").style.display = "none";

        const h = [];

        (data.sections || []).forEach((sec, sIdx) => {{
          h.push('<div class="section">');
          h.push('<h2 class="section-title">' + (sec.title || "") + '</h2>');

          (sec.items || []).forEach((it, iIdx) => {{
            const displayName = it.marketing_name ? it.marketing_name : it.name;
            const key = String(sIdx) + ":" + String(iIdx);
            const p = pairingMap.get(key);

            h.push('<div class="item">');
            h.push('<div class="row">');
            h.push('<div class="name">' + (displayName || "") + '</div>');
            h.push('<div class="price">' + money(it.price, data.currency) + '</div>');
            h.push('</div>');

            if (it.marketing_name) {{
              h.push('<div class="sub">Nom original: ' + (it.name || "") + '</div>');
            }}
            if (it.description) {{
              h.push('<div class="sub">' + it.description + '</div>');
            }}

            if (p && p.wine_name) {{
              const conf = (p.confidence != null) ? (" • " + p.confidence) : "";
              const reason = p.reason ? (" — " + p.reason) : "";
              h.push('<div class="pill">🍷 Accord: ' + p.wine_name + reason + conf + '</div>');
            }}

            h.push('</div>');
          }});

          h.push('</div>');
        }});

        menuCard.innerHTML = h.join("");

        const wines = data.wines || [];
        if (wines.length) {{
          document.getElementById("winesCard").style.display = "block";
          const wl = [];
          wines.forEach(w => {{
            wl.push('<div class="item">');
            wl.push('<div class="row">');
            wl.push('<div class="name">' + (w.name || "") + '</div>');
            wl.push('<div class="price">' + money(w.price, data.currency) + '</div>');
            wl.push('</div>');
            const info = [w.type, w.region, w.grape].filter(Boolean).join(" • ");
            if (info) wl.push('<div class="sub">' + info + '</div>');
            wl.push('</div>');
          }});
          document.getElementById("winesList").innerHTML = wl.join("");
        }}
      }})
      .catch(() => {{
        document.getElementById("loading").textContent = "Erreur de chargement du menu.";
      }});
  </script>
</body>
</html>
"""
    return HTMLResponse(content=html)



@app.get("/api/public/menus/{slug}", response_model=PublicMenuResponse)
def api_public_menu(slug: str, lang: str = "fr", db: Session = Depends(get_db)):
    menu = get_public_menu(db, slug)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu introuvable")

    payload = json.loads(menu.menu_json)
    restaurant_name = payload.get("restaurant_name") or menu.restaurant.name
    currency = payload.get("currency")
    translations = payload.get("translations") or {}
    available = sorted(set(["fr"] + list(translations.keys())))

    lang = (lang or "fr").lower()
    translations = payload.get("translations") or {}
    if lang in translations:
        sections = translations[lang].get("sections", payload.get("sections", []))
        wines = translations[lang].get("wines", payload.get("wines", []))
    else:
        sections = payload.get("sections", [])
        wines = payload.get("wines", [])

    return PublicMenuResponse(
      restaurant_name=restaurant_name,
      lang=lang,
      available_languages=available,
      currency=currency,
      sections=sections,
      wines=wines,
      pairings=payload.get("pairings", []),
  )
