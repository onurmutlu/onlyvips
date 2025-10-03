"""
Sentry Error Tracking Konfigürasyonu
Production ortamında hata izleme ve performans monitoring
"""

import os
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from app.core.config import settings
from app.utils.logger import app_logger


def init_sentry():
    """
    Sentry'yi başlat ve yapılandır
    """
    sentry_dsn = os.getenv("SENTRY_DSN")
    
    if not sentry_dsn:
        app_logger.info("Sentry DSN bulunamadı, error tracking devre dışı")
        return
    
    # Sentry konfigürasyonu
    sentry_sdk.init(
        dsn=sentry_dsn,
        environment=settings.ENVIRONMENT,
        release=f"onlyvips-backend@{os.getenv('APP_VERSION', '1.0.0')}",
        
        # Entegrasyonlar
        integrations=[
            FastApiIntegration(auto_enabling_integrations=False),
            SqlalchemyIntegration(),
            RedisIntegration(),
            LoggingIntegration(
                level=None,  # Capture info and above
                event_level=None  # Send no events from logging
            ),
        ],
        
        # Performance monitoring
        traces_sample_rate=0.1 if settings.ENVIRONMENT == "production" else 1.0,
        
        # Error sampling
        sample_rate=1.0,
        
        # Session tracking
        auto_session_tracking=True,
        
        # Performance monitoring
        enable_tracing=True,
        
        # Profiling
        profiles_sample_rate=0.1 if settings.ENVIRONMENT == "production" else 1.0,
        
        # Kişisel verileri filtreleme
        before_send=filter_sensitive_data,
        before_send_transaction=filter_sensitive_transactions,
        
        # Debug modu
        debug=settings.ENVIRONMENT == "development",
        
        # Attach stacktrace
        attach_stacktrace=True,
        
        # Max breadcrumbs
        max_breadcrumbs=50,
        
        # Request bodies
        max_request_body_size="medium",  # 10KB
        
        # Tag'ler
        default_integrations=False,
    )
    
    # Global tag'ler
    sentry_sdk.set_tag("service", "onlyvips-backend")
    sentry_sdk.set_tag("version", os.getenv('APP_VERSION', '1.0.0'))
    
    app_logger.info(f"Sentry başlatıldı - Environment: {settings.ENVIRONMENT}")


def filter_sensitive_data(event, hint):
    """
    Hassas verileri Sentry'ye gönderilmeden önce filtrele
    """
    # Request data filtreleme
    if 'request' in event:
        request = event['request']
        
        # Headers filtreleme
        if 'headers' in request:
            sensitive_headers = ['authorization', 'x-api-key', 'cookie', 'x-telegram-init-data']
            for header in sensitive_headers:
                if header in request['headers']:
                    request['headers'][header] = '[Filtered]'
        
        # Query string filtreleme
        if 'query_string' in request:
            sensitive_params = ['token', 'password', 'secret', 'key']
            query_string = request['query_string']
            for param in sensitive_params:
                if param in query_string:
                    request['query_string'] = '[Filtered]'
        
        # Body filtreleme
        if 'data' in request:
            if isinstance(request['data'], dict):
                sensitive_fields = ['password', 'token', 'secret', 'api_key', 'telegram_init_data']
                for field in sensitive_fields:
                    if field in request['data']:
                        request['data'][field] = '[Filtered]'
    
    # Exception context filtreleme
    if 'contexts' in event:
        contexts = event['contexts']
        if 'runtime' in contexts:
            # Çevre değişkenlerini filtrele
            if 'env' in contexts['runtime']:
                sensitive_env_vars = ['SECRET_KEY', 'DB_PASSWORD', 'REDIS_PASSWORD', 'BOT_TOKEN']
                for env_var in sensitive_env_vars:
                    if env_var in contexts['runtime']['env']:
                        contexts['runtime']['env'][env_var] = '[Filtered]'
    
    # User bilgilerini filtrele
    if 'user' in event:
        user = event['user']
        sensitive_user_fields = ['telegram_id', 'phone', 'email']
        for field in sensitive_user_fields:
            if field in user:
                # Sadece ilk 3 karakteri göster
                original_value = str(user[field])
                if len(original_value) > 3:
                    user[field] = original_value[:3] + '*' * (len(original_value) - 3)
    
    return event


def filter_sensitive_transactions(event, hint):
    """
    Performance transaction'larını filtrele
    """
    # Hassas endpoint'leri filtrele
    if 'transaction' in event:
        transaction = event['transaction']
        sensitive_endpoints = ['/auth/', '/admin/', '/internal/']
        
        for endpoint in sensitive_endpoints:
            if endpoint in transaction:
                event['transaction'] = f"[Filtered]{endpoint}*"
                break
    
    return event


def capture_exception_with_context(exception: Exception, **context):
    """
    Exception'ı context bilgileriyle birlikte Sentry'ye gönder
    """
    with sentry_sdk.push_scope() as scope:
        # Context bilgilerini ekle
        for key, value in context.items():
            scope.set_context(key, value)
        
        # Exception'ı yakala
        sentry_sdk.capture_exception(exception)


def capture_message_with_context(message: str, level: str = "info", **context):
    """
    Message'ı context bilgileriyle birlikte Sentry'ye gönder
    """
    with sentry_sdk.push_scope() as scope:
        # Context bilgilerini ekle
        for key, value in context.items():
            scope.set_context(key, value)
        
        # Message'ı yakala
        sentry_sdk.capture_message(message, level=level)


def set_user_context(user_id: str, username: str = None, telegram_id: str = None):
    """
    Kullanıcı context'ini ayarla
    """
    sentry_sdk.set_user({
        "id": user_id,
        "username": username,
        "telegram_id": telegram_id[:6] + "***" if telegram_id else None  # Telegram ID'yi maskele
    })


def set_request_context(request_id: str, endpoint: str, method: str, ip: str):
    """
    Request context'ini ayarla
    """
    sentry_sdk.set_context("request", {
        "request_id": request_id,
        "endpoint": endpoint,
        "method": method,
        "ip": ip[:8] + "***" if ip else None  # IP'yi maskele
    })


def add_breadcrumb(message: str, category: str = "custom", level: str = "info", data: dict = None):
    """
    Breadcrumb ekle
    """
    sentry_sdk.add_breadcrumb(
        message=message,
        category=category,
        level=level,
        data=data or {}
    ) 