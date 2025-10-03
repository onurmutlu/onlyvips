"""
Kimlik Doğrulama Modülü
JWT tabanlı kimlik doğrulama ve yetkilendirme işlemleri
"""

import jwt
from jwt.exceptions import PyJWTError
from datetime import datetime, timedelta
from typing import Dict, Optional, Union, Any, List
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.database import db
from app.utils.logger import app_logger

# OAuth2 tanımlamaları
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Token şeması
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_at: int  # Unix timestamp

# Token veri modeli
class TokenData(BaseModel):
    sub: str  # Kullanıcı ID'si
    exp: int  # Bitiş zamanı
    role: Optional[str] = None
    permissions: List[str] = []
    telegram_id: Optional[str] = None

# Kullanıcı modeli
class User(BaseModel):
    id: str
    username: str
    role: str = "user"
    is_active: bool = True
    telegram_id: Optional[str] = None
    permissions: List[str] = Field(default_factory=list)

# Rol bazlı yetkiler
ROLE_PERMISSIONS = {
    "admin": [
        "tasks:read", "tasks:write", "tasks:verify", "tasks:reset",
        "users:read", "users:write", "badges:assign", "metrics:read",
        "settings:read", "settings:write"
    ],
    "showcu": [
        "tasks:read", "users:read", "badges:assign", "content:read", "content:write",
        "metrics:read"
    ],
    "moderator": [
        "tasks:read", "tasks:verify", "users:read", "content:read", "content:moderate"
    ],
    "user": [
        "tasks:read", "user:read"
    ]
}

# JWT token oluşturma
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Kullanıcı verileriyle JWT token oluşturur
    """
    to_encode = data.copy()
    
    # Varsayılan son kullanma tarihi ayarlanmamışsa
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Son kullanma zamanı
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    
    # JWT token oluştur
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    
    return encoded_jwt

# Token doğrulama ve kullanıcı bulma
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    JWT token'dan mevcut kullanıcı bilgisini çıkarır
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kimlik doğrulama bilgileri geçersiz",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Token'ı çözümle
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        
        # Token verisini çıkar
        user_id: str = payload.get("sub")
        exp: int = payload.get("exp")
        role: str = payload.get("role", "user")
        
        if user_id is None:
            raise credentials_exception
        
        # Süresi dolmuş mu kontrol et
        if datetime.utcnow() > datetime.fromtimestamp(exp):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token süresi dolmuş",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        token_data = TokenData(
            sub=user_id,
            exp=exp,
            role=role,
            permissions=payload.get("permissions", []),
            telegram_id=payload.get("telegram_id")
        )
        
    except PyJWTError:
        raise credentials_exception
    
    # Veritabanından kullanıcıyı al
    user_data = await db.get_user(token_data.sub)
    
    if user_data is None:
        raise credentials_exception
    
    # Kullanıcı aktif değilse
    if not user_data.get("is_active", True):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Hesap devre dışı bırakılmış")
    
    # User modeline dönüştür
    user = User(
        id=str(user_data.get("id", token_data.sub)),
        username=user_data.get("username", token_data.sub),
        role=user_data.get("role", token_data.role),
        is_active=user_data.get("is_active", True),
        telegram_id=user_data.get("telegram_id", token_data.telegram_id),
        permissions=user_data.get("permissions", [])
    )
    
    return user

# Token veya API key ile doğrulama
async def get_current_user_from_any(
    token: Optional[str] = Depends(oauth2_scheme),
    api_key: Optional[str] = Depends(api_key_header)
) -> User:
    """
    JWT token veya API key ile kullanıcıyı doğrular
    """
    if token:
        return await get_current_user(token)
    
    # Token yoksa, API key var mı kontrol et
    if api_key:
        try:
            # API key kontrolü (örnek bir implementasyon)
            if api_key == settings.FLIRT_BOT_API_KEY:
                # Flirt-Bot sistem kullanıcısı
                return User(
                    id="system_flirt_bot",
                    username="flirt_bot_system",
                    role="system",
                    permissions=["tasks:read", "tasks:write", "tasks:verify"]
                )
            elif api_key == settings.SHOWCU_PANEL_API_KEY:
                # Showcu Panel sistem kullanıcısı
                return User(
                    id="system_showcu_panel",
                    username="showcu_panel_system",
                    role="system",
                    permissions=["tasks:read", "tasks:write", "users:read", "badges:assign"]
                )
                
            # Diğer özel API keyler buraya eklenebilir
            
        except Exception as e:
            app_logger.error(f"API key doğrulama hatası: {str(e)}")
    
    # Hiçbir yetkilendirme yoksa
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Yetkilendirme gerekli",
        headers={"WWW-Authenticate": "Bearer"},
    )

# Aktif kullanıcı kontrolü
async def get_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Kullanıcının aktif olduğunu kontrol eder
    """
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Hesap devre dışı bırakılmış")
    return current_user

