#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Schedule Post Task - Programlı Gönderi Görevi
Kullanıcının belirli bir tarihte/saatte mesaj göndermesini doğrulayan görev tipi
"""

import logging
from typing import Dict, Any, Optional, Union, List
import asyncio
import time
import datetime
from telethon import events, Button

from ..base_task import BaseTask

logger = logging.getLogger(__name__)

class SchedulePostTask(BaseTask):
    """Kullanıcının belirli bir tarihte/saatte mesaj göndermesini gerektiren görev."""
    
    def __init__(
        self,
        user_id: str,
        task_id: str,
        expiry_time: int,
        verification_engine,
        bot,
        target_chat_id: Union[str, int],
        schedule_timestamp: int,
        required_content: Optional[List[str]] = None,
        min_length: Optional[int] = None,
        time_window: int = 300,  # ±5 dakika tolerans penceresi (saniye)
        **kwargs
    ):
        """
        SchedulePostTask yapıcısı
        
        Args:
            user_id: Kullanıcı ID'si
            task_id: Görev ID'si
            expiry_time: Görevin geçerlilik süresi (Unix timestamp)
            verification_engine: Görev doğrulama motoru
            bot: Bot istemcisi
            target_chat_id: Hedef sohbet ID'si
            schedule_timestamp: Mesajın gönderilmesi gereken zaman (Unix timestamp)
            required_content: Mesajın içermesi gereken kelimeler (isteğe bağlı)
            min_length: Minimum mesaj uzunluğu (isteğe bağlı)
            time_window: Zamanlama tolerans penceresi (saniye)
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
        self.schedule_timestamp = schedule_timestamp
        self.required_content = required_content or []
        self.min_length = min_length or 0
        self.time_window = time_window
        
        # Event handlers
        self._message_handler = None
        self._reminder_task = None
        self._scheduled = False
        
        logger.info(f"SchedulePostTask oluşturuldu: {self.user_id} için {self.target_chat_id} grubuna programlı mesaj gönderme")
    
    async def start_listening(self):
        """Mesaj olaylarını dinlemeye başla ve hatırlatma zamanlayıcısını ayarla"""
        if self._message_handler:
            return
            
        # Zamanlanmış mesaj için hatırlatıcı ayarla
        current_time = int(time.time())
        time_until_scheduled = self.schedule_timestamp - current_time
        
        # Programlanan zaman geçmişte mi kontrol et
        if time_until_scheduled < 0:
            if abs(time_until_scheduled) > self.time_window:
                logger.warning(f"Programlanan zaman geçmişte: {self.user_id}, {time_until_scheduled} saniye önce")
                await self.bot.send_message(
                    int(self.user_id),
                    f"⚠️ Programlanan mesaj zamanı geçmiş. Yine de mesaj gönderebilirsiniz, ancak geç kalınmış sayılabilir."
                )
            else:
                # Tolerans penceresi içinde, sorun yok
                pass
        elif time_until_scheduled > 0:
            # Hatırlatıcıları ayarla
            self._schedule_reminders(time_until_scheduled)
        
        @self.bot.on(events.NewMessage())
        async def on_message(event):
            if not self.is_active or self.is_completed:
                return
                
            try:
                # Kullanıcı ID'sini kontrol et
                if event.sender_id != int(self.user_id):
                    return
                    
                # Hedef sohbet ID'sini kontrol et
                chat = await event.get_chat()
                chat_id = str(chat.id)
                
                # Hedef chat_id belirtilmişse kontrol et
                if self.target_chat_id != "any" and chat_id != self.target_chat_id:
                    logger.debug(f"Farklı sohbet: {chat_id}, beklenen: {self.target_chat_id}")
                    return
                
                # Mesaj içeriğini kontrol et
                message_text = event.message.text or ""
                
                # Minimum uzunluğu kontrol et
                if len(message_text) < self.min_length:
                    logger.debug(f"Mesaj çok kısa: {len(message_text)}, minimum: {self.min_length}")
                    return
                
                # Gerekli içeriği kontrol et
                if self.required_content:
                    all_found = True
                    for required in self.required_content:
                        if required.lower() not in message_text.lower():
                            all_found = False
                            break
                            
                    if not all_found:
                        logger.debug(f"Gerekli içerik bulunamadı: {self.required_content}")
                        return
                
                # Zamanlamayı kontrol et
                current_time = int(time.time())
                time_diff = current_time - self.schedule_timestamp
                
                # Zaman penceresi içinde mi?
                if abs(time_diff) <= self.time_window:
                    logger.info(f"Mesaj doğru zamanda gönderildi: {self.user_id}, fark: {time_diff} saniye")
                    await self._complete_task(perfectly_timed=True)
                elif time_diff > self.time_window:
                    # Geç kalındı ama yine de kabul et
                    logger.info(f"Mesaj geç gönderildi: {self.user_id}, fark: {time_diff} saniye")
                    await self._complete_task(perfectly_timed=False)
                else:
                    # Çok erken, henüz tamamlama
                    early_seconds = abs(time_diff)
                    minutes = early_seconds // 60
                    seconds = early_seconds % 60
                    logger.info(f"Mesaj erken gönderildi: {self.user_id}, {minutes} dakika {seconds} saniye erken")
                    
                    # Kullanıcıya bildir (isteğe bağlı)
                    await self.bot.send_message(
                        int(self.user_id),
                        f"⏰ Mesajınız programlanan zamandan {minutes} dakika {seconds} saniye erken gönderildi. "
                        f"Programlanan zamanda veya {self.time_window//60} dakika içinde göndermeniz gerekmektedir."
                    )
                
            except Exception as e:
                logger.error(f"Mesaj işlenirken hata: {e}")
                
        self._message_handler = on_message
        logger.info(f"Programlı mesaj dinleme başlatıldı: {self.user_id}")
    
    def _schedule_reminders(self, time_until_scheduled):
        """Hatırlatıcıları zamanlama"""
        import asyncio
        
        async def send_reminders():
            try:
                # 1 gün kala
                if time_until_scheduled > 86400:
                    await asyncio.sleep(time_until_scheduled - 86400)
                    await self._send_reminder(86400)
                
                # 1 saat kala
                if time_until_scheduled > 3600:
                    await asyncio.sleep(max(0, time_until_scheduled - 3600 - (time_until_scheduled - 86400 if time_until_scheduled > 86400 else 0)))
                    await self._send_reminder(3600)
                
                # 15 dakika kala
                if time_until_scheduled > 900:
                    await asyncio.sleep(max(0, time_until_scheduled - 900 - (time_until_scheduled - 3600 if time_until_scheduled > 3600 else 0)))
                    await self._send_reminder(900)
                
                # 5 dakika kala
                if time_until_scheduled > 300:
                    await asyncio.sleep(max(0, time_until_scheduled - 300 - (time_until_scheduled - 900 if time_until_scheduled > 900 else 0)))
                    await self._send_reminder(300)
                
                # Tam zamanında
                await asyncio.sleep(max(0, time_until_scheduled - (time_until_scheduled - 300 if time_until_scheduled > 300 else 0)))
                await self._send_reminder(0)
                
            except asyncio.CancelledError:
                logger.info(f"Hatırlatıcı görev iptal edildi: {self.user_id}")
            except Exception as e:
                logger.error(f"Hatırlatıcı görevde hata: {e}")
        
        self._reminder_task = asyncio.create_task(send_reminders())
    
    async def _send_reminder(self, seconds_remaining):
        """Hatırlatma mesajı gönder"""
        if not self.is_active or self.is_completed:
            return
            
        try:
            if seconds_remaining == 0:
                # Tam zamanı
                await self.bot.send_message(
                    int(self.user_id),
                    f"⏰ **Şimdi!** {self.target_chat_id} grubuna mesajınızı gönderme zamanı geldi!"
                )
            elif seconds_remaining == 300:
                # 5 dakika kala
                await self.bot.send_message(
                    int(self.user_id),
                    f"⏰ **5 dakika kaldı!** {self.target_chat_id} grubuna mesajınızı göndermeye hazırlanın."
                )
            elif seconds_remaining == 900:
                # 15 dakika kala
                await self.bot.send_message(
                    int(self.user_id),
                    f"⏰ **15 dakika kaldı!** {self.target_chat_id} grubuna programlı mesaj gönderme göreviniz yaklaşıyor."
                )
            elif seconds_remaining == 3600:
                # 1 saat kala
                await self.bot.send_message(
                    int(self.user_id),
                    f"⏰ **1 saat kaldı!** {self.target_chat_id} grubuna programlı mesaj gönderme göreviniz için 1 saat kaldı."
                )
            elif seconds_remaining == 86400:
                # 1 gün kala
                # Programlı zamanı formatla
                scheduled_dt = datetime.datetime.fromtimestamp(self.schedule_timestamp)
                formatted_time = scheduled_dt.strftime("%H:%M")
                
                await self.bot.send_message(
                    int(self.user_id),
                    f"⏰ **Hatırlatma!** Yarın saat {formatted_time}'da {self.target_chat_id} grubuna mesaj gönderme göreviniz var."
                )
        except Exception as e:
            logger.error(f"Hatırlatma mesajı gönderilirken hata: {e}")
    
    async def _complete_task(self, perfectly_timed=True):
        """Görevi tamamla"""
        if not self.is_active or self.is_completed:
            return
            
        # Görevi tamamlandı olarak işaretle
        success = await self.verification_engine.verify_task(self.user_id, self.task_id)
        
        if success:
            self.is_completed = True
            
            # Hatırlatıcıyı iptal et
            if self._reminder_task:
                self._reminder_task.cancel()
                
            # Kullanıcıya bildirim gönder
            message = f"🎉 Tebrikler! Programlı mesaj gönderme görevini başarıyla tamamladınız."
            if not perfectly_timed:
                message += " Mesajınız biraz geç gönderildi, ancak yine de kabul edildi."
                
            await self.bot.send_message(
                int(self.user_id),
                message
            )
            
            logger.info(f"Programlı mesaj görevi tamamlandı: {self.user_id}_{self.task_id}")
        else:
            logger.error(f"Görev tamamlama hatası: {self.user_id}_{self.task_id}")
    
    async def stop_listening(self):
        """Mesaj olaylarını dinlemeyi durdur"""
        if self._message_handler:
            self.bot.remove_event_handler(self._message_handler)
            self._message_handler = None
            
        if self._reminder_task:
            self._reminder_task.cancel()
            try:
                await self._reminder_task
            except asyncio.CancelledError:
                pass
            except Exception:
                pass
            self._reminder_task = None
            
        logger.info(f"Programlı mesaj dinleme durduruldu: {self.user_id}")
    
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
            
            # Dinleyiciyi durdur
            await self.stop_listening()
            
            # Kullanıcıya bildirim gönder
            await self.bot.send_message(
                int(self.user_id),
                f"🎉 Tebrikler! Programlı mesaj gönderme göreviniz bir yönetici tarafından onaylandı."
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