#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Voting Task - Oylama Görevi
Kullanıcının belirli bir Telegram anketine/oylamasına katılmasını doğrulayan görev tipi
"""

import logging
from typing import Dict, Any, Optional, Union, List
import time
from telethon import events, Button

from ..base_task import BaseTask

logger = logging.getLogger(__name__)

class VotingTask(BaseTask):
    """Kullanıcının belirli bir ankete oy vermesini gerektiren görev."""
    
    def __init__(
        self,
        user_id: str,
        task_id: str,
        expiry_time: int,
        verification_engine,
        bot,
        poll_message_id: int,
        poll_chat_id: Union[str, int],
        expected_option: Optional[int] = None,
        is_anonymous: bool = True,
        check_interval: int = 300,  # 5 dakikada bir kontrol et
        **kwargs
    ):
        """
        VotingTask yapıcısı
        
        Args:
            user_id: Kullanıcı ID'si
            task_id: Görev ID'si
            expiry_time: Görevin geçerlilik süresi (Unix timestamp)
            verification_engine: Görev doğrulama motoru
            bot: Bot istemcisi
            poll_message_id: Anket mesajının ID'si
            poll_chat_id: Anketin bulunduğu sohbet ID'si
            expected_option: Beklenen oy seçeneği (isteğe bağlı)
            is_anonymous: Anketin anonim olup olmadığı
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
        
        self.poll_message_id = poll_message_id
        self.poll_chat_id = str(poll_chat_id)
        self.expected_option = expected_option
        self.is_anonymous = is_anonymous
        self.check_interval = check_interval
        
        # Anket bilgileri
        self.poll_message = None
        self.poll_voters = {}
        
        # İzleme durumu
        self.check_task = None
        self.verification_message_id = None
        
        logger.info(f"VotingTask oluşturuldu: {self.user_id} için anket katılımı görevi")
    
    async def start_listening(self):
        """Anket oy işlemlerini dinlemeye başla"""
        if self.check_task:
            return
            
        # Anket mesajını getir
        try:
            self.poll_message = await self.bot.get_messages(
                entity=self.poll_chat_id,
                ids=self.poll_message_id
            )
            
            if not self.poll_message or not hasattr(self.poll_message, 'poll'):
                logger.error(f"Anket mesajı bulunamadı: {self.poll_chat_id}/{self.poll_message_id}")
                # Kullanıcıya hata bildir
                await self.bot.send_message(
                    int(self.user_id),
                    f"⚠️ Anket mesajı bulunamadı. Lütfen bir yönetici ile iletişime geçin."
                )
                return
                
            logger.info(f"Anket mesajı bulundu: {self.poll_message.id}")
            
            if self.is_anonymous:
                # Anonim anketlerde doğrulama butonu ile kontrol et
                await self._send_verification_message()
            else:
                # Anonim olmayan anketlerde periyodik kontrol başlat
                import asyncio
                self.check_task = asyncio.create_task(self._periodic_check())
                
        except Exception as e:
            logger.error(f"Anket mesajı alınırken hata: {e}")
            # Kullanıcıya hata bildir
            await self.bot.send_message(
                int(self.user_id),
                f"⚠️ Anket kontrolü sırasında bir hata oluştu. Lütfen bir yönetici ile iletişime geçin."
            )
    
    async def _send_verification_message(self):
        """Doğrulama mesajını gönder (anonim anketler için)"""
        try:
            # Anket linkini oluştur
            if isinstance(self.poll_chat_id, str) and self.poll_chat_id.startswith('@'):
                poll_link = f"https://t.me/{self.poll_chat_id.lstrip('@')}/{self.poll_message_id}"
            else:
                # Kanal/grup ID kullanıyorsa, kullanıcılara nasıl erişeceğini açıkla
                poll_link = f"İlgili kanaldaki {self.poll_message_id} ID'li anket"
                
            # Doğrulama mesajını gönder
            message = await self.bot.send_message(
                int(self.user_id),
                f"📊 Aşağıdaki ankete katılın ve ardından 'Oyladım' butonuna tıklayın:\n\n{poll_link}",
                buttons=[Button.inline("✅ Oyladım", data=f"vote_verify_{self.task_id}")]
            )
            
            self.verification_message_id = message.id
            
            # Callback handler ekle
            @self.bot.on(events.CallbackQuery(pattern=f"vote_verify_{self.task_id}"))
            async def on_vote_verify(event):
                if not self.is_active or self.is_completed:
                    return
                    
                # Kullanıcı kontrolü
                if event.sender_id != int(self.user_id):
                    return
                    
                # Kullanıcıya beklemesini söyle
                await event.answer("Oy kontrolü yapılıyor...")
                
                # Manuel doğrulama isteği gönder
                await self._request_manual_verification()
                
                # Mesajı güncelle
                await self.bot.edit_message(
                    int(self.user_id),
                    self.verification_message_id,
                    "✅ Oy doğrulama talebiniz alındı. Kısa süre içinde bir yönetici tarafından incelenecektir.",
                    buttons=None
                )
                
            self._handler = on_vote_verify
            
        except Exception as e:
            logger.error(f"Doğrulama mesajı gönderilirken hata: {e}")
    
    async def _request_manual_verification(self):
        """Yöneticiden manuel doğrulama iste"""
        try:
            # Yönetici grubuna mesaj gönder (burada yönetici grubu ID'sini kullanmalısınız)
            admin_group_id = "-1001234567890"  # Değiştirilmeli
            
            await self.bot.send_message(
                admin_group_id,
                f"🔍 **Anket Katılımı Doğrulama İsteği**\n\n"
                f"👤 Kullanıcı: `{self.user_id}`\n"
                f"🆔 Görev: `{self.task_id}`\n"
                f"📊 Anket: {self.poll_chat_id}/{self.poll_message_id}\n\n"
                f"Bu kullanıcı ankete katıldığını iddia ediyor. Lütfen doğrulayın.",
                buttons=[
                    [
                        Button.inline("✅ Onayla", data=f"admin_verify_{self.user_id}_{self.task_id}"),
                        Button.inline("❌ Reddet", data=f"admin_reject_{self.user_id}_{self.task_id}")
                    ]
                ]
            )
            
            logger.info(f"Manuel doğrulama isteği gönderildi: {self.user_id}_{self.task_id}")
            
        except Exception as e:
            logger.error(f"Manuel doğrulama isteği gönderilirken hata: {e}")
    
    async def _periodic_check(self):
        """Periyodik olarak kullanıcının oy verip vermediğini kontrol et"""
        import asyncio
        
        while self.is_active and not self.is_completed:
            try:
                # Anket mesajını yenile
                updated_poll = await self.bot.get_messages(
                    entity=self.poll_chat_id,
                    ids=self.poll_message_id
                )
                
                if not updated_poll or not hasattr(updated_poll, 'poll'):
                    logger.error(f"Güncel anket bulunamadı: {self.poll_chat_id}/{self.poll_message_id}")
                    await asyncio.sleep(self.check_interval)
                    continue
                
                # Ankete oy verenler
                poll_results = updated_poll.poll.results
                
                if not self.is_anonymous and hasattr(poll_results, 'voters'):
                    for i, voters_info in enumerate(poll_results.voters):
                        voters = getattr(voters_info, 'voters', [])
                        for voter in voters:
                            if str(voter.user_id) == self.user_id:
                                # Beklenen seçenek kontrolü
                                if self.expected_option is None or self.expected_option == i:
                                    await self._complete_task()
                                    return
                
            except Exception as e:
                logger.error(f"Anket kontrolü sırasında hata: {e}")
                
            # Bir sonraki kontrole kadar bekle
            await asyncio.sleep(self.check_interval)
    
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
                await self.bot.send_message(
                    int(self.user_id),
                    f"🎉 Tebrikler! Anket katılımı görevini başarıyla tamamladınız."
                )
            except Exception as e:
                logger.error(f"Bildirim gönderme hatası: {e}")
            
            logger.info(f"Anket katılımı görevi tamamlandı: {self.user_id}_{self.task_id}")
        else:
            logger.error(f"Görev tamamlama hatası: {self.user_id}_{self.task_id}")
    
    async def stop_listening(self):
        """Anket katılımı izlemeyi durdur"""
        if self.check_task:
            self.check_task.cancel()
            try:
                await self.check_task
            except asyncio.CancelledError:
                pass
            self.check_task = None
            
        if self._handler:
            self.bot.remove_event_handler(self._handler)
            self._handler = None
            
        logger.info(f"Anket katılımı görevi izleme durduruldu: {self.user_id}_{self.task_id}")
    
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
            await self.bot.send_message(
                int(self.user_id),
                f"🎉 Tebrikler! Anket katılımı göreviniz bir yönetici tarafından onaylandı."
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