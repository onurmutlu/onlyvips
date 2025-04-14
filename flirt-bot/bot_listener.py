#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OnlyVips Bot Listener - Görev doğrulama botu
Bu bot, kullanıcıların gerçekleştirdiği görevleri otomatik olarak doğrular.
Telethon kütüphanesi kullanılarak geliştirilmiştir.
"""

import os
import json
import asyncio
import logging
import time
import re
import requests
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import MessageEntityUrl, MessageEntityTextUrl, ChannelParticipantAdmin, ChannelParticipantCreator
from telethon.tl.functions.channels import GetParticipantRequest
from dotenv import load_dotenv

# Loglama
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# .env dosyasını yükle
load_dotenv()

# API ve bot bilgileri
API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
SESSION_STRING = os.getenv("SESSION_STRING")
BOT_USERNAME = os.getenv("BOT_USERNAME", "OnlyVipsBot")
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")
ADMIN_KEY = os.getenv("ADMIN_KEY", "your-secret-admin-key")

# Görev doğrulama listesi
VERIFICATION_TYPES = {
    "message_forward": "dm_messages", 
    "bot_mention": "group_mentions",
    "pin_check": "pinned_messages",
    "post_share": "shared_posts",
    "share_count": "forward_count",
    "referral": "joined_users",
    "invite_tracker": "invited_users",
    "deeplink_track": "link_clicks"
}

# Bot client'ını oluştur
if SESSION_STRING:
    # Kullanıcı hesabıyla oturum açma (tüm mesajları görmek için)
    bot = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
else:
    # Sadece bot tokenı ile oturum açma (sınırlı erişim)
    bot = TelegramClient("bot_session", API_ID, API_HASH)

class TaskVerifier:
    def __init__(self, api_url, admin_key):
        self.api_url = api_url
        self.admin_key = admin_key
        self.cache = {}
        self.last_check = 0
        
    async def get_pending_tasks(self):
        """Backend API'den bekleyen görevleri al"""
        try:
            # Saniyede bir kereden fazla kontrol etme
            current_time = time.time()
            if current_time - self.last_check < 1:
                return self.cache.get("pending_tasks", {})
                
            response = requests.get(
                f"{self.api_url}/admin/pending-verifications",
                params={"admin_key": self.admin_key}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.cache["pending_tasks"] = data.get("pending_verifications", {})
                self.last_check = current_time
                return self.cache["pending_tasks"]
            else:
                logger.error(f"API hatası: {response.status_code} - {response.text}")
                return {}
        except Exception as e:
            logger.error(f"Bekleyen görevler alınırken hata: {e}")
            return {}
    
    async def verify_task(self, user_id, task_id, verified=True):
        """Görevi doğrula"""
        try:
            response = requests.post(
                f"{self.api_url}/admin/verify-task",
                json={
                    "user_id": user_id,
                    "task_id": task_id,
                    "verified": verified,
                    "admin_key": self.admin_key
                }
            )
            
            if response.status_code == 200:
                logger.info(f"Görev doğrulandı: {user_id} için görev {task_id}")
                return True
            else:
                logger.error(f"Görev doğrulama hatası: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Görev doğrulanırken hata: {e}")
            return False

verifier = TaskVerifier(BACKEND_API_URL, ADMIN_KEY)

@bot.on(events.NewMessage(pattern=f"^/start"))
async def start_command(event):
    """Başlangıç komutu"""
    await event.respond("👋 Merhaba! Ben OnlyVips görev doğrulama botuyum. Görevlerinizi tamamladığınızda otomatik olarak kontrol edeceğim.")

@bot.on(events.NewMessage(incoming=True, chats="me"))
async def check_dm_messages(event):
    """DM mesajlarını kontrol et - message_forward doğrulaması için"""
    # Görev doğrulama türü: message_forward
    try:
        sender = await event.get_sender()
        user_id = str(sender.id)
        
        # Bekleyen görevleri kontrol et
        pending_tasks = await verifier.get_pending_tasks()
        
        for key, task in pending_tasks.items():
            task_user_id, task_id = key.split("_")
            
            # Kullanıcı ID'si eşleşiyor mu ve message_forward türünde bir görev mi?
            if task_user_id == user_id and task["verification_type"] == "message_forward":
                # Görevi doğrula
                await verifier.verify_task(user_id, task_id)
                await event.respond("✅ Tanıtım mesajı gönderme göreviniz doğrulandı ve ödülünüz verildi!")
    except Exception as e:
        logger.error(f"DM mesaj kontrolünde hata: {e}")

@bot.on(events.NewMessage(incoming=True, pattern=rf".*@{BOT_USERNAME}.*"))
async def check_bot_mentions(event):
    """Bot mentionlarını kontrol et - bot_mention doğrulaması için"""
    # Görev doğrulama türü: bot_mention
    try:
        sender = await event.get_sender()
        user_id = str(sender.id)
        
        # Bekleyen görevleri kontrol et
        pending_tasks = await verifier.get_pending_tasks()
        
        for key, task in pending_tasks.items():
            task_user_id, task_id = key.split("_")
            
            # Kullanıcı ID'si eşleşiyor mu ve bot_mention türünde bir görev mi?
            if task_user_id == user_id and task["verification_type"] == "bot_mention":
                # Grup mesajı mı kontrol et (özel mesaj değil)
                if event.is_group or event.is_channel:
                    # Görevi doğrula
                    await verifier.verify_task(user_id, task_id)
                    await event.reply("✅ Bot etiketleme göreviniz doğrulandı ve ödülünüz verildi!")
    except Exception as e:
        logger.error(f"Bot mention kontrolünde hata: {e}")

@bot.on(events.ChatAction())
async def check_pin_messages(event):
    """Sabitlenmiş mesajları kontrol et - pin_check doğrulaması için"""
    # Görev doğrulama türü: pin_check
    try:
        if event.action_message and event.action_message.pinned:
            # Mesajı sabitleyen kişiyi bul
            if event.is_group or event.is_channel:
                chat = await event.get_chat()
                sender = await event.get_sender()
                
                # Grup yöneticisi mi kontrol et
                try:
                    participant = await bot(GetParticipantRequest(chat.id, sender.id))
                    admin_rights = isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator))
                    
                    if admin_rights:
                        user_id = str(sender.id)
                        
                        # Bekleyen görevleri kontrol et
                        pending_tasks = await verifier.get_pending_tasks()
                        
                        for key, task in pending_tasks.items():
                            task_user_id, task_id = key.split("_")
                            
                            # Kullanıcı ID'si eşleşiyor mu ve pin_check türünde bir görev mi?
                            if task_user_id == user_id and task["verification_type"] == "pin_check":
                                # Görevi doğrula
                                await verifier.verify_task(user_id, task_id)
                except:
                    pass
    except Exception as e:
        logger.error(f"Pin kontrolünde hata: {e}")

