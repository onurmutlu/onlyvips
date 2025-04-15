#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Channel Join Task Plugin - Kanal Katılım Görev Eklentisi
Bu modül kullanıcıların kanallara katılımını kontrol eden görev sınıfını içerir
"""

import logging
import asyncio
from telethon import events, functions, types
from ..base_task import BaseTask

logger = logging.getLogger(__name__)

class ChannelJoinTask(BaseTask):
    """Kanal katılımlarını kontrol eden görev tipi"""
    
    def __init__(self, user_id, task_id, expiry_time, verification_engine, bot, 
                 channel_username=None, channel_id=None, required_duration=None):
        """ChannelJoinTask yapıcısı"""
        super().__init__(user_id, task_id, expiry_time, verification_engine, bot)
        self.handler = None
        self.channel_username = channel_username  # Kanalın kullanıcı adı
        self.channel_id = channel_id  # Kanalın ID'si (iç ID)
        self.required_duration = required_duration  # Katılım sonrası gereken süre (saniye)
        # Bot kullanıcı adını al
        self.bot_username = getattr(verification_engine, 'bot_username', "OnlyVipsBot")
    
    def start_listening(self):
        """Dinlemeye başla"""
        
        # Kullanıcıdan katılım doğrulama komutu geldiğinde tetiklenecek
        @self.bot.on(events.NewMessage(pattern=r"/checkjoin(?:@\w+)?"))
        async def check_join_command(event):
            try:
                # Kullanıcıyı kontrol et
                sender = await event.get_sender()
                user_id = str(sender.id)
                if user_id != self.user_id:
                    return
                
                # Katıldığı kanalın kullanıcı adını almaya çalış
                args = event.text.split()
                target_channel = None
                
                if len(args) > 1:
                    # Kullanıcı komut sonrası kanal adı yazmış olabilir
                    target_channel = args[1].strip().lower()
                    # @ işareti ile başlıyorsa kaldır
                    if target_channel.startswith('@'):
                        target_channel = target_channel[1:]
                else:
                    # Görevde belirtilen kanalı kullan
                    target_channel = self.channel_username
                    if target_channel and target_channel.startswith('@'):
                        target_channel = target_channel[1:]
                
                # Hedef kanal kontrolü
                if not target_channel and not self.channel_id:
                    await event.respond("⚠️ Lütfen kontrol edilecek kanalı belirtin.")
                    return
                
                # Hedef kanalı kontrol et
                await self.verify_channel_join(user_id, target_channel, event)
                
            except Exception as e:
                logger.error(f"Kanal katılım kontrol komutunda hata: {e}")
        
        # Olay işleyicisini kaydet
        self.handler = check_join_command
        logger.debug(f"ChannelJoinTask dinleme başlatıldı: {self.user_id}_{self.task_id}")
    
    async def verify_channel_join(self, user_id, channel_username=None, event=None):
        """Bir kanala katılımı kontrol et"""
        try:
            channel_entity = None
            
            # Kanal bilgilerini al
            try:
                if self.channel_id:
                    # ID ile kanalı bul
                    channel_entity = await self.bot.get_entity(int(self.channel_id))
                elif channel_username:
                    # Kullanıcı adı ile kanalı bul
                    channel_entity = await self.bot.get_entity(f"@{channel_username}")
                else:
                    if event:
                        await event.respond("⚠️ Kanal bilgisi bulunamadı.")
                    return False
                
            except Exception as e:
                logger.error(f"Kanal bulunamadı: {e}")
                if event:
                    await event.respond(f"⚠️ Kanal bulunamadı. Lütfen geçerli bir kanal adı girin.")
                return False
            
            # Kullanıcının kanala katılımını kontrol et
            try:
                # Kullanıcı katılım durumunu al
                result = await self.bot(functions.channels.GetParticipantRequest(
                    channel=channel_entity,
                    participant=int(user_id)
                ))
                
                # Kullanıcı kanala katılmış
                join_date = result.participant.date
                
                # Katılım süresini kontrol et (eğer belirtilmişse)
                if self.required_duration:
                    import time
                    current_time = time.time()
                    join_time = join_date.timestamp()
                    duration = current_time - join_time
                    
                    if duration < self.required_duration:
                        remaining = self.required_duration - duration
                        hours, remainder = divmod(int(remaining), 3600)
                        minutes, seconds = divmod(remainder, 60)
                        time_str = ""
                        if hours > 0:
                            time_str += f"{hours} saat "
                        if minutes > 0:
                            time_str += f"{minutes} dakika "
                        if seconds > 0 and hours == 0:  # Sadece saat yoksa saniye göster
                            time_str += f"{seconds} saniye "
                            
                        if event:
                            await event.respond(f"⌛ Kanala katıldınız ancak görevin tamamlanması için {time_str}daha beklemeniz gerekiyor.")
                        return False
                
                # Görevi doğrula
                task_key = f"{self.user_id}_{self.task_id}"
                success = await self.verification_engine.verify_task(task_key)
                
                if success and event:
                    # Kullanıcıya bildirim gönder
                    from telethon import Button
                    miniapp_url = f"https://t.me/{self.bot_username}/app?startapp={self.user_id}"
                    
                    await event.respond(
                        f"✅ Kanala katılım göreviniz başarıyla tamamlandı ve ödülünüz verildi!",
                        buttons=[Button.url("🚀 OnlyVips MiniApp", miniapp_url)]
                    )
                return True
                
            except errors.UserNotParticipantError:
                # Kullanıcı kanala katılmamış
                if event:
                    await event.respond(f"❌ Henüz kanala katılmamışsınız. Lütfen @{channel_entity.username} kanalına katılın ve tekrar deneyin.")
                return False
                
            except Exception as e:
                logger.error(f"Katılım kontrolünde hata: {e}")
                if event:
                    await event.respond("⚠️ Katılım durumu kontrol edilirken bir hata oluştu, lütfen daha sonra tekrar deneyin.")
                return False
                
        except Exception as e:
            logger.error(f"Kanal katılım doğrulamasında hata: {e}")
            return False
    
    async def verify_manually(self):
        """Manuel katılım kontrolü yap"""
        return await self.verify_channel_join(self.user_id, self.channel_username)
    
    def stop_listening(self):
        """Dinlemeyi durdur"""
        if self.handler:
            # Bot event handler'ını kaldır
            self.bot.remove_event_handler(self.handler)
            self.handler = None
 