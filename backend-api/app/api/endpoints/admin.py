"""
Admin Management Endpoints
Sistem yönetimi ve moderasyon
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status, Query, Depends
from pydantic import BaseModel
import time
from datetime import datetime, timedelta

from app.utils.logger import app_logger
from app.utils.cache import UserCache, ContentCache, cached

router = APIRouter()

# Pydantic Models
class AdminStats(BaseModel):
    total_users: int
    total_showcus: int
    total_contents: int
    total_transactions: int
    total_revenue: float
    active_users_today: int
    new_users_today: int
    pending_verifications: int
    reported_contents: int

class UserManagement(BaseModel):
    id: str
    username: str
    email: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: str
    last_login: Optional[str] = None
    total_spent: float
    total_earned: float

class ContentModeration(BaseModel):
    id: str
    title: str
    creator_id: str
    creator_username: str
    type: str
    status: str  # approved, pending, rejected
    reports_count: int
    created_at: str
    reviewed_at: Optional[str] = None
    reviewer_id: Optional[str] = None

class SystemSettings(BaseModel):
    maintenance_mode: bool
    registration_enabled: bool
    content_upload_enabled: bool
    payment_processing_enabled: bool
    max_file_size_mb: int
    supported_file_types: List[str]
    commission_rate: float
    min_payout_amount: float

class ModerationAction(BaseModel):
    action: str  # approve, reject, ban_user, delete_content
    reason: Optional[str] = None
    duration_days: Optional[int] = None

# Helper functions
async def get_current_user(request):
    """JWT middleware'den kullanıcı bilgilerini al"""
    if hasattr(request.state, 'current_user'):
        return request.state.current_user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required"
    )

def is_admin_user(user_data: dict) -> bool:
    """Kullanıcının admin olup olmadığını kontrol et"""
    return user_data.get("role") == "admin"

def require_admin(user_data: dict):
    """Admin yetkisi gerekli"""
    if not is_admin_user(user_data):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

# Endpoints
@router.get("/stats", response_model=AdminStats)
@cached(ttl=300, key_prefix="admin_stats")
async def get_admin_stats(request = None):
    """
    Admin dashboard istatistikleri
    """
    try:
        # Kullanıcı doğrulama ve yetki kontrolü
        current_user = await get_current_user(request)
        require_admin(current_user)
        
        # Mock istatistikler
        stats = AdminStats(
            total_users=15420,
            total_showcus=1250,
            total_contents=8930,
            total_transactions=45670,
            total_revenue=125430.75,
            active_users_today=890,
            new_users_today=45,
            pending_verifications=23,
            reported_contents=12
        )
        
        app_logger.info(f"Admin stats requested by {current_user.get('user_id')}")
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Get admin stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch admin stats"
        )

@router.get("/users")
async def get_users_list(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    role: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    request = None
):
    """
    Kullanıcı listesini getir (admin)
    """
    try:
        # Kullanıcı doğrulama ve yetki kontrolü
        current_user = await get_current_user(request)
        require_admin(current_user)
        
        # Mock kullanıcı listesi
        mock_users = []
        for i in range(per_page):
            user_id = f"user_{i + ((page - 1) * per_page)}"
            mock_users.append(UserManagement(
                id=user_id,
                username=f"user{i + 1}",
                email=f"user{i + 1}@example.com",
                role=["user", "showcu", "admin"][i % 3],
                is_active=i % 10 != 0,  # %90 aktif
                is_verified=i % 5 != 0,  # %80 doğrulanmış
                created_at="2024-01-01T00:00:00Z",
                last_login="2024-03-15T10:30:00Z" if i % 3 == 0 else None,
                total_spent=100.0 + i * 10.0,
                total_earned=50.0 + i * 5.0 if i % 3 == 1 else 0.0
            ))
        
        return {
            "users": mock_users,
            "total": 15420,
            "page": page,
            "per_page": per_page,
            "has_next": page * per_page < 15420
        }
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Get users list error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch users list"
        )

