"""
Input Validation Middleware
SQL injection, XSS ve diğer güvenlik açıklarına karşı koruma
"""

import re
import json
from typing import Dict, List, Any
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.utils.logger import app_logger


class InputValidationMiddleware(BaseHTTPMiddleware):
    """
    Gelen isteklerin güvenlik açıklarına karşı doğrulanması
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        
        # SQL Injection kalıpları
        self.sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)",
            r"(--|#|/\*|\*/)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
            r"(\b(OR|AND)\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?)",
            r"(UNION\s+SELECT)",
            r"(EXEC\s*\()",
            r"(WAITFOR\s+DELAY)",
        ]
        
        # XSS kalıpları
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
            r"<link[^>]*>",
            r"<meta[^>]*>",
            r"vbscript:",
            r"data:text/html",
        ]
        
        # Path traversal kalıpları
        self.path_traversal_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"%2e%2e%2f",
            r"%2e%2e%5c",
            r"..%2f",
            r"..%5c",
        ]
        
        # Command injection kalıpları
        self.command_injection_patterns = [
            r"[;&|`$]",
            r"\$\(",
            r"`.*`",
            r"\|\s*\w+",
            r"&&\s*\w+",
            r";\s*\w+",
        ]
        
        # Güvenli olmayan karakterler
        self.unsafe_chars = [
            "\x00", "\x01", "\x02", "\x03", "\x04", "\x05", "\x06", "\x07",
            "\x08", "\x0b", "\x0c", "\x0e", "\x0f", "\x10", "\x11", "\x12",
            "\x13", "\x14", "\x15", "\x16", "\x17", "\x18", "\x19", "\x1a",
            "\x1b", "\x1c", "\x1d", "\x1e", "\x1f", "\x7f"
        ]
        
        # Doğrulama atlanacak endpoint'ler
        self.skip_validation_paths = [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/metrics"
        ]
    
    def contains_sql_injection(self, text: str) -> bool:
        """SQL injection kontrolü"""
        text_lower = text.lower()
        for pattern in self.sql_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        return False
    
    def contains_xss(self, text: str) -> bool:
        """XSS kontrolü"""
        text_lower = text.lower()
        for pattern in self.xss_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        return False
    
    def contains_path_traversal(self, text: str) -> bool:
        """Path traversal kontrolü"""
        text_lower = text.lower()
        for pattern in self.path_traversal_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        return False
    
    def contains_command_injection(self, text: str) -> bool:
        """Command injection kontrolü"""
        for pattern in self.command_injection_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def contains_unsafe_chars(self, text: str) -> bool:
        """Güvenli olmayan karakter kontrolü"""
        return any(char in text for char in self.unsafe_chars)
    
    def validate_string(self, text: str, field_name: str = "field") -> List[str]:
        """String değerini doğrula"""
        issues = []
        
        if self.contains_sql_injection(text):
            issues.append(f"{field_name}: SQL injection tespit edildi")
        
        if self.contains_xss(text):
            issues.append(f"{field_name}: XSS tespit edildi")
        
        if self.contains_path_traversal(text):
            issues.append(f"{field_name}: Path traversal tespit edildi")
        
        if self.contains_command_injection(text):
            issues.append(f"{field_name}: Command injection tespit edildi")
        
        if self.contains_unsafe_chars(text):
            issues.append(f"{field_name}: Güvenli olmayan karakterler tespit edildi")
        
        return issues
    
    def validate_data(self, data: Any, prefix: str = "") -> List[str]:
        """Veriyi recursive olarak doğrula"""
        issues = []
        
        if isinstance(data, str):
            issues.extend(self.validate_string(data, prefix or "string"))
        
        elif isinstance(data, dict):
            for key, value in data.items():
                key_issues = self.validate_string(str(key), f"{prefix}.{key}" if prefix else key)
                issues.extend(key_issues)
                
                value_issues = self.validate_data(value, f"{prefix}.{key}" if prefix else key)
                issues.extend(value_issues)
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                item_issues = self.validate_data(item, f"{prefix}[{i}]" if prefix else f"item[{i}]")
                issues.extend(item_issues)
        
        return issues
    
    async def validate_request_body(self, request: Request) -> List[str]:
        """Request body'yi doğrula"""
        issues = []
        
        try:
            # Content-Type kontrolü
            content_type = request.headers.get("content-type", "")
            
            if "application/json" in content_type:
                body = await request.body()
                if body:
                    try:
                        json_data = json.loads(body.decode())
                        issues.extend(self.validate_data(json_data, "body"))
                    except json.JSONDecodeError:
                        issues.append("Geçersiz JSON formatı")
            
            elif "application/x-www-form-urlencoded" in content_type:
                form_data = await request.form()
                for key, value in form_data.items():
                    issues.extend(self.validate_string(str(key), f"form.{key}"))
                    issues.extend(self.validate_string(str(value), f"form.{key}"))
            
        except Exception as e:
            app_logger.error(f"Request body doğrulama hatası: {e}")
            issues.append("Request body okunamadı")
        
        return issues
    
    def validate_query_params(self, request: Request) -> List[str]:
        """Query parametrelerini doğrula"""
        issues = []
        
        for key, value in request.query_params.items():
            issues.extend(self.validate_string(str(key), f"query.{key}"))
            issues.extend(self.validate_string(str(value), f"query.{key}"))
        
        return issues
    
    def validate_headers(self, request: Request) -> List[str]:
        """Header'ları doğrula"""
        issues = []
        
        # Kritik header'ları kontrol et
        critical_headers = ["authorization", "x-api-key", "user-agent"]
        
        for header_name, header_value in request.headers.items():
            if header_name.lower() in critical_headers:
                issues.extend(self.validate_string(str(header_value), f"header.{header_name}"))
        
        return issues
    
    def validate_path(self, request: Request) -> List[str]:
        """URL path'ini doğrula"""
        issues = []
        path = request.url.path
        
        issues.extend(self.validate_string(path, "path"))
        
        return issues
    
    async def dispatch(self, request: Request, call_next):
        """Input validation kontrolü"""
        
        # Doğrulama atlanacak path'ler
        if any(skip_path in request.url.path for skip_path in self.skip_validation_paths):
            return await call_next(request)
        
        all_issues = []
        
        # Path doğrulama
        all_issues.extend(self.validate_path(request))
        
        # Query parametreleri doğrulama
        all_issues.extend(self.validate_query_params(request))
        
        # Header doğrulama
        all_issues.extend(self.validate_headers(request))
        
        # Request body doğrulama (sadece POST, PUT, PATCH için)
        if request.method in ["POST", "PUT", "PATCH"]:
            # Request body'yi okumak için yeniden oluştur
            body = await request.body()
            
            # Yeni request oluştur (body'yi tekrar okuyabilmek için)
            async def receive():
                return {"type": "http.request", "body": body}
            
            request._receive = receive
            
            # Body doğrulama
            if body:
                try:
                    content_type = request.headers.get("content-type", "")
                    if "application/json" in content_type:
                        json_data = json.loads(body.decode())
                        all_issues.extend(self.validate_data(json_data, "body"))
                except Exception as e:
                    all_issues.append(f"Body parsing hatası: {str(e)}")
        
        # Güvenlik ihlali tespit edildiyse
        if all_issues:
            client_ip = request.client.host if request.client else "unknown"
            app_logger.warning(
                f"Güvenlik ihlali tespit edildi - IP: {client_ip}, "
                f"Path: {request.url.path}, Issues: {all_issues}"
            )
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Input validation failed",
                    "message": "Gönderilen veriler güvenlik kontrollerini geçemedi",
                    "issues": all_issues[:5]  # İlk 5 sorunu göster
                }
            )
        
        # İsteği işle
        response = await call_next(request)
        return response 