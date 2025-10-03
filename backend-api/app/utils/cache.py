"""
Redis Cache Layer
Performans optimizasyonu için cache işlemleri
"""

import json
import pickle
import hashlib
from typing import Any, Optional, Union, Dict, List
from functools import wraps
import redis.asyncio as redis

from app.core.config import settings
from app.utils.logger import app_logger


class CacheManager:
    """
    Redis tabanlı cache yöneticisi
    """
    
    def __init__(self):
        self.redis_client = None
        self.default_ttl = 3600  # 1 saat
        self.key_prefix = "onlyvips:cache:"
    
    async def get_redis_client(self):
        """Redis bağlantısını al"""
        if not self.redis_client:
            try:
                self.redis_client = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    password=settings.REDIS_PASSWORD,
                    decode_responses=False  # Binary data için
                )
                await self.redis_client.ping()
            except Exception as e:
                app_logger.warning(f"Redis bağlantısı kurulamadı: {e}")
                return None
        return self.redis_client
    
    def _make_key(self, key: str) -> str:
        """Cache anahtarı oluştur"""
        return f"{self.key_prefix}{key}"
    
    def _serialize_value(self, value: Any) -> bytes:
        """Değeri serialize et"""
        try:
            # JSON serializable ise JSON kullan (daha hızlı)
            json.dumps(value)
            return json.dumps(value).encode('utf-8')
        except (TypeError, ValueError):
            # JSON serializable değilse pickle kullan
            return pickle.dumps(value)
    
    def _deserialize_value(self, data: bytes) -> Any:
        """Değeri deserialize et"""
        try:
            # Önce JSON dene
            return json.loads(data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            # JSON değilse pickle dene
            return pickle.loads(data)
    
    async def get(self, key: str) -> Optional[Any]:
        """Cache'den değer al"""
        redis_client = await self.get_redis_client()
        if not redis_client:
            return None
        
        try:
            cache_key = self._make_key(key)
            data = await redis_client.get(cache_key)
            
            if data is None:
                return None
            
            return self._deserialize_value(data)
        
        except Exception as e:
            app_logger.error(f"Cache get hatası: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Cache'e değer kaydet"""
        redis_client = await self.get_redis_client()
        if not redis_client:
            return False
        
        try:
            cache_key = self._make_key(key)
            serialized_value = self._serialize_value(value)
            ttl = ttl or self.default_ttl
            
            await redis_client.setex(cache_key, ttl, serialized_value)
            return True
        
        except Exception as e:
            app_logger.error(f"Cache set hatası: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Cache'den değer sil"""
        redis_client = await self.get_redis_client()
        if not redis_client:
            return False
        
        try:
            cache_key = self._make_key(key)
            result = await redis_client.delete(cache_key)
            return result > 0
        
        except Exception as e:
            app_logger.error(f"Cache delete hatası: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Cache'de anahtar var mı kontrol et"""
        redis_client = await self.get_redis_client()
        if not redis_client:
            return False
        
        try:
            cache_key = self._make_key(key)
            result = await redis_client.exists(cache_key)
            return result > 0
        
        except Exception as e:
            app_logger.error(f"Cache exists hatası: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1, ttl: Optional[int] = None) -> Optional[int]:
        """Sayısal değeri artır"""
        redis_client = await self.get_redis_client()
        if not redis_client:
            return None
        
        try:
            cache_key = self._make_key(key)
            result = await redis_client.incr(cache_key, amount)
            
            if ttl:
                await redis_client.expire(cache_key, ttl)
            
            return result
        
        except Exception as e:
            app_logger.error(f"Cache increment hatası: {e}")
            return None
    
    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Birden fazla anahtarı al"""
        redis_client = await self.get_redis_client()
        if not redis_client:
            return {}
        
        try:
            cache_keys = [self._make_key(key) for key in keys]
            values = await redis_client.mget(cache_keys)
            
            result = {}
            for i, value in enumerate(values):
                if value is not None:
                    try:
                        result[keys[i]] = self._deserialize_value(value)
                    except Exception as e:
                        app_logger.error(f"Deserialization hatası: {e}")
            
            return result
        
        except Exception as e:
            app_logger.error(f"Cache get_many hatası: {e}")
            return {}
    
    async def set_many(self, data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Birden fazla anahtar-değer çifti kaydet"""
        redis_client = await self.get_redis_client()
        if not redis_client:
            return False
        
        try:
            pipe = redis_client.pipeline()
            ttl = ttl or self.default_ttl
            
            for key, value in data.items():
                cache_key = self._make_key(key)
                serialized_value = self._serialize_value(value)
                pipe.setex(cache_key, ttl, serialized_value)
            
            await pipe.execute()
            return True
        
        except Exception as e:
            app_logger.error(f"Cache set_many hatası: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Pattern'e uyan anahtarları sil"""
        redis_client = await self.get_redis_client()
        if not redis_client:
            return 0
        
        try:
            cache_pattern = self._make_key(pattern)
            keys = await redis_client.keys(cache_pattern)
            
            if keys:
                deleted = await redis_client.delete(*keys)
                return deleted
            
            return 0
        
        except Exception as e:
            app_logger.error(f"Cache clear_pattern hatası: {e}")
            return 0


# Global cache manager instance
cache = CacheManager()


def cache_key_generator(*args, **kwargs) -> str:
    """
    Fonksiyon parametrelerinden cache anahtarı oluştur
    """
    # Parametreleri string'e çevir
    key_parts = []
    
    for arg in args:
        if hasattr(arg, '__dict__'):
            # Object ise ID'sini al
            key_parts.append(str(getattr(arg, 'id', str(arg))))
        else:
            key_parts.append(str(arg))
    
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}:{v}")
    
    # Hash oluştur
    key_string = ":".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


def cached(ttl: int = 3600, key_prefix: str = ""):
    """
    Fonksiyon sonucunu cache'leyen decorator
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Cache anahtarı oluştur
            func_name = f"{func.__module__}.{func.__name__}"
            param_key = cache_key_generator(*args, **kwargs)
            cache_key = f"{key_prefix}:{func_name}:{param_key}" if key_prefix else f"{func_name}:{param_key}"
            
            # Cache'den kontrol et
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                app_logger.debug(f"Cache hit: {cache_key}")
                return cached_result
            
            # Fonksiyonu çalıştır
            result = await func(*args, **kwargs)
            
            # Sonucu cache'le
            await cache.set(cache_key, result, ttl)
            app_logger.debug(f"Cache set: {cache_key}")
            
            return result
        
        return wrapper
    return decorator


def cache_invalidate(key_pattern: str):
    """
    Cache invalidation decorator
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            # Cache'i temizle
            deleted_count = await cache.clear_pattern(key_pattern)
            if deleted_count > 0:
                app_logger.debug(f"Cache invalidated: {key_pattern} ({deleted_count} keys)")
            
            return result
        
        return wrapper
    return decorator


# Özel cache fonksiyonları
class UserCache:
    """Kullanıcı verilerini cache'leme"""
    
    @staticmethod
    async def get_user(user_id: str) -> Optional[Dict]:
        """Kullanıcı bilgilerini cache'den al"""
        return await cache.get(f"user:{user_id}")
    
    @staticmethod
    async def set_user(user_id: str, user_data: Dict, ttl: int = 1800) -> bool:
        """Kullanıcı bilgilerini cache'le"""
        return await cache.set(f"user:{user_id}", user_data, ttl)
    
    @staticmethod
    async def invalidate_user(user_id: str) -> bool:
        """Kullanıcı cache'ini temizle"""
        return await cache.delete(f"user:{user_id}")


class ContentCache:
    """İçerik verilerini cache'leme"""
    
    @staticmethod
    async def get_content(content_id: str) -> Optional[Dict]:
        """İçerik bilgilerini cache'den al"""
        return await cache.get(f"content:{content_id}")
    
    @staticmethod
    async def set_content(content_id: str, content_data: Dict, ttl: int = 3600) -> bool:
        """İçerik bilgilerini cache'le"""
        return await cache.set(f"content:{content_id}", content_data, ttl)
    
    @staticmethod
    async def get_content_list(filters: str) -> Optional[List]:
        """İçerik listesini cache'den al"""
        filter_hash = hashlib.md5(filters.encode()).hexdigest()
        return await cache.get(f"content_list:{filter_hash}")
    
    @staticmethod
    async def set_content_list(filters: str, content_list: List, ttl: int = 600) -> bool:
        """İçerik listesini cache'le"""
        filter_hash = hashlib.md5(filters.encode()).hexdigest()
        return await cache.set(f"content_list:{filter_hash}", content_list, ttl)


class TaskCache:
    """Görev verilerini cache'leme"""
    
    @staticmethod
    async def get_user_tasks(user_id: str) -> Optional[List]:
        """Kullanıcı görevlerini cache'den al"""
        return await cache.get(f"user_tasks:{user_id}")
    
    @staticmethod
    async def set_user_tasks(user_id: str, tasks: List, ttl: int = 300) -> bool:
        """Kullanıcı görevlerini cache'le"""
        return await cache.set(f"user_tasks:{user_id}", tasks, ttl)
    
    @staticmethod
    async def invalidate_user_tasks(user_id: str) -> bool:
        """Kullanıcı görev cache'ini temizle"""
        return await cache.delete(f"user_tasks:{user_id}") 