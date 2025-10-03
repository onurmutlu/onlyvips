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
import random
import datetime
import requests
import math
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import MessageEntityUrl, MessageEntityTextUrl, ChannelParticipantAdmin, ChannelParticipantCreator
from telethon.tl.functions.channels import GetParticipantRequest
from dotenv import load_dotenv
from openai import OpenAI
import sys
from typing import Dict, List, Optional, Any, Union

# Secrets provider modülünü içe aktar
sys.path.append('../backend-api')  # app.core'u erişilebilir yap
try:
    from app.core.secrets_provider import get_secret_provider, SecretBackendType
    # Yapılandırmaya göre uygun secret provider'ı al
    secrets = get_secret_provider(os.getenv("SECRET_PROVIDER", SecretBackendType.ENV))
except ImportError:
    # Eğer import başarısız olursa varsayılan olarak ortam değişkenlerini kullan
    logging.warning("Secret provider modülü bulunamadı, ortam değişkenleri kullanılacak")
    from dotenv import load_dotenv
    load_dotenv()
    
    # Basit bir env-based secret provider
    class EnvSecrets:
        def get_secret(self, key: str, default: Optional[Any] = None) -> Any:
            return os.getenv(key, default)
    
    secrets = EnvSecrets()

# JSON formatında loglama modülünü içe aktar
from src.utils.json_logger import bot_logger, api_logger, task_logger, metrics

# Telethon ve diğer bağımlılıkları içe aktar
from telethon import TelegramClient, events
from telethon.tl.types import User, Message, Channel, Chat
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.channels import JoinChannelRequest

