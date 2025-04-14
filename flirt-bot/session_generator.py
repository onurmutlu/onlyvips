#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Session String Generator
Telegram kullanıcı hesabı için StringSession oluşturan yardımcı script.
Bunu sadece bir kez çalıştırın ve oluşturulan session string'i .env dosyasına ekleyin.
"""

import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# API bilgilerini al
API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")

async def main():
    # Kullanıcıyı bilgilendir
    print("""
    ======================================
    TELETHON STRING SESSION GENERATOR
    ======================================
    Bu script, görev doğrulama botu için kullanıcı oturumu oluşturur.
    
    1. Telefon numaranızı girin (+90 ile başlayan format)
    2. Telegram'dan gelen kodu girin
    3. İki faktörlü doğrulama varsa şifrenizi girin
    4. Oluşturulan session string'i kopyalayıp .env dosyasındaki SESSION_STRING değişkenine yapıştırın
    """)
    
    if not API_ID or not API_HASH:
        print("HATA: API_ID ve API_HASH değerlerini .env dosyasında ayarlamalısınız.")
        print("https://my.telegram.org/apps adresinden alabilirsiniz.")
        return
    
    # Yeni bir client oluştur
    async with TelegramClient(StringSession(), API_ID, API_HASH) as client:
        # String session'ı oluştur
        session_str = client.session.save()
        
        print("\n======================================")
        print("İŞTE SESSION STRING (kopyalayın):")
        print("======================================\n")
        print(session_str)
        print("\n======================================")
        print("Bu string'i .env dosyasındaki SESSION_STRING değişkenine yapıştırın.")
        print("ÖNEMLİ: Bu string'i kimseyle paylaşmayın, hesabınıza tam erişim sağlar!")
        print("======================================")

if __name__ == "__main__":
    asyncio.run(main()) 