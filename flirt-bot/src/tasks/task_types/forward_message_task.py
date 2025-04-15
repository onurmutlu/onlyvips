#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
İleti Yönlendirme Görevi
Bir kullanıcının belirli bir mesajı yönlendirmesini doğrulayan görev sınıfı.
"""

import logging
import time
from typing import Dict, Any, Optional
from telethon import events, utils

from ..base_task import BaseTask

logger = logging.getLogger(__name__)

class ForwardMessageTask(BaseTask):
    """Belirli bir mesajı yönlendirme görevini doğrulayan sınıf."""
    
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
        ForwardMessageTask yapıcısı
        
        Args:
            user_id: Kullanıcı ID'si
            task_id: Görev ID'si
            expiry_time: Görevin geçerlilik süresi (Unix timestamp)
            verification_engine: Görev doğrulama motoru referansı
            bot: Bot istemci referansı
            source_channel (str): Yönlendirilecek mesajın kaynak kanalı
            message_id (int, optional): Yönlendirilecek mesajın ID'si
            target_type (str, optional): Hedef türü ('group', 'channel' veya 'any')
            min_forwards (int, optional): Minimum yönlendirme sayısı
        """
        super().__init__(
            user_id=user_id,
            task_id=task_id,
            expiry_time=expiry_time,
            verification_engine=verification_engine,
            bot=bot,
            **kwargs
        )
        
        # Yönlendirme görevi özellikleri
        self.source_channel = kwargs.get("source_channel")
        if not self.source_channel:
            raise ValueError("source_channel parametresi gereklidir")
            
        self.message_id = kwargs.get("message_id")  # Belirli bir mesaj ID yoksa, kanaldan herhangi bir mesaj
        self.target_type = kwargs.get("target_type", "any")  # Yönlendirme hedefi türü
        self.min_forwards = kwargs.get("min_forwards", 1)  # Minimum yönlendirme sayısı
        
        # İzleme durumu
        self.forward_count = 0
        
        # Olay dinleyici referansı
        self._handler = None
        
    async def start_listening(self):
        """Yönlendirme olaylarını dinlemeye başla"""
        
        logger.info(f"Yönlendirme görevi dinleyicisi başlatılıyor: {self.user_id}_{self.task_id}")
        
        @self.bot.on(events.NewMessage(forwards=True))
        async def forward_handler(event):
            if not self.is_active or self.is_completed:
                return
                
            # Gönderen kullanıcıyı kontrol et
            try:
                sender = await event.get_sender()
                sender_id = str(utils.get_peer_id(sender))
                
                if sender_id != self.user_id:
                    return
                    
                # Yönlendirilen mesajın kaynağını kontrol et
                if event.forward and event.forward.from_id:
                    forward_from_id = str(utils.get_peer_id(event.forward.from_id))
                    
                    # Kaynak kanalı ve opsiyonel olarak mesaj ID'sini kontrol et
                    is_target_source = False
                    
                    if self.source_channel and self.source_channel in forward_from_id:
                        is_target_source = True
                        
                    if self.message_id and event.forward.channel_post != self.message_id:
                        is_target_source = False
                        
                    if is_target_source:
                        # Hedef türünü kontrol et
                        if self.target_type != "any":
                            chat = await event.get_chat()
                            
                            if self.target_type == "group" and not (chat.is_group or chat.is_megagroup):
                                return
                                
                            if self.target_type == "channel" and not chat.is_channel:
                                return
                        
                        # Yönlendirme sayısını artır
                        self.forward_count += 1
                        logger.info(f"Yönlendirme algılandı: {self.user_id}, sayı: {self.forward_count}/{self.min_forwards}")
                        
                        # Minimum yönlendirme sayısına ulaşıldıysa görevi tamamla
                        if self.forward_count >= self.min_forwards:
                            # Görevi tamamla
                            self.is_completed = True
                            
                            # Doğrulama motoruna bildir
                            await self.verification_engine.verify_task(self.user_id, self.task_id, True)
                            
                            # Kullanıcıya tebrik mesajı gönder
                            try:
                                await self.bot.send_message(
                                    int(self.user_id),
                                    f"✅ Tebrikler! Mesaj yönlendirme görevini başarıyla tamamladınız."
                                )
                            except Exception as e:
                                logger.error(f"Kullanıcıya bildirim gönderilemedi: {e}")
                        
            except Exception as e:
                logger.error(f"Yönlendirme kontrolünde hata: {e}")
        
        self._handler = forward_handler
        
    async def stop_listening(self):
        """Yönlendirme olaylarını dinlemeyi durdur"""
        if self._handler:
            logger.info(f"Yönlendirme görevi dinleyicisi durduruluyor: {self.user_id}_{self.task_id}")
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
        logger.info(f"Yönlendirme görevi manuel doğrulandı: {self.user_id}_{self.task_id} (admin: {admin_id})")
        
        self.is_completed = True
        
        # Bot aracılığıyla kullanıcıya bildir
        try:
            await self.bot.send_message(
                int(self.user_id),
                f"✅ Tebrikler! Mesaj yönlendirme göreviniz bir yönetici tarafından onaylandı."
            )
        except Exception as e:
            logger.error(f"Kullanıcıya bildirim gönderilemedi: {e}")
        
        return True 