# Secret değerlerini yeni secret provider ile al
API_ID = secrets.get_secret("TELEGRAM_API_ID")
API_HASH = secrets.get_secret("TELEGRAM_API_HASH")
BOT_TOKEN = secrets.get_secret("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = secrets.get_secret("OPENAI_API_KEY")

# Yapılandırmaları kontrol et
if not API_ID or not API_HASH or not BOT_TOKEN:
    bot_logger.error("Telegram API kimlik bilgileri bulunamadı", 
                    missing_configs=["TELEGRAM_API_ID", "TELEGRAM_API_HASH", "TELEGRAM_BOT_TOKEN"])
    sys.exit(1)

# OpenAI API anahtarını kontrol et
if not OPENAI_API_KEY:
    bot_logger.warning("OpenAI API anahtarı bulunamadı", features_disabled=["AI"])

# Diğer yapılandırma değerlerini secret provider üzerinden al
BACKEND_API_URL = secrets.get_secret("BACKEND_API_URL", "http://localhost:8000")

# Log ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("flirt-bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# .env dosyasını yükle
load_dotenv()

# API ve bot bilgileri
API_ID = API_ID
API_HASH = API_HASH
BOT_TOKEN = BOT_TOKEN
SESSION_STRING = secrets.get_secret("SESSION_STRING")
BOT_USERNAME = secrets.get_secret("BOT_USERNAME", "OnlyVipsBot")
ADMIN_KEY = secrets.get_secret("ADMIN_KEY", "your-secret-admin-key")
OPENAI_MODEL = secrets.get_secret("OPENAI_MODEL", "gpt-3.5-turbo-instruct")  # Daha ucuz model
GPT_MAX_USAGE_DAY = int(secrets.get_secret("GPT_MAX_USAGE_DAY", "50"))  # Günlük maksimum kullanım
GPT_MAX_TOKENS = int(secrets.get_secret("GPT_MAX_TOKENS", "250"))  # Maksimum token sayısı

# OpenAI API istemcisi oluştur
if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    gpt_usage_count = {}  # Kullanıcı ID'si bazında günlük kullanım sayısı
    gpt_usage_date = datetime.datetime.now().date()  # Kullanım tarihini izleme
else:
    openai_client = None
    logger.warning("OPENAI_API_KEY bulunamadı, GPT entegrasyonu devre dışı.")

# Görev doğrulama listesi - Backend ile uyumlu
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

# ------- TELEGRAMDAN MİNİAPP'E YÖNLENDİRME ------

async def send_miniapp_button(event, text="OnlyVips görevlerine Telegram MiniApp üzerinden de erişebilirsiniz:"):
    """Kullanıcıya MiniApp butonu gönder"""
    from telethon import Button
    
    try:
        # Derin bağlantı parametresi ile kullanıcıyı tanıma
        sender = await event.get_sender()
        user_id = str(sender.id)
        miniapp_url = f"https://t.me/{BOT_USERNAME}/app?startapp={user_id}"
        
        # Telegram MiniApp butonu
        await event.respond(
            text,
            buttons=[
                Button.url("🚀 OnlyVips MiniApp", miniapp_url)
            ]
        )
    except Exception as e:
        logger.error(f"MiniApp butonu gönderilemedi: {e}")
        await event.respond("MiniApp'e erişmek için @OnlyVipsBot'u ziyaret edin ve başlatın.")

@bot.on(events.NewMessage(pattern=f"^/start"))
async def start_command(event):
    """Başlangıç komutu"""
    await event.respond("👋 Merhaba! Ben OnlyVips görev doğrulama botuyum. Görevlerinizi tamamladığınızda otomatik olarak kontrol edeceğim.\n\n"
                      "📝 /gorev - Yeni bir görev al\n"
                      "📋 /gorevlerim - Tüm görevlerini görüntüle\n"
                      "💬 /flort - Flört ipuçları al\n"
                      "❓ /yardim - Yardım menüsünü görüntüle")
    
    # MiniApp butonunu da gönder
    await send_miniapp_button(event)

@bot.on(events.NewMessage(pattern=f"^/help|^/yardim"))
async def help_command(event):
    """Yardım komutu"""
    help_text = """**📚 OnlyVips Bot Komutları**

**Temel Komutlar:**
/start - Botu başlat
/yardim - Bu menüyü göster

**Görev Komutları:**
/gorev - Yeni bir görev al
/gorevlerim - Tüm görevlerini görüntüle
/gunluk - Günlük görev al

**Flört Yardımcısı:**
/flort - Flört için ipuçları al
/agent [soru] - Flört asistanı ile konuş
/flortcoach [soru] - Flört koçundan tavsiye al

**Diğer Komutlar:**
/profil - Profil bilgilerinizi görüntüle
/rozet - Sahip olduğunuz rozetleri görüntüle
/match - Benzer ilgi alanlarına sahip kişileri bul (yakında)

Görevleri tamamlayarak XP ve özel rozetler kazanabilirsiniz! 🏆"""
    await event.respond(help_text)

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
                verification_result = await verifier.verify_task(user_id, task_id)
                
                if verification_result:
                    # Görevin tamamlandığını bildiren bir mesaj gönder
                    task_details = None
                    all_tasks = await get_all_tasks()
                    for t in all_tasks:
                        if str(t["id"]) == task_id:
                            task_details = t
                            break
                    
                    if task_details:
                        reward_text = task_details.get("reward", "ödül")
                        await event.respond(f"✅ \"{task_details['title']}\" göreviniz doğrulandı! {reward_text} kazandınız.")
                    else:
                        await event.respond("✅ Tanıtım mesajı gönderme göreviniz doğrulandı ve ödülünüz verildi!")
                    
                    # Kullanıcıya MiniApp butonunu gönder
                    await send_miniapp_button(event, "Görev durumunuzu ve daha fazla görevi MiniApp üzerinden takip edebilirsiniz:")
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
                    verification_result = await verifier.verify_task(user_id, task_id)
                    
                    if verification_result:
                        # Görev tamamlandı mesajı
                        await event.reply("✅ Bot etiketleme göreviniz doğrulandı ve ödülünüz verildi!")
                        
                        # MiniApp üzerinden görevin durumunu takip etmesi için yönlendirme ekle
                        try:
                            # DM olarak MiniApp butonunu gönder
                            from telethon import Button
                            miniapp_url = f"https://t.me/{BOT_USERNAME}/app?startapp={user_id}"
                            await bot.send_message(
                                user_id, 
                                "🎉 Göreviniz tamamlandı! Daha fazla görev ve ödül için MiniApp'i ziyaret edin:",
                                buttons=[Button.url("🚀 OnlyVips MiniApp", miniapp_url)]
                            )
                        except Exception as e:
                            logger.error(f"MiniApp DM gönderilemedi: {e}")
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
                            verification_result = await verifier.verify_task(inviter_id, task_id)
                            
                            if verification_result:
                                try:
                                    # Davet eden kişiye DM ile bildirim gönder
                                    await bot.send_message(
                                        inviter_id,
                                        f"🎉 Tebrikler! '{joined_user.first_name}' kullanıcısını davet ederek görevinizi tamamladınız ve ödülünüz verildi."
                                    )
                                    
                                    # MiniApp butonunu da gönder
                                    await send_miniapp_button(
                                        inviter_id, 
                                        "Görev durumunuzu ve daha fazla görevi MiniApp üzerinden takip edebilirsiniz:"
                                    )
                                except Exception as e:
                                    logger.error(f"Davet eden kişiye DM gönderilemedi: {e}")
    except Exception as e:
        logger.error(f"Kullanıcı katılım kontrolünde hata: {e}")

@bot.on(events.NewMessage(pattern=f"^/verify (\d+) (\d+)$"))
async def admin_verify(event):
    """Admin manuel doğrulama komutu"""
    # Sadece yetkili kişiler kullanabilir
    sender = await event.get_sender()
    admin_ids = secrets.get_secret("ADMIN_IDS", "").split(",")
    
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

# ---------- YENİ EKLENMİŞ GÖREV VE AGENT FONKSİYONLARI ---------- #

def get_user_profile(user_id):
    """Backend API'den kullanıcı profilini al"""
    try:
        response = requests.get(f"{BACKEND_API_URL}/profile/{user_id}")
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            # Kullanıcı yoksa yeni oluştur
            logger.info(f"Kullanıcı {user_id} bulunamadı, yeni kayıt oluşturuluyor")
            create_response = requests.post(
                f"{BACKEND_API_URL}/profile/create",
                json={"user_id": user_id}
            )
            if create_response.status_code == 200:
                return create_response.json()
        return None
    except Exception as e:
        logger.error(f"Kullanıcı profili alınırken hata: {e}")
        return None

async def get_all_tasks():
    """Tüm görevleri getir"""
    try:
        response = requests.get(f"{BACKEND_API_URL}/tasks/list")
        if response.status_code == 200:
            return response.json().get("tasks", [])
        return []
    except Exception as e:
        logger.error(f"Görevler alınırken hata: {e}")
        return []

def get_available_tasks(user_id):
    """Kullanıcı için uygun görevleri getir"""
    try:
        # Tüm görevleri al
        response = requests.get(f"{BACKEND_API_URL}/tasks/list")
        if response.status_code != 200:
            return []
            
        all_tasks = response.json().get("tasks", [])
        
        # Kullanıcı profilini al
        user_profile = get_user_profile(user_id)
        if not user_profile:
            return all_tasks
            
        # Tamamlanmış görevleri filtrele
        completed_tasks = user_profile.get("completed_tasks", [])
        pending_tasks = user_profile.get("pending_tasks", [])
        
        # Tamamlanmamış görevleri döndür
        return [task for task in all_tasks if task["id"] not in completed_tasks and task["id"] not in pending_tasks]
    except Exception as e:
        logger.error(f"Görevler alınırken hata: {e}")
        return []

def complete_task_api(user_id, task_id, verification_data=None):
    """Backend API'ye görev tamamlama isteği gönder"""
    try:
        if not verification_data:
            verification_data = {}
            
        response = requests.post(
            f"{BACKEND_API_URL}/task/complete",
            json={
                "user_id": user_id,
                "task_id": task_id,
                "verification_data": verification_data
            }
        )
        
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        logger.error(f"Görev tamamlama API hatası: {e}")
        return None

def has_received_daily_task(user_id):
    """Kullanıcının bugün görev alıp almadığını kontrol et"""
    try:
        today_date = datetime.datetime.now().strftime("%Y-%m-%d")
        response = requests.get(
            f"{BACKEND_API_URL}/daily-task/check/{user_id}",
            params={"date": today_date}
        )
        if response.status_code == 200:
            return response.json().get("has_received", False)
        return False
    except Exception as e:
        logger.error(f"Günlük görev kontrolünde hata: {e}")
        return False

def set_daily_task(user_id, task):
    """Kullanıcıya günlük görev ata"""
    try:
        today_date = datetime.datetime.now().strftime("%Y-%m-%d")
        response = requests.post(
            f"{BACKEND_API_URL}/daily-task/set",
            json={
                "user_id": user_id,
                "date": today_date,
                "task": task
            }
        )
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Günlük görev atama hatası: {e}")
        return False

@bot.on(events.NewMessage(pattern=f"^/gorev$"))
async def task_command(event):
    """Kullanıcıya yeni görev ver"""
    sender = await event.get_sender()
    user_id = str(sender.id)
    
    # Kullanıcının mevcut görevlerini kontrol et
    available_tasks = get_available_tasks(user_id)
    
    if not available_tasks:
        await event.respond("Şu anda tüm görevleri tamamlamışsın! Yeni görevler yakında eklenecek.")
        
        # MiniApp butonunu gönder
        await send_miniapp_button(event, "Yeni görevlere MiniApp üzerinden de göz atabilirsiniz:")
        return
    
    # Rastgele bir görev seç
    task = random.choice(available_tasks)
    
    # Flört temalı görev mesajları
    flirt_intros = [
        "💘 Bugünkü flört görevin:",
        "❤️ Yeni bir macera seni bekliyor:",
        "💋 İşte senin için özel bir görev:",
        "🔥 Sosyal becerilerini gösterme zamanı:"
    ]
    
    # Doğrulama gerektiren bir görev ise, bu konuda bilgilendir
    verification_info = ""
    if task.get("verification_required", True):
        verification_type = task.get("verification_type", "")
        verification_info = f"\n\n🔍 Bu görev '{get_verification_text(verification_type)}' gerektiriyor."
    
    await event.respond(f"{random.choice(flirt_intros)}\n\n**{task['title']}**\n\nÖdül: {task['reward']}{verification_info}\n\nGörevi tamamladığında bot otomatik olarak kontrol edecek ve ödülünü verecek! Eğer doğrulama gerekiyorsa, bir süre beklemen gerekebilir.")
    
    # Doğrulama türüne göre ipucu ver
    verification_type = task.get("verification_type", "")
    if verification_type in VERIFICATION_TYPES:
        if verification_type == "message_forward":
            await event.respond("💡 **İpucu:** Bu görevi tamamlamak için bana doğrudan mesaj gönder.")
        elif verification_type == "bot_mention":
            await event.respond("💡 **İpucu:** Bu görevi tamamlamak için beni bir grupta etiketle.")
        elif verification_type == "pin_check":
            await event.respond("💡 **İpucu:** Bu görevi tamamlamak için bir mesajı bir grupta sabitle.")
        elif verification_type == "deeplink_track":
            await event.respond(f"💡 **İpucu:** Bu görevi tamamlamak için https://t.me/{BOT_USERNAME} linkini bir grupta paylaş.")

# Doğrulama türünü anlaşılır metne çevir
def get_verification_text(verification_type):
    """Doğrulama türünü anlaşılır metne çevir - MiniApp ile uyumlu"""
    texts = {
        "invite_tracker": "Davet bağlantısı takibi",
        "message_forward": "Mesaj yönlendirme kontrolü",
        "bot_mention": "Bot etiketleme kontrolü",
        "deeplink_track": "Link tıklanma takibi",
        "pin_check": "Sabitlenmiş mesaj kontrolü",
        "post_share": "Gönderi paylaşım kontrolü",
        "share_count": "Paylaşım sayısı kontrolü",
        "referral": "Referans bağlantısı takibi"
    }
    
    return texts.get(verification_type, "Manuel doğrulama")

@bot.on(events.NewMessage(pattern=f"^/miniapp$"))
async def miniapp_command(event):
    """MiniApp'e yönlendirme komutu"""
    await send_miniapp_button(event, "OnlyVips MiniApp'e buradan erişebilirsiniz:")

@bot.on(events.NewMessage(pattern=f"^/gorevlerim$"))
async def my_tasks(event):
    """Kullanıcının görevlerini listele"""
    sender = await event.get_sender()
    user_id = str(sender.id)
    
    user_profile = get_user_profile(user_id)
    if not user_profile:
        await event.respond("Profil bilgilerinize erişilemedi. Lütfen daha sonra tekrar deneyin.")
        return
    
    completed_tasks = user_profile.get("completed_tasks", [])
    pending_tasks = user_profile.get("pending_tasks", [])
    
    all_tasks = await get_all_tasks()
    
    # Tamamlanan görevler
    completed_message = "✅ **Tamamlanan Görevler**\n"
    completed_count = 0
    for task_id in completed_tasks:
        task = next((t for t in all_tasks if t["id"] == task_id), None)
        if task:
            completed_message += f"- {task['title']} ({task['reward']})\n"
            completed_count += 1
    
    if completed_count == 0:
        completed_message += "Henüz tamamlanmış görevin yok.\n"
    
    # Bekleyen görevler
    pending_message = "\n⏳ **Doğrulama Bekleyen Görevler**\n"
    pending_count = 0
    for task_id in pending_tasks:
        task = next((t for t in all_tasks if t["id"] == task_id), None)
        if task:
            pending_message += f"- {task['title']} ({task['reward']})\n"
            pending_count += 1
    
    if pending_count == 0:
        pending_message += "Doğrulama bekleyen görevin yok.\n"
    
    # Yapılabilecek görevler
    available_tasks = [t for t in all_tasks if t["id"] not in completed_tasks and t["id"] not in pending_tasks]
    available_message = f"\n🔍 **Yapabileceğin {len(available_tasks)} Görev**\n"
    
    for i, task in enumerate(available_tasks[:5]):  # En fazla 5 görev göster
        available_message += f"{i+1}. {task['title']} ({task['reward']})\n"
    
    if len(available_tasks) > 5:
        available_message += f"...ve {len(available_tasks)-5} görev daha!\n"
    
    if len(available_tasks) == 0:
        available_message += "Tüm görevleri tamamladın! Tebrikler! 🎉\n"
    
    await event.respond(f"{completed_message}\n{pending_message}\n{available_message}\n\nYeni görev almak için: /gorev")
    
    # MiniApp butonunu gönder
    await send_miniapp_button(event, "Görevlerinizi daha detaylı görüntülemek için MiniApp'i kullanabilirsiniz:")

@bot.on(events.NewMessage(pattern=f"^/flirt$"))
async def flirt_command(event):
    """Flört ipucu ve görevleri ver"""
    tip = random.choice(FLIRT_TIPS)
    
    flirt_tasks = [
        "💕 Bugünkü görevin: Bir arkadaşına güzel bir iltifat et!",
        "👋 Yeni birine selam ver ve onunla tanış!",
        "🤗 Bir arkadaşınla özelden sohbet başlat ve ilgi alanlarını keşfet.",
        "🎭 Bir grupta aktif ol ve en az 3 mesaj gönder!",
        "🌟 Biriyle ortak ilgi alanları bul ve bu konuda sohbet et!"
    ]
    
    message = f"{tip}\n\n{random.choice(flirt_tasks)}"
    await event.respond(message)

@bot.on(events.NewMessage(pattern=f"^/profil$"))
async def profile_command(event):
    """Kullanıcı profilini göster"""
    sender = await event.get_sender()
    user_id = str(sender.id)
    
    user_profile = get_user_profile(user_id)
    if not user_profile:
        await event.respond("Profil bilgilerinize erişilemedi. Lütfen daha sonra tekrar deneyin.")
        return
    
    xp = user_profile.get("xp", 0)
    level = math.floor(xp / 100) + 1
    next_level_xp = (level * 100) - xp
    
    badges = user_profile.get("badges", [])
    badges_text = ", ".join(badges) if badges else "Henüz rozet kazanmadınız"
    
    completed_tasks = len(user_profile.get("completed_tasks", []))
    
    profile_text = f"""**👤 Kullanıcı Profili**

**🆔 ID:** {user_id}
**🌟 XP:** {xp}
**📊 Seviye:** {level}
**⏳ Sonraki seviyeye:** {next_level_xp} XP

**🎯 Tamamlanan Görevler:** {completed_tasks}
**🏅 Rozetler:** {badges_text}

Yeni görevler için /gorev komutunu kullanabilirsiniz.
"""
    await event.respond(profile_text)

@bot.on(events.NewMessage(pattern=f"^/rozet$"))
async def badge_command(event):
    """Kullanıcının rozetlerini göster"""
    sender = await event.get_sender()
    user_id = str(sender.id)
    
    user_profile = get_user_profile(user_id)
    if not user_profile:
        await event.respond("Profil bilgilerinize erişilemedi. Lütfen daha sonra tekrar deneyin.")
        return
    
    badges = user_profile.get("badges", [])
    
    if not badges:
        await event.respond("Henüz hiç rozet kazanmadınız. Görevleri tamamlayarak rozet kazanabilirsiniz!")
        return
    
    badges_text = "**🏅 Rozetleriniz**\n\n"
    for badge in badges:
        badges_text += f"• {badge}\n"
    
    badges_text += "\nDaha fazla rozet kazanmak için görevleri tamamlayın! /gorev"
    await event.respond(badges_text)

@bot.on(events.NewMessage(pattern=f"^/match$"))
async def match_command(event):
    """Kullanıcıya benzer ilgi alanlarına sahip kişileri öner"""
    sender = await event.get_sender()
    user_id = str(sender.id)
    
    await event.respond("💞 Eşleştirme sistemi henüz geliştirme aşamasında! Yakında burada benzer ilgi alanlarına sahip kişilerle tanışabileceksiniz.")

# ---------- GPT ENTEGRASYONU İLE AGENT FONKSİYONLARI ---------- #

# Hazır flört ipuçları ve önerileri
FLIRT_TIPS = [
    "😉 İltifat etmek karşındakini mutlu eder ve sohbeti başlatır!",
    "💬 Açık uçlu sorular sormak, sohbetin devam etmesini sağlar.",
    "🤔 Karşındakinin ilgi alanlarını öğrenmek için sorular sor!",
    "😊 Samimi ve doğal olmak her zaman en iyisidir.",
    "📱 Mesaj yazarken emoji kullanmak duygularını ifade etmene yardımcı olur!",
    "👂 İyi bir dinleyici olmak, iyi bir konuşmacı olmak kadar önemlidir.",
    "🎯 Ortak ilgi alanları bulmak sohbetin akışını kolaylaştırır.",
    "💌 Basit bir 'Nasılsın?' ile başlamak bile etkili olabilir.",
    "🔍 Karşındakinin profilinden ilgi alanlarını keşfedebilirsin.",
    "⏱️ Cevap verme süren çok hızlı veya çok yavaş olmasın.",
    "😎 İlk mesajında kendinden bahsetmekten çok karşındakiyle ilgilen.",
    "💭 Mesajlarında merak uyandıran sorular sor.",
    "🧠 Sadece dış görünüşle ilgili değil, düşünceleriyle de ilgilen.",
    "🔄 Sohbet akışını dengeli tut, sürekli konuşma veya hep dinleme.",
    "📸 Profilinde samimi ve doğal fotoğraflar kullan."
]

FLIRT_ADVICE = [
    "Sohbet başlatmak için karşındakinin profilindeki bir detaydan bahset.",
    "Kendinden emin ol ama kibirli görünme.",
    "Kendine özgü tarzını yansıt, herkes gibi olmaya çalışma.",
    "İlgilendiğin kişiye açık sorular sorarak sohbeti devam ettir.",
    "Karşındakine verdiğin değeri küçük jestlerle göster.",
    "Aşırıya kaçmadan mizah kullan, kendine gülebilmek çekici bir özelliktir.",
    "Kibarlık ve nezaket her zaman kazandırır.",
    "Doğal davran, olmadığın biri gibi davranma.",
    "Dinlemeyi ve anlamayı önemse, sohbeti tekelleştirme.",
    "Açık, samimi ve dürüst ol, kendini olduğun gibi göster.",
    "Karşındakinin mesajlarında anahtar kelimeleri fark et ve bunlarla ilgili sorular sor.",
    "Mesajlarına cevap verirken gecikme ama anında cevap verme zorunluluğu da hissetme.",
    "Bir hobi veya ilgi alanı hakkında konuşmaya davet et.",
    "Karşındakinin sohbette ne kadar rahat olduğuna dikkat et ve ona göre davran.",
    "Son mesajı sen yazma konusunda takıntılı olma, önemli olan kaliteli iletişim."
]

# Daha kapsamlı mesaj cevapları
FLIRT_RESPONSES = {
    "tanışma": [
        "Tanışma mesajlarında özgün ol. 'Merhaba, nasılsın?' yerine profilinden bir şey paylaş: 'Fotoğraflarına bakılırsa dağcılığı seviyorsun, en son nereye tırmandın?'",
        "İyi bir tanışma mesajı karşındakinin cevap vermesini kolaylaştırır. Soru sor ve merakını uyandır.",
        "İlk mesajında kendini kısaca tanıt ve ortak bir ilgi alanı bulmaya çalış."
    ],
    "sohbet": [
        "Sohbeti tek bir konuda tutma, farklı konulara geçiş yap. Böylece karşındakini daha iyi tanırsın.",
        "Mesajlarında karşındakinin söylediklerine referans ver. Bu, dinlediğini gösterir.",
        "Emoji kullanımı duygularını ifade etmene yardımcı olur, ama aşırıya kaçma."
    ],
    "buluşma": [
        "Buluşma teklif etmeden önce sohbetin iyi gittiğinden emin ol. Sonra basit ve net bir şekilde teklif et.",
        "İlk buluşmada hem rahat edebileceğiniz hem de konuşabileceğiniz bir yer seç.",
        "Buluşma öncesi kısa bir mesaj gönderip heyecanını paylaşmak iyi bir fikir."
    ],
    "özgüven": [
        "Özgüven çekicidir. Kendini sevdiğini ve değer verdiğini göster.",
        "Hatalarını kabul etmek ve onlarla dalga geçebilmek güçlü bir özgüven göstergesidir.",
        "Sürekli onay aramak yerine kendin ol ve fikirlerini açıkça ifade et."
    ],
    "red": [
        "Reddedilmek normaldir ve herkesin başına gelir. Kişisel algılama.",
        "Her reddedilme, doğru kişiyi bulmana bir adım daha yaklaştırır.",
        "Nazik ve anlayışlı bir şekilde cevap ver, kapıları tamamen kapatma."
    ]
}

# GPT kullanım sınırlarını kontrol et
def can_use_gpt(user_id):
    """Kullanıcının GPT kullanıp kullanamayacağını kontrol et"""
    # OpenAI API yoksa kullanılamaz
    if not openai_client:
        return False, "GPT entegrasyonu şu anda kullanılamıyor."
        
    # Şu anki tarihi kontrol et
    current_date = datetime.datetime.now().date()
    global gpt_usage_date, gpt_usage_count
    
    # Yeni gün başladıysa sayaçları sıfırla
    if current_date != gpt_usage_date:
        gpt_usage_count = {}
        gpt_usage_date = current_date
    
    # Kullanıcının günlük kullanım sayısını kontrol et
    user_usage = gpt_usage_count.get(user_id, 0)
    if user_usage >= GPT_MAX_USAGE_DAY:
        return False, f"Bugün için GPT kullanım limitinize ({GPT_MAX_USAGE_DAY}) ulaştınız. Yarın tekrar deneyin."
    
    return True, "OK"

# Mesajdan konu analizi yapma
def analyze_message_topic(message):
    """Mesajın konusunu analiz et ve uygun kategori döndür"""
    message = message.lower()
    
    if any(word in message for word in ["tanış", "merhaba", "selam", "ilk mesaj", "başlat"]):
        return "tanışma"
    elif any(word in message for word in ["sohbet", "konuş", "mesaj", "yaz"]):
        return "sohbet"
    elif any(word in message for word in ["buluş", "davet", "çık", "kahve", "yemek"]):
        return "buluşma"
    elif any(word in message for word in ["özgüven", "kendim", "güven", "çekin"]):
        return "özgüven"
    elif any(word in message for word in ["red", "kabul etme", "olmaz", "istemedi", "cevap vermedi"]):
        return "red"
    else:
        return None

@bot.on(events.NewMessage(pattern=f"^/agent (.+)$"))
async def agent_mode(event):
    """Bot'un kişisel asistan modunda çalışması"""
    sender = await event.get_sender()
    user_id = str(sender.id)
    message = event.pattern_match.group(1)
    
    # Tema analizi yap
    topic = analyze_message_topic(message)
    
    # Kısa sorular için veya %60 ihtimalle hazır cevapları kullan (maliyet optimizasyonu)
    if len(message) < 15 or random.random() < 0.6:
        if topic and topic in FLIRT_RESPONSES:
            response = random.choice(FLIRT_RESPONSES[topic])
        else:
            response = random.choice(FLIRT_ADVICE)
        await event.respond(f"💬 {response}")
        return
    
    # GPT kullanım hakkı kontrol et
    can_use, reason = can_use_gpt(user_id)
    if not can_use:
        if topic and topic in FLIRT_RESPONSES:
            advice = random.choice(FLIRT_RESPONSES[topic])
        else:
            advice = random.choice(FLIRT_ADVICE)
        await event.respond(f"{reason}\n\nBunun yerine hazır bir tavsiye verebilirim:\n\n{advice}")
        return
        
    await event.respond("Düşünüyorum... 🤔")
    
    try:
        # GPT kullanım sayısını artır
        gpt_usage_count[user_id] = gpt_usage_count.get(user_id, 0) + 1
        
        # GPT'ye istek gönder
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "Sen flört konusunda uzman, yardımcı olan bir botun adın Flirt Agent. Kullanıcıya çok kısa ve net yanıtlar ver, gereksiz açıklamalardan kaçın."},
                {"role": "user", "content": message}
            ],
            max_tokens=GPT_MAX_TOKENS
        )
        
        bot_response = response.choices[0].message.content
        await event.respond(bot_response)
        
        # Rastgele yeni görev önerisi (azaltılmış sıklık - %15)
        if random.random() < 0.1:
            tasks = get_available_tasks(user_id)
            if tasks:
                task = random.choice(tasks)
                await event.respond(f"\n\n💫 Bu arada, yeni bir görev denemek ister misin?\n\n**{task['title']}**\nÖdül: {task['reward']}")
    
    except Exception as e:
        logger.error(f"Agent hatası: {e}")
        await event.respond(f"Üzgünüm, şu anda cevap veremiyorum. İşte tavsiyem:\n\n{random.choice(FLIRT_ADVICE)}")

