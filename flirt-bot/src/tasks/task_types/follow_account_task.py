#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Follow Account Task - Hesap Takip Görevi
Kullanıcının belirli bir Telegram hesabını takip etmesini doğrulayan görev tipi
"""

import logging
from typing import Dict, Any, Optional, Union
import time
import asyncio

from telethon import events, utils
from telethon.tl.functions.contacts import GetContactsRequest, DeleteContactsRequest, AddContactRequest
from telethon.tl.types import InputPeerUser, InputUser

from ..base_task import BaseTask

logger = logging.getLogger(__name__)

class FollowAccountTask(BaseTask):
    """Kullanıcının belirli bir Telegram hesabını takip etmesini gerektiren görev."""
    
    def __init__(
        self,
        user_id: str,
        task_id: str,
        expiry_time: int,
        verification_engine,
        bot,
        target_username: str,
        min_duration: int = 0,
        check_interval: int = 300,  # 5 dakikada bir kontrol et
        **kwargs
    ):
        """
        FollowAccountTask yapıcısı
        
        Args:
            user_id: Kullanıcı ID'si
            task_id: Görev ID'si
            expiry_time: Görevin geçerlilik süresi (Unix timestamp)
            verification_engine: Görev doğrulama motoru
            bot: Bot istemcisi
            target_username: Takip edilecek hesabın kullanıcı adı
            min_duration: Takip edilmesi gereken minimum süre (saniye)
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
        
        self.target_username = target_username.lstrip('@')  # @ işaretini kaldır
        self.target_id = None
        self.min_duration = min_duration
        self.check_interval = check_interval
        
        # İzleme durumu
        self.follow_time = None
        self.check_task = None
        self.verification_message_id = None
        
        logger.info(f"FollowAccountTask oluşturuldu: {self.user_id} için {self.target_username} hesabını takip etme")
    
    async def _resolve_target_id(self):
        """Takip edilecek hesabın ID'sini çözümle"""
        try:
            entity = await self.bot.get_entity(f"@{self.target_username}")
            self.target_id = utils.get_peer_id(entity)
            logger.info(f"Hedef kullanıcı ID çözümlendi: {self.target_username} -> {self.target_id}")
            return self.target_id
        except Exception as e:
            logger.error(f"Hedef kullanıcı ID çözümlenemedi: {self.target_username}, hata: {e}")
            return None
    
    async def _check_following(self) -> bool:
        """
        Kullanıcının hedef hesabı takip edip etmediğini kontrol et
        
        Returns:
            bool: Kullanıcı hedef hesabı takip ediyorsa True, değilse False
        """
        if not self.target_id:
            await self._resolve_target_id()
            if not self.target_id:
                return False
        
        try:
            # Kullanıcının hesabını takip edip etmediğini kontrol et
            # Not: Bu kısım API sınırlamaları nedeniyle zor olabilir. Kullanıcı hesabına erişim gerekebilir.
            # Telegram, bir hesabın başka bir hesabı takip edip etmediğini doğrudan söyleyen bir API sağlamıyor.
            # Bu nedenle, kullanıcıdan doğrulama isteyeceğiz
            
            # İlk kontrolde veya belirli aralıklarla kullanıcıdan doğrulama iste
            current_time = int(time.time())
            if not self.follow_time or (current_time - self.follow_time) % (24 * 3600) < self.check_interval:
                await self._request_verification()
                
            # Takip ediliyor olarak varsay (kullanıcı doğrulayacak)
            return True
        except Exception as e:
            logger.error(f"Takip kontrolünde hata: {e}")
            return False
    
    async def _request_verification(self):
        """Kullanıcıdan takip doğrulaması iste"""
        try:
            from telethon import Button
            
            # Kullanıcıya doğrulama mesajı gönder
            message = await self.bot.send_message(
                int(self.user_id),
                f"👥 **Hesap Takip Görevi**\n\n"
                f"@{self.target_username} hesabını takip ettiğinizi doğrulamanız gerekmektedir.\n\n"
                f"Eğer bu hesabı takip ediyorsanız 'Takip Ediyorum' butonuna tıklayın.",
                buttons=[Button.inline("✅ Takip Ediyorum", data=f"follow_verify_{self.task_id}")]
            )
            
            self.verification_message_id = message.id
            
            # Callback handler ekle
            @self.bot.on(events.CallbackQuery(pattern=f"follow_verify_{self.task_id}"))
            async def on_follow_verify(event):
                if not self.is_active or self.is_completed:
                    return
                    
                # Kullanıcı kontrolü
                if event.sender_id != int(self.user_id):
                    return
                    
                # Kullanıcıya beklemesini söyle
                await event.answer("Takip kontrolü yapılıyor...")
                
                # İlk kez takip edildiyse zamanı kaydet
                if not self.follow_time:
                    self.follow_time = int(time.time())
                    
                    # Minimum süre yoksa hemen tamamla
                    if self.min_duration <= 0:
                        await self._complete_task()
                        # Mesajı güncelle
                        await self.bot.edit_message(
                            int(self.user_id),
                            self.verification_message_id,
                            f"✅ Tebrikler! @{self.target_username} hesabını takip etme göreviniz tamamlandı.",
                            buttons=None
                        )
                    else:
                        # Minimum süre için beklemesi gerektiğini bildir
                        hours = self.min_duration // 3600
                        minutes = (self.min_duration % 3600) // 60
                        
                        time_text = ""
                        if hours > 0:
                            time_text += f"{hours} saat "
                        if minutes > 0:
                            time_text += f"{minutes} dakika"
                        
                        await self.bot.edit_message(
                            int(self.user_id),
                            self.verification_message_id,
                            f"⏳ @{self.target_username} hesabını takip ettiğiniz doğrulandı.\n\n"
                            f"Görevin tamamlanması için {time_text} boyunca takip etmeye devam etmelisiniz.",
                            buttons=[Button.inline("✅ Hala Takip Ediyorum", data=f"follow_verify_{self.task_id}")]
                        )
                else:
                    # Süre kontrolü
                    current_time = int(time.time())
                    duration = current_time - self.follow_time
                    
                    if duration >= self.min_duration:
                        # Görevi tamamla
                        await self._complete_task()
                        # Mesajı güncelle
                        await self.bot.edit_message(
                            int(self.user_id),
                            self.verification_message_id,
                            f"✅ Tebrikler! @{self.target_username} hesabını takip etme göreviniz tamamlandı.",
                            buttons=None
                        )
                    else:
                        # Kalan süreyi bildir
                        remaining = self.min_duration - duration
                        hours = remaining // 3600
                        minutes = (remaining % 3600) // 60
                        
                        time_text = ""
                        if hours > 0:
                            time_text += f"{hours} saat "
                        if minutes > 0:
                            time_text += f"{minutes} dakika"
                        
                        await event.answer(f"Hala {time_text} takip etmeye devam etmelisiniz.")
                
            self._callback_handler = on_follow_verify
            
        except Exception as e:
            logger.error(f"Doğrulama isteği gönderilirken hata: {e}")
    
    async def _periodic_check(self):
        """Periyodik takip kontrolü yap"""
        while self.is_active and not self.is_completed:
            try:
                is_following = await self._check_following()
                
                if is_following:
                    # İlk takip zamanını kaydet
                    if not self.follow_time:
                        self.follow_time = int(time.time())
                        logger.info(f"Kullanıcı takip etmeye başladı: {self.user_id}, hedef: {self.target_username}")
                    
                    # Minimum süreyi kontrol et
                    if self.min_duration > 0 and self.follow_time:
                        current_time = int(time.time())
                        duration = current_time - self.follow_time
                        
                        if duration >= self.min_duration:
                            logger.info(f"Minimum takip süresi tamamlandı: {self.user_id}, süre: {duration}s")
                            await self._complete_task()
                            break
                else:
                    # Takibi bıraktıysa ve daha önce takip etmeye başladıysa, sıfırla
                    if self.follow_time:
                        logger.info(f"Kullanıcı takibi bıraktı: {self.user_id}, hedef: {self.target_username}")
                        self.follow_time = None
                        
                        # Kullanıcıya bildir
                        await self.bot.send_message(
                            int(self.user_id),
                            f"⚠️ @{self.target_username} hesabını takip etmeyi bıraktığınız tespit edildi. "
                            f"Görevin tamamlanması için takip etmeye devam etmelisiniz."
                        )
            
            except Exception as e:
                logger.error(f"Periyodik kontrol hatası: {e}")
            
            # Bir sonraki kontrole kadar bekle
            await asyncio.sleep(self.check_interval)
    
    async def start_listening(self):
        """Takip durumunu izlemeye başla"""
        if self.check_task:
            return
            
        # İlk durumu kontrol et
        is_following = await self._check_following()
        
        # Periyodik kontrol görevini başlat
        self.check_task = asyncio.create_task(self._periodic_check())
        logger.info(f"Hesap takip görevi izleme başlatıldı: {self.user_id}_{self.task_id}")
    
    async def _complete_task(self):
        """Görevi tamamla"""
        if not self.is_active or self.is_completed:
            return
            
        # Görevi tamamlandı olarak işaretle
        success = await self.verification_engine.verify_task(self.user_id, self.task_id)
        
        if success:
            self.is_completed = True
            
            # Kullanıcıya bildirim gönder (eğer verification mesajı dışında bir bildirim göndermek istenirse)
            if not self.verification_message_id:
                try:
                    await self.bot.send_message(
                        int(self.user_id),
                        f"🎉 Tebrikler! @{self.target_username} hesabını takip etme görevini başarıyla tamamladınız."
                    )
                except Exception as e:
                    logger.error(f"Bildirim gönderme hatası: {e}")
            
            logger.info(f"Hesap takip görevi tamamlandı: {self.user_id}_{self.task_id}")
        else:
            logger.error(f"Görev tamamlama hatası: {self.user_id}_{self.task_id}")
    
    async def stop_listening(self):
        """Takip durumunu izlemeyi durdur"""
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
            
        logger.info(f"Hesap takip görevi izleme durduruldu: {self.user_id}_{self.task_id}")
    
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
                    f"✅ Tebrikler! @{self.target_username} hesabını takip etme göreviniz bir yönetici tarafından onaylandı.",
                    buttons=None
                )
            else:
                await self.bot.send_message(
                    int(self.user_id),
                    f"🎉 Tebrikler! @{self.target_username} hesabını takip etme göreviniz bir yönetici tarafından onaylandı."
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