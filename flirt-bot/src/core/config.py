#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Config Module - Yapılandırma modülü
Bu modül .env dosyasından yapılandırma yüklemeyi sağlar
"""

import os
import logging
from dotenv import load_dotenv
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Config:
    """Bot yapılandırma sınıfı"""
    API_ID: str
    API_HASH: str
    BOT_TOKEN: str
    SESSION_STRING: str
    BOT_USERNAME: str
    BACKEND_API_URL: str
    ADMIN_KEY: str
    OPENAI_API_KEY: str
    OPENAI_MODEL: str
    GPT_MAX_USAGE_DAY: int
    GPT_MAX_TOKENS: int
    ADMIN_IDS: list

def load_config() -> Config:
    """Yapılandırma yükle"""
    # .env dosyasını yükle
    load_dotenv()
    
    # API ve bot bilgileri
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")
    bot_token = os.getenv("BOT_TOKEN")
    session_string = os.getenv("SESSION_STRING", "")
    bot_username = os.getenv("BOT_USERNAME", "OnlyVipsBot")
    backend_api_url = os.getenv("BACKEND_API_URL", "http://localhost:8000")
    admin_key = os.getenv("ADMIN_KEY", "your-secret-admin-key")
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo-instruct")
    gpt_max_usage_day = int(os.getenv("GPT_MAX_USAGE_DAY", "50"))
    gpt_max_tokens = int(os.getenv("GPT_MAX_TOKENS", "250"))
    
    # Admin ID'leri
    admin_ids_str = os.getenv("ADMIN_IDS", "")
    admin_ids = [id.strip() for id in admin_ids_str.split(",") if id.strip()]
    
    # Yapılandırma değerlerini kontrol et
    if not all([api_id, api_hash, bot_token]):
        logger.error("API_ID, API_HASH ve BOT_TOKEN değerleri gereklidir.")
        raise ValueError("Gerekli yapılandırma değerleri eksik.")
    
    # Config sınıfı döndür
    return Config(
        API_ID=api_id,
        API_HASH=api_hash,
        BOT_TOKEN=bot_token,
        SESSION_STRING=session_string,
        BOT_USERNAME=bot_username,
        BACKEND_API_URL=backend_api_url,
        ADMIN_KEY=admin_key,
        OPENAI_API_KEY=openai_api_key,
        OPENAI_MODEL=openai_model,
        GPT_MAX_USAGE_DAY=gpt_max_usage_day,
        GPT_MAX_TOKENS=gpt_max_tokens,
        ADMIN_IDS=admin_ids
    ) 