from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time

from app.api.endpoints.metrics import (
    increment_request_count, 
    observe_request_latency, 
    increment_error_count
)
from app.utils.logger import api_logger

class MetricsMiddleware(BaseHTTPMiddleware):
    """
    API isteklerini izlemek için middleware.
    Bu middleware her istek için şunları yapar:
    1. İstek süresini ölçer
    2. İstek sayısını artırır
    3. Hataları izler
    """
    
    async def dispatch(self, request: Request, call_next):
        # İstek detaylarını al
        method = request.method
        path = request.url.path
        
        # Metrik endpoints'ini izlemeyi atla
        if path == "/api/metrics" or path == "/metrics":
            return await call_next(request)
        
        # İstek süresini ölçmeye başla
        start_time = time.time()
        
        try:
            # İsteği işle
            response = await call_next(request)
            
            # İstek durumunu kaydet
            status_code = response.status_code
            
            # Hata durumlarını kontrol et
            if status_code >= 400:
                error_type = "client_error" if status_code < 500 else "server_error"
                increment_error_count(error_type, path)
                
                # Hataları logla
                api_logger.warning(
                    f"Hatalı istek: {method} {path}",
                    status_code=status_code,
                    method=method,
                    path=path,
                    client_host=request.client.host if request.client else "unknown"
                )
            
            # İstek süresini hesapla
            duration = time.time() - start_time
            
            # Metrikleri güncelle
            increment_request_count(method, path, status_code)
            observe_request_latency(method, path, duration)
            
            # Başarılı istekleri debug seviyesinde logla
            api_logger.debug(
                f"İstek tamamlandı: {method} {path}",
                duration=duration,
                status_code=status_code,
                method=method,
                path=path
            )
            
            return response
            
        except Exception as e:
            # İstek süresini hesapla
            duration = time.time() - start_time
            
            # Hata metriğini artır
            increment_error_count("unhandled_exception", path)
            
            # Hatayı logla
            api_logger.error(
                f"İşlenmeyen hata: {method} {path}",
                exc_info=True,
                error=str(e),
                error_type=type(e).__name__,
                method=method,
                path=path,
                duration=duration
            )
            
            # Hatayı yukarı aktar
            raise 