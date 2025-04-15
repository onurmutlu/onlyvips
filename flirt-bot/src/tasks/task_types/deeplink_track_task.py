#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Link Takip Görevi
Bir kullanıcının bot bağlantısı veya proje linki paylaşmasını doğrulayan görev sınıfı.
"""

import logging
import re
from typing import Dict, Any, Optional, List
from telethon import events
from telethon.tl.types import MessageEntityUrl, MessageEntityTextUrl

from ..base_task import BaseTask

logger = logging.getLogger(__name__)

class DeeplinkTrackTask(BaseTask):
    """Link paylaşımı görevini doğrulayan sınıf."""
    
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
        DeeplinkTrackTask yapıcısı
        
        Args:
            user_id: Kullanıcı ID'si
            task_id: Görev ID'si
            expiry_time: Görevin geçerlilik süresi (Unix timestamp)
            verification_engine: Görev doğrulama motoru referansı
            bot: Bot istemci referansı
            domains (List[str], optional): İzlenen alan adları
            target_group (str, optional): Paylaşım yapılacak hedef grup/kanal
            require_custom_text (bool, optional): Özel metin gerekli mi
            min_shares (int, optional): Minimum paylaşım sayısı
        """
        super().__init__(
            user_id=user_id,
            task_id=task_id,
            expiry_time=expiry_time,
            verification_engine=verification_engine,
            bot=bot,
            **kwargs
        )
        
        # Link takip görevi özellikleri
        self.domains = kwargs.get("domains", ["t.me", "onlyvips.com"])  # İzlenen alan adları
        self.target_group = kwargs.get("target_group", None)  # Hedef grup/kanal
        self.require_custom_text = kwargs.get("require_custom_text", False)  # Özel metin gerekli mi
        self.min_shares = kwargs.get("min_shares", 1)  # Minimum paylaşım sayısı
        
        # Bot kullanıcı adını al
        self.bot_username = getattr(verification_engine, 'bot_username', "OnlyVipsBot")
        
        # İzleme durumu
        self.share_count = 0
        
        # Olay dinleyici referansı
        self._handler = None
        
    async def start_listening(self):
        """Link paylaşım olaylarını dinlemeye başla"""
        
        logger.info(f"Link takip görevi dinleyicisi başlatılıyor: {self.user_id}_{self.task_id}")
        
        # URL içeren mesajları dinle
        @self.bot.on(events.NewMessage(from_users=int(self.user_id), pattern=r"https?://[^\s]+"))
        async def link_handler(event):
            if not self.is_active or self.is_completed:
                return
                
            try:
                # Mesajın içeriğini ve linklerini kontrol et
                message = event.message
                
                # Mesaj varlıklarını (entities) kontrol et
                if not message.entities:
                    return
                
                # Grup kontrolü yap
                if self.target_group:
                    chat = await event.get_chat()
                    chat_id = str(chat.id)
                    chat_username = getattr(chat, 'username', '')
                    
                    # Hedef grup ID veya kullanıcı adı ile eşleşmiyor
                    if chat_id != self.target_group and chat_username != self.target_group:
                        if not chat_username or (self.target_group not in ["@" + chat_username, chat_username]):
                            return
                
                # URL'leri kontrol et
                valid_domains_found = False
                for entity in message.entities:
                    if isinstance(entity, (MessageEntityUrl, MessageEntityTextUrl)):
                        # Entity'den URL'yi çıkar
                        if isinstance(entity, MessageEntityUrl):
                            url = message.text[entity.offset:entity.offset + entity.length]
                        else:  # MessageEntityTextUrl
                            url = entity.url
                        
                        # URL beklenen alan adlarından birini içeriyor mu?
                        for domain in self.domains:
                            if domain in url:
                                # Bot kullanıcı adını kontrol et
                                if domain == "t.me" and self.bot_username:
                                    # Spesifik olarak bot username'ı var mı?
                                    if f"t.me/{self.bot_username}" in url:
                                        valid_domains_found = True
                                        break
                                else:
                                    valid_domains_found = True
                                    break
                        
                        if valid_domains_found:
                            break
                
                # Geçerli bir domain bulunduysa
                if valid_domains_found:
                    # Özel metin gerekli mi?
                    if self.require_custom_text:
                        # Mesajda sadece link olmasın, en az bir kaç kelime daha olsun
                        text_without_urls = message.text
                        for entity in message.entities:
                            if isinstance(entity, (MessageEntityUrl, MessageEntityTextUrl)):
                                start = entity.offset
                                end = entity.offset + entity.length
                                text_without_urls = text_without_urls[:start] + text_without_urls[end:]
                        
                        # Kalan metini temizle ve boş mu kontrol et
                        text_without_urls = text_without_urls.strip()
                        if len(text_without_urls.split()) < 2:  # En az 2 kelime olsun
                            logger.info(f"Link paylaşıldı ama yeterli metin yok: {self.user_id}")
                            return
                    
                    # Paylaşım sayısını artır
                    self.share_count += 1
                    logger.info(f"Link paylaşımı tespit edildi: {self.user_id}, sayı: {self.share_count}/{self.min_shares}")
                    
                    # Minimum paylaşım sayısına ulaşıldıysa görevi tamamla
                    if self.share_count >= self.min_shares:
                        await self._complete_task(event)
                
            except Exception as e:
                logger.error(f"Link kontrolünde hata: {e}")
        
        self._handler = link_handler
        
    async def _complete_task(self, event=None):
        """Görevi tamamla"""
        if not self.is_completed:
            self.is_completed = True
            
            # Doğrulama motoruna bildir
            await self.verification_engine.verify_task(self.user_id, self.task_id, True)
            
            # Kullanıcıya tebrik mesajı gönder
            try:
                # Eğer event varsa ve grup içindeyse, yanıt ver
                if event:
                    try:
                        await event.reply("✅ Link paylaşım göreviniz başarıyla tamamlandı ve ödülünüz verildi!")
                    except Exception as e:
                        logger.error(f"Grup içinde bildirim gönderilemedi: {e}")
                
                # Her durumda özel mesaj gönder
                from telethon import Button
                miniapp_url = f"https://t.me/{self.bot_username}/app?startapp={self.user_id}"
                
                await self.bot.send_message(
                    int(self.user_id),
                    f"🔗 Link paylaşım göreviniz başarıyla tamamlandı ve ödülünüz verildi! Daha fazla görev için MiniApp'i ziyaret edebilirsiniz.",
                    buttons=[Button.url("🚀 OnlyVips MiniApp", miniapp_url)]
                )
            except Exception as e:
                logger.error(f"Kullanıcıya bildirim gönderilemedi: {e}")
        
    async def stop_listening(self):
        """Link paylaşım olaylarını dinlemeyi durdur"""
        if self._handler:
            logger.info(f"Link takip görevi dinleyicisi durduruluyor: {self.user_id}_{self.task_id}")
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
        logger.info(f"Link paylaşım görevi manuel doğrulandı: {self.user_id}_{self.task_id} (admin: {admin_id})")
        
        self.is_completed = True
        
        # Bot aracılığıyla kullanıcıya bildir
        try:
            await self.bot.send_message(
                int(self.user_id),
                f"✅ Tebrikler! Link paylaşım göreviniz bir yönetici tarafından onaylandı."
            )
        except Exception as e:
            logger.error(f"Kullanıcıya bildirim gönderilemedi: {e}")
        
        return True 