@bot.on(events.NewMessage(pattern=f"^/flortcoach (.+)$"))
async def flirt_coach(event):
    """Kişisel flört koçu"""
    sender = await event.get_sender()
    user_id = str(sender.id)
    question = event.pattern_match.group(1)
    
    # Tema analizi yap
    topic = analyze_message_topic(question)
    
    # Hazır cevapları kullanma olasılığını artır (%70)
    if len(question) < 20 or random.random() < 0.7:
        if topic and topic in FLIRT_RESPONSES:
            advice = random.choice(FLIRT_RESPONSES[topic])
        else:
            tip = random.choice(FLIRT_TIPS)
            advice = random.choice(FLIRT_ADVICE)
            advice = f"{tip}\n\n{advice}"
        
        user_profile = get_user_profile(user_id)
        if user_profile:
            level = math.floor((user_profile.get("xp", 0) / 100) + 1)
            await event.respond(f"🌟 **Seviye {level} Flört Koçundan İpucu**\n\n{advice}")
        else:
            await event.respond(f"🌟 **Flört Koçundan İpucu**\n\n{advice}")
        return
    
    # GPT kullanım hakkı kontrol et
    can_use, reason = can_use_gpt(user_id)
    if not can_use:
        if topic and topic in FLIRT_RESPONSES:
            advice = random.choice(FLIRT_RESPONSES[topic])
        else:
            advice = random.choice(FLIRT_TIPS)
        await event.respond(f"{reason}\n\nYerine size bir flört ipucu vereyim:\n\n{advice}")
        return
    
    await event.respond("Tavsiyemi düşünüyorum... 💭")
    
    try:
        # GPT kullanım sayısını artır
        gpt_usage_count[user_id] = gpt_usage_count.get(user_id, 0) + 1
            
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "Sen bir flört ve sosyal beceri koçusun. Kısa, net ve somut tavsiyeler ver. Kelime sayını sınırlı tut."},
                {"role": "user", "content": question}
            ],
            max_tokens=GPT_MAX_TOKENS
        )
        
        advice = response.choices[0].message.content
        
        # Kullanıcı deneyimini kişiselleştir
        user_profile = get_user_profile(user_id)
        if user_profile:
            level = math.floor((user_profile.get("xp", 0) / 100) + 1)
            await event.respond(f"🌟 **Seviye {level} Flört Koçundan Öneri**\n\n{advice}")
        else:
            await event.respond(f"🌟 **Flört Koçundan Öneri**\n\n{advice}")
            
    except Exception as e:
        logger.error(f"OpenAI API hatası: {e}")
        await event.respond(f"Şu anda GPT tavsiyelere ulaşamıyorum. İşte size bir ipucu:\n\n{random.choice(FLIRT_TIPS)}")

