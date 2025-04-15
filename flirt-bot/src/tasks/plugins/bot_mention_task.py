#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bot Mention Task Plugin - Bot Etiketleme Görev Eklentisi
Bu modül kullanıcıların gruplar içerisinde botu etiketlemesini dinleyen görev sınıfını içerir
"""

import logging
import re
from telethon import events
from ..base_task import BaseTask

logger = logging.getLogger(__name__)

class BotMentionTask(BaseTask):
    """Bot etiketlemelerini kontrol eden görev tipi"""
    
    def __init__(self, user_id, task_id, expiry_time, verification_engine, bot):
        """BotMentionTask yapıcısı"""
        super().__init__(user_id, task_id, expiry_time, verification_engine, bot)
        self.handler = None
        # Bot kullanıcı adını al
        self.bot_username = getattr(verification_engine, 'bot_username', None)
        if not self.bot_username:
            try:
                # Bot'un kendi kullanıcı adını al
                self.bot_username = self.bot.get_me().username
            except:
                # Varsayılan değer kullan
                self.bot_username = "OnlyVipsBot"
    
    def start_listening(self):
        """Dinlemeye başla"""
        
        # Mesajlarda bot etiketlemelerini dinle
        mention_pattern = rf".*@{self.bot_username}.*"
        
        @self.bot.on(events.NewMessage(incoming=True, pattern=mention_pattern))
        async def check_bot_mention(event):
            try:
                # Grup veya kanal mesajı mı kontrol et
                if not (event.is_group or event.is_channel):
                    return
                
                sender = await event.get_sender()
                sender_id = str(sender.id)
                
                # Bu görevin sahibi kullanıcıdan gelen bir etiketleme mi?
                if sender_id == self.user_id:
                    logger.info(f"Bot etiketleme tespit edildi, görev doğrulanıyor: {self.user_id}_{self.task_id}")
                    
                    # Görevi doğrula
                    task_key = f"{self.user_id}_{self.task_id}"
                    success = await self.verification_engine.verify_task(task_key)
                    
                    if success:
                        # Kullanıcıya bildirim (grup içinde)
                        try:
                            await event.reply("✅ Bot etiketleme göreviniz başarıyla doğrulandı ve ödülünüz verildi!")
                        except Exception as e:
                            logger.error(f"Kullanıcıya grup içinde bildirim gönderilirken hata: {e}")
                        
                        # Kullanıcıya özel mesaj olarak da bildirim gönder
                        try:
                            from telethon import Button
                            bot_username = self.bot_username
                            miniapp_url = f"https://t.me/{bot_username}/app?startapp={self.user_id}"
                            
                            await self.bot.send_message(
                                self.user_id, 
                                "🎉 Bot etiketleme göreviniz başarıyla tamamlandı! Daha fazla görev için MiniApp'i ziyaret edebilirsiniz.",
                                buttons=[Button.url("🚀 OnlyVips MiniApp", miniapp_url)]
                            )
                        except Exception as e:
                            logger.error(f"Kullanıcıya DM bildirim gönderilirken hata: {e}")
            except Exception as e:
                logger.error(f"Bot etiketleme kontrolünde hata: {e}")
        
        # Olay işleyicisini kaydet
        self.handler = check_bot_mention
        logger.debug(f"BotMentionTask dinleme başlatıldı: {self.user_id}_{self.task_id}")
    
    def stop_listening(self):
        """Dinlemeyi durdur"""
        if self.handler:
            # Bot event handler'ını kaldır
            self.bot.remove_event_handler(self.handler)
            self.handler = None
            logger.debug(f"BotMentionTask dinleme durduruldu: {self.user_id}_{self.task_id}") 