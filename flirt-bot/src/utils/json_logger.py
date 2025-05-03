#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JSON Logger Module - JSON Loglama modülü
Bu modül structlog kullanarak JSON formatında loglama sağlar
"""

import os
import time
import sys
import logging
import structlog
from typing import Dict, Any, Optional, List
from datetime import datetime

# Log dizini
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Farklı log türleri için alt dizinler
TASK_LOG_DIR = os.path.join(LOG_DIR, "tasks")
ERROR_LOG_DIR = os.path.join(LOG_DIR, "errors")
os.makedirs(TASK_LOG_DIR, exist_ok=True)
os.makedirs(ERROR_LOG_DIR, exist_ok=True)

# Loglama seviyesi
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_LEVEL_NUM = getattr(logging, LOG_LEVEL)

# Standart logging handler'larını yapılandır
logging.basicConfig(
    format="%(message)s",
    level=LOG_LEVEL_NUM
)

# Structlog zaman formatlayıcısı
def time_stamper(_, __, event_dict):
    """Olay sözlüğüne zaman damgası ekle"""
    event_dict["timestamp"] = datetime.utcnow().isoformat() + "Z"
    return event_dict

# Ek context bilgisi ekleyici
def add_app_context(_, __, event_dict):
    """Olay sözlüğüne uygulama bağlamı ekle"""
    event_dict["app"] = "flirt-bot"
    event_dict["host"] = os.uname().nodename
    return event_dict

# Structlog processor'larını yapılandır
structlog.configure(
    processors=[
        # Standart işlemciler
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        time_stamper,
        add_app_context,
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(sort_keys=True)
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Yapılandırılmış logger'ları oluştur
def get_logger(name: str):
    """Yapılandırılmış logger döndür"""
    return structlog.get_logger(name)

# Ön tanımlı logger'lar
bot_logger = get_logger("bot")
api_logger = get_logger("api")
task_logger = get_logger("task")
auth_logger = get_logger("auth")

# Görev loglama
def log_task_completion(task_data: Dict[str, Any]):
    """Tamamlanan görev log dosyasına JSON kaydı ekle"""
    task_log_file = os.path.join(
        TASK_LOG_DIR, 
        f"completed_{datetime.now().strftime('%Y%m%d')}.jsonl"
    )
    
    task_logger.info(
        "task_completed",
        task_id=task_data.get("task_id"),
        user_id=task_data.get("user_id"),
        verification_type=task_data.get("verification_type"),
        duration=task_data.get("duration", 0)
    )

def log_task_failure(task_data: Dict[str, Any], error: Optional[str] = None):
    """Başarısız görev log dosyasına JSON kaydı ekle"""
    task_log_file = os.path.join(
        TASK_LOG_DIR, 
        f"failed_{datetime.now().strftime('%Y%m%d')}.jsonl"
    )
    
    task_logger.error(
        "task_failed",
        task_id=task_data.get("task_id"),
        user_id=task_data.get("user_id"),
        verification_type=task_data.get("verification_type"),
        error=error or "Unknown error"
    )

# Metrik izleme
class TaskMetrics:
    """Görev metriklerini takip eden sınıf"""
    
    def __init__(self):
        self.task_counts: Dict[str, int] = {}
        self.task_durations: Dict[str, List[float]] = {}
        self.error_counts: Dict[str, int] = {}
        self.start_time: float = time.time()
    
    def add_task_completion(self, task_type: str, duration: float):
        """Tamamlanan görevi metriklere ekle"""
        if task_type not in self.task_counts:
            self.task_counts[task_type] = 0
            self.task_durations[task_type] = []
        
        self.task_counts[task_type] += 1
        self.task_durations[task_type].append(duration)
    
    def add_error(self, error_type: str):
        """Hatayı metriklere ekle"""
        if error_type not in self.error_counts:
            self.error_counts[error_type] = 0
        
        self.error_counts[error_type] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Mevcut metrikleri döndür"""
        uptime = time.time() - self.start_time
        
        metrics = {
            "uptime_seconds": uptime,
            "task_counts": self.task_counts,
            "error_counts": self.error_counts,
            "task_avg_durations": {}
        }
        
        # Ortalama süreleri hesapla
        for task_type, durations in self.task_durations.items():
            if durations:
                metrics["task_avg_durations"][task_type] = sum(durations) / len(durations)
        
        return metrics

# Global metrik izleyici
metrics = TaskMetrics() 