#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Flirt Bot sağlık kontrolü.
Bu script bot servisinin sağlık durumunu kontrol eder.
"""

import os
import sys
import time
import logging
from pathlib import Path

# Kontrol edilecek dosyalar
BOT_PID_FILE = "bot.pid"
LAST_ALIVE_FILE = "logs/last_alive.txt"

def check_bot_health():
    """Bot sağlık durumunu kontrol et"""
    
    # 1. Bot PID kontrolü
    if os.path.exists(BOT_PID_FILE):
        try:
            with open(BOT_PID_FILE, "r") as f:
                pid = int(f.read().strip())
            
            # Linux'ta process kontrolü
            if os.name == "posix" and os.path.exists(f"/proc/{pid}"):
                return True
        except (ValueError, FileNotFoundError):
            pass
    
    # 2. Son aktif zaman kontrolü
    if os.path.exists(LAST_ALIVE_FILE):
        try:
            last_time = os.path.getmtime(LAST_ALIVE_FILE)
            current_time = time.time()
            
            # Son 5 dakika içinde aktif olmuş mu?
            if current_time - last_time < 300:  # 5 dakika
                return True
        except:
            pass
    
    # 3. Son log kontrolü
    log_dir = Path("logs")
    if log_dir.exists():
        log_files = list(log_dir.glob("*.log"))
        if log_files:
            newest_log = max(log_files, key=os.path.getmtime)
            last_modified = os.path.getmtime(newest_log)
            
            # Son 10 dakika içinde log yazılmış mı?
            if time.time() - last_modified < 600:  # 10 dakika
                return True
    
    return False

if __name__ == "__main__":
    if check_bot_health():
        print("Bot sağlıklı çalışıyor.")
        sys.exit(0)
    else:
        print("Bot yanıt vermiyor!")
        sys.exit(1) 