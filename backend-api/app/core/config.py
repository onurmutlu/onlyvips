import os
import secrets
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Uygulama yapılandırma ayarları"""
    
    # API temel ayarları
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 gün
    
    # Telgram ayarları
    TELEGRAM_API_ID: str = os.getenv("API_ID", "")
    TELEGRAM_API_HASH: str = os.getenv("API_HASH", "")
    TELEGRAM_BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    
    # Veritabanı ayarları
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./onlyvips.db")
    
    # Dosya yükleme ayarları
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100 MB
    UPLOAD_DIRECTORY: str = os.getenv("UPLOAD_DIR", "./uploads")
    ALLOWED_FILE_TYPES: List[str] = ["image/jpeg", "image/png", "video/mp4", "application/pdf"]
    
    # CORS ayarları
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # Showcu Panel geliştirme ortamı
        "http://localhost:5173",  # Admin Panel geliştirme ortamı
        "https://onlyvips.com",   # Prodüksiyon ortamı
        "https://admin.onlyvips.com",
        "https://showcu.onlyvips.com",
    ]
    
    # TON blockchain ayarları
    TON_API_KEY: str = os.getenv("TON_API_KEY", "")
    TON_WALLET_ADDRESS: str = os.getenv("TON_WALLET_ADDRESS", "")
    
    # OpenAI API ayarları
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo-instruct")
    
    # Admin panel yapılandırması
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@onlyvips.com")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "changeme")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings() 