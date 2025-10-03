#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Comment Task - Yorum Yapma Görevi
Kullanıcının belirli bir mesaja veya gönderi altına yorum yapmasını doğrulayan görev tipi
"""

import logging
from typing import Dict, Any, Optional, Union, List
import time
from telethon import events, utils
from telethon.tl.functions.messages import GetRepliesRequest

from ..base_task import BaseTask

logger = logging.getLogger(__name__)

class CommentTask(BaseTask):
    """Kullanıcının belirli bir mesaja veya gönderi altına yorum yapmasını gerektiren görev."""
    
    def __init__(
        self,
        user_id: str,
        task_id: str,
        expiry_time: int,
        verification_engine,
        bot,
        target_chat_id: Union[str, int],
        target_message_id: int,
        required_content: Optional[List[str]] = None,
        min_length: Optional[int] = None,
        check_interval: int = 300,  # 5 dakikada bir kontrol et
        **kwargs
    ):
        """
        CommentTask yapıcısı
        
        Args:
            user_id: Kullanıcı ID'si
            task_id: Görev ID'si
            expiry_time: Görevin geçerlilik süresi (Unix timestamp)
            verification_engine: Görev doğrulama motoru
            bot: Bot istemcisi
            target_chat_id: Hedef sohbet ID'si
            target_message_id: Yorum yapılacak mesaj ID'si
            required_content: Yorumun içermesi gereken kelimeler (isteğe bağlı)
            min_length: Minimum yorum uzunluğu (isteğe bağlı)
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
        self.required_content = required_content or []
        self.min_length = min_length or 0
        self.check_interval = check_interval
        
        # Mesaj bilgileri
        self.target_message = None
        self.comments_checked = False
        
        # İzleme durumu
        self.check_task = None
        self.verification_message_id = None
        
        logger.info(f"CommentTask oluşturuldu: {self.user_id} için yorum yapma görevi")
    
    async def start_listening(self):
        """Yorum yapma olaylarını dinlemeye başla"""
        if self.check_task:
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
                    f"⚠️ Yorum yapmanız gereken mesaj bulunamadı. Lütfen bir yönetici ile iletişime geçin."
                )
                return
                
            logger.info(f"Hedef mesaj bulundu: {self.target_message.id}")
            
            # Kullanıcıya görev bilgisi gönder
            await self._send_task_info()
            
            # Periyodik kontrol görevini başlat
            import asyncio
            self.check_task = asyncio.create_task(self._periodic_check())
            
        except Exception as e:
            logger.error(f"Hedef mesaj alınırken hata: {e}")
            # Kullanıcıya hata bildir
            await self.bot.send_message(
                int(self.user_id),
                f"⚠️ Yorum görevi kontrolü sırasında bir hata oluştu. Lütfen bir yönetici ile iletişime geçin."
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
                
            # İçerik gereksinimleri metni
            content_requirements = ""
            if self.required_content:
                content_requirements = f"\n\n🔑 Yorumunuzda şu kelimeler bulunmalıdır: {', '.join(self.required_content)}"
                
            length_requirements = ""
            if self.min_length > 0:
                length_requirements = f"\n📏 Yorumunuz en az {self.min_length} karakter uzunluğunda olmalıdır."
                
            # Görev mesajını gönder
            from telethon import Button
            message = await self.bot.send_message(
                int(self.user_id),
                f"📝 **Yorum Görevi**\n\n"
                f"Aşağıdaki mesaja yorum yapmanız gerekmektedir:\n"
                f"{message_link}{content_requirements}{length_requirements}\n\n"
                f"Yorum yaptıktan sonra doğrulamak için aşağıdaki butona tıklayın.",
                buttons=[Button.inline("✅ Yorumu Doğrula", data=f"check_comment_{self.task_id}")]
            )
            
            self.verification_message_id = message.id
            
            # Callback handler ekle
            @self.bot.on(events.CallbackQuery(pattern=f"check_comment_{self.task_id}"))
            async def on_comment_verify(event):
                if not self.is_active or self.is_completed:
                    return
                    
                # Kullanıcı kontrolü
                if event.sender_id != int(self.user_id):
                    return
                    
                # Kullanıcıya beklemesini söyle
                await event.answer("Yorumunuz kontrol ediliyor...")
                
                # Yorumu kontrol et
                verified = await self._check_comments(manual_check=True)
                
                if verified:
                    # Zaten doğrulandı veya şimdi doğrulandı, mesajı güncelle
                    await self.bot.edit_message(
                        int(self.user_id),
                        self.verification_message_id,
                        f"✅ Tebrikler! Yorum göreviniz başarıyla tamamlandı.",
                        buttons=None
                    )
                else:
                    # Kullanıcıya yorumunun bulunamadığını bildir
                    await self.bot.edit_message(
                        int(self.user_id),
                        self.verification_message_id,
                        f"🔍 **Yorum Görevi**\n\n"
                        f"Henüz yorumunuz bulunamadı. Lütfen yorumunuzu yapmış olduğunuzdan emin olun ve tekrar deneyin.\n\n"
                        f"Not: Yorumların görünmesi biraz zaman alabilir. Eğer yorum yaptıysanız, lütfen birkaç dakika bekleyin ve tekrar deneyin.",
                        buttons=[Button.inline("🔄 Tekrar Kontrol Et", data=f"check_comment_{self.task_id}")]
                    )
                    
            self._callback_handler = on_comment_verify
            
        except Exception as e:
            logger.error(f"Görev bilgisi gönderilirken hata: {e}")
    
    async def _periodic_check(self):
        """Periyodik olarak kullanıcının yorum yapıp yapmadığını kontrol et"""
        import asyncio
        
        while self.is_active and not self.is_completed:
            try:
                # Yorumları kontrol et
                verified = await self._check_comments()
                if verified:
                    # Görev tamamlandı, döngüyü sonlandır
                    break
                    
            except Exception as e:
                logger.error(f"Periyodik yorum kontrolünde hata: {e}")
                
            # Bir sonraki kontrole kadar bekle
            await asyncio.sleep(self.check_interval)
    
    async def _check_comments(self, manual_check=False):
        """
        Kullanıcının mesaja yorum yapıp yapmadığını kontrol et
        
        Args:
            manual_check: Manuel bir kontrol ise True, periyodik kontrol ise False
            
        Returns:
            bool: Doğrulama başarılı ise True, aksi halde False
        """
        if self.is_completed:
            return True
            
        try:
            # Mesajın yorumlarını getir
            replies = await self.bot(GetRepliesRequest(
                peer=self.target_chat_id,
                msg_id=self.target_message_id,
                offset_id=0,
                offset_date=None,
                add_offset=0,
                limit=100,
                max_id=0,
                min_id=0,
                hash=0
            ))
            
            if not replies or not hasattr(replies, 'messages'):
                logger.warning(f"Yorumlar getirilemedi: {self.target_chat_id}/{self.target_message_id}")
                return False
                
            # Kullanıcının yorumunu ara
            for message in replies.messages:
                if message.from_id and hasattr(message.from_id, 'user_id') and str(message.from_id.user_id) == self.user_id:
                    # Yorum bulundu, içerik kontrolü yap
                    comment_text = message.message or ""
                    
                    # Minimum uzunluğu kontrol et
                    if len(comment_text) < self.min_length:
                        logger.debug(f"Yorum çok kısa: {len(comment_text)}, minimum: {self.min_length}")
                        if manual_check:
                            await self.bot.send_message(
                                int(self.user_id),
                                f"⚠️ Yorumunuz çok kısa. En az {self.min_length} karakter olmalıdır."
                            )
                        continue
                    
                    # Gerekli içeriği kontrol et
                    if self.required_content:
                        all_found = True
                        missing_keywords = []
                        
                        for required in self.required_content:
                            if required.lower() not in comment_text.lower():
                                all_found = False
                                missing_keywords.append(required)
                                
                        if not all_found:
                            logger.debug(f"Gerekli içerik bulunamadı: {missing_keywords}")
                            if manual_check:
                                await self.bot.send_message(
                                    int(self.user_id),
                                    f"⚠️ Yorumunuzda şu kelimeler eksik: {', '.join(missing_keywords)}"
                                )
                            continue
                    
                    # Tüm koşulları sağlayan bir yorum bulundu
                    logger.info(f"Geçerli yorum bulundu: {self.user_id}, mesaj ID: {message.id}")
                    await self._complete_task()
                    return True
            
            # Hiç uygun yorum bulunamadı
            self.comments_checked = True
            logger.debug(f"Uygun yorum bulunamadı: {self.user_id}")
            return False
            
        except Exception as e:
            logger.error(f"Yorum kontrolünde hata: {e}")
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
                        f"✅ Tebrikler! Yorum göreviniz başarıyla tamamlandı.",
                        buttons=None
                    )
                else:
                    await self.bot.send_message(
                        int(self.user_id),
                        f"🎉 Tebrikler! Yorum yapma görevini başarıyla tamamladınız."
                    )
            except Exception as e:
                logger.error(f"Bildirim gönderme hatası: {e}")
            
            logger.info(f"Yorum görevi tamamlandı: {self.user_id}_{self.task_id}")
        else:
            logger.error(f"Görev tamamlama hatası: {self.user_id}_{self.task_id}")
    
    async def stop_listening(self):
        """Yorum yapma olaylarını dinlemeyi durdur"""
        if self.check_task:
            self.check_task.cancel()
            try:
                await self.check_task
            except asyncio.CancelledError:
                pass
            self.check_task = None
            
        if hasattr(self, '_callback_handler') and self._callback_handler:
            self.bot.remove_event_handler(self._callback_handler)
            self._callback_handler = None
            
        logger.info(f"Yorum görevi izleme durduruldu: {self.user_id}_{self.task_id}")
    
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
                    f"✅ Tebrikler! Yorum göreviniz bir yönetici tarafından onaylandı.",
                    buttons=None
                )
            else:
                await self.bot.send_message(
                    int(self.user_id),
                    f"🎉 Tebrikler! Yorum yapma göreviniz bir yönetici tarafından onaylandı."
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