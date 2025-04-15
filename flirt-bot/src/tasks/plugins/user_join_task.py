#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
User Join Task Plugin - Kullanıcı Katılım Görevi Eklentisi
Bu modül kullanıcıların belirli bir kanala/gruba katılımını kontrol eden görev sınıfını içerir
"""

import logging
import asyncio
from telethon import events, utils
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors import UserNotParticipantError
from ..base_task import BaseTask

logger = logging.getLogger(__name__)

class UserJoinTask(BaseTask):
    """Kullanıcının belirli bir kanala/gruba katılımını kontrol eden görev"""
    
    def __init__(self, user_id, task_id, expiry_time, verification_engine, bot, 
                 target_channel=None, min_join_time=None):
        """UserJoinTask yapıcısı"""
        super().__init__(user_id, task_id, expiry_time, verification_engine, bot)
        self.handler = None
        self.target_channel = target_channel  # Katılılacak kanal/grup
        self.min_join_time = min_join_time  # En az katılım süresi (saniye cinsinden, opsiyonel)
    
    def start_listening(self):
        """Dinlemeye başla"""
        
        # Kullanıcının kontrol komutunu dinle
        @self.bot.on(events.NewMessage(pattern=r'^/checkjoin(?:\s+|$)'))
        async def check_join_handler(event):
            try:
                # Komutu gönderen kullanıcıyı kontrol et
                sender = await event.get_sender()
                user_id = str(sender.id)
                
                # Sadece görev sahibi kullanıcıların komutunu işle
                if user_id != self.user_id:
                    return
                
                # Katılım doğrulamasını başlat
                await event.respond(f"🔍 Kanal katılımınız kontrol ediliyor...")
                
                # Katılımı doğrula
                verified = await self.verify_join(user_id)
                
                if verified:
                    await event.respond("✅ Tebrikler! Kanal katılım göreviniz başarıyla tamamlandı ve ödülünüz verildi.")
                else:
                    # Katılım bağlantısını oluştur
                    channel_link = f"https://t.me/{self.target_channel}" if not self.target_channel.startswith('@') else f"https://t.me/{self.target_channel[1:]}"
                    
                    # Min süre varsa bilgilendirme ekle
                    time_info = ""
                    if self.min_join_time:
                        minutes = self.min_join_time // 60
                        time_info = f" ve en az {minutes} dakika kanalda kalmanız gerekiyor"
                    
                    await event.respond(
                        f"⚠️ Henüz kanala katılmamışsınız{time_info}.\n\n"
                        f"Lütfen bu kanala katılın ve tekrar deneyin: {channel_link}"
                    )
                
            except Exception as e:
                logger.error(f"Kanal katılım kontrolünde hata: {e}")
                await event.respond("⚠️ Kanal katılımı kontrolü sırasında bir hata oluştu. Lütfen daha sonra tekrar deneyin.")
        
        # Olay işleyicisini kaydet
        self.handler = check_join_handler
        logger.debug(f"UserJoinTask dinleme başlatıldı: {self.user_id}_{self.task_id}")
    
    async def verify_join(self, user_id):
        """Kullanıcının kanala katılıp katılmadığını doğrula"""
        try:
            # Kullanıcı ID'sini integer'a çevir
            user_id_int = int(user_id)
            
            # Kanal varlığını al
            target_channel = self.target_channel
            if target_channel.startswith('@'):
                target_channel = target_channel[1:]
            
            channel = await self.bot.get_entity(target_channel)
            
            try:
                # Kullanıcının katılım durumunu kontrol et
                participant = await self.bot(GetParticipantRequest(
                    channel=channel,
                    participant=user_id_int
                ))
                
                # Kullanıcı kanala katılmış
                if participant:
                    # Eğer minimum katılım süresi belirtilmişse, join_date kontrolü yap
                    if self.min_join_time and hasattr(participant.participant, 'date'):
                        # Şu anki zaman
                        current_time = asyncio.get_event_loop().time()
                        # Katılım zamanı (Unix timestamp)
                        join_time = participant.participant.date.timestamp()
                        # Geçen süre (saniye)
                        elapsed_time = current_time - join_time
                        
                        if elapsed_time < self.min_join_time:
                            # Minimum süre geçmemiş
                            return False
                    
                    # Görev doğrulandı
                    task_key = f"{self.user_id}_{self.task_id}"
                    await self.verification_engine.verify_task(task_key)
                    return True
                    
            except UserNotParticipantError:
                # Kullanıcı kanala katılmamış
                return False
            except Exception as e:
                logger.error(f"Katılım kontrolünde hata: {e}")
                return False
            
            return False
            
        except Exception as e:
            logger.error(f"Katılım doğrulama hatası: {e}")
            return False
    
    async def verify_manually(self):
        """Manuel doğrulama"""
        try:
            # Bu, bir yönetici tarafından manuel olarak doğrulama yapıldığında kullanılır
            task_key = f"{self.user_id}_{self.task_id}"
            return await self.verification_engine.verify_task(task_key)
        except Exception as e:
            logger.error(f"Manuel katılım doğrulamasında hata: {e}")
            return False
    
    def stop_listening(self):
        """Dinlemeyi durdur"""
        if self.handler:
            # Bot event handler'ını kaldır
            self.bot.remove_event_handler(self.handler)
            self.handler = None
            logger.debug(f"UserJoinTask dinleme durduruldu: {self.user_id}_{self.task_id}") 