#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Emoji Reaction Task - Emoji Reaksiyon Görevi
Kullanıcının belirli bir mesaja emoji reaksiyon bırakmasını doğrulayan görev tipi
"""

import logging
from typing import Dict, Any, Optional, Union, List
import time
from telethon import events, Button
from telethon.tl.types import MessageReactions, ReactionEmoji

from ..base_task import BaseTask

logger = logging.getLogger(__name__)

class EmojiReactionTask(BaseTask):
    """Kullanıcının belirli bir mesaja emoji tepkisi vermesini gerektiren görev."""
    
    def __init__(
        self,
        user_id: str,
        task_id: str,
        expiry_time: int,
        verification_engine,
        bot,
        target_chat_id: Union[str, int],
        target_message_id: int,
        target_emoji: str,
        check_interval: int = 60,  # 1 dakikada bir kontrol et
        **kwargs
    ):
        """
        EmojiReactionTask yapıcısı
        
        Args:
            user_id: Kullanıcı ID'si
            task_id: Görev ID'si
            expiry_time: Görevin geçerlilik süresi (Unix timestamp)
            verification_engine: Görev doğrulama motoru
            bot: Bot istemcisi
            target_chat_id: Emoji reaksiyonu yapılacak sohbet ID'si
            target_message_id: Emoji reaksiyonu yapılacak mesaj ID'si
            target_emoji: Verilmesi gereken emoji (örn: "👍")
            check_interval: Kontrol aralığı (saniye)
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
        
        self.target_chat_id = str(target_chat_id)
        self.target_message_id = target_message_id
        self.target_emoji = target_emoji
        self.check_interval = check_interval
        
        # Mesaj bilgileri
        self.target_message = None
        
        # İzleme durumu
        self.check_task = None
        self.verification_message_id = None
        self._reaction_handler = None
        
        logger.info(f"EmojiReactionTask oluşturuldu: {self.user_id} için emoji tepkisi görevi")
    
    async def start_listening(self):
        """Emoji reaksiyon olaylarını dinlemeye başla"""
        if self.check_task or self._reaction_handler:
            return
            
        # Hedef mesajı getir
        try:
            self.target_message = await self.bot.get_messages(
                entity=self.target_chat_id,
                ids=self.target_message_id
            )
            
            if not self.target_message:
                logger.error(f"Hedef mesaj bulunamadı: {self.target_chat_id}/{self.target_message_id}")
                # Kullanıcıya hata bildir
                await self.bot.send_message(
                    int(self.user_id),
                    f"⚠️ Emoji tepkisi vermeniz gereken mesaj bulunamadı. Lütfen bir yönetici ile iletişime geçin."
                )
                return
                
            logger.info(f"Hedef mesaj bulundu: {self.target_message.id}")
            
            # Kullanıcıya görev bilgisi gönder
            await self._send_task_info()
            
            # Emoji reaksiyon olayını dinle
            @self.bot.on(events.MessageEdited(chats=self.target_chat_id, ids=self.target_message_id))
            async def on_reaction_update(event):
                if not self.is_active or self.is_completed:
                    return
                    
                try:
                    # Mesajı tüm reaksiyon bilgileriyle getir
                    message = await self.bot.get_messages(
                        entity=self.target_chat_id,
                        ids=self.target_message_id
                    )
                    
                    if not message or not hasattr(message, 'reactions'):
                        return
                        
                    # Kullanıcının emoji tepkisi olup olmadığını kontrol et
                    await self._check_user_reaction()
                    
                except Exception as e:
                    logger.error(f"Reaksiyon kontrolünde hata: {e}")
                
            self._reaction_handler = on_reaction_update
            
            # Periyodik kontrol görevini başlat (bazı emoji reaksiyonları olaylar aracılığıyla yakalanamayabilir)
            import asyncio
            self.check_task = asyncio.create_task(self._periodic_check())
            
        except Exception as e:
            logger.error(f"Hedef mesaj alınırken hata: {e}")
            # Kullanıcıya hata bildir
            await self.bot.send_message(
                int(self.user_id),
                f"⚠️ Emoji tepkisi görevi kontrolü sırasında bir hata oluştu. Lütfen bir yönetici ile iletişime geçin."
            )
    
    async def _send_task_info(self):
        """Görev bilgisini kullanıcıya gönder"""
        try:
            # Mesaj linkini oluştur
            if isinstance(self.target_chat_id, str) and self.target_chat_id.startswith('@'):
                message_link = f"https://t.me/{self.target_chat_id.lstrip('@')}/{self.target_message_id}"
            else:
                # Kanal/grup ID kullanıyorsa, kullanıcılara nasıl erişeceğini açıkla
                message_link = f"Belirtilen kanaldaki {self.target_message_id} ID'li mesaj"
                
            # Görev mesajını gönder
            from telethon import Button
            message = await self.bot.send_message(
                int(self.user_id),
                f"🎭 **Emoji Tepkisi Görevi**\n\n"
                f"Aşağıdaki mesaja '{self.target_emoji}' emoji tepkisi vermeniz gerekmektedir:\n"
                f"{message_link}\n\n"
                f"Emoji tepkisi verdikten sonra doğrulamak için aşağıdaki butona tıklayın.",
                buttons=[Button.inline("✅ Emoji Tepkisini Doğrula", data=f"check_reaction_{self.task_id}")]
            )
            
            self.verification_message_id = message.id
            
            # Callback handler ekle
            @self.bot.on(events.CallbackQuery(pattern=f"check_reaction_{self.task_id}"))
            async def on_reaction_verify(event):
                if not self.is_active or self.is_completed:
                    return
                    
                # Kullanıcı kontrolü
                if event.sender_id != int(self.user_id):
                    return
                    
                # Kullanıcıya beklemesini söyle
                await event.answer("Emoji tepkiniz kontrol ediliyor...")
                
                # Emoji tepkisini kontrol et
                verified = await self._check_user_reaction(manual_check=True)
                
                if verified:
                    # Zaten doğrulandı veya şimdi doğrulandı, mesajı güncelle
                    await self.bot.edit_message(
                        int(self.user_id),
                        self.verification_message_id,
                        f"✅ Tebrikler! Emoji tepkisi göreviniz başarıyla tamamlandı.",
                        buttons=None
                    )
                else:
                    # Kullanıcıya emoji tepkisinin bulunamadığını bildir
                    await self.bot.edit_message(
                        int(self.user_id),
                        self.verification_message_id,
                        f"🔍 **Emoji Tepkisi Görevi**\n\n"
                        f"Henüz '{self.target_emoji}' emoji tepkiniz bulunamadı. Lütfen doğru mesaja emoji tepkisi verdiğinizden emin olun ve tekrar deneyin.\n\n"
                        f"Not: Emoji tepkilerinin görünmesi biraz zaman alabilir. Eğer tepki verdiyseniz, lütfen birkaç saniye bekleyin ve tekrar deneyin.",
                        buttons=[Button.inline("🔄 Tekrar Kontrol Et", data=f"check_reaction_{self.task_id}")]
                    )
                    
            self._callback_handler = on_reaction_verify
            
        except Exception as e:
            logger.error(f"Görev bilgisi gönderilirken hata: {e}")
    
    async def _periodic_check(self):
        """Periyodik olarak kullanıcının emoji tepkisini kontrol et"""
        import asyncio
        
        while self.is_active and not self.is_completed:
            try:
                # Emoji tepkisini kontrol et
                verified = await self._check_user_reaction()
                if verified:
                    # Görev tamamlandı, döngüyü sonlandır
                    break
                    
            except Exception as e:
                logger.error(f"Periyodik emoji tepkisi kontrolünde hata: {e}")
                
            # Bir sonraki kontrole kadar bekle
            await asyncio.sleep(self.check_interval)
    
    async def _check_user_reaction(self, manual_check=False):
        """
        Kullanıcının mesaja emoji tepkisi verip vermediğini kontrol et
        
        Args:
            manual_check: Manuel bir kontrol ise True, periyodik kontrol ise False
            
        Returns:
            bool: Doğrulama başarılı ise True, aksi halde False
        """
        if self.is_completed:
            return True
            
        try:
            from telethon.tl.functions.messages import GetMessageReactionsRequest
            
            # Mesajın reaksiyonlarını getir
            result = await self.bot(GetMessageReactionsRequest(
                peer=self.target_chat_id,
                id=self.target_message_id
            ))
            
            if not result or not hasattr(result, 'reactions'):
                logger.warning(f"Reaksiyonlar getirilemedi: {self.target_chat_id}/{self.target_message_id}")
                return False
                
            # Kullanıcının tepkisini ara
            user_reaction_found = False
            
            # Tüm reaksiyonları kontrol et
            for reaction in result.reactions:
                # Emoji'yi kontrol et
                emoji = None
                if hasattr(reaction, 'reaction'):
                    if isinstance(reaction.reaction, ReactionEmoji):
                        emoji = reaction.reaction.emoticon
                
                if emoji == self.target_emoji:
                    # Reaksiyon listesini kontrol et (sadece sınırlı sayıda kullanıcı görüntülenebilir)
                    if hasattr(reaction, 'recent_reactions'):
                        for recent in reaction.recent_reactions:
                            if recent.peer_id.user_id == int(self.user_id):
                                user_reaction_found = True
                                break
            
            # Eğer kullanıcının reaksiyonu bulunduysa, görevi tamamla
            if user_reaction_found:
                logger.info(f"Kullanıcının emoji tepkisi bulundu: {self.user_id}, emoji: {self.target_emoji}")
                await self._complete_task()
                return True
            
            # Kullanıcının tepkisi bulunamadı, manuel kontrol için bir hata mesajı gösterilebilir
            if manual_check:
                logger.debug(f"Kullanıcının emoji tepkisi bulunamadı: {self.user_id}, emoji: {self.target_emoji}")
            
            return False
            
        except Exception as e:
            logger.error(f"Emoji tepkisi kontrolünde hata: {e}")
            return False
    
    async def _complete_task(self):
        """Görevi tamamla"""
        if not self.is_active or self.is_completed:
            return
            
        # Görevi tamamlandı olarak işaretle
        success = await self.verification_engine.verify_task(self.user_id, self.task_id)
        
        if success:
            self.is_completed = True
            
            # Kullanıcıya bildirim gönder
            try:
                if self.verification_message_id:
                    await self.bot.edit_message(
                        int(self.user_id),
                        self.verification_message_id,
                        f"✅ Tebrikler! Emoji tepkisi göreviniz başarıyla tamamlandı.",
                        buttons=None
                    )
                else:
                    await self.bot.send_message(
                        int(self.user_id),
                        f"🎉 Tebrikler! Emoji tepkisi görevini başarıyla tamamladınız."
                    )
            except Exception as e:
                logger.error(f"Bildirim gönderme hatası: {e}")
            
            logger.info(f"Emoji tepkisi görevi tamamlandı: {self.user_id}_{self.task_id}")
        else:
            logger.error(f"Görev tamamlama hatası: {self.user_id}_{self.task_id}")
    
    async def stop_listening(self):
        """Emoji tepkisi olaylarını dinlemeyi durdur"""
        if self.check_task:
            self.check_task.cancel()
            try:
                await self.check_task
            except asyncio.CancelledError:
                pass
            self.check_task = None
            
        if self._reaction_handler:
            self.bot.remove_event_handler(self._reaction_handler)
            self._reaction_handler = None
            
        if hasattr(self, '_callback_handler') and self._callback_handler:
            self.bot.remove_event_handler(self._callback_handler)
            self._callback_handler = None
            
        logger.info(f"Emoji tepkisi görevi izleme durduruldu: {self.user_id}_{self.task_id}")
    
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
            if self.verification_message_id:
                await self.bot.edit_message(
                    int(self.user_id),
                    self.verification_message_id,
                    f"✅ Tebrikler! Emoji tepkisi göreviniz bir yönetici tarafından onaylandı.",
                    buttons=None
                )
            else:
                await self.bot.send_message(
                    int(self.user_id),
                    f"🎉 Tebrikler! Emoji tepkisi göreviniz bir yönetici tarafından onaylandı."
                )
            
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