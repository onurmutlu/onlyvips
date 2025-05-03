import os
import secrets
from functools import lru_cache
from typing import Any, Dict, List, Optional

from pydantic_settings import BaseSettings

from app.core.secrets_provider import get_secret_provider, SecretBackendType

class Settings(BaseSettings):
    """Uygulama yapılandırma ayarları"""
    
    # Secrets backend yapılandırması
    SECRET_PROVIDER: str = os.getenv("SECRET_PROVIDER", SecretBackendType.ENV)
    
    # API temel ayarları
    API_V1_STR: str = "/api"
    SECRET_KEY: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 gün
    ENV: str = os.getenv("NODE_ENV", "development")
    
    # Telgram ayarları
    TELEGRAM_API_ID: str = ""
    TELEGRAM_API_HASH: str = ""
    TELEGRAM_BOT_TOKEN: str = ""
    
    # Veritabanı ayarları
    DATABASE_URL: str = ""
    
    # Dosya yükleme ayarları
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100 MB
    UPLOAD_DIRECTORY: str = ""
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
    TON_API_KEY: str = ""
    TON_WALLET_ADDRESS: str = ""
    
    # OpenAI API ayarları
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = ""
    
    # Admin panel yapılandırması
    ADMIN_EMAIL: str = ""
    ADMIN_PASSWORD: str = ""
    
    # Log ayarları
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        
        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            # Secret provider'ı kullanarak değerleri doldurma mekanizması ekleniyor
            def secrets_backend_settings(settings_cls) -> Dict[str, Any]:
                provider = get_secret_provider(os.getenv("SECRET_PROVIDER"))
                secrets_dict = {}
                for field in settings_cls.__fields__.values():
                    field_value = provider.get_secret(field.name)
                    if field_value is not None:
                        secrets_dict[field.name] = field_value
                return secrets_dict
                
            # Normal Pydantic sources'den önce kendi özel kaynağımızı ekle
            return (
                init_settings,
                secrets_backend_settings,  # Bizim eklediğimiz kaynak
                env_settings,
                file_secret_settings,
            )

@lru_cache()
def get_settings() -> Settings:
    """Singleton Settings nesnesi döndürür"""
    settings = Settings()
    
    # Boş olan değerleri varsayılanlarla doldur
    if not settings.SECRET_KEY:
        settings.SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    
    if not settings.DATABASE_URL:
        settings.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./onlyvips.db")
    
    if not settings.UPLOAD_DIRECTORY:
        settings.UPLOAD_DIRECTORY = os.getenv("UPLOAD_DIR", "./uploads")
        
    if not settings.OPENAI_MODEL:
        settings.OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo-instruct")
        
    if not settings.ADMIN_EMAIL:
        settings.ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@onlyvips.com")
        
    if not settings.ADMIN_PASSWORD:
        settings.ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme")
    
    return settings

settings = get_settings() 