@bot.on(events.NewMessage(pattern=f"^/gunluk$"))
async def daily_task(event):
    """Günlük görev dağıt"""
    sender = await event.get_sender()
    user_id = str(sender.id)
    
    # Günlük görev verilip verilmediğini kontrol et
    if has_received_daily_task(user_id):
        await event.respond("Bugünkü görevini zaten aldın! Yarın tekrar gel 😉")
        return
    
    # Günlük görev seçimi (flört temalarına uygun)
    daily_tasks = [
        {"id": "daily_1", "title": "3 farklı kişiye selam gönder", "reward": "+10 XP", "verification_type": "message_forward", "verification_required": True},
        {"id": "daily_2", "title": "Bir gruba katıl ve kendini tanıt", "reward": "+15 XP", "verification_type": "bot_mention", "verification_required": True},
        {"id": "daily_3", "title": "Bir arkadaşının mesajına emoji ile tepki ver", "reward": "+5 XP", "verification_type": "message_forward", "verification_required": True},
        {"id": "daily_4", "title": "DM'den birine iltifat et", "reward": "Çekici 🧲 rozeti", "verification_type": "message_forward", "verification_required": True}
    ]
    
    task = random.choice(daily_tasks)
    set_daily_task(user_id, task)
    
    # Doğrulama bilgisi ekle
    verification_info = ""
    if task.get("verification_required", True):
        verification_type = task.get("verification_type", "")
        verification_info = f"\n\n🔍 Bu görev '{get_verification_text(verification_type)}' gerektiriyor."
    
    await event.respond(f"💌 **Günlük Flört Görevin**\n\n{task['title']}\n\nBu görevi tamamlayarak {task['reward']} kazanabilirsin!{verification_info}")
    
    # Doğrulama türüne göre ipucu ver
    verification_type = task.get("verification_type", "")
    if verification_type in VERIFICATION_TYPES:
        if verification_type == "message_forward":
            await event.respond("💡 **İpucu:** Bu görevi tamamlamak için bana doğrudan mesaj gönder.")
        elif verification_type == "bot_mention":
            await event.respond("💡 **İpucu:** Bu görevi tamamlamak için beni bir grupta etiketle.")
        elif verification_type == "pin_check":
            await event.respond("💡 **İpucu:** Bu görevi tamamlamak için bir mesajı bir grupta sabitle.")
        elif verification_type == "deeplink_track":
            await event.respond(f"💡 **İpucu:** Bu görevi tamamlamak için https://t.me/{BOT_USERNAME} linkini bir grupta paylaş.")

