"""
Rozet Yönetimi Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body
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
async def list_badges():
    """
    Tüm rozetleri listele (herkes erişebilir)
    """
    try:
        badges = await db.get_all_badges()
        return {"badges": badges}
    except Exception as e:
        app_logger.error(f"Rozetler listelenirken hata: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Rozetler listelenirken hata oluştu"
        )

@router.post("/create")
async def create_badge(
    badge_data: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_user_with_permission("badges:write"))
):
    """
    Yeni rozet oluştur (admin ve moderatörler için)
    """
    # Zorunlu alanları kontrol et
    required_fields = ["id", "name", "description"]
    for field in required_fields:
        if field not in badge_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"'{field}' alanı gerekli"
            )
    
    # Rozet ID'si benzersiz mi kontrol et
    existing_badge = await db.get_badge(badge_data["id"])
    
    if existing_badge:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"'{badge_data['id']}' ID'li rozet zaten mevcut"
        )
    
    # Rozeti oluştur
    success = await db.save_badge(badge_data["id"], badge_data)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Rozet oluşturulamadı"
        )
    
    # Log kaydı
    app_logger.info(f"Yeni rozet oluşturuldu: {badge_data['id']}, oluşturan: {current_user.username}")
    
    return {"message": "Rozet başarıyla oluşturuldu", "badge": badge_data}

@router.put("/{badge_id}")
async def update_badge(
    badge_id: str,
    badge_data: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_user_with_permission("badges:write"))
):
    """
    Rozet bilgilerini güncelle (admin ve moderatörler için)
    """
    # Rozet var mı kontrol et
    existing_badge = await db.get_badge(badge_id)
    
    if not existing_badge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"'{badge_id}' ID'li rozet bulunamadı"
        )
    
    # ID değiştirilemez
    if "id" in badge_data and badge_data["id"] != badge_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rozet ID'si değiştirilemez"
        )
    
    # Rozeti güncelle
    success = await db.save_badge(badge_id, badge_data)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Rozet güncellenemedi"
        )
    
    # Log kaydı
    app_logger.info(f"Rozet güncellendi: {badge_id}, güncelleyen: {current_user.username}")
    
    # Güncellenmiş rozeti getir
    updated_badge = await db.get_badge(badge_id)
    
    return {"message": "Rozet başarıyla güncellendi", "badge": updated_badge}

@router.delete("/{badge_id}")
async def delete_badge(
    badge_id: str,
    current_user: User = Depends(get_user_with_permission("badges:write"))
):
    """
    Rozeti sil (admin için)
    """
    # Rozet var mı kontrol et
    existing_badge = await db.get_badge(badge_id)
    
    if not existing_badge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"'{badge_id}' ID'li rozet bulunamadı"
        )
    
    # Admin mi kontrol et
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Rozet silme yetkiniz yok"
        )
    
    # Rozeti sil
    success = await db.delete_badge(badge_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Rozet silinemedi"
        )
    
    # Log kaydı
    app_logger.warning(f"Rozet silindi: {badge_id}, silen: {current_user.username}")
    
    return {"message": "Rozet başarıyla silindi"}

@router.post("/assign")
async def assign_badge(
    assignment_data: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_user_with_permission("badges:assign"))
):
    """
    Kullanıcıya rozet ata (moderatör ve adminler için)
    """
    # Zorunlu alanları kontrol et
    if "user_id" not in assignment_data or "badge_id" not in assignment_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id ve badge_id alanları gerekli"
        )
    
    user_id = assignment_data["user_id"]
    badge_id = assignment_data["badge_id"]
    
    # Kullanıcı var mı kontrol et
    user = await db.get_user(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"'{user_id}' ID'li kullanıcı bulunamadı"
        )
    
    # Rozet var mı kontrol et
    badge = await db.get_badge(badge_id)
    
    if not badge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"'{badge_id}' ID'li rozet bulunamadı"
        )
    
    # Kullanıcıya rozet ekle
    success = await db.add_badge_to_user(user_id, badge_id)
    
    # Başarısız olursa
    if not success:
        # Muhtemelen rozet zaten var, hata döndürme
        return {"message": "Bu rozet zaten kullanıcıda var", "status": "info"}
    
    # Log kaydı
    app_logger.info(f"Rozet atandı: {badge_id}, kullanıcı: {user_id}, atayan: {current_user.username}")
    
    # Görev veya başarı logu
    await db.add_log({
        "action": "badge_awarded",
        "user_id": user_id,
        "badge_id": badge_id,
        "awarded_by": current_user.username
    })
    
    return {
        "message": f"'{badge['name']}' rozeti başarıyla {user_id} kullanıcısına atandı",
        "status": "success"
    } 