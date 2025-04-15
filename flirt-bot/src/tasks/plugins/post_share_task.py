#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Post Share Task Plugin - Gönderi Paylaşma Görev Eklentisi
Bu modül kullanıcıların belirli gönderileri paylaşmasını kontrol eden görev sınıfını içerir
"""

import logging
import asyncio
from telethon import events, functions, types
from ..base_task import BaseTask

logger = logging.getLogger(__name__)

class PostShareTask(BaseTask):
    """Kullanıcının belirli bir gönderiyi paylaşmasını kontrol eden görev"""
    
    def __init__(self, user_id, task_id, expiry_time, verification_engine, bot, 
                 post_channel=None, post_id=None):
        """PostShareTask yapıcısı"""
        super().__init__(user_id, task_id, expiry_time, verification_engine, bot)
        self.handler = None
        self.post_channel = post_channel  # Paylaşılması gereken gönderinin kanal ID'si veya kullanıcı adı
        self.post_id = post_id  # Paylaşılması gereken gönderi ID'si
    
    def start_listening(self):
        """Dinlemeye başla"""
        
        # Kullanıcının paylaşım komutunu dinle
        @self.bot.on(events.NewMessage(pattern=r'^/checkshare(?:\s+|$)'))
        async def check_share_handler(event):
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
                    post_link = f"https://t.me/{self.post_channel.replace('@', '')}/{self.post_id}"
                    await event.respond(
                        f"⚠️ Henüz paylaşım yapmamışsınız veya paylaşımınız bulunamadı.\n\n"
                        f"Lütfen bu gönderiyi paylaşın ve tekrar deneyin: {post_link}"
                    )
                
            except Exception as e:
                logger.error(f"Paylaşım kontrol olayında hata: {e}")
                await event.respond("⚠️ Paylaşım kontrolü sırasında bir hata oluştu. Lütfen daha sonra tekrar deneyin.")
        
        # Olay işleyicisini kaydet
        self.handler = check_share_handler
        logger.debug(f"PostShareTask dinleme başlatıldı: {self.user_id}_{self.task_id}")
    
    async def verify_post_share(self, user_id):
        """Kullanıcının belirli gönderiyi paylaşıp paylaşmadığını doğrula"""
        try:
            # Kullanıcı ID'sini integer'a çevir
            user_id_int = int(user_id)
            
            # Kullanıcının son paylaştığı mesajları al (son 100 mesaj)
            # Kullanıcının mesaj geçmişini alabilmek için user_id bir entity olmalı
            # Bu API çağrısını yapabilmek için bot'un kullanıcıyla bir diyalog başlatmış olması gerekir
            
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
                # Paylaşılan mesaj kontrolü (mesaj türüne göre)
                if hasattr(message, 'fwd_from') and message.fwd_from:
                    # Paylaşımın kaynağını kontrol et
                    fwd = message.fwd_from
                    
                    # Kanaldaki bir gönderiyi paylaşmış mı?
                    if (fwd.channel_id and str(fwd.channel_id) == self.post_channel) or \
                       (fwd.channel_post and str(fwd.channel_post) == self.post_id):
                        # Paylaşım doğrulandı, görevi tamamla
                        task_key = f"{self.user_id}_{self.task_id}"
                        await self.verification_engine.verify_task(task_key)
                        return True
            
            # Paylaşım bulunamadı
            return False
            
        except Exception as e:
            logger.error(f"Gönderi paylaşımı doğrulama hatası: {e}")
            return False
    
    async def verify_manually(self):
        """Manuel doğrulama"""
        try:
            # Bu, bir yönetici tarafından manuel olarak doğrulama yapıldığında kullanılır
            task_key = f"{self.user_id}_{self.task_id}"
            return await self.verification_engine.verify_task(task_key)
        except Exception as e:
            logger.error(f"Manuel gönderi paylaşımı doğrulamasında hata: {e}")
            return False
    
    def stop_listening(self):
        """Dinlemeyi durdur"""
        if self.handler:
            # Bot event handler'ını kaldır
            self.bot.remove_event_handler(self.handler)
            self.handler = None
            logger.debug(f"PostShareTask dinleme durduruldu: {self.user_id}_{self.task_id}") 