@bot.on(events.NewMessage(pattern=f"^/tamamla (\d+)$"))
async def manual_complete_task(event):
    """Manuel görev tamamlama - kullanıcı tarafından görev tamamlama"""
    try:
        task_id = int(event.pattern_match.group(1))
        sender = await event.get_sender()
        user_id = str(sender.id)
        
        # Görevi API üzerinden tamamla
        response = complete_task_api(user_id, task_id)
        
        if not response:
            await event.respond("❌ Görev tamamlanamadı. Lütfen daha sonra tekrar deneyin.")
            return
        
        # Görev durumuna göre cevap ver
        if response.get("status") == "ok":
            await event.respond(f"🎉 {response.get('message', 'Görev başarıyla tamamlandı!')}")
        elif response.get("status") == "pending":
            await event.respond(f"⏳ {response.get('message', 'Göreviniz doğrulanmayı bekliyor...')}")
        elif response.get("status") == "warning":
            await event.respond(f"⚠️ {response.get('message', 'Bu görev zaten tamamlanmış veya beklemede.')}")
        else:
            await event.respond(f"❌ Hata: {response.get('error', 'Bilinmeyen bir hata oluştu.')}")
    except Exception as e:
        logger.error(f"Manuel görev tamamlamada hata: {e}")
        await event.respond("❌ Görev tamamlanırken bir hata oluştu.")

