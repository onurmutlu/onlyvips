"""
Yapılandırma Ayarları
"""

import os
from typing import List, Dict, Any, Optional, Union, ClassVar
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Uygulama ayarları sınıfı
    """
    # API ayarları
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "OnlyVips API"
    API_DEBUG: bool = True
    
    # Güvenlik
    SECRET_KEY: str = os.getenv("SECRET_KEY", "gizli-anahtar-burada-saklanir")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 gün
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "100"))
    
    # Input Validation
    INPUT_VALIDATION_ENABLED: bool = os.getenv("INPUT_VALIDATION_ENABLED", "true").lower() == "true"
    
    # JWT Security
    JWT_ROTATION_ENABLED: bool = os.getenv("JWT_ROTATION_ENABLED", "true").lower() == "true"
    
    # API Keys
    FLIRT_BOT_API_KEY: str = os.getenv("FLIRT_BOT_API_KEY", "flirtbot-secret-api-key-12345")
    SHOWCU_PANEL_API_KEY: str = os.getenv("SHOWCU_PANEL_API_KEY", "showcupanel-secret-api-key-67890")
    MINIAPP_API_KEY: str = os.getenv("MINIAPP_API_KEY", "miniapp-secret-api-key-abcde")
    
    # CORS ayarları
    CORS_ORIGINS: List[str] = ["*"]
    
    # Veritabanı
    DB_PROVIDER: str = os.getenv("DB_PROVIDER", "memory")  # memory, mongodb, postgresql
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "27017"))
    DB_USER: Optional[str] = os.getenv("DB_USER")
    DB_PASSWORD: Optional[str] = os.getenv("DB_PASSWORD")
    DB_NAME: str = os.getenv("DB_NAME", "onlyvips")
    DB_URL: Optional[str] = os.getenv("DB_URL")
    
    # Telgram Bot 
    BOT_TOKEN: Optional[str] = os.getenv("BOT_TOKEN")
    BOT_WEBHOOK_URL: Optional[str] = os.getenv("BOT_WEBHOOK_URL")
    
    # Redis (önbellek, kuyruk, rate limiting)
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    
    # Entegrasyon noktaları
    FLIRT_BOT_API_URL: str = os.getenv("FLIRT_BOT_API_URL", "http://localhost:8001/api")
    SHOWCU_PANEL_API_URL: str = os.getenv("SHOWCU_PANEL_API_URL", "http://localhost:8002/api")
    MINIAPP_API_URL: str = os.getenv("MINIAPP_API_URL", "http://localhost:8003/api")
    
    # Yapay Zeka
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_ORG_ID: Optional[str] = os.getenv("OPENAI_ORG_ID")
    
    # Loglama
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_JSON: bool = os.getenv("LOG_JSON", "false").lower() == "true"
    
    # Uygulama modu
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Görev sistemi
    TASK_CONFIG_PATH: str = os.getenv("TASK_CONFIG_PATH", "app/config/tasks.json")
    TASK_AUTO_VERIFY: bool = os.getenv("TASK_AUTO_VERIFY", "false").lower() == "true"
    
    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Ayarlar nesnesi
settings = Settings()

# Ortam değişkenleri doğrulama ve yapılandırma özeti
def setup_config() -> None:
    """
    Yapılandırmayı doğrula ve özetle
    """
    env_mode = {
        "development": "GELİŞTİRME MODU ⚙️",
        "production": "ÜRETİM MODU 🚀",
        "test": "TEST MODU 🧪"
    }.get(settings.ENVIRONMENT, "BİLİNMEYEN MOD ❓")
    
    db_mode = {
        "memory": "BELLEK MODU (veriler kalıcı değil) ⚠️",
        "mongodb": "MongoDB VERİTABANI 🗄️",
        "postgresql": "PostgreSQL VERİTABANI 🗄️"
    }.get(settings.DB_PROVIDER, "BİLİNMEYEN VERİTABANI ❓")
    
    config_summary = f"""
    ===============================================
    🌟 OnlyVips API v1.0 - {env_mode}
    ===============================================
    🔄 API Yolu: {settings.API_V1_STR}
    📊 Veritabanı: {db_mode}
    🔒 CORS Origin: {', '.join(settings.CORS_ORIGINS) if isinstance(settings.CORS_ORIGINS, list) else settings.CORS_ORIGINS}
    📝 Log Level: {settings.LOG_LEVEL}
    ===============================================
    """
    
    print(config_summary)
    
    # Eksiklik ve uyarı kontrolü
    if settings.DB_PROVIDER != "memory" and not settings.DB_URL and not (settings.DB_HOST and settings.DB_USER):
        print("⚠️ UYARI: Veritabanı bilgileri eksik (DB_URL veya DB_HOST+DB_USER gerekli)")
    
    if settings.ENVIRONMENT == "production" and settings.API_DEBUG:
        print("⚠️ UYARI: Üretim modunda debug modu açık bırakılmış!")
    
    if settings.CORS_ORIGINS == ["*"] and settings.ENVIRONMENT == "production":
        print("⚠️ UYARI: Üretim modunda tüm kaynaklar CORS için izin veriliyor!")
    
    if settings.SECRET_KEY == "gizli-anahtar-burada-saklanir":
        print("⚠️ UYARI: Varsayılan SECRET_KEY kullanılıyor. Güvenli bir anahtar belirleyin!")
    
    if settings.ENVIRONMENT == "production":
        if any([
            settings.FLIRT_BOT_API_KEY == "flirtbot-secret-api-key-12345",
            settings.SHOWCU_PANEL_API_KEY == "showcupanel-secret-api-key-67890",
            settings.MINIAPP_API_KEY == "miniapp-secret-api-key-abcde"
        ]):
            print("⚠️ UYARI: Üretim modunda varsayılan API anahtarları kullanılıyor!")

# Ortam değerlerini başlatma
if __name__ == "__main__":
    setup_config() 