@bot.on(events.NewMessage(incoming=True))
async def check_post_shares(event):
    """Gönderi paylaşımlarını kontrol et - post_share doğrulaması için"""
    # Görev doğrulama türü: post_share
    try:
        if event.forward:
            sender = await event.get_sender()
            user_id = str(sender.id)
            
            # Bekleyen görevleri kontrol et
            pending_tasks = await verifier.get_pending_tasks()
            
            for key, task in pending_tasks.items():
                task_user_id, task_id = key.split("_")
                
                # Kullanıcı ID'si eşleşiyor mu ve post_share türünde bir görev mi?
                if task_user_id == user_id and task["verification_type"] == "post_share":
                    # Grup mesajı mı kontrol et
                    if event.is_group or event.is_channel:
                        # Görevi doğrula
                        await verifier.verify_task(user_id, task_id)
    except Exception as e:
        logger.error(f"Post share kontrolünde hata: {e}")

@bot.on(events.NewMessage(pattern=r"https?://[^\s]+"))
async def check_link_clicks(event):
    """Link tıklamalarını kontrol et - deeplink_track doğrulaması için"""
    # Görev doğrulama türü: deeplink_track
    try:
        message = event.message
        # Link içeren mesajsa
        if message.entities:
            for entity in message.entities:
                if isinstance(entity, (MessageEntityUrl, MessageEntityTextUrl)):
                    url = message.text[entity.offset:entity.offset + entity.length]
                    # OnlyVips linki içeriyor mu?
                    if "onlyvips.com" in url or "t.me/OnlyVips" in url:
                        sender = await event.get_sender()
                        user_id = str(sender.id)
                        
                        # Bekleyen görevleri kontrol et
                        pending_tasks = await verifier.get_pending_tasks()
                        
                        for key, task in pending_tasks.items():
                            task_user_id, task_id = key.split("_")
                            
                            # Kullanıcı ID'si eşleşiyor mu ve deeplink_track türünde bir görev mi?
                            if task_user_id == user_id and task["verification_type"] == "deeplink_track":
                                # Görevi doğrula
                                await verifier.verify_task(user_id, task_id)
    except Exception as e:
        logger.error(f"Link kontrolünde hata: {e}")

