#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bot Etiketleme Görevi
Bir kullanıcının bir grup içinde botu etiketlemesini doğrulayan görev sınıfı.
"""

import logging
import re
from typing import Dict, Any, Optional
from telethon import events

from ..base_task import BaseTask

logger = logging.getLogger(__name__)

class BotMentionTask(BaseTask):
    """Belirli bir grupta bot etiketleme görevini doğrulayan sınıf."""
    
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
        BotMentionTask yapıcısı
        
        Args:
            user_id: Kullanıcı ID'si
            task_id: Görev ID'si
            expiry_time: Görevin geçerlilik süresi (Unix timestamp)
            verification_engine: Görev doğrulama motoru referansı
            bot: Bot istemci referansı
            target_group (str, optional): Etiketleme yapılacak hedef grup/kanal
            min_mentions (int, optional): Minimum etiketleme sayısı
        """
        super().__init__(
            user_id=user_id,
            task_id=task_id,
            expiry_time=expiry_time,
            verification_engine=verification_engine,
            bot=bot,
            **kwargs
        )
        
        # Bot etiketleme görevi özellikleri
        self.target_group = kwargs.get("target_group", None)  # Hedef grup/kanal
        self.min_mentions = kwargs.get("min_mentions", 1)  # Minimum etiketleme sayısı
        
        # Bot kullanıcı adını al
        self.bot_username = None
        self._get_bot_username()
        
        # İzleme durumu
        self.mention_count = 0
        
        # Olay dinleyici referansı
        self._handler = None
        
    def _get_bot_username(self):
        """Bot kullanıcı adını al"""
        try:
            # Doğrulama motorundan al
            self.bot_username = getattr(self.verification_engine, 'bot_username', None)
            
            # Eğer yoksa, bot nesnesinden almaya çalış
            if not self.bot_username:
                # Not: Bu asenkron değil, bu yüzden sadece bir fallback
                bot_info = self.bot.get_me()
                if hasattr(bot_info, "username"):
                    self.bot_username = bot_info.username
                else:
                    # Varsayılan değer kullan
                    self.bot_username = "OnlyVipsBot"
                    logger.warning("Bot kullanıcı adı alınamadı, varsayılan kullanılıyor")
            
            logger.info(f"Bot etiketleme görevi için kullanıcı adı: @{self.bot_username}")
            return self.bot_username
        except Exception as e:
            logger.error(f"Bot kullanıcı adı alınırken hata: {e}")
            # Varsayılan değer kullan
            self.bot_username = "OnlyVipsBot"
            return self.bot_username
        
    async def start_listening(self):
        """Bot etiketlemelerini dinlemeye başla"""
        
        logger.info(f"Bot etiketleme görevi dinleyicisi başlatılıyor: {self.user_id}_{self.task_id}")
        
        # Bot kullanıcı adını doğru şekilde almak için 
        if not self.bot_username:
            try:
                # Asenkron olarak bot bilgisini al
                bot_info = await self.bot.get_me()
                self.bot_username = bot_info.username
                logger.info(f"Bot kullanıcı adı asenkron olarak alındı: @{self.bot_username}")
            except Exception as e:
                logger.error(f"Bot kullanıcı adı asenkron olarak alınırken hata: {e}")
                self.bot_username = "OnlyVipsBot"
        
        # Etiketleme deseni oluştur
        mention_pattern = rf"@{self.bot_username}\b"
        
        @self.bot.on(events.NewMessage(incoming=True, pattern=mention_pattern))
        async def mention_handler(event):
            if not self.is_active or self.is_completed:
                return
                
            try:
                # Gönderen kullanıcıyı kontrol et
                sender = await event.get_sender()
                sender_id = str(sender.id)
                
                if sender_id != self.user_id:
                    return
                
                # Grup veya kanal mesajı mı kontrol et
                if not (event.is_group or event.is_channel):
                    return
                
                # Hedef grup belirtilmişse, sadece o grubu kontrol et
                if self.target_group:
                    chat = await event.get_chat()
                    chat_id = str(chat.id)
                    chat_username = getattr(chat, 'username', '')
                    
                    # Hedef grup ID veya kullanıcı adı ile eşleşmiyor
                    if chat_id != self.target_group and chat_username != self.target_group:
                        if not chat_username or (self.target_group not in ["@" + chat_username, chat_username]):
                            return
                
                # Etiketleme sayısını artır
                self.mention_count += 1
                logger.info(f"Bot etiketleme algılandı: {self.user_id}, sayı: {self.mention_count}/{self.min_mentions}")
                
                # Minimum etiketleme sayısına ulaşıldıysa görevi tamamla
                if self.mention_count >= self.min_mentions:
                    await self._complete_task(event)
                    
            except Exception as e:
                logger.error(f"Bot etiketleme kontrolünde hata: {e}")
        
        self._handler = mention_handler
        
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
                        await event.reply("✅ Bot etiketleme göreviniz başarıyla tamamlandı ve ödülünüz verildi!")
                    except Exception as e:
                        logger.error(f"Grup içinde bildirim gönderilemedi: {e}")
                
                # Her durumda özel mesaj gönder
                from telethon import Button
                miniapp_url = f"https://t.me/{self.bot_username}/app?startapp={self.user_id}"
                
                await self.bot.send_message(
                    int(self.user_id),
                    f"🎉 Bot etiketleme göreviniz başarıyla tamamlandı! Daha fazla görev için MiniApp'i ziyaret edebilirsiniz.",
                    buttons=[Button.url("🚀 OnlyVips MiniApp", miniapp_url)]
                )
            except Exception as e:
                logger.error(f"Kullanıcıya bildirim gönderilemedi: {e}")
        
    async def stop_listening(self):
        """Bot etiketleme olaylarını dinlemeyi durdur"""
        if self._handler:
            logger.info(f"Bot etiketleme görevi dinleyicisi durduruluyor: {self.user_id}_{self.task_id}")
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
        logger.info(f"Bot etiketleme görevi manuel doğrulandı: {self.user_id}_{self.task_id} (admin: {admin_id})")
        
        self.is_completed = True
        
        # Bot aracılığıyla kullanıcıya bildir
        try:
            await self.bot.send_message(
                int(self.user_id),
                f"✅ Tebrikler! Bot etiketleme göreviniz bir yönetici tarafından onaylandı."
            )
        except Exception as e:
            logger.error(f"Kullanıcıya bildirim gönderilemedi: {e}")
        
        return True 