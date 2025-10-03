"""
Health Check Endpoints
Sistem sağlığı ve bağımlılık kontrolü
"""

import time
import asyncio
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends
import redis.asyncio as redis
import httpx

from app.core.config import settings
from app.core.database import db
from app.utils.logger import app_logger

router = APIRouter()


async def check_database() -> Dict[str, Any]:
    """Veritabanı bağlantısını kontrol et"""
    try:
        start_time = time.time()
        
        if settings.DB_PROVIDER == "memory":
            return {
                "status": "healthy",
                "type": "memory",
                "response_time_ms": 0,
                "message": "Memory database active"
            }
        
        elif settings.DB_PROVIDER == "mongodb":
            # MongoDB ping
            await db.command("ping")
            response_time = int((time.time() - start_time) * 1000)
            
            return {
                "status": "healthy",
                "type": "mongodb",
                "response_time_ms": response_time,
                "message": "MongoDB connection successful"
            }
        
        else:
            return {
                "status": "unknown",
                "type": settings.DB_PROVIDER,
                "response_time_ms": 0,
                "message": f"Unknown database provider: {settings.DB_PROVIDER}"
            }
    
    except Exception as e:
        app_logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "type": settings.DB_PROVIDER,
            "response_time_ms": 0,
            "error": str(e)
        }


async def check_redis() -> Dict[str, Any]:
    """Redis bağlantısını kontrol et"""
    try:
        start_time = time.time()
        
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )
        
        # Redis ping
        await redis_client.ping()
        response_time = int((time.time() - start_time) * 1000)
        
        # Redis info
        info = await redis_client.info()
        
        await redis_client.close()
        
        return {
            "status": "healthy",
            "response_time_ms": response_time,
            "version": info.get("redis_version", "unknown"),
            "memory_usage": info.get("used_memory_human", "unknown"),
            "connected_clients": info.get("connected_clients", 0),
            "message": "Redis connection successful"
        }
    
    except Exception as e:
        app_logger.error(f"Redis health check failed: {e}")
        return {
            "status": "unhealthy",
            "response_time_ms": 0,
            "error": str(e)
        }


async def check_external_services() -> Dict[str, Any]:
    """Harici servisleri kontrol et"""
    services = {}
    
    # OpenAI API kontrolü
    if settings.OPENAI_API_KEY:
        try:
            start_time = time.time()
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    "https://api.openai.com/v1/models",
                    headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
                )
                response_time = int((time.time() - start_time) * 1000)
                
                if response.status_code == 200:
                    services["openai"] = {
                        "status": "healthy",
                        "response_time_ms": response_time,
                        "message": "OpenAI API accessible"
                    }
                else:
                    services["openai"] = {
                        "status": "unhealthy",
                        "response_time_ms": response_time,
                        "error": f"HTTP {response.status_code}"
                    }
        except Exception as e:
            services["openai"] = {
                "status": "unhealthy",
                "response_time_ms": 0,
                "error": str(e)
            }
    
    # Telegram Bot API kontrolü
    if settings.BOT_TOKEN:
        try:
            start_time = time.time()
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"https://api.telegram.org/bot{settings.BOT_TOKEN}/getMe"
                )
                response_time = int((time.time() - start_time) * 1000)
                
                if response.status_code == 200:
                    bot_info = response.json()
                    services["telegram"] = {
                        "status": "healthy",
                        "response_time_ms": response_time,
                        "bot_username": bot_info.get("result", {}).get("username", "unknown"),
                        "message": "Telegram Bot API accessible"
                    }
                else:
                    services["telegram"] = {
                        "status": "unhealthy",
                        "response_time_ms": response_time,
                        "error": f"HTTP {response.status_code}"
                    }
        except Exception as e:
            services["telegram"] = {
                "status": "unhealthy",
                "response_time_ms": 0,
                "error": str(e)
            }
    
    return services


@router.get("/health")
async def basic_health_check():
    """
    Basit sağlık kontrolü
    Load balancer ve monitoring için hızlı endpoint
    """
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }


@router.get("/health/detailed")
async def detailed_health_check():
    """
    Detaylı sağlık kontrolü
    Tüm bağımlılıkları kontrol eder
    """
    start_time = time.time()
    
    # Paralel olarak tüm kontrolleri yap
    database_check, redis_check, external_services = await asyncio.gather(
        check_database(),
        check_redis(),
        check_external_services(),
        return_exceptions=True
    )
    
    total_time = int((time.time() - start_time) * 1000)
    
    # Genel durum belirleme
    overall_status = "healthy"
    
    # Database kontrolü
    if isinstance(database_check, Exception) or database_check.get("status") != "healthy":
        overall_status = "unhealthy"
    
    # Redis kontrolü
    if isinstance(redis_check, Exception) or redis_check.get("status") != "healthy":
        overall_status = "degraded" if overall_status == "healthy" else "unhealthy"
    
    # External services kontrolü
    if isinstance(external_services, Exception):
        external_services = {"error": str(external_services)}
    else:
        for service_name, service_status in external_services.items():
            if service_status.get("status") != "healthy":
                overall_status = "degraded" if overall_status == "healthy" else overall_status
    
    return {
        "status": overall_status,
        "timestamp": time.time(),
        "total_check_time_ms": total_time,
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "checks": {
            "database": database_check if not isinstance(database_check, Exception) else {"status": "error", "error": str(database_check)},
            "redis": redis_check if not isinstance(redis_check, Exception) else {"status": "error", "error": str(redis_check)},
            "external_services": external_services
        }
    }


@router.get("/health/readiness")
async def readiness_check():
    """
    Readiness probe - Kubernetes için
    Servisin istekleri kabul etmeye hazır olup olmadığını kontrol eder
    """
    try:
        # Kritik bağımlılıkları kontrol et
        database_check = await check_database()
        
        if database_check.get("status") != "healthy":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database not ready"
            )
        
        return {
            "status": "ready",
            "timestamp": time.time(),
            "message": "Service is ready to accept requests"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not ready"
        )


@router.get("/health/liveness")
async def liveness_check():
    """
    Liveness probe - Kubernetes için
    Servisin çalışır durumda olup olmadığını kontrol eder
    """
    return {
        "status": "alive",
        "timestamp": time.time(),
        "uptime_seconds": time.time() - start_time if 'start_time' in globals() else 0,
        "message": "Service is alive"
    }


@router.get("/metrics")
async def metrics_endpoint():
    """
    Prometheus metrics endpoint
    """
    try:
        from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
        from fastapi import Response
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
    except ImportError:
        return {"error": "Prometheus client not installed"}


# Startup time'ı kaydet
start_time = time.time()