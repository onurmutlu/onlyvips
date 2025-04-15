#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mesaj Sabitleme Görevi
Bir kullanıcının bir grupta mesaj sabitlemesini doğrulayan görev sınıfı.
"""

import logging
from typing import Dict, Any, Optional
from telethon import events
from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator
from telethon.tl.functions.channels import GetParticipantRequest

from ..base_task import BaseTask

logger = logging.getLogger(__name__)

class PinCheckTask(BaseTask):
    """Bir kullanıcının mesaj sabitlemesini doğrulayan görev sınıfı."""
    
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
        PinCheckTask yapıcısı
        
        Args:
            user_id: Kullanıcı ID'si
            task_id: Görev ID'si
            expiry_time: Görevin geçerlilik süresi (Unix timestamp)
            verification_engine: Görev doğrulama motoru referansı
            bot: Bot istemci referansı
            target_group (str, optional): Sabitleme yapılacak hedef grup/kanal
            require_admin (bool, optional): Sabitleme için yönetici yetkisi gerekli mi
        """
        super().__init__(
            user_id=user_id,
            task_id=task_id,
            expiry_time=expiry_time,
            verification_engine=verification_engine,
            bot=bot,
            **kwargs
        )
        
        # Sabitleme görevi özellikleri
        self.target_group = kwargs.get("target_group", None)  # Hedef grup/kanal
        self.require_admin = kwargs.get("require_admin", True)  # Yönetici yetkisi gerekli mi
        
        # Bot kullanıcı adını al
        self.bot_username = getattr(verification_engine, 'bot_username', "OnlyVipsBot")
        
        # Olay dinleyici referansı
        self._handler = None
        
    async def start_listening(self):
        """Sabitleme olaylarını dinlemeye başla"""
        
        logger.info(f"Mesaj sabitleme görevi dinleyicisi başlatılıyor: {self.user_id}_{self.task_id}")
        
        @self.bot.on(events.ChatAction())
        async def pin_handler(event):
            if not self.is_active or self.is_completed:
                return
                
            try:
                # Sabitleme olayı mı kontrol et
                if not (event.action_message and event.action_message.pinned):
                    return
                
                # Grup veya kanal mesajı mı kontrol et
                if not (event.is_group or event.is_channel):
                    return
                
                # Sabitleyen kullanıcıyı al
                chat = await event.get_chat()
                sender = await event.get_sender()
                sender_id = str(sender.id)
                
                # Bu görevi yapan kullanıcı mı kontrol et
                if sender_id != self.user_id:
                    return
                
                # Hedef grup belirtilmişse, sadece o grubu kontrol et
                if self.target_group:
                    chat_id = str(chat.id)
                    chat_username = getattr(chat, 'username', '')
                    
                    # Hedef grup ID veya kullanıcı adı ile eşleşmiyor
                    if chat_id != self.target_group and chat_username != self.target_group:
                        if not chat_username or (self.target_group not in ["@" + chat_username, chat_username]):
                            return
                
                # Yönetici kontrolü gerekiyorsa yap
                if self.require_admin:
                    is_admin = await self._check_admin_status(chat.id, int(self.user_id))
                    if not is_admin:
                        logger.warning(f"Kullanıcı {self.user_id} yönetici değil, sabitleme görevi doğrulanamaz")
                        return
                
                # Görevi tamamla
                await self._complete_task()
                
            except Exception as e:
                logger.error(f"Mesaj sabitleme kontrolünde hata: {e}")
        
        self._handler = pin_handler
    
    async def _check_admin_status(self, chat_id, user_id) -> bool:
        """Kullanıcının yönetici olup olmadığını kontrol et"""
        try:
            participant = await self.bot(GetParticipantRequest(
                channel=chat_id,
                participant=user_id
            ))
            
            return isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator))
        except Exception as e:
            logger.error(f"Yönetici durumu kontrolünde hata: {e}")
            return False
    
    async def _complete_task(self):
        """Görevi tamamla"""
        if not self.is_completed:
            self.is_completed = True
            
            # Doğrulama motoruna bildir
            await self.verification_engine.verify_task(self.user_id, self.task_id, True)
            
            # Kullanıcıya tebrik mesajı gönder
            try:
                from telethon import Button
                miniapp_url = f"https://t.me/{self.bot_username}/app?startapp={self.user_id}"
                
                await self.bot.send_message(
                    int(self.user_id),
                    f"📌 Mesaj sabitleme göreviniz başarıyla tamamlandı ve ödülünüz verildi! Daha fazla görev için MiniApp'i ziyaret edebilirsiniz.",
                    buttons=[Button.url("🚀 OnlyVips MiniApp", miniapp_url)]
                )
            except Exception as e:
                logger.error(f"Kullanıcıya bildirim gönderilemedi: {e}")
        
    async def stop_listening(self):
        """Sabitleme olaylarını dinlemeyi durdur"""
        if self._handler:
            logger.info(f"Mesaj sabitleme görevi dinleyicisi durduruluyor: {self.user_id}_{self.task_id}")
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
        logger.info(f"Mesaj sabitleme görevi manuel doğrulandı: {self.user_id}_{self.task_id} (admin: {admin_id})")
        
        self.is_completed = True
        
        # Bot aracılığıyla kullanıcıya bildir
        try:
            await self.bot.send_message(
                int(self.user_id),
                f"✅ Tebrikler! Mesaj sabitleme göreviniz bir yönetici tarafından onaylandı."
            )
        except Exception as e:
            logger.error(f"Kullanıcıya bildirim gönderilemedi: {e}")
        
        return True 