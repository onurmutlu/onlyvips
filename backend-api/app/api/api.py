"""
API Rotaları
Tüm API endpoint'lerinin kaydedildiği ana modül
"""

from fastapi import APIRouter

from app.api.endpoints import auth, tasks, users, badges, health, content, showcus, payments, admin

# Ana API router
api_router = APIRouter()

# Auth endpoint'leri
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"]
)

# Görev endpoint'leri
api_router.include_router(
    tasks.router,
    prefix="/tasks",
    tags=["tasks"]
)

# Kullanıcı endpoint'leri
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)

# Rozet endpoint'leri
api_router.include_router(
    badges.router,
    prefix="/badges",
    tags=["badges"]
)

# İçerik endpoint'leri
api_router.include_router(
    content.router,
    prefix="/content",
    tags=["content"]
)

# Showcus (İçerik Üretici) endpoint'leri
api_router.include_router(
    showcus.router,
    prefix="/showcus",
    tags=["showcus"]
)

# Ödeme endpoint'leri
api_router.include_router(
    payments.router,
    prefix="/payments",
    tags=["payments"]
)

# Admin endpoint'leri
api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"]
)

# Health endpoint'leri
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["health"]
) 