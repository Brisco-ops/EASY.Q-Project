import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./serveur_ai.db")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
STORAGE_DIR = os.getenv("STORAGE_DIR", "./storage")
