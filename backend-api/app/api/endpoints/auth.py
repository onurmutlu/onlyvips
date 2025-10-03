"""
Kimlik Doğrulama Endpoints
Kullanıcı giriş, oturum kontrolü ve Telegram doğrulama işlemleri
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pydantic import BaseModel, EmailStr, Field

from app.core.auth import (
    User,
    Token,
    create_access_token,
    get_current_user,
    get_active_user,
    verify_telegram_auth
)
from app.core.config import settings
from app.core.database import db
from app.utils.logger import app_logger
from app.utils.password import create_password_hash, verify_password_hash

router = APIRouter()

# Kullanıcı kayıt şeması
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    email: Optional[EmailStr] = None
    telegram_id: Optional[str] = None
    full_name: Optional[str] = None

@router.post("/register", response_model=Token)
async def register(user_data: UserRegister):
    """
    Yeni kullanıcı kaydı
    """
    # Kullanıcı adı mevcut mu?
    existing_user = await db.get_user(user_data.username)
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu kullanıcı adı zaten kullanılıyor"
        )
    
    # Telegram ID varsa kontrol et
    if user_data.telegram_id:
        existing_tg_user = await db.get_user_by_telegram_id(user_data.telegram_id)
        if existing_tg_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bu Telegram ID zaten başka bir hesapla ilişkilendirilmiş"
            )
    
    # Şifreyi hashle
    hashed_password = create_password_hash(user_data.password)
    
    # Yeni kullanıcı dokümanı
    new_user = {
        "username": user_data.username,
        "password_hash": hashed_password,
        "email": user_data.email,
        "role": "user",  # Varsayılan rol
        "is_active": True,
        "xp": 0,
        "badges": [],
        "completed_tasks": [],
        "created_at": datetime.now().isoformat()
    }
    
    if user_data.telegram_id:
        new_user["telegram_id"] = user_data.telegram_id
    
    if user_data.full_name:
        new_user["full_name"] = user_data.full_name
    
    # Kullanıcıyı kaydet
    success = await db.save_user(user_data.username, new_user)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Kullanıcı kayıt edilemedi"
        )
    
    # Token oluştur
    token_data = {
        "sub": user_data.username,
        "role": "user"
    }
    
    if user_data.telegram_id:
        token_data["telegram_id"] = user_data.telegram_id
    
    # Token oluştur
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data=token_data, expires_delta=access_token_expires
    )
    
    # Token süresinin bitiş zamanını hesapla
    expires_at = int((datetime.now() + access_token_expires).timestamp())
    
    # Kullanıcı kaydı logla
    app_logger.info(f"Yeni kullanıcı kaydedildi: {user_data.username}")
    
    # Token oluştur ve döndür
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_at=expires_at
    )

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Kullanıcı adı ve şifre ile giriş (Admin ve Sistem Kullanıcıları için)
    """
    # Veritabanından kullanıcı doğrulama
    user_data = await db.get_user(form_data.username)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanıcı adı veya şifre hatalı",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Şifre doğrulama
    if "password_hash" in user_data:
        if not verify_password_hash(form_data.password, user_data["password_hash"]):
            # Başarısız giriş logla
            app_logger.warning(f"Başarısız giriş denemesi: {form_data.username}")
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Kullanıcı adı veya şifre hatalı",
                headers={"WWW-Authenticate": "Bearer"},
            )
    else:
        # Şifre hash yoksa hata
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanıcı adı veya şifre hatalı",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Hesap aktif mi?
    if not user_data.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hesap devre dışı bırakılmış",
        )
    
    # Kullanıcı bilgilerini token data'ya ekle
    token_data = {
        "sub": user_data.get("username"),
        "role": user_data.get("role", "user")
    }
    
    # Telegram ID varsa ekle
    if "telegram_id" in user_data:
        token_data["telegram_id"] = user_data["telegram_id"]
    
    # Özel izinler varsa ekle
    if "permissions" in user_data:
        token_data["permissions"] = user_data["permissions"]
    
    # Token oluştur
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data=token_data, expires_delta=access_token_expires
    )
    
    # Son giriş tarihini güncelle
    await db.update_user(user_data["username"], {"last_login": datetime.now().isoformat()})
    
    # Başarılı giriş logla
    app_logger.info(f"Başarılı giriş: {form_data.username}, rol: {user_data.get('role', 'user')}")
    
    # Token süresinin bitiş zamanını hesapla
    expires_at = int((datetime.now() + access_token_expires).timestamp())
    
    # Token sonucunu döndür
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_at=expires_at
    )

@router.post("/telegram", response_model=Token)
async def telegram_auth(auth_data: Dict[str, Any] = Body(...)):
    """
    Telegram ile kimlik doğrulama
    """
    # Telegram doğrulama
    username = await verify_telegram_auth(auth_data)
    
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Telegram doğrulama başarısız",
        )
    
    # Kullanıcı bilgilerini al
    user_data = await db.get_user(username)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı bulunamadı",
        )
    
    # Token oluştur
    token_data = {
        "sub": username,
        "role": user_data.get("role", "user"),
        "telegram_id": auth_data.get("id")
    }
    
    # Özel izinler varsa ekle
    if "permissions" in user_data:
        token_data["permissions"] = user_data["permissions"]
    
    # Token oluştur
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data=token_data, expires_delta=access_token_expires
    )
    
    # Son giriş tarihini güncelle
    await db.update_user(username, {"last_login": datetime.now().isoformat()})
    
    # Token süresinin bitiş zamanını hesapla
    expires_at = int((datetime.now() + access_token_expires).timestamp())
    
    # Token sonucunu döndür
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_at=expires_at
    )

@router.get("/me", response_model=User)
async def get_me(current_user: User = Depends(get_active_user)):
    """
    Mevcut kullanıcı bilgilerini getir
    """
    return current_user

@router.post("/refresh", response_model=Token)
async def refresh_token(current_user: User = Depends(get_active_user)):
    """
    Token yenileme - mevcut token ile yeni bir token oluştur
    """
    # Token oluştur
    token_data = {
        "sub": current_user.username,
        "role": current_user.role
    }
    
    # Telegram ID varsa ekle
    if current_user.telegram_id:
        token_data["telegram_id"] = current_user.telegram_id
    
    # İzinleri ekle
    if current_user.permissions:
        token_data["permissions"] = current_user.permissions
    
    # Token oluştur
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data=token_data, expires_delta=access_token_expires
    )
    
    # Son yenileme tarihini güncelle
    await db.update_user(current_user.username, {"last_token_refresh": datetime.now().isoformat()})
    
    # Token süresinin bitiş zamanını hesapla
    expires_at = int((datetime.now() + access_token_expires).timestamp())
    
    # Token sonucunu döndür
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_at=expires_at
    )

@router.post("/logout")
async def logout(current_user: User = Depends(get_active_user)):
    """
    Oturumu kapat (token'ı karalistye alma)
    Not: JWT token'lar gerçekte sunucuda tutulmaz, bu nedenle tam logout için 
    client tarafında token'ın silinmesi ve kısa süreli token kullanılması önerilir
    """
    # Çıkış kaydı tutma
    await db.add_log({
        "action": "logout",
        "user_id": current_user.username,
        "role": current_user.role,
        "success": True
    })
    
    return {"message": "Başarıyla çıkış yapıldı"}

@router.get("/check-username/{username}")
async def check_username_availability(username: str):
    """
    Kullanıcı adının kullanılabilir olup olmadığını kontrol et
    """
    # Kullanıcı adı kontrolü
    user = await db.get_user(username)
    
    is_available = user is None
    
    return {
        "username": username,
        "available": is_available
    } 