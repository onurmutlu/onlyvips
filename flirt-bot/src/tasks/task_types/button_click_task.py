#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Button Click Task - Buton Tıklama Görevi
Kullanıcının belirli bir inline butona tıklamasını doğrulayan görev tipi
"""

import logging
from typing import Dict, Any, Optional, List, Union
import time
import re

from telethon import events, Button

from ..base_task import BaseTask

logger = logging.getLogger(__name__)

class ButtonClickTask(BaseTask):
    """Kullanıcının belirli bir inline butona tıklamasını doğrulayan görev."""
    
    def __init__(
        self,
        user_id: str,
        task_id: str,
        expiry_time: int,
        verification_engine,
        bot,
        button_data: str,
        message_text: Optional[str] = None,
        message_photo: Optional[str] = None,
        buttons: Optional[List[List[Dict[str, str]]]] = None,
        send_task_message: bool = True,
        **kwargs
    ):
        """
        ButtonClickTask yapıcısı
        
        Args:
            user_id: Kullanıcı ID'si
            task_id: Görev ID'si
            expiry_time: Görevin geçerlilik süresi (Unix timestamp)
            verification_engine: Görev doğrulama motoru
            bot: Bot istemcisi
            button_data: Buton callback data'sı (doğrulama için)
            message_text: Gönderilecek mesaj metni (isteğe bağlı)
            message_photo: Gönderilecek mesaj fotoğraf URL'si (isteğe bağlı)
            buttons: Buton yapılandırması (isteğe bağlı, otomatik oluşturulacak)
            send_task_message: Görev mesajı gönderilsin mi (varsayılan True)
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
        
        self.button_data = button_data
        self.message_text = message_text or "Lütfen görevi tamamlamak için aşağıdaki butona tıklayın."
        self.message_photo = message_photo
        self.buttons = buttons
        self.send_task_message = send_task_message
        
        # Görev mesajı ID'si (daha sonra düzenleme/silme için)
        self.task_message_id = None
        
        # Callback handler
        self._callback_handler = None
        
        logger.info(f"ButtonClickTask oluşturuldu: {self.user_id} için buton tıklama görevi (data: {self.button_data})")
    
    async def _generate_buttons(self):
        """Butonları oluştur"""
        if self.buttons:
            # Özel buton yapılandırması
            button_rows = []
            for row in self.buttons:
                button_row = []
                for btn in row:
                    text = btn.get("text", "Tıkla")
                    data = btn.get("data", "click")
                    button_row.append(Button.inline(text, data=data))
                button_rows.append(button_row)
            return button_rows
        else:
            # Varsayılan tek buton
            return [
                [Button.inline("Görevi Tamamla", data=self.button_data)]
            ]
    
    async def _send_task_message(self):
        """Görev mesajını gönder"""
        if not self.send_task_message:
            return
            
        try:
            buttons = await self._generate_buttons()
            
            # Mesajı gönder
            if self.message_photo:
                # Fotoğraf ile mesaj
                message = await self.bot.send_file(
                    int(self.user_id),
                    self.message_photo,
                    caption=self.message_text,
                    buttons=buttons
                )
            else:
                # Sadece metin mesajı
                message = await self.bot.send_message(
                    int(self.user_id),
                    self.message_text,
                    buttons=buttons
                )
                
            self.task_message_id = message.id
            logger.info(f"Görev mesajı gönderildi: {self.user_id}, message_id: {self.task_message_id}")
        except Exception as e:
            logger.error(f"Görev mesajı gönderme hatası: {e}")
    
    async def start_listening(self):
        """Callback olaylarını dinlemeye başla"""
        if self._callback_handler:
            return
            
        # Görev mesajını gönder
        await self._send_task_message()
        
        @self.bot.on(events.CallbackQuery())
        async def on_callback(event):
            if not self.is_active or self.is_completed:
                return
                
            try:
                # Kullanıcı kontrolü
                if event.sender_id != int(self.user_id):
                    return
                    
                # Data kontrolü
                callback_data = event.data.decode('utf-8')
                
                if callback_data == self.button_data:
                    logger.info(f"Doğru buton tıklandı: {self.user_id}, data: {callback_data}")
                    
                    # Kullanıcıya bilgi mesajı
                    await event.answer("Görev tamamlanıyor...", alert=True)
                    
                    # Görevi tamamla
                    await self.verification_engine.verify_task(self.user_id, self.task_id)
                    self.is_completed = True
                    
                    # Mesajı güncelle (opsiyonel)
                    try:
                        if self.task_message_id:
                            await self.bot.edit_message(
                                int(self.user_id),
                                self.task_message_id,
                                f"✅ {self.message_text}\n\n🎉 Tebrikler! Görev başarıyla tamamlandı.",
                                buttons=None
                            )
                    except Exception as e:
                        logger.error(f"Mesaj güncelleme hatası: {e}")
                    
                    # Kullanıcıya teşekkür/bilgi mesajı
                    await self.bot.send_message(
                        int(self.user_id),
                        "🎉 Tebrikler! Buton tıklama görevini başarıyla tamamladınız."
                    )
                else:
                    # Yanlış buton tıklandı
                    logger.debug(f"Yanlış buton tıklandı: {self.user_id}, data: {callback_data}")
                    await event.answer("Bu buton görev için geçerli değil.", alert=True)
                    
            except Exception as e:
                logger.error(f"Callback işlenirken hata: {e}")
                await event.answer("Bir hata oluştu, lütfen tekrar deneyin.", alert=True)
                
        self._callback_handler = on_callback
        logger.info(f"Buton tıklama dinleme başlatıldı: {self.user_id}")
    
    async def stop_listening(self):
        """Callback olaylarını dinlemeyi durdur"""
        if self._callback_handler:
            self.bot.remove_event_handler(self._callback_handler)
            self._callback_handler = None
            logger.info(f"Buton tıklama dinleme durduruldu: {self.user_id}")
    
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
            
            # Mesajı güncelle (opsiyonel)
            try:
                if self.task_message_id:
                    await self.bot.edit_message(
                        int(self.user_id),
                        self.task_message_id,
                        f"✅ {self.message_text}\n\n🎉 Göreviniz bir yönetici tarafından onaylandı.",
                        buttons=None
                    )
            except Exception as e:
                logger.error(f"Mesaj güncelleme hatası: {e}")
            
            # Kullanıcıya bildirim gönder
            await self.bot.send_message(
                int(self.user_id),
                "🎉 Tebrikler! Buton tıklama göreviniz bir yönetici tarafından onaylandı."
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