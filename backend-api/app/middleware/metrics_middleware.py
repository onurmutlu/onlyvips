"""
Metrics Middleware
Prometheus metrikleri ve API performans izleme
"""

import time
from typing import Optional
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

try:
    from prometheus_client import Counter, Histogram, Gauge
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

from app.utils.logger import app_logger

class MetricsMiddleware(BaseHTTPMiddleware):
    """
    API metrikleri toplayan middleware
    Prometheus metrikleri ve performans izleme
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        
        if PROMETHEUS_AVAILABLE:
            # Prometheus metrikleri
            self.request_count = Counter(
                'http_requests_total',
                'Total HTTP requests',
                ['method', 'endpoint', 'status_code']
            )
            
            self.request_duration = Histogram(
                'http_request_duration_seconds',
                'HTTP request duration in seconds',
                ['method', 'endpoint']
            )
            
            self.active_requests = Gauge(
                'http_requests_active',
                'Active HTTP requests'
            )
            
            self.request_size = Histogram(
                'http_request_size_bytes',
                'HTTP request size in bytes',
                ['method', 'endpoint']
            )
            
            self.response_size = Histogram(
                'http_response_size_bytes',
                'HTTP response size in bytes',
                ['method', 'endpoint']
            )
        else:
            app_logger.warning("Prometheus client not available, metrics disabled")
    
    def get_endpoint_pattern(self, path: str) -> str:
        """
        URL path'ini endpoint pattern'ine çevir
        """
        # API versiyonunu kaldır
        if path.startswith('/api'):
            path = path[4:]
        
        # Path parametrelerini normalize et
        path_parts = path.split('/')
        normalized_parts = []
        
        for part in path_parts:
            if not part:
                continue
            # UUID veya ID pattern'lerini {id} ile değiştir
            if (len(part) > 10 and 
                (part.replace('-', '').replace('_', '').isalnum() or
                 part.isdigit())):
                normalized_parts.append('{id}')
            else:
                normalized_parts.append(part)
        
        return '/' + '/'.join(normalized_parts) if normalized_parts else '/'
    
    def get_request_size(self, request: Request) -> int:
        """
        Request boyutunu hesapla
        """
        size = 0
        
        # Headers boyutu
        for name, value in request.headers.items():
            size += len(name) + len(value) + 4  # ": " ve "\r\n"
        
        # Content-Length varsa ekle
        content_length = request.headers.get('content-length')
        if content_length:
            try:
                size += int(content_length)
            except ValueError:
                pass
        
        return size
    
    def get_response_size(self, response) -> int:
        """
        Response boyutunu hesapla
        """
        size = 0
        
        # Headers boyutu
        for name, value in response.headers.items():
            size += len(name) + len(value) + 4
        
        # Content-Length varsa ekle
        content_length = response.headers.get('content-length')
        if content_length:
            try:
                size += int(content_length)
            except ValueError:
                pass
        
        return size
    
    async def dispatch(self, request: Request, call_next):
        """
        Metrics toplama ve request işleme
        """
        start_time = time.time()
        
        # Request bilgileri
        method = request.method
        path = request.url.path
        endpoint = self.get_endpoint_pattern(path)
        
        # Request boyutu
        request_size = self.get_request_size(request)
        
        # Aktif request sayısını artır
        if PROMETHEUS_AVAILABLE:
            self.active_requests.inc()
            self.request_size.labels(method=method, endpoint=endpoint).observe(request_size)
        
        try:
            # Request'i işle
            response = await call_next(request)
            
            # İşlem süresi
            duration = time.time() - start_time
            status_code = response.status_code
            
            # Response boyutu
            response_size = self.get_response_size(response)
            
            # Metrikleri kaydet
            if PROMETHEUS_AVAILABLE:
                self.request_count.labels(
                    method=method,
                    endpoint=endpoint,
                    status_code=status_code
                ).inc()
                
                self.request_duration.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(duration)
                
                self.response_size.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(response_size)
            
            # Performance headers ekle
            response.headers["X-Process-Time"] = f"{duration:.3f}"
            response.headers["X-Request-ID"] = getattr(request.state, 'request_id', 'unknown')
            
            # Log kaydı
            app_logger.info(
                f"API Call: {method} {endpoint} - {status_code} - {duration:.3f}s",
                extra={
                    "method": method,
                    "endpoint": endpoint,
                    "status_code": status_code,
                    "duration": duration,
                    "request_size": request_size,
                    "response_size": response_size
                }
            )
            
            return response
            
        except Exception as e:
            # Hata durumu
            duration = time.time() - start_time
            
            if PROMETHEUS_AVAILABLE:
                self.request_count.labels(
                    method=method,
                    endpoint=endpoint,
                    status_code=500
                ).inc()
                
                self.request_duration.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(duration)
            
            # Hata log'u
            app_logger.error(
                f"API Error: {method} {endpoint} - 500 - {duration:.3f}s - {str(e)}",
                extra={
                    "method": method,
                    "endpoint": endpoint,
                    "status_code": 500,
                    "duration": duration,
                    "error": str(e)
                }
            )
            
            raise
            
        finally:
            # Aktif request sayısını azalt
            if PROMETHEUS_AVAILABLE:
                self.active_requests.dec() 