@bot.on(events.ChatAction(func=lambda e: e.user_joined))
async def check_user_joined(event):
    """Kullanıcı katılımını kontrol et - referral doğrulaması için"""
    # Görev doğrulama türü: referral ve invite_tracker
    try:
        # Yeni katılan kullanıcı
        joined_user = await event.get_user()
        joined_user_id = str(joined_user.id)
        
        # Katıldığı grubu al
        chat = await event.get_chat()
        
        # Son 10 mesajı kontrol et ve davet eden kişiyi bul
        async for message in bot.iter_messages(chat.id, limit=10):
            if message.action and hasattr(message.action, 'users') and joined_user_id in [str(u) for u in message.action.users]:
                if hasattr(message, 'from_id') and message.from_id:
                    inviter_id = str(message.from_id.user_id)
                    
                    # Bekleyen görevleri kontrol et
                    pending_tasks = await verifier.get_pending_tasks()
                    
                    for key, task in pending_tasks.items():
                        task_user_id, task_id = key.split("_")
                        
                        # Davet eden kişi için referral görevini doğrula
                        if task_user_id == inviter_id and task["verification_type"] in ["referral", "invite_tracker"]:
                            await verifier.verify_task(inviter_id, task_id)
    except Exception as e:
        logger.error(f"Kullanıcı katılım kontrolünde hata: {e}")

@bot.on(events.NewMessage(pattern=f"^/verify (\d+) (\d+)$"))
async def admin_verify(event):
    """Admin manuel doğrulama komutu"""
    # Sadece yetkili kişiler kullanabilir
    sender = await event.get_sender()
    admin_ids = os.getenv("ADMIN_IDS", "").split(",")
    
    if str(sender.id) not in admin_ids:
        return
    
    try:
        args = event.pattern_match.group(1, 2)
        user_id, task_id = args
        
        # Görevi doğrula
        result = await verifier.verify_task(user_id, task_id)
        
        if result:
            await event.respond(f"✅ Görev {task_id} başarıyla doğrulandı (Kullanıcı: {user_id})")
        else:
            await event.respond(f"❌ Görev doğrulama başarısız (Kullanıcı: {user_id}, Görev: {task_id})")
    except Exception as e:
        await event.respond(f"Hata: {str(e)}")

async def main():
    """Ana fonksiyon - botu başlat"""
    if SESSION_STRING:
        await bot.start()
    else:
        await bot.start(bot_token=BOT_TOKEN)
    
    logger.info("Bot dinlemeye başladı...")
    
    # Botun devamlı çalışması için
    await bot.run_until_disconnected()

if __name__ == "__main__":
    # Botu başlat
    asyncio.run(main()) 