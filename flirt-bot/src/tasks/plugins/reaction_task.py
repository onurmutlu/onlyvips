#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Reaction Task Plugin - Reaksiyon Görev Eklentisi
Bu modül kullanıcıların mesajlara reaksiyon vermesini kontrol eden görev sınıfını içerir
"""

import logging
import asyncio
from telethon import events, utils
from telethon.tl.functions.messages import GetMessagesReactionsRequest
from ..base_task import BaseTask

logger = logging.getLogger(__name__)

class ReactionTask(BaseTask):
    """Kullanıcının belirli bir gönderiye reaksiyon eklemesini kontrol eden görev"""
    
    def __init__(self, user_id, task_id, expiry_time, verification_engine, bot, 
                 channel_id=None, message_id=None, required_reaction=None):
        """ReactionTask yapıcısı"""
        super().__init__(user_id, task_id, expiry_time, verification_engine, bot)
        self.handler = None
        self.channel_id = channel_id  # Reaksiyon verilecek kanalın ID'si
        self.message_id = message_id  # Reaksiyon verilecek mesajın ID'si
        self.required_reaction = required_reaction  # Gerekli reaksiyon türü (ör: "👍", "❤️", "👏" veya None)
    
    def start_listening(self):
        """Dinlemeye başla"""
        
        # Kullanıcının reaksiyon komutunu dinle
        @self.bot.on(events.NewMessage(pattern=r'^/checkreaction(?:\s+|$)'))
        async def check_reaction_handler(event):
            try:
                # Komutu gönderen kullanıcıyı kontrol et
                sender = await event.get_sender()
                user_id = str(sender.id)
                
                # Sadece görev sahibi kullanıcıların komutunu işle
                if user_id != self.user_id:
                    return
                
                # Reaksiyon doğrulamasını başlat
                await event.respond(f"🔍 Reaksiyon kontrolü başlatılıyor...")
                
                # Reaksiyonu doğrula
                verified = await self.verify_reaction(user_id)
                
                if verified:
                    await event.respond("✅ Tebrikler! Reaksiyon göreviniz başarıyla tamamlandı ve ödülünüz verildi.")
                else:
                    # Reaksiyon bağlantısını oluştur
                    reaction_text = f"'{self.required_reaction}' reaksiyonu" if self.required_reaction else "bir reaksiyon"
                    message_link = f"https://t.me/c/{self.channel_id}/{self.message_id}"
                    
                    await event.respond(
                        f"⚠️ Henüz {reaction_text} vermemişsiniz veya reaksiyonunuz bulunamadı.\n\n"
                        f"Lütfen bu mesaja reaksiyon verin ve tekrar deneyin: {message_link}"
                    )
                
            except Exception as e:
                logger.error(f"Reaksiyon kontrol olayında hata: {e}")
                await event.respond("⚠️ Reaksiyon kontrolü sırasında bir hata oluştu. Lütfen daha sonra tekrar deneyin.")
        
        # Olay işleyicisini kaydet
        self.handler = check_reaction_handler
        logger.debug(f"ReactionTask dinleme başlatıldı: {self.user_id}_{self.task_id}")
    
    async def verify_reaction(self, user_id):
        """Kullanıcının belirli mesaja reaksiyon verip vermediğini doğrula"""
        try:
            # Kullanıcı ID'sini integer'a çevir
            user_id_int = int(user_id)
            
            # Mesajın reaksiyonlarını al
            try:
                # Kanal varlığını al
                channel = await self.bot.get_entity(int(self.channel_id))
                
                # Mesajın reaksiyonlarını al
                reactions = await self.bot(GetMessagesReactionsRequest(
                    peer=channel,
                    id=[int(self.message_id)]
                ))
                
                # Tepki listesini kontrol et
                if hasattr(reactions, 'reactions') and reactions.reactions:
                    for reaction_user in reactions.reactions[0].recent_reactions:
                        # Kullanıcı kontrol
                        if reaction_user.peer_id.user_id == user_id_int:
                            # Belirli bir reaksiyon gerekiyorsa kontrol et
                            if self.required_reaction:
                                # Emoji reaksiyonu mu?
                                if hasattr(reaction_user.reaction, 'emoticon'):
                                    if reaction_user.reaction.emoticon == self.required_reaction:
                                        # Reaksiyon doğrulandı, görevi tamamla
                                        task_key = f"{self.user_id}_{self.task_id}"
                                        await self.verification_engine.verify_task(task_key)
                                        return True
                            else:
                                # Herhangi bir reaksiyon yeterli
                                task_key = f"{self.user_id}_{self.task_id}"
                                await self.verification_engine.verify_task(task_key)
                                return True
            except Exception as e:
                logger.error(f"Reaksiyon alırken hata: {e}")
            
            # Reaksiyon bulunamadı veya doğrulanamadı
            return False
            
        except Exception as e:
            logger.error(f"Reaksiyon doğrulama hatası: {e}")
            return False
    
    async def verify_manually(self):
        """Manuel doğrulama"""
        try:
            # Bu, bir yönetici tarafından manuel olarak doğrulama yapıldığında kullanılır
            task_key = f"{self.user_id}_{self.task_id}"
            return await self.verification_engine.verify_task(task_key)
        except Exception as e:
            logger.error(f"Manuel reaksiyon doğrulamasında hata: {e}")
            return False
    
    def stop_listening(self):
        """Dinlemeyi durdur"""
        if self.handler:
            # Bot event handler'ını kaldır
            self.bot.remove_event_handler(self.handler)
            self.handler = None
            logger.debug(f"ReactionTask dinleme durduruldu: {self.user_id}_{self.task_id}") 