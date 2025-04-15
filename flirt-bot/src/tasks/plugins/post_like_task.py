#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Post Like Task Plugin - Gönderi Beğenme Görev Eklentisi
Bu modül kullanıcıların kanal gönderilerini beğenmesini kontrol eden görev sınıfını içerir
"""

import logging
import time
import asyncio
from telethon import events, functions
from ..base_task import BaseTask

logger = logging.getLogger(__name__)

class PostLikeTask(BaseTask):
    """Gönderi beğenilerini kontrol eden görev tipi"""
    
    def __init__(self, user_id, task_id, expiry_time, verification_engine, bot, 
                 channel_id=None, message_id=None, required_count=1):
        """PostLikeTask yapıcısı"""
        super().__init__(user_id, task_id, expiry_time, verification_engine, bot)
        self.handler = None
        self.channel_id = channel_id  # Kanalın ID'si
        self.message_id = message_id  # Beğenilecek mesaj ID'si (None ise tüm mesajlar)
        self.required_count = required_count  # Gerekli beğeni sayısı
        self.liked_count = 0  # Şu ana kadar yapılan beğeni sayısı
        self.last_check = 0  # Son kontrol zamanı (flood koruması için)
        # Bot kullanıcı adını al
        self.bot_username = getattr(verification_engine, 'bot_username', "OnlyVipsBot")
    
    def start_listening(self):
        """Dinlemeye başla"""
        
        # Beğeni olaylarını dinlemek için doğrudan bir olay yok,
        # bu nedenle periyodik olarak kontrol etmek gerekiyor.
        # Bu durumda, kullanıcı beğeni yapınca bize bildirim gönderecek
        # bir komut eklemeliyiz.
        @self.bot.on(events.NewMessage(pattern=r"/liked(?:@\w+)?"))
        async def check_like_command(event):
            try:
                # Kullanıcıyı kontrol et
                sender = await event.get_sender()
                user_id = str(sender.id)
                if user_id != self.user_id:
                    return
                
                # Mesajın yanıt olduğu orijinal mesajı al
                if event.reply_to:
                    replied_msg = await event.get_reply_message()
                    chat = await event.get_chat()
                    
                    # Hedef kanal belirtilmişse, sadece o kanalı kontrol et
                    if self.channel_id:
                        chat_id = str(chat.id)
                        if chat_id != self.channel_id:
                            await event.respond("⚠️ Bu kanal için beğeni göreviniz bulunmuyor.")
                            return
                    
                    # Hedef mesaj belirtilmişse, sadece o mesajı kontrol et
                    if self.message_id:
                        message_id = replied_msg.id
                        if message_id != self.message_id:
                            await event.respond("⚠️ Bu mesaj için beğeni göreviniz bulunmuyor.")
                            return
                    
                    # Mesajı beğendi mi kontrol et
                    await self.verify_post_like(chat.id, replied_msg.id, user_id, event)
                else:
                    # Yanıt olmadan /liked komutunu kullandı
                    await event.respond("📝 Bu komutu beğendiğiniz bir mesaja yanıt olarak kullanmalısınız.")
            except Exception as e:
                logger.error(f"Beğeni kontrol komutunda hata: {e}")
        
        # Olay işleyicisini kaydet
        self.handler = check_like_command
        logger.debug(f"PostLikeTask dinleme başlatıldı: {self.user_id}_{self.task_id}")
    
    async def verify_post_like(self, channel_id, message_id, user_id, event=None):
        """Bir gönderi beğenisini kontrol et"""
        try:
            # Flood koruması (çok sık kontrol etmeyi önle)
            current_time = time.time()
            if (current_time - self.last_check) < 5:  # En az 5 saniye ara ile kontrol et
                if event:
                    await event.respond("⏳ Lütfen kontrol etmek için biraz bekleyin.")
                return False
            
            self.last_check = current_time
            
            # Telethon API ile beğenileri al
            try:
                # Mesaj beğenilerini al
                result = await self.bot(functions.messages.GetMessageReactionsListRequest(
                    peer=channel_id,
                    id=message_id,
                    limit=100
                ))
                
                # Kullanıcının beğenisi var mı kontrol et
                user_liked = False
                for reaction in result.reactions:
                    reactor_id = str(reaction.peer_id.user_id) if hasattr(reaction.peer_id, 'user_id') else None
                    if reactor_id == user_id:
                        user_liked = True
                        break
                
                if user_liked:
                    # Beğeni sayısını artır
                    self.liked_count += 1
                    logger.info(f"Kullanıcı beğeni tespit edildi ({self.liked_count}/{self.required_count}): {self.user_id}_{self.task_id}")
                    
                    # Gerekli sayıya ulaşılınca görevi doğrula
                    if self.liked_count >= self.required_count:
                        # Görevi doğrula
                        task_key = f"{self.user_id}_{self.task_id}"
                        success = await self.verification_engine.verify_task(task_key)
                        
                        if success and event:
                            # Kullanıcıya bildirim gönder
                            from telethon import Button
                            miniapp_url = f"https://t.me/{self.bot_username}/app?startapp={self.user_id}"
                            
                            await event.respond(
                                "👍 Beğeni göreviniz başarıyla tamamlandı ve ödülünüz verildi!",
                                buttons=[Button.url("🚀 OnlyVips MiniApp", miniapp_url)]
                            )
                        return True
                    elif event:
                        await event.respond(f"👍 Beğeni kaydedildi! ({self.liked_count}/{self.required_count})")
                        return True
                else:
                    if event:
                        await event.respond("❌ Bu gönderiyi henüz beğenmemişsiniz. Lütfen önce beğenin sonra tekrar deneyin.")
                    return False
                    
            except Exception as e:
                logger.error(f"Beğeni kontrol API'sinde hata: {e}")
                if event:
                    await event.respond("⚠️ Beğeniler kontrol edilirken bir hata oluştu, lütfen daha sonra tekrar deneyin.")
                return False
                
        except Exception as e:
            logger.error(f"Beğeni doğrulamasında hata: {e}")
            return False
    
    async def verify_manually(self):
        """Manuel beğeni kontrolü yap"""
        if not self.channel_id or not self.message_id:
            logger.warning("Manuel beğeni kontrolü için kanal ve mesaj ID gerekli")
            return False
        
        return await self.verify_post_like(self.channel_id, self.message_id, self.user_id)
    
    def stop_listening(self):
        """Dinlemeyi durdur"""
        if self.handler:
            # Bot event handler'ını kaldır
            self.bot.remove_event_handler(self.handler)
            self.handler = None
            logger.debug(f"PostLikeTask dinleme durduruldu: {self.user_id}_{self.task_id}") 