@router.get("/content/moderation")
async def get_content_moderation_queue(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query("pending"),
    request = None
):
    """
    İçerik moderasyon kuyruğunu getir
    """
    try:
        # Kullanıcı doğrulama ve yetki kontrolü
        current_user = await get_current_user(request)
        require_admin(current_user)
        
        # Mock moderasyon kuyruğu
        mock_contents = []
        for i in range(per_page):
            content_id = f"content_{i + ((page - 1) * per_page)}"
            mock_contents.append(ContentModeration(
                id=content_id,
                title=f"Content {i + 1} - Needs Review",
                creator_id=f"creator_{i}",
                creator_username=f"creator{i + 1}",
                type=["image", "video", "audio"][i % 3],
                status=status or "pending",
                reports_count=i % 5,
                created_at="2024-03-15T10:00:00Z",
                reviewed_at=None,
                reviewer_id=None
            ))
        
        return {
            "contents": mock_contents,
            "total": 150,
            "page": page,
            "per_page": per_page,
            "has_next": page * per_page < 150
        }
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Get content moderation queue error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch content moderation queue"
        )

@router.post("/content/{content_id}/moderate")
async def moderate_content(
    content_id: str,
    action: ModerationAction,
    request = None
):
    """
    İçeriği modere et
    """
    try:
        # Kullanıcı doğrulama ve yetki kontrolü
        current_user = await get_current_user(request)
        require_admin(current_user)
        
        admin_id = current_user.get("user_id")
        
        # Moderasyon işlemini uygula
        if action.action == "approve":
            # İçeriği onayla
            app_logger.info(f"Content approved: {content_id} by admin {admin_id}")
            result_message = "Content approved successfully"
            
        elif action.action == "reject":
            # İçeriği reddet
            app_logger.info(f"Content rejected: {content_id} by admin {admin_id}, reason: {action.reason}")
            result_message = f"Content rejected: {action.reason}"
            
        elif action.action == "delete_content":
            # İçeriği sil
            app_logger.info(f"Content deleted: {content_id} by admin {admin_id}")
            result_message = "Content deleted successfully"
            
        elif action.action == "ban_user":
            # Kullanıcıyı banla
            duration = action.duration_days or 30
            app_logger.info(f"User banned for content {content_id} by admin {admin_id}, duration: {duration} days")
            result_message = f"User banned for {duration} days"
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid moderation action"
            )
        
        # Cache'leri temizle
        await ContentCache.delete(f"content:{content_id}")
        
        return {
            "message": result_message,
            "content_id": content_id,
            "action": action.action,
            "moderator_id": admin_id,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Moderate content error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to moderate content"
        )

@router.post("/users/{user_id}/ban")
async def ban_user(
    user_id: str,
    duration_days: int = Query(30, ge=1, le=365),
    reason: str = Query(...),
    request = None
):
    """
    Kullanıcıyı banla
    """
    try:
        # Kullanıcı doğrulama ve yetki kontrolü
        current_user = await get_current_user(request)
        require_admin(current_user)
        
        admin_id = current_user.get("user_id")
        
        # Ban işlemini uygula (mock)
        ban_until = datetime.now() + timedelta(days=duration_days)
        
        app_logger.info(f"User banned: {user_id} by admin {admin_id}, duration: {duration_days} days, reason: {reason}")
        
        # Cache'i temizle
        await UserCache.invalidate_user(user_id)
        
        return {
            "message": "User banned successfully",
            "user_id": user_id,
            "duration_days": duration_days,
            "reason": reason,
            "ban_until": ban_until.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "banned_by": admin_id,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Ban user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to ban user"
        )

