#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Logger Module - Loglama modülü
Bu modül JSON formatında loglama işlevlerini sağlar
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional, Union

from loguru import logger

# Log dizini
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Log dosya yolları
LOG_FILE_PATH = os.path.join(LOG_DIR, "onlyvips_{time}.log")
JSON_LOG_FILE_PATH = os.path.join(LOG_DIR, "onlyvips_json_{time}.jsonl")

# Loguru temel ayarları - Sıfırlama ve tekrar yapılandırma
logger.remove()

# Standart formatı konsol için ekle
logger.add(
    sys.stderr,
    format="<level>{level}</level> <green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True,
)

# JSON formatı için fonksiyon
def json_formatter(record: Dict[str, Any]) -> str:
    """
    Loguru kayıtlarını JSON formatına dönüştürür
    """
    log_record = {
        "timestamp": record["time"].strftime("%Y-%m-%d %H:%M:%S.%f"),
        "level": record["level"].name,
        "message": record["message"],
        "name": record["name"],
        "function": record["function"],
        "line": record["line"],
        "process_id": record["process"].id,
    }
    
    # Exception bilgisi
    if record["exception"]:
        log_record["exception"] = {
            "type": record["exception"].type,
            "value": str(record["exception"].value),
            "traceback": record["exception"].traceback,
        }
    
    # Ek veri varsa
    if "extra" in record and record["extra"]:
        for key, value in record["extra"].items():
            if key not in log_record:
                log_record[key] = value
    
    return json.dumps(log_record, ensure_ascii=False)

# JSON logları dosyaya yazma
logger.add(
    JSON_LOG_FILE_PATH,
    format=json_formatter,
    level="INFO",
    rotation="1 day",
    retention="7 days",
    compression="gz",
    serialize=True,
)

# Normal dosya logları
logger.add(
    LOG_FILE_PATH,
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}",
    level="DEBUG",
    rotation="1 day",
    retention="7 days",
    compression="gz",
)

def get_logger(name: str = "onlyvips"):
    """
    Modül adıyla yapılandırılmış logger döndürür
    """
    return logger.bind(name=name)

# Ana logger
app_logger = get_logger("app")
api_logger = get_logger("api")
db_logger = get_logger("db") 