# Yetki kontrolü - rol bazlı
def get_user_with_role(required_role: str):
    """
    Kullanıcının belirtilen role sahip olup olmadığını kontrol eden bağımlılık
    """
    async def role_checker(current_user: User = Depends(get_active_user)) -> User:
        if current_user.role == "admin":
            # Admin her şeye erişebilir
            return current_user
            
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Bu işlem için {required_role} rolü gerekli"
            )
        return current_user
    return role_checker

# Yetki kontrolü - izin bazlı
def get_user_with_permission(required_permission: str):
    """
    Kullanıcının belirtilen izne sahip olup olmadığını kontrol eden bağımlılık
    """
    async def permission_checker(current_user: User = Depends(get_active_user)) -> User:
        # Kullanıcının rolüne göre izinleri
        role_perms = ROLE_PERMISSIONS.get(current_user.role, [])
        
        # Kullanıcının özel izinleri
        user_perms = current_user.permissions
        
        # Tüm izinler
        all_permissions = set(role_perms + user_perms)
        
        if required_permission not in all_permissions and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Bu işlem için '{required_permission}' izni gerekli"
            )
        return current_user
    return permission_checker

# Telegram kimlik doğrulama
async def verify_telegram_auth(auth_data: Dict[str, Any]) -> Optional[str]:
    """
    Telegram kimlik doğrulama verisini doğrula ve kullanıcı ID'si döndür
    """
    try:
        # Telegram'dan gelen hash değerini doğrula
        # (Burada gerçek implementasyon için Telegram doğrulama kodu olmalı)
        telegram_id = auth_data.get("id")
        auth_date = auth_data.get("auth_date")
        
        if not telegram_id or not auth_date:
            return None
        
        # Burada gerçek bir Telegram doğrulaması yapılmalıdır
        # Örnek: https://core.telegram.org/widgets/login#checking-authorization
        
        # Basitleştirilmiş örnek
        current_time = int(datetime.now().timestamp())
        auth_time = int(auth_date)
        
        # 24 saatten eski ise reddet
        if current_time - auth_time > 86400:
            return None
            
        # Kullanıcı veritabanında mevcut mu?
        user = await db.get_user_by_telegram_id(telegram_id)
        
        if not user:
            # Yeni kullanıcı oluştur
            username = f"telegram_{telegram_id}"
            new_user = {
                "username": username,
                "telegram_id": telegram_id,
                "auth_date": auth_time,
                "role": "user",
                "is_active": True,
                "created_at": datetime.now()
            }
            
            # Kaynağa ekstra bilgiler ekle
            if "first_name" in auth_data:
                new_user["first_name"] = auth_data["first_name"]
            if "last_name" in auth_data:
                new_user["last_name"] = auth_data["last_name"]
            if "username" in auth_data and auth_data["username"]:
                new_user["telegram_username"] = auth_data["username"]
            if "photo_url" in auth_data:
                new_user["avatar_url"] = auth_data["photo_url"]
                
            # Kullanıcıyı kaydet
            await db.save_user(username, new_user)
            return username
        
        # Mevcut kullanıcının kimliğini döndür
        return user.get("username")
    
    except Exception as e:
        app_logger.error(f"Telegram kimlik doğrulama hatası: {str(e)}")
        return None

# API key doğrulama (sistem servisler için)
async def validate_api_key(api_key: str = Security(api_key_header)) -> bool:
    """
    API key'i doğrula
    """
    if not api_key:
        return False
    
    # API key kontrolü
    valid_keys = [
        settings.FLIRT_BOT_API_KEY,
        settings.SHOWCU_PANEL_API_KEY,
        settings.MINIAPP_API_KEY
    ]
    
    return api_key in valid_keys 