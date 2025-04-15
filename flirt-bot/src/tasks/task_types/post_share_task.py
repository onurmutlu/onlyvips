#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gönderi Paylaşma Görevi
Bir kullanıcının belirli bir gönderiyi paylaşmasını doğrulayan görev sınıfı.
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from telethon import events, functions, types, utils

from ..base_task import BaseTask

logger = logging.getLogger(__name__)

class PostShareTask(BaseTask):
    """Belirli bir gönderiyi paylaşma görevini doğrulayan sınıf."""
    
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
        PostShareTask yapıcısı
        
        Args:
            user_id: Kullanıcı ID'si
            task_id: Görev ID'si
            expiry_time: Görevin geçerlilik süresi (Unix timestamp)
            verification_engine: Görev doğrulama motoru referansı
            bot: Bot istemci referansı
            post_channel (str): Paylaşılacak gönderinin kanal ID'si veya kullanıcı adı
            post_id (int, optional): Paylaşılacak gönderinin ID'si
            target_type (str, optional): Hedef tür (örn: 'group', 'channel', 'private')
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
        
        # Paylaşım görevi özellikleri
        self.post_channel = kwargs.get("post_channel")
        if not self.post_channel:
            raise ValueError("post_channel parametresi gereklidir")
            
        self.post_id = kwargs.get("post_id")  # Belirli bir mesaj ID yoksa, kanaldan herhangi bir mesaj
        self.target_type = kwargs.get("target_type", "any")  # Paylaşım hedefi türü
        self.min_shares = kwargs.get("min_shares", 1)  # Minimum paylaşım sayısı
        
        # İzleme durumu
        self.share_count = 0
        
        # Bot kullanıcı adını al
        self.bot_username = getattr(verification_engine, 'bot_username', "OnlyVipsBot")
        
        # Olay dinleyici referansı
        self._handler = None
        
    async def start_listening(self):
        """Paylaşım kontrol olaylarını dinlemeye başla"""
        
        logger.info(f"Gönderi paylaşma görevi dinleyicisi başlatılıyor: {self.user_id}_{self.task_id}")
        
        # Komut ile paylaşım kontrolü dinleme
        @self.bot.on(events.NewMessage(pattern=r'^/checkshare(?:\s+|$)'))
        async def check_share_handler(event):
            if not self.is_active or self.is_completed:
                return
                
            try:
                # Komutu gönderen kullanıcıyı kontrol et
                sender = await event.get_sender()
                user_id = str(sender.id)
                
                # Sadece görev sahibi kullanıcıların komutunu işle
                if user_id != self.user_id:
                    return
                
                # Paylaşım doğrulamasını başlat
                await event.respond(f"🔍 Gönderi paylaşımınız kontrol ediliyor...")
                
                # Paylaşımı doğrula
                verified = await self.verify_post_share(user_id)
                
                if verified:
                    await event.respond("✅ Tebrikler! Gönderi paylaşım göreviniz başarıyla tamamlandı ve ödülünüz verildi.")
                else:
                    # Kullanıcıya henüz paylaşmadığını bildir
                    channel_name = self.post_channel
                    if not channel_name.startswith('@'):
                        channel_name = '@' + channel_name
                    
                    post_link = f"https://t.me/{channel_name.replace('@', '')}/{self.post_id}" if self.post_id else f"https://t.me/{channel_name.replace('@', '')}"
                    
                    await event.respond(
                        f"⚠️ Henüz paylaşım yapmamışsınız veya paylaşımınız bulunamadı.\n\n"
                        f"Lütfen {post_link} adresinden bir gönderiyi paylaşın ve tekrar deneyin."
                    )
                
            except Exception as e:
                logger.error(f"Paylaşım kontrol olayında hata: {e}")
                await event.respond("⚠️ Paylaşım kontrolü sırasında bir hata oluştu. Lütfen daha sonra tekrar deneyin.")
        
        self._handler = check_share_handler
        
    async def verify_post_share(self, user_id):
        """Kullanıcının belirli gönderiyi paylaşıp paylaşmadığını doğrula"""
        try:
            # Kullanıcı ID'sini integer'a çevir
            user_id_int = int(user_id)
            
            # Kullanıcının son paylaştığı mesajları al (son 100 mesaj)
            try:
                # Önce kullanıcının varlığını al
                user_entity = await self.bot.get_entity(user_id_int)
                
                # Kullanıcının mesaj geçmişini al
                messages = await self.bot(functions.messages.GetHistoryRequest(
                    peer=user_entity,
                    limit=100,
                    offset_date=None,
                    offset_id=0,
                    max_id=0,
                    min_id=0,
                    add_offset=0,
                    hash=0
                ))
                
                # Paylaşımları kontrol et
                for message in messages.messages:
                    # Paylaşılan mesaj kontrolü
                    if hasattr(message, 'fwd_from') and message.fwd_from:
                        # Paylaşımın kaynağını kontrol et
                        fwd = message.fwd_from
                        
                        # Hedef kanal adını normalize et
                        normalized_channel = self.post_channel.lower()
                        if normalized_channel.startswith('@'):
                            normalized_channel = normalized_channel[1:]
                        
                        # Kanal bilgisi kontrolü
                        is_target_channel = False
                        
                        # Kanal ID veya kullanıcı adı kontrolü
                        if hasattr(fwd, 'from_id') and hasattr(fwd.from_id, 'channel_id'):
                            # Kanal ID ile kontrol
                            channel_id = str(fwd.from_id.channel_id)
                            is_target_channel = (channel_id == normalized_channel or str(utils.get_peer_id(fwd.from_id)) == normalized_channel)
                            
                        elif hasattr(fwd, 'channel_id'):
                            # Eski format için kontrol
                            channel_id = str(fwd.channel_id)
                            is_target_channel = (channel_id == normalized_channel)
                            
                        elif hasattr(fwd, 'from_name'):
                            # İsim kontrolü (tam güvenilir değil)
                            from_name = fwd.from_name.lower()
                            is_target_channel = (normalized_channel in from_name)
                        
                        # Mesaj ID kontrolü
                        is_target_message = True
                        if self.post_id:
                            post_id = str(self.post_id)
                            message_id = str(fwd.channel_post) if hasattr(fwd, 'channel_post') else None
                            is_target_message = (message_id == post_id)
                        
                        # Hedef kanal ve mesaj eşleşiyorsa
                        if is_target_channel and is_target_message:
                            # Hedef türünü kontrol et
                            if self.target_type != "any":
                                chat = await message.get_chat()
                                
                                if self.target_type == "group" and not (chat.is_group or chat.is_megagroup):
                                    continue
                                    
                                if self.target_type == "channel" and not chat.is_channel:
                                    continue
                                    
                                if self.target_type == "private" and (chat.is_group or chat.is_channel):
                                    continue
                            
                            # Paylaşım sayısını artır
                            self.share_count += 1
                            logger.info(f"Gönderi paylaşımı tespit edildi: {self.user_id}, sayı: {self.share_count}/{self.min_shares}")
                            
                            # Minimum paylaşım sayısına ulaşıldıysa görevi tamamla
                            if self.share_count >= self.min_shares:
                                await self._complete_task()
                                return True
                
                return False
                
            except Exception as e:
                logger.error(f"Kullanıcı mesaj geçmişi alınırken hata: {e}")
                return False
            
        except Exception as e:
            logger.error(f"Gönderi paylaşımı doğrulama hatası: {e}")
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
                    f"🔄 Gönderi paylaşma göreviniz başarıyla tamamlandı ve ödülünüz verildi! Daha fazla görev için MiniApp'i ziyaret edebilirsiniz.",
                    buttons=[Button.url("🚀 OnlyVips MiniApp", miniapp_url)]
                )
            except Exception as e:
                logger.error(f"Kullanıcıya bildirim gönderilemedi: {e}")
    
    async def stop_listening(self):
        """Paylaşım kontrol olaylarını dinlemeyi durdur"""
        if self._handler:
            logger.info(f"Gönderi paylaşma görevi dinleyicisi durduruluyor: {self.user_id}_{self.task_id}")
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
        logger.info(f"Gönderi paylaşma görevi manuel doğrulandı: {self.user_id}_{self.task_id} (admin: {admin_id})")
        
        self.is_completed = True
        
        # Bot aracılığıyla kullanıcıya bildir
        try:
            await self.bot.send_message(
                int(self.user_id),
                f"✅ Tebrikler! Gönderi paylaşma göreviniz bir yönetici tarafından onaylandı."
            )
        except Exception as e:
            logger.error(f"Kullanıcıya bildirim gönderilemedi: {e}")
        
        return True 