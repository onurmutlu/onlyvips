from fastapi import APIRouter, Response
from prometheus_client import (
    Counter, Gauge, Histogram, REGISTRY,
    generate_latest, CONTENT_TYPE_LATEST
)
import time

# Prometheus metrik tanımlamaları
REQUEST_COUNT = Counter(
    "onlyvips_api_request_count", 
    "API istek sayacı",
    ["method", "endpoint", "status_code"]
)
REQUEST_LATENCY = Histogram(
    "onlyvips_api_request_latency_seconds", 
    "API istek işleme süresi (saniye)",
    ["method", "endpoint"]
)
ACTIVE_USERS = Gauge(
    "onlyvips_active_users", 
    "Aktif kullanıcı sayısı"
)
MESSAGE_SENT_COUNT = Counter(
    "onlyvips_message_sent_count", 
    "Gönderilen mesaj sayısı",
    ["user_id", "message_type"]
)
ERROR_COUNT = Counter(
    "onlyvips_error_count", 
    "Hata sayısı",
    ["error_type", "endpoint"]
)
CONTENT_UPLOAD_COUNT = Counter(
    "onlyvips_content_upload_count", 
    "Yüklenen içerik sayısı",
    ["content_type", "user_id"]
)

router = APIRouter()

@router.get("/metrics")
async def metrics():
    """
    Prometheus metrikleri. Bu endpoint Prometheus tarafından düzenli olarak 
    çağrılır ve mevcut metrik değerlerini toplar.
    """
    return Response(
        content=generate_latest(REGISTRY),
        media_type=CONTENT_TYPE_LATEST
    )

# Yardımcı fonksiyonlar
def increment_request_count(method: str, endpoint: str, status_code: int):
    """API istek sayacını artır"""
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status_code).inc()

def observe_request_latency(method: str, endpoint: str, duration: float):
    """API istek süresini kaydet"""
    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)

def increment_message_sent(user_id: str, message_type: str = "text"):
    """Mesaj gönderim sayacını artır"""
    MESSAGE_SENT_COUNT.labels(user_id=user_id, message_type=message_type).inc()

def increment_error_count(error_type: str, endpoint: str = "unknown"):
    """Hata sayacını artır"""
    ERROR_COUNT.labels(error_type=error_type, endpoint=endpoint).inc()

def set_active_users(count: int):
    """Aktif kullanıcı sayısını ayarla"""
    ACTIVE_USERS.set(count)

def increment_content_upload(content_type: str, user_id: str):
    """İçerik yükleme sayacını artır"""
    CONTENT_UPLOAD_COUNT.labels(content_type=content_type, user_id=user_id).inc() 