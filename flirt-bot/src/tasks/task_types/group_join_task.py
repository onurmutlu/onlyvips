#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Grup Katılma Görevi
Bir kullanıcının belirli bir gruba katılmasını doğrulayan görev sınıfı.
"""

import logging
import time
from typing import Dict, Any, Optional
from telethon import events, utils
from telethon.tl.functions.messages import GetFullChatRequest

from ..base_task import BaseTask

logger = logging.getLogger(__name__)

class GroupJoinTask(BaseTask):
    """Belirli bir gruba katılma görevini doğrulayan sınıf."""
    
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
        GroupJoinTask yapıcısı
        
        Args:
            user_id: Kullanıcı ID'si
            task_id: Görev ID'si
            expiry_time: Görevin geçerlilik süresi (Unix timestamp)
            verification_engine: Görev doğrulama motoru referansı
            bot: Bot istemci referansı
            group_id (str): Katılınacak grup ID'si
            group_username (str, optional): Katılınacak grubun kullanıcı adı
            min_duration (int, optional): Grupta kalınması gereken minimum süre (saniye)
        """
        super().__init__(
            user_id=user_id,
            task_id=task_id,
            expiry_time=expiry_time,
            verification_engine=verification_engine,
            bot=bot,
            **kwargs
        )
        
        # Grup katılma görevi özellikleri
        self.group_id = kwargs.get("group_id", None)  # Hedef grup ID
        self.group_username = kwargs.get("group_username", None)  # Hedef grup kullanıcı adı
        
        # En az birinin belirtilmiş olması gerekir
        if not self.group_id and not self.group_username:
            raise ValueError("group_id veya group_username parametrelerinden en az biri gereklidir")
            
        self.min_duration = kwargs.get("min_duration", 0)  # Minimum kalma süresi (saniye)
        
        # Bot kullanıcı adını al
        self.bot_username = getattr(verification_engine, 'bot_username', "OnlyVipsBot")
        
        # İzleme durumu
        self.join_time = None
        
        # Olay dinleyici referansları
        self._join_handler = None
        self._leave_handler = None
        
    async def start_listening(self):
        """Grup katılma olaylarını dinlemeye başla"""
        
        logger.info(f"Grup katılma görevi dinleyicisi başlatılıyor: {self.user_id}_{self.task_id}")
        
        # İlk durum kontrolü - kullanıcı zaten grupta olabilir
        is_member = await self._check_membership()
        if is_member:
            logger.info(f"Kullanıcı zaten grupta: {self.user_id}")
            self.join_time = int(time.time())
            
            # Minimum süre yoksa hemen tamamla
            if self.min_duration <= 0:
                await self._complete_task()
        
        # Katılma olaylarını dinle
        @self.bot.on(events.ChatAction())
        async def join_handler(event):
            if not self.is_active or self.is_completed:
                return
                
            # Katılma olayı mı kontrol et
            if not (event.user_joined or event.user_added):
                return
            
            try:
                # Kullanıcıyı kontrol et
                joined_user = await event.get_user()
                if not joined_user:
                    return
                    
                user_id = str(joined_user.id)
                if user_id != self.user_id:
                    return
                
                # Grubu kontrol et
                chat = await event.get_chat()
                chat_id = str(chat.id)
                chat_username = getattr(chat, 'username', '')
                
                # Hedef grup kontrolü
                is_target_group = False
                
                if self.group_id and chat_id == self.group_id:
                    is_target_group = True
                elif self.group_username:
                    normalized_username = self.group_username.lower().replace('@', '')
                    if chat_username.lower() == normalized_username:
                        is_target_group = True
                
                if not is_target_group:
                    return
                    
                # Katılma olayı doğrulandı
                logger.info(f"Grup katılımı algılandı: {self.user_id}, grup: {chat_id}")
                self.join_time = int(time.time())
                
                # Minimum süre yoksa hemen tamamla
                if self.min_duration <= 0:
                    await self._complete_task()
                    
            except Exception as e:
                logger.error(f"Grup katılımı kontrolünde hata: {e}")
        
        # Eğer minimum süre varsa, ayrılma olaylarını da dinle
        if self.min_duration > 0:
            @self.bot.on(events.ChatAction())
            async def leave_handler(event):
                if not self.is_active or self.is_completed or not self.join_time:
                    return
                    
                # Ayrılma olayı mı kontrol et
                if not (event.user_left or event.user_kicked):
                    return
                
                try:
                    # Kullanıcıyı kontrol et
                    left_user = await event.get_user()
                    if not left_user:
                        return
                        
                    user_id = str(left_user.id)
                    if user_id != self.user_id:
                        return
                    
                    # Grubu kontrol et
                    chat = await event.get_chat()
                    chat_id = str(chat.id)
                    chat_username = getattr(chat, 'username', '')
                    
                    # Hedef grup kontrolü
                    is_target_group = False
                    
                    if self.group_id and chat_id == self.group_id:
                        is_target_group = True
                    elif self.group_username:
                        normalized_username = self.group_username.lower().replace('@', '')
                        if chat_username.lower() == normalized_username:
                            is_target_group = True
                    
                    if not is_target_group:
                        return
                        
                    # Ayrılma olayı doğrulandı
                    current_time = int(time.time())
                    duration = current_time - self.join_time
                    
                    logger.info(f"Gruptan ayrılma algılandı: {self.user_id}, grup: {chat_id}, süre: {duration}s")
                    
                    # Minimum süre kontrolü
                    if duration >= self.min_duration:
                        await self._complete_task()
                    else:
                        # Minimum süreyi tamamlamadan ayrıldı, sıfırla
                        self.join_time = None
                        logger.info(f"Kullanıcı minimum süreyi tamamlamadan ayrıldı: {self.user_id}")
                        
                except Exception as e:
                    logger.error(f"Grup ayrılma kontrolünde hata: {e}")
            
            self._leave_handler = leave_handler
        
        self._join_handler = join_handler
        
        # Periyodik kontrol için zamanlayıcı başlat (minimum süre varsa)
        if self.min_duration > 0 and self.join_time:
            self.bot.loop.create_task(self._check_duration_timer())
    
    async def _check_membership(self) -> bool:
        """Kullanıcının grup üyeliğini kontrol et"""
        try:
            # Grup ID yoksa kullanıcı adından bulmaya çalış
            if not self.group_id and self.group_username:
                try:
                    group_entity = await self.bot.get_entity(self.group_username)
                    self.group_id = str(utils.get_peer_id(group_entity))
                except Exception as e:
                    logger.error(f"Grup bilgisi alınamadı: {self.group_username}, hata: {e}")
                    return False
            
            # Grup bilgisi al
            chat_id = int(self.group_id)
            
            try:
                # Grup katılımcılarını alma (çok büyük gruplar için çalışmayabilir)
                participants = await self.bot.get_participants(chat_id, search=self.user_id, limit=1)
                return len(participants) > 0
            except Exception as e:
                # Alternatif yöntem: Kullanıcı varlığını doğrulamak için mesaj geçmişini kontrol et
                logger.warning(f"Grup üyeliği doğrudan kontrol edilemedi: {e}, alternatif yöntem deneniyor")
                
                try:
                    # Kullanıcı varlığını doğrulamak için mesaj geçmişini kontrol et
                    messages = await self.bot.get_messages(chat_id, from_user=int(self.user_id), limit=1)
                    return len(messages) > 0
                except Exception as e2:
                    logger.error(f"Kullanıcı grupta mesaj göndermiş mi kontrolü başarısız: {e2}")
                    return False
                
        except Exception as e:
            logger.error(f"Grup üyeliği kontrolünde hata: {e}")
            return False
    
    async def _check_duration_timer(self):
        """Minimum süreyi kontrol etmek için periyodik zamanlayıcı"""
        import asyncio
        
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
                from telethon import Button
                miniapp_url = f"https://t.me/{self.bot_username}/app?startapp={self.user_id}"
                
                # Grup adını bulmaya çalış
                group_name = self.group_username or self.group_id
                try:
                    if self.group_id:
                        group_entity = await self.bot.get_entity(int(self.group_id))
                        if hasattr(group_entity, 'title'):
                            group_name = group_entity.title
                except Exception:
                    pass
                
                await self.bot.send_message(
                    int(self.user_id),
                    f"👥 {group_name} grubuna katılma göreviniz başarıyla tamamlandı ve ödülünüz verildi! Daha fazla görev için MiniApp'i ziyaret edebilirsiniz.",
                    buttons=[Button.url("🚀 OnlyVips MiniApp", miniapp_url)]
                )
            except Exception as e:
                logger.error(f"Kullanıcıya bildirim gönderilemedi: {e}")
    
    async def stop_listening(self):
        """Grup katılma olaylarını dinlemeyi durdur"""
        if self._join_handler:
            logger.info(f"Grup katılım görevi dinleyicisi durduruluyor: {self.user_id}_{self.task_id}")
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
        logger.info(f"Grup katılma görevi manuel doğrulandı: {self.user_id}_{self.task_id} (admin: {admin_id})")
        
        self.is_completed = True
        
        # Bot aracılığıyla kullanıcıya bildir
        try:
            # Grup adını bulmaya çalış
            group_name = self.group_username or self.group_id
            try:
                if self.group_id:
                    group_entity = await self.bot.get_entity(int(self.group_id))
                    if hasattr(group_entity, 'title'):
                        group_name = group_entity.title
            except Exception:
                pass
            
            await self.bot.send_message(
                int(self.user_id),
                f"✅ Tebrikler! {group_name} grubuna katılma göreviniz bir yönetici tarafından onaylandı."
            )
        except Exception as e:
            logger.error(f"Kullanıcıya bildirim gönderilemedi: {e}")
        
        return True 