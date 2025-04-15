#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pin Check Task Plugin - Sabitleme Kontrol Görev Eklentisi
Bu modül kullanıcıların gruplarda mesaj sabitlemesini dinleyen görev sınıfını içerir
"""

import logging
from telethon import events
from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator
from telethon.tl.functions.channels import GetParticipantRequest
from ..base_task import BaseTask

logger = logging.getLogger(__name__)

class PinCheckTask(BaseTask):
    """Mesaj sabitleme işlemlerini kontrol eden görev tipi"""
    
    def __init__(self, user_id, task_id, expiry_time, verification_engine, bot):
        """PinCheckTask yapıcısı"""
        super().__init__(user_id, task_id, expiry_time, verification_engine, bot)
        self.handler = None
    
    def start_listening(self):
        """Dinlemeye başla"""
        
        # Sabitleme olaylarını dinle
        @self.bot.on(events.ChatAction())
        async def check_pin(event):
            try:
                # Sabitleme olayı mı kontrol et
                if not (event.action_message and event.action_message.pinned):
                    return
                
                # Grup veya kanal mesajı mı kontrol et
                if not (event.is_group or event.is_channel):
                    return
                
                # Mesajı sabitleyen kişiyi bul
                chat = await event.get_chat()
                sender = await event.get_sender()
                sender_id = str(sender.id)
                
                # Bu görevi yapan kullanıcı mı kontrol et
                if sender_id != self.user_id:
                    return
                
                # Grup yöneticisi mi kontrol et
                try:
                    participant = await self.bot(GetParticipantRequest(chat.id, int(self.user_id)))
                    is_admin = isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator))
                    
                    if not is_admin:
                        logger.warning(f"Kullanıcı {self.user_id} yönetici değil, sabitleme görevi doğrulanamaz")
                        return
                except Exception as e:
                    logger.error(f"Yönetici kontrolünde hata: {e}")
                    return
                
                logger.info(f"Mesaj sabitleme tespit edildi, görev doğrulanıyor: {self.user_id}_{self.task_id}")
                
                # Görevi doğrula
                task_key = f"{self.user_id}_{self.task_id}"
                success = await self.verification_engine.verify_task(task_key)
                
                if success:
                    # Kullanıcıya DM olarak bildirim gönder
                    try:
                        from telethon import Button
                        bot_username = getattr(self.verification_engine, 'bot_username', "OnlyVipsBot")
                        miniapp_url = f"https://t.me/{bot_username}/app?startapp={self.user_id}"
                        
                        await self.bot.send_message(
                            self.user_id, 
                            "📌 Mesaj sabitleme göreviniz başarıyla tamamlandı! Daha fazla görev için MiniApp'i ziyaret edebilirsiniz.",
                            buttons=[Button.url("🚀 OnlyVips MiniApp", miniapp_url)]
                        )
                    except Exception as e:
                        logger.error(f"Kullanıcıya bildirim gönderilirken hata: {e}")
            except Exception as e:
                logger.error(f"Sabitleme kontrolünde hata: {e}")
        
        # Olay işleyicisini kaydet
        self.handler = check_pin
        logger.debug(f"PinCheckTask dinleme başlatıldı: {self.user_id}_{self.task_id}")
    
    def stop_listening(self):
        """Dinlemeyi durdur"""
        if self.handler:
            # Bot event handler'ını kaldır
            self.bot.remove_event_handler(self.handler)
            self.handler = None
            logger.debug(f"PinCheckTask dinleme durduruldu: {self.user_id}_{self.task_id}") 