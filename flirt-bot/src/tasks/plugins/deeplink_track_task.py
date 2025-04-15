#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Deeplink Track Task Plugin - Link Takip Görev Eklentisi
Bu modül kullanıcıların link paylaşımını dinleyen görev sınıfını içerir
"""

import logging
import re
from telethon import events
from telethon.tl.types import MessageEntityUrl, MessageEntityTextUrl
from ..base_task import BaseTask

logger = logging.getLogger(__name__)

class DeeplinkTrackTask(BaseTask):
    """Link paylaşımlarını kontrol eden görev tipi"""
    
    def __init__(self, user_id, task_id, expiry_time, verification_engine, bot):
        """DeeplinkTrackTask yapıcısı"""
        super().__init__(user_id, task_id, expiry_time, verification_engine, bot)
        self.handler = None
        # Bot kullanıcı adını al
        self.bot_username = getattr(verification_engine, 'bot_username', "OnlyVipsBot")
    
    def start_listening(self):
        """Dinlemeye başla"""
        
        # Link içeren mesajları dinle
        @self.bot.on(events.NewMessage(pattern=r"https?://[^\s]+"))
        async def check_link(event):
            try:
                # Göndereni kontrol et
                sender = await event.get_sender()
                sender_id = str(sender.id)
                
                # Bu görevi yapan kullanıcı mı kontrol et
                if sender_id != self.user_id:
                    return
                
                # Mesajda link var mı kontrol et
                message = event.message
                if not message.entities:
                    return
                
                # Linkleri kontrol et
                for entity in message.entities:
                    if isinstance(entity, (MessageEntityUrl, MessageEntityTextUrl)):
                        # Entity'den URL'yi çıkar
                        url = message.text[entity.offset:entity.offset + entity.length]
                        
                        # URL, bot username veya onlyvips.com içeriyor mu kontrol et
                        if f"t.me/{self.bot_username}" in url or "onlyvips.com" in url:
                            logger.info(f"Uygun link paylaşımı tespit edildi, görev doğrulanıyor: {self.user_id}_{self.task_id}")
                            
                            # Görevi doğrula
                            task_key = f"{self.user_id}_{self.task_id}"
                            success = await self.verification_engine.verify_task(task_key)
                            
                            if success:
                                # Kullanıcıya bildirim
                                try:
                                    await event.reply("✅ Link paylaşım göreviniz başarıyla doğrulandı!")
                                except Exception as e:
                                    logger.error(f"Kullanıcıya bildirim gönderilirken hata: {e}")
                                
                                # Kullanıcıya DM olarak da bildirim gönder
                                try:
                                    from telethon import Button
                                    miniapp_url = f"https://t.me/{self.bot_username}/app?startapp={self.user_id}"
                                    
                                    await self.bot.send_message(
                                        self.user_id, 
                                        "🔗 Link paylaşım göreviniz başarıyla tamamlandı ve ödülünüz verildi! Daha fazla görev için MiniApp'i ziyaret edebilirsiniz.",
                                        buttons=[Button.url("🚀 OnlyVips MiniApp", miniapp_url)]
                                    )
                                except Exception as e:
                                    logger.error(f"Kullanıcıya DM bildirim gönderilirken hata: {e}")
                            
                            return
            except Exception as e:
                logger.error(f"Link kontrolünde hata: {e}")
        
        # Olay işleyicisini kaydet
        self.handler = check_link
        logger.debug(f"DeeplinkTrackTask dinleme başlatıldı: {self.user_id}_{self.task_id}")
    
    def stop_listening(self):
        """Dinlemeyi durdur"""
        if self.handler:
            # Bot event handler'ını kaldır
            self.bot.remove_event_handler(self.handler)
            self.handler = None
            logger.debug(f"DeeplinkTrackTask dinleme durduruldu: {self.user_id}_{self.task_id}") 