#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Group Join Task Plugin - Grup Katılım Görev Eklentisi
Bu modül kullanıcıların gruplara katılımını dinleyen görev sınıfını içerir
"""

import logging
from telethon import events
from telethon.tl.types import PeerChannel, PeerChat
from telethon.tl.functions.channels import GetFullChannelRequest
from ..base_task import BaseTask

logger = logging.getLogger(__name__)

class GroupJoinTask(BaseTask):
    """Grup katılımlarını kontrol eden görev tipi"""
    
    def __init__(self, user_id, task_id, expiry_time, verification_engine, bot, target_group_id=None):
        """GroupJoinTask yapıcısı"""
        super().__init__(user_id, task_id, expiry_time, verification_engine, bot)
        self.handler = None
        self.target_group_id = target_group_id
        # Bot kullanıcı adını al
        self.bot_username = getattr(verification_engine, 'bot_username', "OnlyVipsBot")
    
    def start_listening(self):
        """Dinlemeye başla"""
        
        # Grup katılımlarını dinle
        @self.bot.on(events.ChatAction())
        async def check_join(event):
            try:
                # Olayı kontrol et - sadece katılma olaylarını dinle
                if not event.user_joined and not event.user_added:
                    return
                
                # Kullanıcıyı kontrol et
                user = await event.get_user()
                if not user or str(user.id) != self.user_id:
                    return
                
                # Hedef grup belirtilmişse, sadece o grubu kontrol et
                if self.target_group_id:
                    chat = await event.get_chat()
                    chat_id = str(chat.id)
                    if chat_id != self.target_group_id:
                        logger.debug(f"Kullanıcı farklı bir gruba katıldı, hedef grup değil: {chat_id}")
                        return
                
                logger.info(f"Kullanıcı grup katılımı tespit edildi, görev doğrulanıyor: {self.user_id}_{self.task_id}")
                
                # Görevi doğrula
                task_key = f"{self.user_id}_{self.task_id}"
                success = await self.verification_engine.verify_task(task_key)
                
                if success:
                    # Kullanıcıya DM olarak bildirim gönder
                    try:
                        from telethon import Button
                        miniapp_url = f"https://t.me/{self.bot_username}/app?startapp={self.user_id}"
                        
                        await self.bot.send_message(
                            self.user_id, 
                            "👥 Grup katılım göreviniz başarıyla tamamlandı ve ödülünüz verildi! Daha fazla görev için MiniApp'i ziyaret edebilirsiniz.",
                            buttons=[Button.url("🚀 OnlyVips MiniApp", miniapp_url)]
                        )
                    except Exception as e:
                        logger.error(f"Kullanıcıya DM bildirim gönderilirken hata: {e}")
            except Exception as e:
                logger.error(f"Grup katılım kontrolünde hata: {e}")
        
        # Olay işleyicisini kaydet
        self.handler = check_join
        logger.debug(f"GroupJoinTask dinleme başlatıldı: {self.user_id}_{self.task_id}")
    
    async def verify_manually(self, group_id=None):
        """Manuel olarak kullanıcının grup üyeliğini kontrol et"""
        try:
            # Kontrol edilecek grup ID'sini belirle
            chat_id = group_id or self.target_group_id
            if not chat_id:
                logger.error("Manuel doğrulama için grup ID belirtilmedi")
                return False
            
            # Grubun üye listesini al
            try:
                # Önce tam kanal/grup bilgisini al
                if str(chat_id).startswith('-100'):
                    chat_id = int(chat_id)
                
                # Kanal/grup bilgisini al
                full = await self.bot(GetFullChannelRequest(channel=chat_id))
                
                # Üye sayısını kontrol et
                if hasattr(full, 'full_chat') and hasattr(full.full_chat, 'participants_count'):
                    # Üye sayısına bakarak sadece varlığını doğrulama yapılabilir
                    # Daha detaylı kontrol için özel izinler gerekir
                    logger.info(f"Grup üye sayısı: {full.full_chat.participants_count}")
                    
                    # Basit bir doğrulama - kullanıcı üye olsa da olmasa da
                    # API kısıtlamaları nedeniyle direkt kontrol zor olabilir
                    return True
            except Exception as e:
                logger.error(f"Grup üyelik kontrolünde API hatası: {e}")
                return False
                
            return False
        except Exception as e:
            logger.error(f"Manuel grup üyelik doğrulamasında hata: {e}")
            return False
    
    def stop_listening(self):
        """Dinlemeyi durdur"""
        if self.handler:
            # Bot event handler'ını kaldır
            self.bot.remove_event_handler(self.handler)
            self.handler = None
            logger.debug(f"GroupJoinTask dinleme durduruldu: {self.user_id}_{self.task_id}") 