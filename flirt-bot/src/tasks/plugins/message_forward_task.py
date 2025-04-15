#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Message Forward Task Plugin - İleti Yönlendirme Görev Eklentisi
Bu modül kullanıcıların belirli mesajları yönlendirmesini takip eden görev sınıfını içerir
"""

import logging
from telethon import events
from ..base_task import BaseTask

logger = logging.getLogger(__name__)

class MessageForwardTask(BaseTask):
    """Mesaj yönlendirmelerini kontrol eden görev tipi"""
    
    def __init__(self, user_id, task_id, expiry_time, verification_engine, bot, 
                 target_chat_id=None, required_count=1):
        """MessageForwardTask yapıcısı"""
        super().__init__(user_id, task_id, expiry_time, verification_engine, bot)
        self.handler = None
        self.target_chat_id = target_chat_id  # Yönlendirmenin yapılması gereken sohbet/kanal ID'si
        self.required_count = required_count  # Gerekli yönlendirme sayısı
        self.forwarded_count = 0  # Şu ana kadar yapılan yönlendirme sayısı
        # Bot kullanıcı adını al
        self.bot_username = getattr(verification_engine, 'bot_username', "OnlyVipsBot")
    
    def start_listening(self):
        """Dinlemeye başla"""
        
        # Mesaj yönlendirmelerini dinle
        @self.bot.on(events.MessageForwarded())
        async def check_forward(event):
            try:
                # Olayı kontrol et - sadece ileri yönlendirmeleri dinle
                if not event.forwards:
                    return
                
                # Kullanıcıyı kontrol et
                user_id = str(event.sender_id)
                if user_id != self.user_id:
                    return
                
                # Hedef sohbet belirtilmişse, sadece o sohbeti kontrol et
                if self.target_chat_id:
                    chat = await event.get_chat()
                    chat_id = str(chat.id)
                    if chat_id != self.target_chat_id:
                        logger.debug(f"Kullanıcı farklı bir sohbete yönlendirdi, hedef sohbet değil: {chat_id}")
                        return
                
                # Yönlendirme sayısını artır
                self.forwarded_count += 1
                logger.info(f"Kullanıcı mesaj yönlendirme tespit edildi ({self.forwarded_count}/{self.required_count}): {self.user_id}_{self.task_id}")
                
                # Gerekli sayıya ulaşılınca görevi doğrula
                if self.forwarded_count >= self.required_count:
                    # Görevi doğrula
                    task_key = f"{self.user_id}_{self.task_id}"
                    success = await self.verification_engine.verify_task(task_key)
                    
                    if success:
                        # Kullanıcıya DM olarak bildirim gönder
                        try:
                            from telethon import Button
                            miniapp_url = f"https://t.me/{self.bot_username}/app?startapp={self.user_id}"
                            
                            await self.bot.send_message(
                                self.user_id, 
                                "📤 Mesaj yönlendirme göreviniz başarıyla tamamlandı ve ödülünüz verildi! Daha fazla görev için MiniApp'i ziyaret edebilirsiniz.",
                                buttons=[Button.url("🚀 OnlyVips MiniApp", miniapp_url)]
                            )
                        except Exception as e:
                            logger.error(f"Kullanıcıya DM bildirim gönderilirken hata: {e}")
            except Exception as e:
                logger.error(f"Mesaj yönlendirme kontrolünde hata: {e}")
        
        # Olay işleyicisini kaydet
        self.handler = check_forward
        logger.debug(f"MessageForwardTask dinleme başlatıldı: {self.user_id}_{self.task_id}")
    
    async def verify_manually(self):
        """Bu görev tipi için manuel doğrulama şu anda desteklenmiyor"""
        logger.warning(f"Mesaj yönlendirme görevi için manuel doğrulama desteklenmiyor: {self.user_id}_{self.task_id}")
        return False
    
    def stop_listening(self):
        """Dinlemeyi durdur"""
        if self.handler:
            # Bot event handler'ını kaldır
            self.bot.remove_event_handler(self.handler)
            self.handler = None
            logger.debug(f"MessageForwardTask dinleme durduruldu: {self.user_id}_{self.task_id}") 