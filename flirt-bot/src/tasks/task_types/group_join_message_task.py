#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Group Join & Message Task - Grup Katılma ve İlk Mesaj Görevi
Kullanıcının bir gruba katılıp ilk mesajını göndermesini doğrulayan görev tipi
"""

import logging
from typing import Dict, Any, Optional, Union
import time
import asyncio

from telethon import events, utils
from telethon.tl.functions.messages import GetFullChatRequest

from ..base_task import BaseTask

logger = logging.getLogger(__name__)

class GroupJoinMessageTask(BaseTask):
    """Kullanıcının bir gruba katılıp ilk mesajını göndermesini gerektiren görev."""
    
    def __init__(
        self,
        user_id: str,
        task_id: str,
        expiry_time: int,
        verification_engine,
        bot,
        group_id: Optional[Union[str, int]] = None,
        group_username: Optional[str] = None,
        min_length: int = 0,
        max_time: int = 3600,  # Katılımdan sonra mesaj göndermek için maksimum süre (varsayılan: 1 saat)
        **kwargs
    ):
        """
        GroupJoinMessageTask yapıcısı
        
        Args:
            user_id: Kullanıcı ID'si
            task_id: Görev ID'si
            expiry_time: Görevin geçerlilik süresi (Unix timestamp)
            verification_engine: Görev doğrulama motoru
            bot: Bot istemcisi
            group_id: Hedef grup ID'si (isteğe bağlı, group_username ile birlikte en az biri gerekli)
            group_username: Hedef grup kullanıcı adı (isteğe bağlı, group_id ile birlikte en az biri gerekli)
            min_length: Minimum mesaj uzunluğu (isteğe bağlı)
            max_time: Katılımdan sonra mesaj göndermek için maksimum süre (saniye)
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
        
        self.group_id = str(group_id) if group_id else None
        self.group_username = group_username.lstrip('@') if group_username else None
        self.min_length = min_length
        self.max_time = max_time
        
        # En az bir grup tanımlayıcısı gerekli
        if not self.group_id and not self.group_username:
            raise ValueError("group_id veya group_username parametrelerinden en az biri gereklidir")
        
        # Durum izleme
        self.joined = False
        self.join_time = None
        self.sent_message = False
        self._join_handler = None
        self._message_handler = None
        self._timeout_task = None
        
        logger.info(f"GroupJoinMessageTask oluşturuldu: {self.user_id} için grup katılma ve mesaj gönderme görevi")
    
    async def start_listening(self):
        """Grup katılma ve mesaj olaylarını dinlemeye başla"""
        if self._join_handler or self._message_handler:
            return
            
        # Grup katılımını dinle
        @self.bot.on(events.ChatAction())
        async def on_chat_action(event):
            if not self.is_active or self.is_completed:
                return
                
            # Sadece kullanıcı katılma olaylarını işle
            if not (event.user_joined or event.user_added):
                return
                
            try:
                # Kullanıcıyı kontrol et
                joined_user = await event.get_user()
                if not joined_user or str(joined_user.id) != self.user_id:
                    return
                
                # Grubu kontrol et
                chat = await event.get_chat()
                chat_id = str(chat.id)
                chat_username = getattr(chat, 'username', '').lower()
                
                # Hedef grup kontrolü
                is_target_group = False
                
                if self.group_id and chat_id == self.group_id:
                    is_target_group = True
                elif self.group_username and chat_username == self.group_username.lower():
                    is_target_group = True
                    # Grup ID'yi güncelle (sonraki mesaj kontrolü için)
                    self.group_id = chat_id
                
                if not is_target_group:
                    return
                    
                # Katılma olayı doğrulandı
                logger.info(f"Grup katılımı algılandı: {self.user_id}, grup: {chat_id}")
                self.joined = True
                self.join_time = int(time.time())
                
                # Zaman aşımı görevi başlat
                self._timeout_task = asyncio.create_task(self._set_max_time_timer())
                
                # Kullanıcıya mesaj gönderme hatırlatması gönder
                try:
                    await self.bot.send_message(
                        int(self.user_id),
                        f"👋 Gruba katıldınız! Görevi tamamlamak için gruba bir mesaj göndermeniz gerekiyor."
                    )
                except Exception as e:
                    logger.error(f"Hatırlatma mesajı gönderilirken hata: {e}")
                
            except Exception as e:
                logger.error(f"Grup katılımı kontrolünde hata: {e}")
        
        self._join_handler = on_chat_action
        
        # Kullanıcı mesajlarını dinle
        @self.bot.on(events.NewMessage())
        async def on_message(event):
            if not self.is_active or self.is_completed or not self.joined:
                return
                
            try:
                # Kullanıcı ID'sini kontrol et
                if event.sender_id != int(self.user_id):
                    return
                    
                # Grup ID'sini kontrol et
                chat = await event.get_chat()
                chat_id = str(chat.id)
                
                # Hedef grup kontrolü
                if self.group_id and chat_id != self.group_id:
                    return
                
                # Mesaj içeriğini kontrol et
                message_text = event.message.text or ""
                
                # Minimum uzunluğu kontrol et
                if len(message_text) < self.min_length:
                    logger.debug(f"Mesaj çok kısa: {len(message_text)}, minimum: {self.min_length}")
                    # Kullanıcıya bildirim göndermeyi de düşünebilirsiniz
                    return
                
                # Mesaj gönderme başarılı
                logger.info(f"Grup mesajı algılandı: {self.user_id}, grup: {chat_id}")
                self.sent_message = True
                
                # Görevi tamamla
                await self._complete_task()
                
            except Exception as e:
                logger.error(f"Mesaj kontrolünde hata: {e}")
                
        self._message_handler = on_message
        
        # Kullanıcı zaten grupta mı kontrol et
        await self._check_already_in_group()
        
        logger.info(f"Grup katılma ve mesaj dinleme başlatıldı: {self.user_id}")
    
    async def _check_already_in_group(self):
        """Kullanıcının zaten grupta olup olmadığını kontrol et"""
        try:
            # Önce grup kimliğini bul
            if not self.group_id and self.group_username:
                try:
                    entity = await self.bot.get_entity(f"@{self.group_username}")
                    self.group_id = str(utils.get_peer_id(entity))
                except Exception as e:
                    logger.error(f"Grup kimliği çözümlenemedi: {e}")
                    return
            
            # Kullanıcı grup üyesi mi kontrol et
            if self.group_id:
                chat_id = int(self.group_id)
                
                try:
                    # Grup katılımcılarını alma (çok büyük gruplar için çalışmayabilir)
                    participants = await self.bot.get_participants(chat_id, search=self.user_id, limit=1)
                    
                    if len(participants) > 0:
                        # Kullanıcı zaten grupta
                        self.joined = True
                        self.join_time = int(time.time())
                        logger.info(f"Kullanıcı zaten grupta: {self.user_id}, grup: {self.group_id}")
                        
                        # Zaman aşımı görevi başlat
                        self._timeout_task = asyncio.create_task(self._set_max_time_timer())
                        
                        # Kullanıcıya mesaj gönderme hatırlatması gönder
                        try:
                            await self.bot.send_message(
                                int(self.user_id),
                                f"👋 Zaten gruptasınız! Görevi tamamlamak için gruba bir mesaj göndermeniz gerekiyor."
                            )
                        except Exception as e:
                            logger.error(f"Hatırlatma mesajı gönderilirken hata: {e}")
                        
                except Exception as e:
                    logger.error(f"Grup üyeliği kontrolünde hata: {e}")
        
        except Exception as e:
            logger.error(f"Mevcut grup üyeliği kontrolünde hata: {e}")
    
    async def _set_max_time_timer(self):
        """Katılımdan sonra mesaj göndermek için maksimum süre zamanlayıcısı"""
        try:
            await asyncio.sleep(self.max_time)
            
            # Süre doldu ve hala mesaj gönderilmediyse görevi tamamlayamadı
            if self.is_active and not self.is_completed and self.joined and not self.sent_message:
                logger.info(f"Mesaj gönderme süresi doldu: {self.user_id}, grup: {self.group_id}")
                
                # Kullanıcıya bildir
                try:
                    await self.bot.send_message(
                        int(self.user_id),
                        f"⏰ Gruba katıldıktan sonra mesaj gönderme süresi doldu. Görevi tamamlamak için lütfen tekrar deneyin."
                    )
                except Exception as e:
                    logger.error(f"Süre aşımı mesajı gönderilirken hata: {e}")
        
        except asyncio.CancelledError:
            # Normal iptal
            pass
        except Exception as e:
            logger.error(f"Zaman aşımı kontrolünde hata: {e}")
    
    async def _complete_task(self):
        """Görevi tamamla"""
        if not self.is_active or self.is_completed:
            return
            
        # Görevi tamamlandı olarak işaretle
        success = await self.verification_engine.verify_task(self.user_id, self.task_id)
        
        if success:
            self.is_completed = True
            
            # Zaman aşımı görevini iptal et
            if self._timeout_task:
                self._timeout_task.cancel()
                try:
                    await self._timeout_task
                except asyncio.CancelledError:
                    pass
                self._timeout_task = None
            
            # Kullanıcıya bildirim gönder
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
                    f"🎉 Tebrikler! {group_name} grubuna katılma ve mesaj gönderme görevini başarıyla tamamladınız."
                )
            except Exception as e:
                logger.error(f"Bildirim gönderme hatası: {e}")
            
            logger.info(f"Grup katılma ve mesaj görevi tamamlandı: {self.user_id}_{self.task_id}")
        else:
            logger.error(f"Görev tamamlama hatası: {self.user_id}_{self.task_id}")
    
    async def stop_listening(self):
        """Grup katılma ve mesaj olaylarını dinlemeyi durdur"""
        if self._join_handler:
            self.bot.remove_event_handler(self._join_handler)
            self._join_handler = None
        
        if self._message_handler:
            self.bot.remove_event_handler(self._message_handler)
            self._message_handler = None
            
        if self._timeout_task:
            self._timeout_task.cancel()
            try:
                await self._timeout_task
            except asyncio.CancelledError:
                pass
            self._timeout_task = None
            
        logger.info(f"Grup katılma ve mesaj dinleme durduruldu: {self.user_id}")
    
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
            
            # İzlemeyi durdur
            await self.stop_listening()
            
            # Kullanıcıya bildirim gönder
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
                    f"🎉 Tebrikler! {group_name} grubuna katılma ve mesaj gönderme göreviniz bir yönetici tarafından onaylandı."
                )
            except Exception as e:
                logger.error(f"Bildirim gönderme hatası: {e}")
            
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