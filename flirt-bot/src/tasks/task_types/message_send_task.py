#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Message Send Task - Mesaj Gönderme Görevi
Kullanıcının belirli bir Telegram grubuna mesaj göndermesini doğrulayan görev tipi
"""

import logging
from typing import Dict, Any, List, Optional, Union
import asyncio
import re
import time

from ..base_task import BaseTask

logger = logging.getLogger(__name__)

class MessageSendTask(BaseTask):
    """Kullanıcının belirli bir gruba mesaj göndermesini gerektiren görev."""
    
    def __init__(
        self,
        user_id: str,
        task_id: str,
        expiry_time: int,
        verification_engine,
        bot,
        target_chat_id: Union[str, int],
        required_content: Optional[List[str]] = None,
        min_length: Optional[int] = None,
        max_messages: int = 1,
        **kwargs
    ):
        """
        MessageSendTask yapıcısı
        
        Args:
            user_id: Kullanıcı ID'si
            task_id: Görev ID'si
            expiry_time: Görevin geçerlilik süresi (Unix timestamp)
            verification_engine: Görev doğrulama motoru
            bot: Bot istemcisi
            target_chat_id: Hedef sohbet ID'si
            required_content: Mesajın içermesi gereken kelimeler (isteğe bağlı)
            min_length: Minimum mesaj uzunluğu (isteğe bağlı)
            max_messages: Gönderilmesi gereken maksimum mesaj sayısı (varsayılan 1)
            **kwargs: Ek parametreler
        """
        super().__init__(
            user_id=user_id,
            task_id=task_id,
            expiry_time=expiry_time,
            verification_engine=verification_engine,
            bot=bot,
            **kwargs
        )
        
        self.target_chat_id = str(target_chat_id)
        self.required_content = required_content or []
        self.min_length = min_length or 0
        self.max_messages = max_messages
        self.messages_sent = 0
        
        # Event handlers
        self._message_handler = None
        
        logger.info(f"MessageSendTask oluşturuldu: {self.user_id} için {self.target_chat_id} grubuna mesaj gönderme")
    
    async def start_listening(self):
        """Mesaj olaylarını dinlemeye başla"""
        if self._message_handler:
            return
            
        @self.bot.on(events.NewMessage())
        async def on_message(event):
            if not self.is_active or self.is_completed:
                return
                
            try:
                # Kullanıcı ID'sini kontrol et
                if event.sender_id != int(self.user_id):
                    return
                    
                # Hedef sohbet ID'sini kontrol et
                chat = await event.get_chat()
                chat_id = str(chat.id)
                
                # Hedef chat_id belirtilmişse kontrol et, yoksa tümünü kabul et
                if self.target_chat_id != "any" and chat_id != self.target_chat_id:
                    logger.debug(f"Farklı sohbet: {chat_id}, beklenen: {self.target_chat_id}")
                    return
                
                # Mesaj içeriğini kontrol et
                message_text = event.message.text or ""
                
                # Minimum uzunluğu kontrol et
                if len(message_text) < self.min_length:
                    logger.debug(f"Mesaj çok kısa: {len(message_text)}, minimum: {self.min_length}")
                    return
                
                # Gerekli içeriği kontrol et
                if self.required_content:
                    all_found = True
                    for required in self.required_content:
                        if required.lower() not in message_text.lower():
                            all_found = False
                            break
                            
                    if not all_found:
                        logger.debug(f"Gerekli içerik bulunamadı: {self.required_content}")
                        return
                
                # Mesaj sayısını artır
                self.messages_sent += 1
                logger.info(f"Kullanıcı bir mesaj gönderdi: {self.user_id}, sayı: {self.messages_sent}/{self.max_messages}")
                
                # Yeterli sayıda mesaj gönderildi mi?
                if self.messages_sent >= self.max_messages:
                    # Görevi tamamlandı olarak işaretle
                    await self.verification_engine.verify_task(self.user_id, self.task_id)
                    
                    # Kullanıcıya bildirim gönder
                    await self.bot.send_message(
                        int(self.user_id),
                        f"🎉 Tebrikler! '{self.target_chat_id}' grubuna mesaj gönderme görevini başarıyla tamamladınız."
                    )
                    
            except Exception as e:
                logger.error(f"Mesaj işlenirken hata: {e}")
                
        self._message_handler = on_message
        logger.info(f"Mesaj dinleme başlatıldı: {self.user_id}")
    
    async def stop_listening(self):
        """Mesaj olaylarını dinlemeyi durdur"""
        if self._message_handler:
            self.bot.remove_event_handler(self._message_handler)
            self._message_handler = None
            logger.info(f"Mesaj dinleme durduruldu: {self.user_id}")
    
    async def verify_manually(self, admin_id: str) -> bool:
        """
        Görevi manuel olarak doğrula
        
        Args:
            admin_id: Yönetici ID'si
            
        Returns:
            bool: Doğrulama başarılı ise True, aksi halde False
        """
        if not self.is_active:
            return False
            
        # Görevi tamamlandı olarak işaretle
        result = await self.verification_engine.verify_task(self.user_id, self.task_id)
        
        if result:
            # Görev durumunu güncelle
            self.is_completed = True
            self.is_active = False
            
            # Dinleyiciyi durdur
            await self.stop_listening()
            
            # Kullanıcıya bildirim gönder
            await self.bot.send_message(
                int(self.user_id),
                f"🎉 Tebrikler! Mesaj gönderme göreviniz bir yönetici tarafından onaylandı."
            )
            
            # Yöneticiye bildirim gönder
            await self.bot.send_message(
                int(admin_id),
                f"✅ Görev başarıyla doğrulandı: {self.user_id} için {self.task_id}"
            )
            
            logger.info(f"Görev manuel olarak doğrulandı: {self.user_id}_{self.task_id} by {admin_id}")
            return True
        else:
            logger.error(f"Görev doğrulanamadı: {self.user_id}_{self.task_id}")
            return False 