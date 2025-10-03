#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Logger Modülü
Uygulamanın log mekanizması için ayarlar ve yardımcı fonksiyonlar
"""

import os
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional

from app.core.config import settings


# Log formatları
log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
log_date_format = "%Y-%m-%d %H:%M:%S"

# Log dizini oluştur
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
os.makedirs(log_dir, exist_ok=True)

# Log dosya yolları
app_log_path = os.path.join(log_dir, "app.log")
error_log_path = os.path.join(log_dir, "error.log")
tasks_log_path = os.path.join(log_dir, "tasks.log")


# Log seviyesini belirle
def get_log_level() -> int:
    """
    Yapılandırmaya göre log seviyesini belirler
    """
    log_level_str = settings.LOG_LEVEL.upper()
    
    log_levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    return log_levels.get(log_level_str, logging.INFO)


# JSON formatında log oluşturma sınıfı
class JsonFormatter(logging.Formatter):
    """
    Log kayıtlarını JSON formatında biçimlendirir
    """
    def format(self, record):
        log_record = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "pathname": record.pathname,
            "lineno": record.lineno,
            "funcName": record.funcName
        }
        
        if hasattr(record, "extra") and record.extra:
            log_record.update(record.extra)
            
        # Exception bilgisi varsa ekle
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_record)


# Ana logger ayarları
def setup_logger() -> logging.Logger:
    """
    Ana uygulama logger'ını yapılandırır ve döndürür
    """
    logger = logging.getLogger("onlyvips-api")
    logger.setLevel(get_log_level())
    
    # Handler'ları temizle (çoklu çağrılarda yineleme olmaması için)
    if logger.handlers:
        logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(get_log_level())
    
    # Dosya handler'ları
    file_handler = logging.FileHandler(app_log_path)
    file_handler.setLevel(get_log_level())
    
    error_handler = logging.FileHandler(error_log_path)
    error_handler.setLevel(logging.ERROR)
    
    # Formatlar
    if settings.LOG_JSON:
        # JSON formatında
        formatter = JsonFormatter()
    else:
        # Metin formatında
        formatter = logging.Formatter(log_format, log_date_format)
    
    # Handler'lara formatları uygula
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)
    
    # Logger'a handler'ları ekle
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    
    return logger


# Görev tamamlama logger'ı
def setup_task_logger() -> logging.Logger:
    """
    Görev tamamlama kayıtları için özel logger'ı yapılandırır
    """
    task_logger = logging.getLogger("onlyvips-tasks")
    task_logger.setLevel(logging.INFO)
    
    # Handler'ları temizle
    if task_logger.handlers:
        task_logger.handlers = []
    
    # Dosya handler
    task_handler = logging.FileHandler(tasks_log_path)
    task_handler.setLevel(logging.INFO)
    
    # JSON formatı kullan
    task_handler.setFormatter(JsonFormatter())
    
    # Logger'a handler ekle
    task_logger.addHandler(task_handler)
    
    return task_logger


# Ana uygulama logger'ını oluştur
app_logger = setup_logger()

# Görev logger'ını oluştur
task_logger = setup_task_logger()


# Görev tamamlama log fonksiyonu
def log_task_completion(user_id: str, task_id: Any, status: str, details: Optional[Dict[str, Any]] = None) -> None:
    """
    Görev tamamlama/doğrulama işlemlerini loglar
    """
    log_data = {
        "user_id": user_id,
        "task_id": task_id,
        "status": status,
        "timestamp": datetime.now().isoformat()
    }
    
    if details:
        log_data.update(details)
    
    task_logger.info(json.dumps(log_data))

def log_api_call(endpoint, method, user_id=None, status_code=200, response_time=0):
    """API çağrısı metriğini logla"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"{timestamp}|{endpoint}|{method}|{status_code}|{response_time}ms"
    
    if user_id:
        message += f"|{user_id}"
        
    metrics_logger.info(message)
    
# Hata ayıklama
if __name__ == "__main__":
    app_logger.debug("Debug log mesajı")
    app_logger.info("Info log mesajı")
    app_logger.warning("Warning log mesajı")
    app_logger.error("Error log mesajı")
    app_logger.critical("Critical log mesajı")
    
    log_task_completion("123", "join_channel", "SUCCESS", {"xp": 10})
    log_api_call("/api/tasks", "GET", "123", 200, 125) 