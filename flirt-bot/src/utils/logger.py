#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Logger Module - Loglama modülü
Bu modül loglama işlevlerini sağlar
"""

import os
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional, Union

# Loglama formatı
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Loglama dizini
LOG_DIR = 'logs'

def setup_logging(log_level: int = logging.INFO) -> None:
    """Loglama ayarları"""
    # Dizini oluştur
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # Ana logger'ı yapılandır
    logging.basicConfig(
        level=log_level,
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
        handlers=[
            # Konsol loglama
            logging.StreamHandler(),
            # Dosya loglama
            logging.FileHandler(os.path.join(LOG_DIR, f'bot_{datetime.now().strftime("%Y%m%d")}.log'))
        ]
    )
    
    # Fazla loglama yapan modülleri bastır
    logging.getLogger('telethon').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    # Log dizinleri oluştur
    os.makedirs(os.path.join(LOG_DIR, 'completed'), exist_ok=True)
    os.makedirs(os.path.join(LOG_DIR, 'expired'), exist_ok=True)

def log_task_completed(task_data: Dict[str, Any]) -> None:
    """Tamamlanan görevi logla"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        **task_data,
        "status": "COMPLETED"
    }
    
    # Günlük dosya adı
    filename = os.path.join(LOG_DIR, 'completed', f'completed_{datetime.now().strftime("%Y%m%d")}.jsonl')
    
    # Log girdisini yaz
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    # Logger'a da bilgi ver
    logging.getLogger(__name__).info(f"Görev tamamlandı: {task_data.get('user_id')} için {task_data.get('task_id')}")

def log_task_expired(task_data: Dict[str, Any]) -> None:
    """Süresi dolan görevi logla"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        **task_data,
        "status": "EXPIRED"
    }
    
    # Günlük dosya adı
    filename = os.path.join(LOG_DIR, 'expired', f'expired_{datetime.now().strftime("%Y%m%d")}.jsonl')
    
    # Log girdisini yaz
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    # Logger'a da bilgi ver
    logging.getLogger(__name__).warning(f"Görev süresi doldu: {task_data.get('user_id')} için {task_data.get('task_id')}")

def get_logger(name: str) -> logging.Logger:
    """Adlandırılmış logger al"""
    return logging.getLogger(name) 