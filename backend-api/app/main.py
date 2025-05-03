from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.core.config import settings
from app.api.endpoints import users, tasks, contents, showcus, payments, analytics, auth, webhooks, ai, metrics
from app.middleware.metrics_middleware import MetricsMiddleware
from app.core.database import create_tables
from app.utils.logger import app_logger

app = FastAPI(
    title="OnlyVips API",
    description="OnlyVips platformu için backend API",
    version="1.0.0",
)

# Metrik ve loglama middleware'i
app.add_middleware(MetricsMiddleware)

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router'ları ekle
app.include_router(auth.router, prefix="/api/auth", tags=["Kimlik Doğrulama"])
app.include_router(users.router, prefix="/api/users", tags=["Kullanıcılar"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Görevler"])
app.include_router(contents.router, prefix="/api/contents", tags=["İçerikler"])
app.include_router(showcus.router, prefix="/api/showcus", tags=["Şovcular"])
app.include_router(payments.router, prefix="/api/payments", tags=["Ödemeler"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analitik"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["Webhooks"])
app.include_router(ai.router, prefix="/api/ai", tags=["Yapay Zeka"])
app.include_router(metrics.router, prefix="/api", tags=["Metrikler"])

@app.on_event("startup")
async def startup():
    """Uygulama başladığında yapılacak işlemler"""
    # Veritabanı tablolarını oluştur
    create_tables()
    
    # Uygulama başlangıcını logla
    app_logger.info(
        "OnlyVips API başlatıldı",
        version="1.0.0",
        environment=settings.ENV,
    )
    
@app.on_event("shutdown")
async def shutdown():
    """Uygulama kapatıldığında yapılacak işlemler"""
    app_logger.info("OnlyVips API kapatıldı")

@app.get("/", tags=["Root"])
async def root():
    """API durumunu kontrol etmek için kök endpoint"""
    return {
        "status": "online",
        "service": "OnlyVips API",
        "version": "1.0.0"
    }

# OpenAPI şemasını özelleştir
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
        
    openapi_schema = get_openapi(
        title="OnlyVips API",
        version="1.0.0",
        description="OnlyVips platformu için backend API",
        routes=app.routes,
    )
    
    # Logo ve diğer marka öğeleri
    openapi_schema["info"]["x-logo"] = {
        "url": "https://onlyvips.com/logo.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi 