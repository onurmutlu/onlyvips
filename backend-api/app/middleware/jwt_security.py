"""
JWT Security Middleware
JWT token rotation, blacklist ve güvenli doğrulama
"""

import time
import jwt
import hashlib
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import redis.asyncio as redis

from app.core.config import settings
from app.utils.logger import app_logger


class JWTSecurityMiddleware(BaseHTTPMiddleware):
    """
    JWT güvenlik middleware'i
    Token rotation, blacklist ve güvenli doğrulama
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.redis_client = None
        
        # JWT ayarları
        self.algorithm = "HS256"
        self.access_token_expire = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        self.refresh_token_expire = 7 * 24 * 60 * 60  # 7 gün
        
        # Korumasız endpoint'ler
        self.public_paths = [
            "/",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/metrics",
            "/api/auth/login",
            "/api/auth/register",
            "/api/auth/refresh",
            "/api/auth/telegram",
        ]
    
    async def get_redis_client(self):
        """Redis bağlantısını al"""
        if not self.redis_client:
            try:
                self.redis_client = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    password=settings.REDIS_PASSWORD,
                    decode_responses=True
                )
                await self.redis_client.ping()
            except Exception as e:
                app_logger.warning(f"Redis bağlantısı kurulamadı: {e}")
                return None
        return self.redis_client
    
    def get_current_secret(self) -> str:
        """Mevcut JWT secret'ını al (rotation için)"""
        # Secret rotation için timestamp bazlı secret
        current_hour = int(time.time()) // 3600
        base_secret = settings.SECRET_KEY
        return hashlib.sha256(f"{base_secret}_{current_hour}".encode()).hexdigest()
    
    def get_previous_secret(self) -> str:
        """Önceki JWT secret'ını al (geçiş dönemi için)"""
        previous_hour = (int(time.time()) // 3600) - 1
        base_secret = settings.SECRET_KEY
        return hashlib.sha256(f"{base_secret}_{previous_hour}".encode()).hexdigest()
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Access token oluştur"""
        to_encode = data.copy()
        expire = time.time() + self.access_token_expire
        to_encode.update({
            "exp": expire,
            "iat": time.time(),
            "type": "access"
        })
        
        return jwt.encode(to_encode, self.get_current_secret(), algorithm=self.algorithm)
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Refresh token oluştur"""
        to_encode = data.copy()
        expire = time.time() + self.refresh_token_expire
        to_encode.update({
            "exp": expire,
            "iat": time.time(),
            "type": "refresh"
        })
        
        return jwt.encode(to_encode, self.get_current_secret(), algorithm=self.algorithm)
    
    async def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Token'ı decode et"""
        try:
            # Önce mevcut secret ile dene
            payload = jwt.decode(token, self.get_current_secret(), algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token süresi dolmuş"
            )
        except jwt.InvalidTokenError:
            try:
                # Önceki secret ile dene (rotation geçiş dönemi)
                payload = jwt.decode(token, self.get_previous_secret(), algorithms=[self.algorithm])
                return payload
            except jwt.InvalidTokenError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Geçersiz token"
                )
    
    async def is_token_blacklisted(self, token: str) -> bool:
        """Token blacklist kontrolü"""
        redis_client = await self.get_redis_client()
        if not redis_client:
            return False
        
        try:
            # Token hash'ini oluştur
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            result = await redis_client.get(f"blacklist:{token_hash}")
            return result is not None
        except Exception as e:
            app_logger.error(f"Blacklist kontrolü hatası: {e}")
            return False
    
    async def blacklist_token(self, token: str, expire_time: int = None):
        """Token'ı blacklist'e ekle"""
        redis_client = await self.get_redis_client()
        if not redis_client:
            return
        
        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            ttl = expire_time or self.access_token_expire
            await redis_client.setex(f"blacklist:{token_hash}", ttl, "1")
        except Exception as e:
            app_logger.error(f"Token blacklist hatası: {e}")
    
    async def validate_telegram_hash(self, init_data: str) -> bool:
        """Telegram hash doğrulama"""
        if not settings.BOT_TOKEN:
            return False
        
        try:
            # Telegram init data parsing
            params = {}
            for item in init_data.split('&'):
                if '=' in item:
                    key, value = item.split('=', 1)
                    params[key] = value
            
            # Hash'i al ve kaldır
            received_hash = params.pop('hash', '')
            
            # Parametreleri sırala ve birleştir
            sorted_params = sorted(params.items())
            data_check_string = '\n'.join([f"{k}={v}" for k, v in sorted_params])
            
            # Secret key oluştur
            secret_key = hashlib.sha256(settings.BOT_TOKEN.encode()).digest()
            
            # HMAC hesapla
            import hmac
            calculated_hash = hmac.new(
                secret_key,
                data_check_string.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return calculated_hash == received_hash
            
        except Exception as e:
            app_logger.error(f"Telegram hash doğrulama hatası: {e}")
            return False
    
    def extract_token_from_header(self, request: Request) -> Optional[str]:
        """Header'dan token'ı çıkar"""
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None
        
        if not auth_header.startswith("Bearer "):
            return None
        
        return auth_header.split(" ")[1]
    
    async def get_current_user(self, token: str) -> Optional[Dict[str, Any]]:
        """Token'dan kullanıcı bilgilerini al"""
        try:
            payload = await self.decode_token(token)
            
            # Token tipi kontrolü
            if payload.get("type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Geçersiz token tipi"
                )
            
            # Blacklist kontrolü
            if await self.is_token_blacklisted(token):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token iptal edilmiş"
                )
            
            return payload
            
        except HTTPException:
            raise
        except Exception as e:
            app_logger.error(f"Token doğrulama hatası: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token doğrulama hatası"
            )
    
    def is_public_path(self, path: str) -> bool:
        """Path'in public olup olmadığını kontrol et"""
        return any(public_path in path for public_path in self.public_paths)
    
    async def dispatch(self, request: Request, call_next):
        """JWT güvenlik kontrolü"""
        
        # Public path kontrolü
        if self.is_public_path(request.url.path):
            return await call_next(request)
        
        # Token'ı al
        token = self.extract_token_from_header(request)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token gerekli",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Token doğrulama
        try:
            user_data = await self.get_current_user(token)
            
            # Request'e kullanıcı bilgilerini ekle
            request.state.current_user = user_data
            request.state.token = token
            
        except HTTPException:
            raise
        except Exception as e:
            app_logger.error(f"JWT middleware hatası: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Kimlik doğrulama hatası"
            )
        
        # İsteği işle
        response = await call_next(request)
        
        # Token rotation kontrolü (token'ın %75'i geçmişse yeni token oluştur)
        try:
            payload = await self.decode_token(token)
            issued_at = payload.get("iat", 0)
            expires_at = payload.get("exp", 0)
            current_time = time.time()
            
            token_age = current_time - issued_at
            token_lifetime = expires_at - issued_at
            
            if token_age > (token_lifetime * 0.75):
                # Yeni token oluştur
                new_token = self.create_access_token({
                    "sub": payload.get("sub"),
                    "user_id": payload.get("user_id"),
                    "username": payload.get("username")
                })
                
                # Response header'ına yeni token'ı ekle
                response.headers["X-New-Token"] = new_token
                
                app_logger.info(f"Token rotation yapıldı - User: {payload.get('user_id')}")
        
        except Exception as e:
            app_logger.error(f"Token rotation hatası: {e}")
        
        return response 