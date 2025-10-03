#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Kanala Katılma Görevi (getChatMember metodu ile)
Bir kullanıcının belirli bir Telegram kanalına üye olup olmadığını kontrol eden görev sınıfı.
"""

import logging
import time
from typing import Dict, Any, Optional, Union
import asyncio

from telethon import events, utils
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipant, ChannelParticipantAdmin, ChannelParticipantCreator

from ..base_task import BaseTask

logger = logging.getLogger(__name__)

class ChannelJoinTask(BaseTask):
    """Belirli bir kanala katılma görevini doğrulayan sınıf."""
    
    def __init__(
        self,
        user_id: str,
        task_id: str,
        expiry_time: int,
        verification_engine,
        bot,
        channel_username: str,
        min_duration: int = 0,
        check_interval: int = 300,  # 5 dakikada bir kontrol et
        **kwargs
    ):
        """
        ChannelJoinTask yapıcısı
        
        Args:
            user_id: Kullanıcı ID'si
            task_id: Görev ID'si
            expiry_time: Görevin geçerlilik süresi (Unix timestamp)
            verification_engine: Görev doğrulama motoru referansı
            bot: Bot istemci referansı
            channel_username (str): Katılınacak kanal kullanıcı adı (@ işareti olmadan)
            min_duration (int, optional): Kanalda kalınması gereken minimum süre (saniye)
            check_interval (int, optional): Kontrol aralığı (saniye)
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
        
        # Kanal bilgileri
        self.channel_username = channel_username.lstrip('@')  # @ işaretini kaldır
        self.channel_id = None
        self.min_duration = min_duration
        self.check_interval = check_interval
        
        # İzleme durumu
        self.join_time = None
        self.check_task = None
        
        logger.info(f"ChannelJoinTask oluşturuldu: {self.user_id} için {self.channel_username} kanalına katılma")
    
    async def _resolve_channel_id(self):
        """Kanal kullanıcı adını ID'ye çözümle"""
        try:
            entity = await self.bot.get_entity(f"@{self.channel_username}")
            self.channel_id = utils.get_peer_id(entity)
            logger.info(f"Kanal ID çözümlendi: {self.channel_username} -> {self.channel_id}")
            return self.channel_id
        except Exception as e:
            logger.error(f"Kanal ID çözümlenemedi: {self.channel_username}, hata: {e}")
            return None
    
    async def _check_membership(self) -> bool:
        """
        getChatMember metodu ile kullanıcının kanala üyeliğini kontrol et
        
        Returns:
            bool: Kullanıcı kanalın üyesiyse True, değilse False
        """
        if not self.channel_id:
            await self._resolve_channel_id()
            if not self.channel_id:
                return False
        
        try:
            # GetParticipantRequest fonksiyonu ile üyelik kontrolü
            participant = await self.bot(GetParticipantRequest(
                channel=self.channel_id,
                participant=int(self.user_id)
            ))
            
            # Katılımcı türünü kontrol et
            member_status = "unknown"
            is_member = False
            
            if isinstance(participant.participant, ChannelParticipant):
                member_status = "member"
                is_member = True
            elif isinstance(participant.participant, ChannelParticipantAdmin):
                member_status = "administrator"
                is_member = True
            elif isinstance(participant.participant, ChannelParticipantCreator):
                member_status = "creator"
                is_member = True
                
            logger.info(f"Kanal üyelik kontrolü: {self.user_id} için {self.channel_username}, durum: {member_status}")
            return is_member
        
        except Exception as e:
            logger.error(f"Üyelik kontrolünde hata: {e}")
            return False
    
    async def _periodic_check(self):
        """Periyodik üyelik kontrolü yap"""
        while self.is_active and not self.is_completed:
            try:
                is_member = await self._check_membership()
                
                if is_member:
                    # İlk kez katıldıysa, katılma zamanını kaydet
                    if not self.join_time:
                        self.join_time = int(time.time())
                        logger.info(f"Kullanıcı kanala katıldı: {self.user_id}, kanal: {self.channel_username}")
                        
                        # Minimum süre yoksa hemen tamamla
                        if self.min_duration <= 0:
                            await self._complete_task()
                            break
                    
                    # Minimum süreyi kontrol et
                    elif self.min_duration > 0:
                        current_time = int(time.time())
                        duration = current_time - self.join_time
                        
                        if duration >= self.min_duration:
                            logger.info(f"Minimum süre tamamlandı: {self.user_id}, süre: {duration}s")
                            await self._complete_task()
                            break
                else:
                    # Üye değilse ve daha önce üye olduysa, sıfırla
                    if self.join_time:
                        logger.info(f"Kullanıcı kanaldan ayrıldı: {self.user_id}, kanal: {self.channel_username}")
                        self.join_time = None
            
            except Exception as e:
                logger.error(f"Periyodik kontrol hatası: {e}")
            
            # Bir sonraki kontrole kadar bekle
            await asyncio.sleep(self.check_interval)
    
    async def _complete_task(self):
        """Görevi tamamla"""
        if not self.is_active or self.is_completed:
            return
            
        # Görevi tamamlandı olarak işaretle
        success = await self.verification_engine.verify_task(self.user_id, self.task_id)
        
        if success:
            self.is_completed = True
            
            # Kullanıcıya bildirim gönder
            try:
                await self.bot.send_message(
                    int(self.user_id),
                    f"🎉 Tebrikler! '{self.channel_username}' kanalına katılma görevini başarıyla tamamladınız."
                )
            except Exception as e:
                logger.error(f"Bildirim gönderme hatası: {e}")
            
            logger.info(f"Kanal katılma görevi tamamlandı: {self.user_id}_{self.task_id}")
        else:
            logger.error(f"Görev tamamlama hatası: {self.user_id}_{self.task_id}")
    
    async def start_listening(self):
        """Kanal katılma durumunu izlemeye başla"""
        if self.check_task:
            return
            
        # İlk durumu kontrol et
        is_member = await self._check_membership()
        if is_member:
            logger.info(f"Kullanıcı zaten kanalda: {self.user_id}, kanal: {self.channel_username}")
            self.join_time = int(time.time())
            
            # Minimum süre yoksa hemen tamamla
            if self.min_duration <= 0:
                await self._complete_task()
                return
        
        # Periyodik kontrol görevini başlat
        self.check_task = asyncio.create_task(self._periodic_check())
        logger.info(f"Kanal katılma görevi izleme başlatıldı: {self.user_id}_{self.task_id}")
    
    async def stop_listening(self):
        """Kanal katılma durumunu izlemeyi durdur"""
        if self.check_task:
            self.check_task.cancel()
            try:
                await self.check_task
            except asyncio.CancelledError:
                pass
            self.check_task = None
            logger.info(f"Kanal katılma görevi izleme durduruldu: {self.user_id}_{self.task_id}")
    
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
            
            # İzlemeyi durdur
            await self.stop_listening()
            
            # Kullanıcıya bildirim gönder
            await self.bot.send_message(
                int(self.user_id),
                f"🎉 Tebrikler! '{self.channel_username}' kanalına katılma göreviniz bir yönetici tarafından onaylandı."
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