# GÖREV YÖNETİM KOMUTLARI
@bot.on(events.NewMessage(pattern='^/tasks'))
async def handle_tasks_command(event):
    """Mevcut görevleri liste halinde göster"""
    try:
        user_id = str(event.sender_id)
        sender = await event.get_sender()
        
        logger.info(f"Kullanıcı görevleri istedi: {user_id}")
        
        # Backend API'den aktif görevleri al
        tasks = []
        try:
            # Örnek: REST API'den görevleri al
            if "api_client" in globals() and api_client:
                tasks = await api_client.get_tasks()
            # Veya görevleri direkt task_manager üzerinden al
            else:
                # Temel görevleri yükle
                tasks = [
                    {
                        "id": "join_channel",
                        "title": "Kanala Katıl",
                        "description": "Resmi telegram kanalımıza katıl",
                        "reward": {"xp": 10, "token": 1}
                    },
                    {
                        "id": "send_message",
                        "title": "Mesaj Gönder",
                        "description": "Gruba mesaj gönder",
                        "reward": {"xp": 5, "token": 1}
                    },
                    {
                        "id": "emoji_reaction",
                        "title": "Emoji Tepkisi Ver",
                        "description": "Duyuru mesajına emoji tepkisi ver",
                        "reward": {"xp": 5, "token": 1}
                    },
                    {
                        "id": "group_join_message",
                        "title": "Gruba Katıl ve Mesaj Gönder",
                        "description": "Yeni grubumuza katıl ve kendini tanıt",
                        "reward": {"xp": 20, "token": 3}
                    }
                ]
        except Exception as e:
            logger.error(f"Görevler alınırken hata: {e}")
            await event.respond("⚠️ Görevler alınırken bir hata oluştu. Lütfen daha sonra tekrar deneyin.")
            return
        
        if not tasks:
            await event.respond("📋 Şu anda mevcut görev bulunmamaktadır.")
            return
        
        # Görevlerden inline butonlar oluştur
        from telethon import Button
        
        # Her görev için bir buton oluştur
        task_buttons = []
        for task in tasks:
            # Görev bilgisi ve ödül
            reward_text = f"{task.get('reward', {}).get('xp', 0)} XP + {task.get('reward', {}).get('token', 0)} $VIPX"
            
            # Her satırda bir görev butonu
            task_buttons.append([
                Button.inline(
                    f"🎯 {task['title']} ({reward_text})",
                    data=f"task_info_{task['id']}"
                )
            ])
            
        # Mesajı gönder
        await event.respond(
            f"📋 **Mevcut Görevler**\n\n"
            f"Aşağıdaki görevlerden birini seçerek detayları görebilir ve görevi başlatabilirsiniz:",
            buttons=task_buttons
        )
        
    except Exception as e:
        logger.error(f"/tasks komutunda hata: {e}")
        await event.respond("⚠️ Bir hata oluştu. Lütfen daha sonra tekrar deneyin.")

