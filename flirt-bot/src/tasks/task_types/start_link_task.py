#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Start Link Task - Start Link Görevi
Kullanıcının botu belirli bir start parametresi ile başlatmasını doğrulayan görev tipi
"""

import logging
from typing import Dict, Any, Optional, Union
import time
import re

from telethon import events

from ..base_task import BaseTask

logger = logging.getLogger(__name__)

class StartLinkTask(BaseTask):
    """Kullanıcının botu belirli bir start parametresi ile başlatmasını doğrulayan görev."""
    
    def __init__(
        self,
        user_id: str,
        task_id: str,
        expiry_time: int,
        verification_engine,
        bot,
        start_param: str,
        exact_match: bool = True,
        notify_on_complete: bool = True,
        **kwargs
    ):
        """
        StartLinkTask yapıcısı
        
        Args:
            user_id: Kullanıcı ID'si
            task_id: Görev ID'si
            expiry_time: Görevin geçerlilik süresi (Unix timestamp)
            verification_engine: Görev doğrulama motoru
            bot: Bot istemcisi
            start_param: Beklenen start parametresi
            exact_match: Tam eşleşme gereksin mi (varsayılan True)
            notify_on_complete: Tamamlandığında kullanıcıya bildirim gönderilsin mi (varsayılan True)
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
        
        self.start_param = start_param
        self.exact_match = exact_match
        self.notify_on_complete = notify_on_complete
        
        # Event handlers
        self._message_handler = None
        
        logger.info(f"StartLinkTask oluşturuldu: {self.user_id} için start link görevi (param: {self.start_param})")
    
    async def start_listening(self):
        """Start komut olaylarını dinlemeye başla"""
        if self._message_handler:
            return
            
        @self.bot.on(events.NewMessage(pattern=r'/start(?: (.+))?'))
        async def on_start_command(event):
            if not self.is_active or self.is_completed:
                return
                
            try:
                # Kullanıcı ID'sini kontrol et
                if event.sender_id != int(self.user_id):
                    return
                    
                # Start parametresini al
                start_params = event.pattern_match.group(1)
                
                # Parametre yoksa atla
                if not start_params:
                    return
                    
                logger.debug(f"Start komutu algılandı: {self.user_id}, param: {start_params}")
                
                # Parametreyi kontrol et
                if self.exact_match:
                    # Tam eşleşme
                    if start_params == self.start_param:
                        await self._complete_task()
                else:
                    # Kısmi eşleşme (içeriyor mu)
                    if self.start_param in start_params:
                        await self._complete_task()
                
            except Exception as e:
                logger.error(f"Start komutu işlenirken hata: {e}")
                
        self._message_handler = on_start_command
        logger.info(f"Start link dinleme başlatıldı: {self.user_id}")
    
    async def _complete_task(self):
        """Görevi tamamla"""
        if not self.is_active or self.is_completed:
            return
            
        # Görevi tamamlandı olarak işaretle
        success = await self.verification_engine.verify_task(self.user_id, self.task_id)
        
        if success:
            self.is_completed = True
            
            # Kullanıcıya bildirim gönder
            if self.notify_on_complete:
                try:
                    await self.bot.send_message(
                        int(self.user_id),
                        f"🎉 Tebrikler! Start link görevini başarıyla tamamladınız."
                    )
                except Exception as e:
                    logger.error(f"Bildirim gönderme hatası: {e}")
            
            logger.info(f"Start link görevi tamamlandı: {self.user_id}_{self.task_id}")
        else:
            logger.error(f"Görev tamamlama hatası: {self.user_id}_{self.task_id}")
    
    async def stop_listening(self):
        """Start komut olaylarını dinlemeyi durdur"""
        if self._message_handler:
            self.bot.remove_event_handler(self._message_handler)
            self._message_handler = None
            logger.info(f"Start link dinleme durduruldu: {self.user_id}")
    
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
            if self.notify_on_complete:
                await self.bot.send_message(
                    int(self.user_id),
                    f"🎉 Tebrikler! Start link göreviniz bir yönetici tarafından onaylandı."
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
            
    @staticmethod
    def generate_start_link(bot_username: str, param: str) -> str:
        """
        Start linki oluştur
        
        Args:
            bot_username: Bot kullanıcı adı (@ işareti olmadan)
            param: Start parametresi
            
        Returns:
            str: Start linki
        """
        bot_username = bot_username.lstrip('@')
        return f"https://t.me/{bot_username}?start={param}" 