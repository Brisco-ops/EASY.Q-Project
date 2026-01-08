from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.db import engine, Base
from app.routers import menu, public
from app.services.file_service import ensure_dirs
from app.config import STORAGE_DIR

ensure_dirs()
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ServeurAI", description="Restaurant Menu AI Assistant", version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/storage", StaticFiles(directory=STORAGE_DIR), name="storage")

app.include_router(menu.router)
app.include_router(public.router)


@app.get("/")
async def root():
    return {"status": "ServeurAI API Running", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/menu/{slug}")
async def redirect_to_frontend(slug: str):
    """Redirect QR code scans to frontend"""
    return RedirectResponse(url=f"http://localhost:5173/menu/{slug}")
