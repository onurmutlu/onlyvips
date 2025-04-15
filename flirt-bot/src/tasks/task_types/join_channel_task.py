#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Kanala Katılma Görevi
Bir kullanıcının belirli bir kanala katılmasını doğrulayan görev sınıfı.
"""

import logging
import time
from typing import Dict, Any, Optional
from telethon import events, utils

from ..base_task import BaseTask

logger = logging.getLogger(__name__)

class JoinChannelTask(BaseTask):
    """Belirli bir kanala katılma görevini doğrulayan sınıf."""
    
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
        JoinChannelTask yapıcısı
        
        Args:
            user_id: Kullanıcı ID'si
            task_id: Görev ID'si
            expiry_time: Görevin geçerlilik süresi (Unix timestamp)
            verification_engine: Görev doğrulama motoru referansı
            bot: Bot istemci referansı
            channel_username (str): Katılınacak kanal kullanıcı adı
            min_duration (int, optional): Kanalda kalınması gereken minimum süre (saniye)
        """
        super().__init__(
            user_id=user_id,
            task_id=task_id,
            expiry_time=expiry_time,
            verification_engine=verification_engine,
            bot=bot,
            **kwargs
        )
        
        # Kanala katılma görevi özellikleri
        self.channel_username = kwargs.get("channel_username")
        if not self.channel_username:
            raise ValueError("channel_username parametresi gereklidir")
            
        # Kanal ID'yi daha sonra çözeceğiz
        self.channel_id = None
        
        # Minimum süre (saniye olarak) - varsayılan: hemen kontrol et
        self.min_duration = kwargs.get("min_duration", 0)
        
        # İzleme durumu
        self.join_time = None
        
        # Olay dinleyici referansları
        self._join_handler = None
        self._leave_handler = None
        
    async def _resolve_channel_id(self):
        """Kanal kullanıcı adını ID'ye çözümle"""
        try:
            entity = await self.bot.get_entity(self.channel_username)
            self.channel_id = str(utils.get_peer_id(entity))
            logger.info(f"Kanal ID çözümlendi: {self.channel_username} -> {self.channel_id}")
            return self.channel_id
        except Exception as e:
            logger.error(f"Kanal ID çözümlenemedi: {self.channel_username}, hata: {e}")
            return None
            
    async def _check_membership(self):
        """Kullanıcının kanala üyeliğini kontrol et"""
        if not self.channel_id:
            await self._resolve_channel_id()
            if not self.channel_id:
                return False
                
        try:
            # Kanal varlığını al
            channel_entity = await self.bot.get_entity(int(self.channel_id))
            
            # Katılımcı mı kontrol et
            participant = await self.bot.get_participants(channel_entity, limit=1, 
                                                         search=str(self.user_id))
            
            return len(participant) > 0
        except Exception as e:
            logger.error(f"Üyelik kontrolünde hata: {e}")
            return False
            
    async def start_listening(self):
        """Kanal katılma olaylarını dinlemeye başla"""
        
        logger.info(f"Kanala katılma görevi dinleyicisi başlatılıyor: {self.user_id}_{self.task_id}")
        
        # Kanal ID'yi çözümlemeye çalış
        if not self.channel_id:
            await self._resolve_channel_id()
        
        # İlk durumu kontrol et (kullanıcı zaten kanalda olabilir)
        is_member = await self._check_membership()
        if is_member:
            logger.info(f"Kullanıcı zaten kanalda: {self.user_id}, kanal: {self.channel_username}")
            self.join_time = int(time.time())
            
            # Minimum süre yoksa hemen tamamla
            if self.min_duration <= 0:
                await self._complete_task()
        
        # Katılma olayını dinle
        @self.bot.on(events.ChatAction())
        async def join_handler(event):
            if not self.is_active or self.is_completed:
                return
                
            # Kanala katılma olayı mı kontrol et
            if event.user_joined or event.user_added:
                try:
                    # Kullanıcıyı kontrol et
                    user_id = str(utils.get_peer_id(event.user_id))
                    if user_id != self.user_id:
                        return
                        
                    # Kanalı kontrol et
                    chat_id = str(utils.get_peer_id(event.chat_id))
                    
                    # Kanal ID henüz çözülmediyse tekrar dene
                    if not self.channel_id:
                        await self._resolve_channel_id()
                        
                    # Doğru kanala katılma olayı mı kontrol et
                    if self.channel_id and chat_id == self.channel_id:
                        logger.info(f"Kanala katılma algılandı: {self.user_id}, kanal: {self.channel_username}")
                        self.join_time = int(time.time())
                        
                        # Minimum süre yoksa hemen tamamla
                        if self.min_duration <= 0:
                            await self._complete_task()
                            
                except Exception as e:
                    logger.error(f"Katılma olayı kontrolünde hata: {e}")
        
        # Ayrılma olayını dinle (minimum süre varsa)
        @self.bot.on(events.ChatAction())
        async def leave_handler(event):
            if not self.is_active or self.is_completed or not self.join_time or self.min_duration <= 0:
                return
                
            # Kanaldan ayrılma olayı mı kontrol et
            if event.user_left or event.user_kicked:
                try:
                    # Kullanıcıyı kontrol et
                    user_id = str(utils.get_peer_id(event.user_id))
                    if user_id != self.user_id:
                        return
                        
                    # Kanalı kontrol et
                    chat_id = str(utils.get_peer_id(event.chat_id))
                    
                    # Doğru kanaldan ayrılma olayı mı kontrol et
                    if self.channel_id and chat_id == self.channel_id:
                        current_time = int(time.time())
                        duration = current_time - self.join_time
                        
                        logger.info(f"Kanaldan ayrılma algılandı: {self.user_id}, kanal: {self.channel_username}, süre: {duration}s")
                        
                        # Minimum süre kontrolü
                        if duration >= self.min_duration:
                            await self._complete_task()
                        else:
                            # Minimum süreyi tamamlamadan ayrıldı, sıfırla
                            self.join_time = None
                            logger.info(f"Kullanıcı minimum süreyi tamamlamadan ayrıldı: {self.user_id}")
                            
                except Exception as e:
                    logger.error(f"Ayrılma olayı kontrolünde hata: {e}")
        
        self._join_handler = join_handler
        self._leave_handler = leave_handler
        
        # Periyodik kontrol için zamanlayıcı başlat (minimum süre varsa)
        if self.min_duration > 0 and self.join_time:
            self.bot.loop.create_task(self._check_duration_timer())
    
    async def _check_duration_timer(self):
        """Minimum süreyi kontrol etmek için periyodik zamanlayıcı"""
        while self.is_active and not self.is_completed and self.join_time:
            current_time = int(time.time())
            duration = current_time - self.join_time
            
            # Minimum süreyi geçti mi kontrol et
            if duration >= self.min_duration:
                # Hala üye mi kontrol et
                is_still_member = await self._check_membership()
                if is_still_member:
                    await self._complete_task()
                break
                
            # Her 30 saniyede bir kontrol et
            await asyncio.sleep(30)
    
    async def _complete_task(self):
        """Görevi tamamla"""
        if not self.is_completed:
            self.is_completed = True
            
            # Doğrulama motoruna bildir
            await self.verification_engine.verify_task(self.user_id, self.task_id, True)
            
            # Kullanıcıya tebrik mesajı gönder
            try:
                await self.bot.send_message(
                    int(self.user_id),
                    f"✅ Tebrikler! {self.channel_username} kanalına katılma görevini başarıyla tamamladınız."
                )
            except Exception as e:
                logger.error(f"Kullanıcıya bildirim gönderilemedi: {e}")
    
    async def stop_listening(self):
        """Kanal katılma olaylarını dinlemeyi durdur"""
        if self._join_handler:
            logger.info(f"Kanala katılma görevi dinleyicisi durduruluyor: {self.user_id}_{self.task_id}")
            self.bot.remove_event_handler(self._join_handler)
            self._join_handler = None
            
        if self._leave_handler:
            self.bot.remove_event_handler(self._leave_handler)
            self._leave_handler = None
    
    async def verify_manually(self, admin_id: str) -> bool:
        """
        Görevi manuel olarak doğrula
        
        Args:
            admin_id: Yönetici ID'si
            
        Returns:
            bool: Doğrulama başarılı ise True
        """
        logger.info(f"Kanala katılma görevi manuel doğrulandı: {self.user_id}_{self.task_id} (admin: {admin_id})")
        
        self.is_completed = True
        
        # Bot aracılığıyla kullanıcıya bildir
        try:
            await self.bot.send_message(
                int(self.user_id),
                f"✅ Tebrikler! {self.channel_username} kanalına katılma göreviniz bir yönetici tarafından onaylandı."
            )
        except Exception as e:
            logger.error(f"Kullanıcıya bildirim gönderilemedi: {e}")
        
        return True 