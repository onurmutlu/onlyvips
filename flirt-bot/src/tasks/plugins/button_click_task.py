#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Button Click Task Plugin - Buton Tıklama Görev Eklentisi
Bu modül kullanıcıların butonlara tıklamasını kontrol eden görev sınıfını içerir
"""

import logging
import asyncio
from telethon import events, Button
from ..base_task import BaseTask

logger = logging.getLogger(__name__)

class ButtonClickTask(BaseTask):
    """Buton tıklamalarını kontrol eden görev tipi"""
    
    def __init__(self, user_id, task_id, expiry_time, verification_engine, bot, 
                 button_id=None, channel_id=None, message_id=None):
        """ButtonClickTask yapıcısı"""
        super().__init__(user_id, task_id, expiry_time, verification_engine, bot)
        self.handler = None
        self.button_id = button_id  # Tıklanması gereken butonun ID'si
        self.channel_id = channel_id  # Mesajın bulunduğu kanal ID'si
        self.message_id = message_id  # Butonun bulunduğu mesaj ID'si
        # Bot kullanıcı adını al
        self.bot_username = getattr(verification_engine, 'bot_username', "OnlyVipsBot")
    
    def start_listening(self):
        """Dinlemeye başla"""
        
        # Kullanıcı buton tıklamasını dinle
        @self.bot.on(events.CallbackQuery(data=self.button_id))
        async def button_clicked(event):
            try:
                # Kullanıcıyı kontrol et
                sender = await event.get_sender()
                user_id = str(sender.id)
                
                # Sadece görev sahibi kullanıcıların tıklamasını al
                if user_id != self.user_id:
                    return
                
                # Tıklama doğrulamasını yap
                await self.verify_button_click(user_id, event)
                
            except Exception as e:
                logger.error(f"Buton tıklama olayında hata: {e}")
        
        # Olay işleyicisini kaydet
        self.handler = button_clicked
        logger.debug(f"ButtonClickTask dinleme başlatıldı: {self.user_id}_{self.task_id}")
    
    async def verify_button_click(self, user_id, event=None):
        """Buton tıklamasını doğrula"""
        try:
            # Kullanıcının buton tıklamasını doğrula ve görevi tamamla
            task_key = f"{self.user_id}_{self.task_id}"
            success = await self.verification_engine.verify_task(task_key)
            
            # Bildirim göster
            if success and event:
                # Kullanıcıya bildirim gönder
                miniapp_url = f"https://t.me/{self.bot_username}/app?startapp={self.user_id}"
                
                # Callback query'yi önce yanıtla
                await event.answer("✅ Buton tıklama göreviniz tamamlandı!")
                
                # Ayrıca bir mesaj gönder
                chat = await event.get_input_chat()
                await self.bot.send_message(
                    chat,
                    f"✅ Buton tıklama göreviniz başarıyla tamamlandı ve ödülünüz verildi!",
                    buttons=[Button.url("🚀 OnlyVips MiniApp", miniapp_url)]
                )
            elif event:
                await event.answer("⚠️ Görev doğrulanırken bir sorun oluştu. Lütfen daha sonra tekrar deneyin.")
            
            return success
        
        except Exception as e:
            logger.error(f"Buton tıklama doğrulamasında hata: {e}")
            if event:
                await event.answer("⚠️ Bir hata oluştu.")
            return False
    
    async def verify_manually(self):
        """Manuel doğrulama"""
        # Buton tıklama görevleri normalde manuel doğrulanamaz, 
        # ancak zorunlu durumlar için yardımcı bir metot sağlıyoruz
        try:
            task_key = f"{self.user_id}_{self.task_id}"
            return await self.verification_engine.verify_task(task_key)
        except Exception as e:
            logger.error(f"Manuel buton tıklama doğrulamasında hata: {e}")
            return False
    
    def stop_listening(self):
        """Dinlemeyi durdur"""
        if self.handler:
            # Bot event handler'ını kaldır
            self.bot.remove_event_handler(self.handler)
            self.handler = None
            logger.debug(f"ButtonClickTask dinleme durduruldu: {self.user_id}_{self.task_id}") 