#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mesaj Gönderme Görevi
Bir kullanıcının bot veya belirli bir kullanıcıya mesaj göndermesini doğrulayan görev sınıfı.
"""

import logging
import re
from typing import Dict, Any, Optional, List, Union
from telethon import events

from ..base_task import BaseTask

logger = logging.getLogger(__name__)

class MessageTask(BaseTask):
    """Belirli bir mesaj gönderme görevini doğrulayan sınıf."""
    
    def __init__(
        self,
        user_id: str,
        task_id: str,
        expiry_time: int,
        verification_engine,
        bot,
        **kwargs
    ):
        """
        MessageTask yapıcısı
        
        Args:
            user_id: Kullanıcı ID'si
            task_id: Görev ID'si
            expiry_time: Görevin geçerlilik süresi (Unix timestamp)
            verification_engine: Görev doğrulama motoru referansı
            bot: Bot istemci referansı
            target_id (str, optional): Hedef kullanıcı/bot ID'si (belirtilmezse bota mesaj)
            required_content (List[str], optional): Mesajın içermesi gereken kelime/ifade listesi
            min_length (int, optional): Minimum mesaj uzunluğu
            is_private (bool, optional): Sadece özel mesaj mı kabul edilsin
        """
        super().__init__(
            user_id=user_id,
            task_id=task_id,
            expiry_time=expiry_time,
            verification_engine=verification_engine,
            bot=bot,
            **kwargs
        )
        
        # Mesaj görevi özellikleri
        self.target_id = kwargs.get("target_id", None)  # Hedef ID, None ise bota mesaj
        self.required_content = kwargs.get("required_content", [])  # Gerekli içerik
        self.min_length = kwargs.get("min_length", 0)  # Minimum uzunluk
        self.is_private = kwargs.get("is_private", True)  # Sadece özel mesaj
        
        # Bot kullanıcı adını al
        self.bot_username = getattr(verification_engine, 'bot_username', "OnlyVipsBot")
        
        # Olay dinleyici referansı
        self._handler = None
        
    async def start_listening(self):
        """Mesaj olaylarını dinlemeye başla"""
        
        logger.info(f"Mesaj gönderme görevi dinleyicisi başlatılıyor: {self.user_id}_{self.task_id}")
        
        # Hedef ID belirtilmemişse, bot ID'sini kullan
        target_id = self.target_id
        if not target_id:
            # Bot ID'sini al
            try:
                me = await self.bot.get_me()
                target_id = str(me.id)
                logger.info(f"Mesaj hedefi olarak bot ID kullanılıyor: {target_id}")
            except Exception as e:
                logger.error(f"Bot ID alınamadı: {e}")
                target_id = None
        
        # Dinleme filtresi oluştur
        if self.is_private:
            # Sadece özel mesajları dinle
            filter_private = lambda e: e.is_private
        else:
            # Tüm mesajları dinle
            filter_private = lambda e: True
        
        @self.bot.on(events.NewMessage(incoming=True, func=filter_private))
        async def message_handler(event):
            if not self.is_active or self.is_completed:
                return
                
            try:
                # Gönderen kullanıcıyı kontrol et
                sender = await event.get_sender()
                sender_id = str(sender.id)
                
                if sender_id != self.user_id:
                    return
                
                # Hedef kontrolü yap
                if target_id:
                    # Mesajın hedefinin doğru olduğundan emin ol
                    chat = await event.get_chat()
                    chat_id = str(chat.id)
                    
                    # Hedef ID ile eşleşiyor mu?
                    if chat_id != target_id:
                        return
                
                # Mesaj içeriğini kontrol et
                message_text = event.message.text
                
                # Minimum uzunluk kontrolü
                if self.min_length > 0 and len(message_text) < self.min_length:
                    logger.info(f"Mesaj çok kısa: {len(message_text)} / {self.min_length}")
                    return
                
                # Gerekli içerik kontrolü
                if self.required_content:
                    all_content_found = True
                    for required in self.required_content:
                        if required.lower() not in message_text.lower():
                            all_content_found = False
                            break
                    
                    if not all_content_found:
                        logger.info(f"Mesaj gerekli içeriği barındırmıyor: {self.required_content}")
                        return
                
                # Tüm kriterler sağlandı, görevi tamamla
                logger.info(f"Mesaj gönderme görevi tamamlandı: {self.user_id}")
                await self._complete_task(event)
                
            except Exception as e:
                logger.error(f"Mesaj kontrolünde hata: {e}")
        
        self._handler = message_handler
        
    async def _complete_task(self, event=None):
        """Görevi tamamla"""
        if not self.is_completed:
            self.is_completed = True
            
            # Doğrulama motoruna bildir
            await self.verification_engine.verify_task(self.user_id, self.task_id, True)
            
            # Kullanıcıya tebrik mesajı gönder
            try:
                # Eğer event varsa, yanıt ver
                if event:
                    try:
                        await event.reply("✅ Mesaj gönderme göreviniz başarıyla tamamlandı ve ödülünüz verildi!")
                    except Exception as e:
                        logger.error(f"Yanıt gönderilemedi: {e}")
                
                # Her durumda özel mesaj gönder
                from telethon import Button
                miniapp_url = f"https://t.me/{self.bot_username}/app?startapp={self.user_id}"
                
                await self.bot.send_message(
                    int(self.user_id),
                    f"💬 Mesaj gönderme göreviniz başarıyla tamamlandı ve ödülünüz verildi! Daha fazla görev için MiniApp'i ziyaret edebilirsiniz.",
                    buttons=[Button.url("🚀 OnlyVips MiniApp", miniapp_url)]
                )
            except Exception as e:
                logger.error(f"Kullanıcıya bildirim gönderilemedi: {e}")
    
    async def stop_listening(self):
        """Mesaj olaylarını dinlemeyi durdur"""
        if self._handler:
            logger.info(f"Mesaj gönderme görevi dinleyicisi durduruluyor: {self.user_id}_{self.task_id}")
            self.bot.remove_event_handler(self._handler)
            self._handler = None
    
    async def verify_manually(self, admin_id: str) -> bool:
        """
        Görevi manuel olarak doğrula
        
        Args:
            admin_id: Yönetici ID'si
            
        Returns:
            bool: Doğrulama başarılı ise True
        """
        logger.info(f"Mesaj gönderme görevi manuel doğrulandı: {self.user_id}_{self.task_id} (admin: {admin_id})")
        
        self.is_completed = True
        
        # Bot aracılığıyla kullanıcıya bildir
        try:
            await self.bot.send_message(
                int(self.user_id),
                f"✅ Tebrikler! Mesaj gönderme göreviniz bir yönetici tarafından onaylandı."
            )
        except Exception as e:
            logger.error(f"Kullanıcıya bildirim gönderilemedi: {e}")
        
        return True 