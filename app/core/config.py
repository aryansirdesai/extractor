from pathlib import Path
from dotenv import load_dotenv
import os

# Load .env from the project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

class Settings:
    """Application settings loaded from environment variables."""
    
    # Environment
    ENV: str = os.getenv("ENV", "local")
    
    # Gemini API Key
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    
    # Any future settings like DB, storage, etc.
    # DATABASE_URL: str = os.getenv("DATABASE_URL")

# Instantiate settings
settings = Settings()