@bot.on(events.CallbackQuery(pattern=r"task_info_(.+)"))
async def handle_task_info(event):
    """Görev detaylarını göster ve başlatma seçeneği sun"""
    try:
        user_id = str(event.sender_id)
        task_id = event.data.decode('utf-8').split('_')[-1]
        
        logger.info(f"Kullanıcı görev detayı istedi: {user_id}, görev: {task_id}")
        
        # İlgili görevi bul (backend API'den veya yerel cache'den)
        task = None
        try:
            # Örnek: REST API'den görevi al
            if "api_client" in globals() and api_client:
                task = await api_client.get_task(task_id)
            # Veya görevi direkt task_manager üzerinden al
            else:
                # Örnek veri
                tasks = {
                    "join_channel": {
                        "id": "join_channel",
                        "title": "Kanala Katıl",
                        "description": "Resmi telegram kanalımıza katılarak ödül kazanın. Katıldıktan sonra bot otomatik olarak tamamlandığını tespit edecektir.",
                        "type": "channel_join_v2",
                        "reward": {"xp": 10, "token": 1},
                        "params": {
                            "channel_id": "@onlyvips_channel"
                        },
                        "duration": "24 saat",
                        "difficulty": "Kolay"
                    },
                    "send_message": {
                        "id": "send_message",
                        "title": "Mesaj Gönder",
                        "description": "Topluluğumuza destek olmak için gruba mesaj gönderin. Mesajınız en az 10 karakter uzunluğunda olmalıdır.",
                        "type": "message_send",
                        "reward": {"xp": 5, "token": 1},
                        "params": {
                            "chat_id": "@onlyvips_group",
                            "min_length": 10
                        },
                        "duration": "24 saat",
                        "difficulty": "Kolay"
                    },
                    "emoji_reaction": {
                        "id": "emoji_reaction",
                        "title": "Emoji Tepkisi Ver",
                        "description": "Kanalımızdaki son duyuru mesajına 👍 emoji tepkisi verin.",
                        "type": "emoji_reaction",
                        "reward": {"xp": 5, "token": 1},
                        "params": {
                            "target_chat_id": "@onlyvips_channel",
                            "target_message_id": 456,
                            "target_emoji": "👍"
                        },
                        "duration": "24 saat",
                        "difficulty": "Kolay"
                    },
                    "group_join_message": {
                        "id": "group_join_message",
                        "title": "Gruba Katıl ve Mesaj Gönder",
                        "description": "Yeni topluluk grubumuza katılın ve kendinizi tanıtan bir mesaj gönderin. Mesajınız en az 30 karakter uzunluğunda olmalıdır.",
                        "type": "group_join_message",
                        "reward": {"xp": 20, "token": 3},
                        "params": {
                            "group_username": "@onlyvips_community",
                            "min_length": 30
                        },
                        "duration": "7 gün",
                        "difficulty": "Orta"
                    }
                }
                task = tasks.get(task_id)
        except Exception as e:
            logger.error(f"Görev detayı alınırken hata: {e}")
            await event.answer("Görev detayları alınamadı", alert=True)
            return
        
        if not task:
            await event.answer("Bu görev artık mevcut değil", alert=True)
            return
        
        # Görev bilgilerini hazırla
        reward_text = f"{task.get('reward', {}).get('xp', 0)} XP + {task.get('reward', {}).get('token', 0)} $VIPX"
        difficulty = task.get('difficulty', 'Normal')
        duration = task.get('duration', '24 saat')
        
        # Butonları hazırla
        from telethon import Button
        buttons = [
            [Button.inline("🚀 Görevi Başlat", data=f"start_task_{task_id}")],
            [Button.inline("◀️ Geri Dön", data="back_to_tasks")]
        ]
        
        # Mesajı gönder
        await event.edit(
            f"🎯 **{task['title']}**\n\n"
            f"📝 **Açıklama:** {task['description']}\n\n"
            f"💰 **Ödül:** {reward_text}\n"
            f"⏱️ **Süre:** {duration}\n"
            f"📊 **Zorluk:** {difficulty}\n\n"
            f"Görevi başlatmak için aşağıdaki butona tıklayın:",
            buttons=buttons
        )
        
    except Exception as e:
        logger.error(f"Görev detayları gösterilirken hata: {e}")
        await event.answer("Bir hata oluştu", alert=True)

@bot.on(events.CallbackQuery(pattern=r"back_to_tasks"))
async def handle_back_to_tasks(event):
    """Görev listesine geri dön"""
    try:
        # /tasks komutunu yeniden çağır
        message = await event.get_message()
        await message.delete()
        
        # Yeni bir /tasks komutu oluştur
        new_event = events.NewMessage.Event(
            message=message,
            pattern='/tasks',
            out=False,
            forwards=False
        )
        new_event._sender = await event.get_sender()
        
        # /tasks komut işleyicisini çağır
        await handle_tasks_command(new_event)
        
    except Exception as e:
        logger.error(f"Görev listesine dönülürken hata: {e}")
        await event.answer("Görev listesi yüklenemedi", alert=True)

@bot.on(events.CallbackQuery(pattern=r"start_task_(.+)"))
async def handle_start_task(event):
    """Görevi başlat"""
    try:
        user_id = str(event.sender_id)
        task_id = event.data.decode('utf-8').split('_')[-1]
        
        logger.info(f"Kullanıcı görev başlatıyor: {user_id}, görev: {task_id}")
        
        # Kullanıcının günlük limit aşımını kontrol et
        # TaskLogger import
        from src.utils.task_logger import TaskLogger
        task_logger = TaskLogger()
        
        # İlgili görev tipini bul
        task_type = None
        try:
            # Örnek: görev tipini bul
            if "api_client" in globals() and api_client:
                task = await api_client.get_task(task_id)
                task_type = task.get("type")
            else:
                # Örnek veri
                task_types = {
                    "join_channel": "channel_join_v2",
                    "send_message": "message_send",
                    "emoji_reaction": "emoji_reaction",
                    "group_join_message": "group_join_message"
                }
                task_type = task_types.get(task_id)
        except Exception as e:
            logger.error(f"Görev tipi belirlenirken hata: {e}")
            await event.answer("Görev başlatılamadı", alert=True)
            return
        
        if not task_type:
            await event.answer("Görev tipi belirlenemedi", alert=True)
            return
        
        # Günlük limit kontrolü
        if not await task_logger.check_daily_limit(user_id, task_type):
            await event.answer("Bu görevi bugün zaten tamamladınız. Lütfen yarın tekrar deneyin.", alert=True)
            return
        
        # Görevi başlat
        try:
            # Görev parametrelerini al
            if "api_client" in globals() and api_client:
                task = await api_client.get_task(task_id)
                params = task.get("params", {})
            else:
                # Örnek veri
                params_map = {
                    "join_channel": {"channel_id": "@onlyvips_channel"},
                    "send_message": {"chat_id": "@onlyvips_group", "min_length": 10},
                    "emoji_reaction": {"target_chat_id": "@onlyvips_channel", "target_message_id": 456, "target_emoji": "👍"},
                    "group_join_message": {"group_username": "@onlyvips_community", "min_length": 30}
                }
                params = params_map.get(task_id, {})
            
            # Görevi ata ve başlat
            # Task Manager'a havale et - gerçek sistemde TaskManager.create_task() çağrılmalı
            from src.tasks.task_manager import TaskManager
            if 'task_manager' in globals() and task_manager:
                # Görev oluştur
                await task_manager.create_task(
                    user_id=user_id,
                    task_id=task_id,
                    task_type=task_type,
                    params=params
                )
                success = True
            else:
                # Task Manager yoksa manuel doğrulama gerekecek
                success = True
                logger.warning(f"Task Manager bulunamadı, görev manuel doğrulama gerektirecek: {task_id}")
            
            if success:
                # Günlük limit sayacını artır
                await task_logger.increment_daily_limit(user_id, task_type)
                
                # Başarılı mesajını göster
                from telethon import Button
                
                # Görev tipine göre özel mesajlar
                task_instructions = {
                    "channel_join_v2": f"Kanala katılmak için: [Kanala Git](https://t.me/{params.get('channel_id', '').lstrip('@')})",
                    "message_send": f"Mesaj göndermek için: [Gruba Git](https://t.me/{params.get('chat_id', '').lstrip('@')})",
                    "emoji_reaction": f"Emoji tepkisi vermek için: [Mesaja Git](https://t.me/{params.get('target_chat_id', '').lstrip('@')}/{params.get('target_message_id')})",
                    "group_join_message": f"Gruba katılmak için: [Gruba Git](https://t.me/{params.get('group_username', '').lstrip('@')})"
                }
                
                instruction = task_instructions.get(task_type, "Görev başlatıldı. Devam etmek için talimatları takip edin.")
                
                await event.edit(
                    f"🚀 **Görev Başlatıldı**\n\n"
                    f"**Görev:** {task_id}\n\n"
                    f"📝 **Yapılacaklar:**\n{instruction}\n\n"
                    f"Görev otomatik olarak kontrol edilecektir. Tamamlandığında size bildirim gönderilecektir.",
                    buttons=[Button.inline("◀️ Görevlere Dön", data="back_to_tasks")],
                    link_preview=True
                )
                
                logger.info(f"Görev başarıyla başlatıldı: {user_id}, görev: {task_id}")
            else:
                await event.answer("Görev başlatılamadı. Lütfen daha sonra tekrar deneyin.", alert=True)
                
        except Exception as e:
            logger.error(f"Görev başlatılırken hata: {e}")
            await event.answer("Görev başlatılırken bir hata oluştu", alert=True)
        
    except Exception as e:
        logger.error(f"Görev başlatma işleminde hata: {e}")
        await event.answer("Bir hata oluştu", alert=True)

