"""
OnlyVips Backend API
FastAPI tabanlı backend servisi
"""

import time
import sys
import os
from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import asyncio

# Modül yolunu ayarla
current_file = Path(__file__).resolve()
project_root = current_file.parent
sys.path.insert(0, str(project_root))

from app.api.api import api_router
from app.core.config import settings, setup_config
from app.core.database import db, create_tables, close_connection
from app.core.sentry_config import init_sentry
from app.utils.logger import app_logger
from app.middleware.rate_limiting import RateLimitingMiddleware
from app.middleware.input_validation import InputValidationMiddleware
from app.middleware.jwt_security import JWTSecurityMiddleware
from app.middleware.metrics_middleware import MetricsMiddleware


# Uygulama başlatma
def create_application() -> FastAPI:
    """
    FastAPI uygulamasını oluştur ve yapılandır
    """
    setup_config()  # Yapılandırma kontrol
    init_sentry()  # Sentry error tracking
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="OnlyVips Backend API",
        version="1.0.0",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        debug=settings.API_DEBUG
    )
    
    # CORS ayarı
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Güvenlik middleware'leri (sıra önemli!)
    app.add_middleware(MetricsMiddleware)  # En son - metrics toplama
    app.add_middleware(RateLimitingMiddleware)  # Rate limiting
    app.add_middleware(InputValidationMiddleware)  # Input validation
    app.add_middleware(JWTSecurityMiddleware)  # JWT güvenlik
    
    # API rotaları
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    return app


# FastAPI uygulaması
app = create_application()


# Başlangıç ve kaplama events
@app.on_event("startup")
async def startup_event():
    """
    Uygulama başlangıcında çalıştırılacak işlemler
    """
    app_logger.info("🚀 OnlyVips Backend API başlatılıyor...")
    
    try:
        # Veritabanı tablolarını oluştur
        await create_tables()
        app_logger.info("✅ Veritabanı tabloları hazır")
    except Exception as e:
        app_logger.error(f"❌ Veritabanı tabloları hazırlanırken hata: {str(e)}")
    
    app_logger.info(f"📌 API Dokümantasyonu: {settings.API_V1_STR}/docs")
    app_logger.info("✅ Uygulama başarıyla başlatıldı!")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Uygulama kapanırken çalıştırılacak işlemler
    """
    app_logger.info("🔄 Uygulama kapatılıyor...")
    
    # Veritabanı bağlantısını kapat
    await close_connection()
    
    app_logger.info("👋 Uygulama başarıyla kapatıldı!")


# Özel 404 hata sayfası
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Özel HTTP hata işleyici
    """
    if exc.status_code == 404:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Bu endpoint bulunamadı. Lütfen API belgelerine bakın."}
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.detail)}
    )


# Genel hata işleyici
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Genel istisna işleyici
    """
    app_logger.error(f"Genel hata: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Sunucu hatası"}
    )


# Basit sağlık kontrolü
@app.get("/")
async def root():
    """
    API kök endpoint'i - basit sağlık kontrolü
    """
    return {
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
        "status": "active",
        "docs_url": f"{settings.API_V1_STR}/docs"
    }


@app.get(f"{settings.API_V1_STR}/health")
async def health_check():
    """
    Sağlık kontrolü endpoint'i
    """
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "db_status": "connected" if settings.DB_PROVIDER != "memory" else "memory_only",
        "environment": settings.ENVIRONMENT
    }


# Uygulama doğrudan çalıştırıldığında
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT != "production"
    )