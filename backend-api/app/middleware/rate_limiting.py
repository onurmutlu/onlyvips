"""
Rate Limiting Middleware
Redis tabanlı rate limiting ile API güvenliği
"""

import time
import json
from typing import Dict, Optional
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import redis.asyncio as redis

from app.core.config import settings
from app.utils.logger import app_logger


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """
    Redis tabanlı rate limiting middleware'i
    IP bazlı ve kullanıcı bazlı rate limiting uygular
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.redis_client = None
        self.rate_limits = {
            # IP bazlı limitler (dakika başına)
            "ip_default": {"requests": 100, "window": 60},
            "ip_auth": {"requests": 200, "window": 60},
            
            # Kullanıcı bazlı limitler (dakika başına)
            "user_default": {"requests": 500, "window": 60},
            "user_premium": {"requests": 1000, "window": 60},
            
            # Endpoint bazlı limitler
            "auth_endpoints": {"requests": 10, "window": 60},
            "upload_endpoints": {"requests": 20, "window": 60},
        }
    
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
    
    def get_client_ip(self, request: Request) -> str:
        """İstemci IP adresini al"""
        # Proxy arkasında çalışıyorsa
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def get_user_id(self, request: Request) -> Optional[str]:
        """JWT token'dan kullanıcı ID'sini al"""
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        try:
            # JWT decode işlemi burada yapılacak
            # Şimdilik basit bir implementasyon
            token = auth_header.split(" ")[1]
            # JWT decode logic here
            return None  # Placeholder
        except Exception:
            return None
    
    def get_rate_limit_key(self, request: Request, client_ip: str, user_id: Optional[str]) -> tuple:
        """Rate limit anahtarını ve limitini belirle"""
        path = request.url.path
        
        # Endpoint bazlı kontrol
        if any(endpoint in path for endpoint in ["/auth/", "/login", "/register"]):
            return f"rate_limit:auth:{client_ip}", self.rate_limits["auth_endpoints"]
        
        if any(endpoint in path for endpoint in ["/upload", "/media"]):
            return f"rate_limit:upload:{client_ip}", self.rate_limits["upload_endpoints"]
        
        # Kullanıcı bazlı kontrol
        if user_id:
            # Premium kullanıcı kontrolü burada yapılabilir
            return f"rate_limit:user:{user_id}", self.rate_limits["user_default"]
        
        # IP bazlı kontrol
        return f"rate_limit:ip:{client_ip}", self.rate_limits["ip_default"]
    
    async def check_rate_limit(self, key: str, limit_config: Dict) -> tuple:
        """Rate limit kontrolü yap"""
        redis_client = await self.get_redis_client()
        if not redis_client:
            # Redis yoksa rate limiting yapma
            return True, 0, 0
        
        try:
            current_time = int(time.time())
            window_start = current_time - limit_config["window"]
            
            # Sliding window log algoritması
            pipe = redis_client.pipeline()
            
            # Eski kayıtları temizle
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Mevcut istek sayısını al
            pipe.zcard(key)
            
            # Yeni isteği ekle
            pipe.zadd(key, {str(current_time): current_time})
            
            # TTL ayarla
            pipe.expire(key, limit_config["window"])
            
            results = await pipe.execute()
            current_requests = results[1]
            
            # Limit kontrolü
            if current_requests >= limit_config["requests"]:
                # Rate limit aşıldı
                remaining_time = limit_config["window"] - (current_time % limit_config["window"])
                return False, current_requests, remaining_time
            
            return True, current_requests, 0
            
        except Exception as e:
            app_logger.error(f"Rate limit kontrolü hatası: {e}")
            # Hata durumunda geçiş ver
            return True, 0, 0
    
    async def dispatch(self, request: Request, call_next):
        """Rate limiting kontrolü"""
        client_ip = self.get_client_ip(request)
        user_id = self.get_user_id(request)
        
        # Rate limit anahtarını al
        rate_limit_key, limit_config = self.get_rate_limit_key(request, client_ip, user_id)
        
        # Rate limit kontrolü
        allowed, current_requests, retry_after = await self.check_rate_limit(
            rate_limit_key, limit_config
        )
        
        if not allowed:
            app_logger.warning(
                f"Rate limit aşıldı - IP: {client_ip}, User: {user_id}, "
                f"Path: {request.url.path}, Requests: {current_requests}"
            )
            
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "message": "Çok fazla istek gönderdiniz. Lütfen bekleyin.",
                    "retry_after": retry_after,
                    "limit": limit_config["requests"],
                    "window": limit_config["window"]
                },
                headers={"Retry-After": str(retry_after)}
            )
        
        # İsteği işle
        response = await call_next(request)
        
        # Rate limit bilgilerini header'a ekle
        response.headers["X-RateLimit-Limit"] = str(limit_config["requests"])
        response.headers["X-RateLimit-Remaining"] = str(
            max(0, limit_config["requests"] - current_requests - 1)
        )
        response.headers["X-RateLimit-Reset"] = str(
            int(time.time()) + limit_config["window"]
        )
        
        return response 