@bot.on(events.NewMessage(pattern='^/myprogress'))
async def handle_myprogress_command(event):
    """Kullanıcının görev ilerlemesini göster"""
    try:
        user_id = str(event.sender_id)
        sender = await event.get_sender()
        
        logger.info(f"Kullanıcı ilerleme durumunu istedi: {user_id}")
        
        # Kullanıcı ilerleme durumunu al
        from src.utils.task_logger import TaskLogger
        task_logger = TaskLogger()
        
        progress = await task_logger.get_user_progress(user_id)
        
        # İlerleme mesajını oluştur
        total_tasks = progress.get("completed_tasks", 0)
        xp = progress.get("xp", 0)
        token = progress.get("token", 0)
        last_week = progress.get("last_week_tasks", 0)
        
        # Görev tiplerine göre dağılım
        task_types = progress.get("task_types", {})
        type_text = ""
        
        if task_types:
            type_text = "\n**Görev Tiplerine Göre:**\n"
            for task_type, count in task_types.items():
                # Task tipini daha okunabilir hale getir
                readable_type = {
                    "channel_join_v2": "Kanala Katılma",
                    "message_send": "Mesaj Gönderme",
                    "button_click": "Buton Tıklama",
                    "start_link": "Start Link",
                    "voting": "Oylama",
                    "schedule_post": "Zamanlanmış Mesaj",
                    "comment": "Yorum Yapma",
                    "follow_account": "Hesap Takip",
                    "emoji_reaction": "Emoji Tepkisi",
                    "group_join_message": "Gruba Katılma ve Mesaj"
                }.get(task_type, task_type)
                
                type_text += f"- {readable_type}: {count} görev\n"
        
        # Seviye hesapla (basit bir formül)
        level = 1 + (xp // 100)  # Her 100 XP'de bir seviye
        next_level_xp = (level * 100)
        xp_progress = xp % 100  # Bir sonraki seviyeye kalan XP
        
        # Seviye ilerleme çubuğu
        progress_bar = "▓" * (xp_progress // 10) + "░" * (10 - (xp_progress // 10))
        
        # Mesajı gönder
        from telethon import Button
        
        await event.respond(
            f"📊 **İlerleme Durumunuz**\n\n"
            f"👤 **Kullanıcı:** {sender.first_name}\n"
            f"⭐ **Seviye:** {level}\n"
            f"📈 **XP:** {xp}/{next_level_xp} [{xp_progress}%]\n"
            f"[{progress_bar}]\n\n"
            f"💰 **$VIPX Token:** {token}\n"
            f"🎯 **Tamamlanan Görevler:** {total_tasks}\n"
            f"📅 **Son 7 Gün:** {last_week} görev\n"
            f"{type_text}\n\n"
            f"Daha fazla görev tamamlayarak seviyenizi yükseltebilir ve ödüller kazanabilirsiniz!",
            buttons=[Button.inline("📋 Görevleri Görüntüle", data="back_to_tasks")]
        )
        
    except Exception as e:
        logger.error(f"/myprogress komutunda hata: {e}")
        await event.respond("⚠️ İlerleme durumunuz alınırken bir hata oluştu. Lütfen daha sonra tekrar deneyin.")

# TaskManager global değişkeni
task_manager = None

async def main():
    """Ana fonksiyon - botu başlat"""
    global task_manager
    
    if SESSION_STRING:
        await bot.start()
    else:
        await bot.start(bot_token=BOT_TOKEN)
    
    logger.info("Bot dinlemeye başladı...")
    
    # Task Manager'ı başlat
    try:
        from src.tasks.task_manager import TaskManager
        from src.utils.json_logger import bot_logger
        
        # Basit bir veritabanı sınıfı oluşturalım
        class SimpleDBManager:
            async def get_active_tasks(self):
                return []
                
            async def save_task(self, user_id, task_id, task_type, expiry_time, params, status):
                logger.info(f"Görev kaydedildi: {user_id}_{task_id} ({task_type})")
                return True
                
            async def get_user_tasks(self, user_id, status=None):
                return []
                
            async def get_task(self, user_id, task_id):
                return None
                
            async def update_task_status(self, user_id, task_id, status):
                return True
        
        # TaskManager oluştur ve başlat
        db_manager = SimpleDBManager()
        task_manager = TaskManager(bot, db_manager, BOT_USERNAME)
        await task_manager.start()
        
        logger.info("TaskManager başarıyla başlatıldı")
        
    except Exception as e:
        logger.error(f"TaskManager başlatılırken hata: {e}")
    
    # Botun devamlı çalışması için
    await bot.run_until_disconnected()

if __name__ == "__main__":
    # Botu başlat
    asyncio.run(main()) 