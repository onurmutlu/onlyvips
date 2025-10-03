"""
Kullanıcı İşlemleri Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Dict, Any, Optional

from app.core.auth import (
    User,
    get_current_user,
    get_active_user,
    get_user_with_permission
)
from app.core.database import db
from app.utils.logger import app_logger

router = APIRouter()

@router.get("/list")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_user_with_permission("users:read"))
):
    """
    Kullanıcı listesini getir (yetkili kullanıcılar için)
    """
    try:
        users = await db.get_users(skip=skip, limit=limit)
        total = await db.count_users()
        
        return {
            "users": users,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        app_logger.error(f"Kullanıcı listesi alınırken hata: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Kullanıcı listesi alınamadı"
        )

@router.get("/{user_id}")
async def get_user_details(
    user_id: str,
    current_user: User = Depends(get_active_user)
):
    """
    Kullanıcı detaylarını getir
    """
    # Kendi profilini veya admin/moderator ise başkasının profilini görebilir
    if user_id != current_user.id and current_user.role not in ["admin", "moderator", "showcu"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Başka bir kullanıcının bilgilerini görüntüleme yetkiniz yok"
        )
    
    user_data = await db.get_user(user_id)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı bulunamadı"
        )
    
    # Hassas bilgileri çıkar
    if "password_hash" in user_data:
        del user_data["password_hash"]
    
    return user_data

@router.put("/{user_id}")
async def update_user(
    user_id: str,
    updates: Dict[str, Any],
    current_user: User = Depends(get_user_with_permission("users:write"))
):
    """
    Kullanıcı bilgilerini güncelle (admin yetkililer için)
    """
    # Güvenlik kontrolleri
    if "role" in updates and updates["role"] == "admin" and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin rolü atama yetkiniz yok"
        )
    
    if "is_active" in updates and not current_user.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hesap aktivasyon durumunu değiştirme yetkiniz yok"
        )
    
    # Kullanıcı var mı kontrol et
    user_data = await db.get_user(user_id)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı bulunamadı"
        )
    
    # Güncelleme zamanı
    updates["updated_at"] = None  # DB'de otomatik atanacak
    
    # Kullanıcıyı güncelle
    success = await db.update_user(user_id, updates)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Kullanıcı güncellenemedi"
        )
    
    # Güncellenmiş kullanıcıyı getir
    updated_user = await db.get_user(user_id)
    
    # Log kaydı
    app_logger.info(f"Kullanıcı güncellendi: {user_id}, güncelleyen: {current_user.username}")
    
    return updated_user

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_user_with_permission("users:delete"))
):
    """
    Kullanıcıyı sil (sadece admin için)
    """
    # Admin mi kontrol et
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Kullanıcı silme yetkiniz yok"
        )
    
    # Kullanıcı var mı kontrol et
    user_data = await db.get_user(user_id)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı bulunamadı"
        )
    
    # Kendini silmeye çalışıyor mu?
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kendi hesabınızı silemezsiniz"
        )
    
    # Kullanıcıyı sil
    success = await db.delete_user(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Kullanıcı silinemedi"
        )
    
    # Log kaydı
    app_logger.warning(f"Kullanıcı silindi: {user_id}, silen: {current_user.username}")
    
    return {"message": "Kullanıcı başarıyla silindi"} 