@router.post("/users/{user_id}/unban")
async def unban_user(user_id: str, request = None):
    """
    Kullanıcının banını kaldır
    """
    try:
        # Kullanıcı doğrulama ve yetki kontrolü
        current_user = await get_current_user(request)
        require_admin(current_user)
        
        admin_id = current_user.get("user_id")
        
        app_logger.info(f"User unbanned: {user_id} by admin {admin_id}")
        
        # Cache'i temizle
        await UserCache.invalidate_user(user_id)
        
        return {
            "message": "User unbanned successfully",
            "user_id": user_id,
            "unbanned_by": admin_id,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Unban user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unban user"
        )

@router.get("/settings", response_model=SystemSettings)
async def get_system_settings(request = None):
    """
    Sistem ayarlarını getir
    """
    try:
        # Kullanıcı doğrulama ve yetki kontrolü
        current_user = await get_current_user(request)
        require_admin(current_user)
        
        # Mock sistem ayarları
        settings = SystemSettings(
            maintenance_mode=False,
            registration_enabled=True,
            content_upload_enabled=True,
            payment_processing_enabled=True,
            max_file_size_mb=50,
            supported_file_types=[".jpg", ".jpeg", ".png", ".gif", ".mp4", ".mov", ".mp3", ".wav"],
            commission_rate=0.15,  # %15
            min_payout_amount=50.0
        )
        
        return settings
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Get system settings error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch system settings"
        )

@router.put("/settings")
async def update_system_settings(
    settings: SystemSettings,
    request = None
):
    """
    Sistem ayarlarını güncelle
    """
    try:
        # Kullanıcı doğrulama ve yetki kontrolü
        current_user = await get_current_user(request)
        require_admin(current_user)
        
        admin_id = current_user.get("user_id")
        
        # Ayarları güncelle (mock)
        app_logger.info(f"System settings updated by admin {admin_id}")
        
        return {
            "message": "System settings updated successfully",
            "updated_by": admin_id,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "settings": settings.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Update system settings error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update system settings"
        )

@router.get("/reports")
async def get_reports(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query("pending"),
    request = None
):
    """
    Şikayet raporlarını getir
    """
    try:
        # Kullanıcı doğrulama ve yetki kontrolü
        current_user = await get_current_user(request)
        require_admin(current_user)
        
        # Mock raporlar
        mock_reports = []
        for i in range(per_page):
            report_id = f"report_{i + ((page - 1) * per_page)}"
            mock_reports.append({
                "id": report_id,
                "type": ["content", "user", "comment"][i % 3],
                "target_id": f"target_{i}",
                "reporter_id": f"user_{i}",
                "reason": ["spam", "inappropriate", "copyright", "harassment"][i % 4],
                "description": f"Report description {i + 1}",
                "status": status or "pending",
                "created_at": "2024-03-15T10:00:00Z",
                "reviewed_at": None,
                "reviewer_id": None
            })
        
        return {
            "reports": mock_reports,
            "total": 75,
            "page": page,
            "per_page": per_page,
            "has_next": page * per_page < 75
        }
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Get reports error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch reports"
        )

@router.get("/analytics/revenue")
async def get_revenue_analytics(
    period: str = Query("month", regex="^(day|week|month|year)$"),
    request = None
):
    """
    Gelir analitiği
    """
    try:
        # Kullanıcı doğrulama ve yetki kontrolü
        current_user = await get_current_user(request)
        require_admin(current_user)
        
        # Mock gelir analitiği
        analytics = {
            "period": period,
            "total_revenue": 125430.75,
            "commission_earned": 18814.61,  # %15 komisyon
            "payout_amount": 106616.14,
            "transaction_count": 45670,
            "avg_transaction_value": 2.75,
            "revenue_by_category": {
                "content_sales": 85230.50,
                "subscriptions": 32150.25,
                "tips": 8050.00
            },
            "daily_revenue": [
                {"date": "2024-03-01", "revenue": 1250.30},
                {"date": "2024-03-02", "revenue": 1380.45},
                {"date": "2024-03-03", "revenue": 1120.80}
            ]
        }
        
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Get revenue analytics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch revenue analytics"
        ) 