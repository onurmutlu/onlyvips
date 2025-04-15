#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Görev Yöneticisi
Görev oluşturma, atama, takip etme ve doğrulama işlemlerini yöneten sınıf.
"""

import logging
import time
import asyncio
import json
from typing import Dict, List, Any, Optional, Union, Type
import random

# Görev tipleri
from .task_types.bot_mention_task import BotMentionTask
from .task_types.pin_check_task import PinCheckTask
from .task_types.post_share_task import PostShareTask
from .task_types.forward_message_task import ForwardMessageTask
from .task_types.deeplink_track_task import DeeplinkTrackTask
from .task_types.group_join_task import GroupJoinTask
from .task_types.join_channel_task import JoinChannelTask
from .task_types.message_task import MessageTask

from .base_task import BaseTask

logger = logging.getLogger(__name__)

class TaskManager:
    """Görev yönetimi için ana sınıf."""
    
    def __init__(self, bot, database_manager, bot_username=None, api_client=None):
        """
        TaskManager yapıcısı
        
        Args:
            bot: Telethon bot istemci nesnesi
            database_manager: Veritabanı yönetici nesnesi
            bot_username (str, optional): Bot kullanıcı adı
            api_client: Backend API istemcisi (isteğe bağlı)
        """
        self.bot = bot
        self.db = database_manager
        self.bot_username = bot_username
        self.api_client = api_client
        
        # Aktif görevleri saklayacak sözlük: {user_id_task_id: task_instance}
        self.active_tasks = {}
        
        # Görev tipleri haritası
        self.task_types = {
            "mention": BotMentionTask,
            "pin": PinCheckTask,
            "share": PostShareTask,
            "forward": ForwardMessageTask,
            "link": DeeplinkTrackTask,
            "group_join": GroupJoinTask,
            "channel_join": JoinChannelTask,
            "message": MessageTask
        }
        
        # Görev süre aşımı kontrol döngüsü
        self._expiry_check_task = None
        
    async def start(self):
        """Görev yöneticisini başlat"""
        logger.info("Görev yöneticisi başlatılıyor...")
        
        # Aktif görevleri veritabanından yükle
        await self._load_active_tasks()
        
        # Süre aşımı kontrol döngüsünü başlat
        self._expiry_check_task = asyncio.create_task(self._check_expired_tasks())
        
        logger.info(f"Görev yöneticisi başlatıldı. {len(self.active_tasks)} aktif görev yüklendi.")
        
    async def _load_active_tasks(self):
        """Aktif görevleri veritabanından yükle ve başlat"""
        try:
            # Veritabanından aktif görevleri al
            active_tasks_data = await self.db.get_active_tasks()
            
            if not active_tasks_data:
                logger.info("Yüklenecek aktif görev bulunamadı.")
                return
            
            # Her görevi yükle ve başlat
            for task_data in active_tasks_data:
                user_id = task_data.get("user_id")
                task_id = task_data.get("task_id")
                task_type = task_data.get("task_type")
                expiry_time = task_data.get("expiry_time")
                params = task_data.get("params", {})
                
                if not (user_id and task_id and task_type and expiry_time):
                    logger.warning(f"Eksik görev verisi, atlanıyor: {task_data}")
                    continue
                
                # Görev sınıfını bul
                task_class = self.task_types.get(task_type)
                if not task_class:
                    logger.warning(f"Bilinmeyen görev tipi: {task_type}, atlanıyor.")
                    continue
                
                # Görev nesnesini oluştur ve başlat
                try:
                    task = task_class(
                        user_id=user_id,
                        task_id=task_id,
                        expiry_time=expiry_time,
                        verification_engine=self,
                        bot=self.bot,
                        **params
                    )
                    
                    # Aktif görevler listesine ekle
                    task_key = f"{user_id}_{task_id}"
                    self.active_tasks[task_key] = task
                    
                    # Görevi dinlemeye başla
                    await task.start_listening()
                    
                    logger.info(f"Görev yüklendi ve başlatıldı: {task_key} ({task_type})")
                    
                except Exception as e:
                    logger.error(f"Görev yüklenirken hata: {task_key}, {e}")
                    
        except Exception as e:
            logger.error(f"Aktif görevler yüklenirken hata: {e}")
            
    async def assign_task(
        self, 
        user_id: str, 
        task_type: str, 
        task_params: Dict[str, Any] = None,
        duration_hours: int = 24
    ) -> Optional[str]:
        """
        Kullanıcıya yeni bir görev ata
        
        Args:
            user_id: Kullanıcı ID'si
            task_type: Görev tipi
            task_params: Görev parametreleri
            duration_hours: Görevin geçerlilik süresi (saat)
            
        Returns:
            str or None: Başarılı ise task_id, başarısız ise None
        """
        try:
            # Görev sınıfını bul
            task_class = self.task_types.get(task_type)
            if not task_class:
                logger.error(f"Bilinmeyen görev tipi: {task_type}")
                return None
            
            # Görev ID'si oluştur
            task_id = f"{int(time.time())}_{random.randint(1000, 9999)}"
            
            # Görev bitiş zamanını hesapla
            expiry_time = int(time.time()) + (duration_hours * 3600)
            
            # Görev parametrelerini hazırla
            params = task_params or {}
            
            # Görev nesnesini oluştur
            task = task_class(
                user_id=user_id,
                task_id=task_id,
                expiry_time=expiry_time,
                verification_engine=self,
                bot=self.bot,
                **params
            )
            
            # Görevi veritabanına kaydet
            await self.db.save_task(
                user_id=user_id,
                task_id=task_id,
                task_type=task_type,
                expiry_time=expiry_time,
                params=params,
                status="active"
            )
            
            # Aktif görevler listesine ekle
            task_key = f"{user_id}_{task_id}"
            self.active_tasks[task_key] = task
            
            # Görevi dinlemeye başla
            await task.start_listening()
            
            logger.info(f"Yeni görev atandı: {task_key} ({task_type})")
            
            return task_id
            
        except Exception as e:
            logger.error(f"Görev atanırken hata: {e}")
            return None
            
    async def get_user_tasks(
        self, 
        user_id: str,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Kullanıcının görevlerini getir
        
        Args:
            user_id: Kullanıcı ID'si
            status (optional): Filtrelenecek görev durumu (active, completed, expired)
            
        Returns:
            List[Dict]: Görevlerin listesi
        """
        try:
            # Veritabanından kullanıcının görevlerini al
            tasks = await self.db.get_user_tasks(user_id, status)
            return tasks
        except Exception as e:
            logger.error(f"Kullanıcı görevleri alınırken hata: {user_id}, {e}")
            return []
            
    async def verify_task(self, user_id: str, task_id: str, is_completed: bool) -> bool:
        """
        Görevi doğrula ve tamamla
        
        Args:
            user_id: Kullanıcı ID'si
            task_id: Görev ID'si
            is_completed: Görev başarıyla tamamlandı mı
            
        Returns:
            bool: İşlem başarılı mı
        """
        try:
            task_key = f"{user_id}_{task_id}"
            
            # Görev kaydını güncelle
            status = "completed" if is_completed else "failed"
            await self.db.update_task_status(user_id, task_id, status)
            
            # Görevi durdur
            task = self.active_tasks.get(task_key)
            if task:
                await task.stop_listening()
                self.active_tasks.pop(task_key, None)
            
            # Backend API'ye bildir
            if self.api_client and is_completed:
                try:
                    await self.api_client.task_completed(user_id, task_id)
                except Exception as e:
                    logger.error(f"API'ye görev tamamlama bildirimi gönderilirken hata: {e}")
            
            logger.info(f"Görev doğrulandı: {task_key}, durum: {status}")
            
            return True
            
        except Exception as e:
            logger.error(f"Görev doğrulanırken hata: {task_key}, {e}")
            return False
            
    async def manually_verify_task(self, user_id: str, task_id: str, admin_id: str) -> bool:
        """
        Görevi manuel olarak doğrula
        
        Args:
            user_id: Kullanıcı ID'si
            task_id: Görev ID'si
            admin_id: Doğrulayan yönetici ID'si
            
        Returns:
            bool: İşlem başarılı mı
        """
        try:
            task_key = f"{user_id}_{task_id}"
            
            # Görev nesnesini bul
            task = self.active_tasks.get(task_key)
            if not task:
                # Veritabanından görev bilgilerini al
                task_data = await self.db.get_task(user_id, task_id)
                if not task_data:
                    logger.warning(f"Manuel doğrulama için görev bulunamadı: {task_key}")
                    return False
                
                # Görev sınıfını bul
                task_type = task_data.get("task_type")
                task_class = self.task_types.get(task_type)
                if not task_class:
                    logger.warning(f"Bilinmeyen görev tipi: {task_type}")
                    return False
                
                # Görev nesnesini geçici olarak oluştur
                task = task_class(
                    user_id=user_id,
                    task_id=task_id,
                    expiry_time=int(time.time()) + 3600,  # 1 saat geçerli (önemsiz)
                    verification_engine=self,
                    bot=self.bot,
                    **(task_data.get("params", {}))
                )
            
            # Manuel doğrula
            result = await task.verify_manually(admin_id)
            
            if result:
                # Görev durumunu güncelle
                await self.db.update_task_status(user_id, task_id, "completed")
                
                # Aktif görevlerden kaldır
                if task_key in self.active_tasks:
                    await self.active_tasks[task_key].stop_listening()
                    self.active_tasks.pop(task_key, None)
                
                # Backend API'ye bildir
                if self.api_client:
                    try:
                        await self.api_client.task_completed(user_id, task_id, manual=True, admin_id=admin_id)
                    except Exception as e:
                        logger.error(f"API'ye manuel görev tamamlama bildirimi gönderilirken hata: {e}")
                
                logger.info(f"Görev manuel olarak doğrulandı: {task_key}, admin: {admin_id}")
                
            return result
            
        except Exception as e:
            logger.error(f"Görev manuel doğrulanırken hata: {task_key}, {e}")
            return False
    
    async def cancel_task(self, user_id: str, task_id: str) -> bool:
        """
        Görevi iptal et
        
        Args:
            user_id: Kullanıcı ID'si
            task_id: Görev ID'si
            
        Returns:
            bool: İşlem başarılı mı
        """
        try:
            task_key = f"{user_id}_{task_id}"
            
            # Görev nesnesini bul ve durdur
            task = self.active_tasks.get(task_key)
            if task:
                await task.stop_listening()
                self.active_tasks.pop(task_key, None)
            
            # Görev durumunu güncelle
            await self.db.update_task_status(user_id, task_id, "cancelled")
            
            logger.info(f"Görev iptal edildi: {task_key}")
            
            return True
            
        except Exception as e:
            logger.error(f"Görev iptal edilirken hata: {task_key}, {e}")
            return False
    
    async def get_task_details(self, user_id: str, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Görev detaylarını getir
        
        Args:
            user_id: Kullanıcı ID'si
            task_id: Görev ID'si
            
        Returns:
            Dict or None: Görev detayları veya None (bulunamadı)
        """
        try:
            # Veritabanından görev detaylarını al
            task_data = await self.db.get_task(user_id, task_id)
            return task_data
        except Exception as e:
            logger.error(f"Görev detayları alınırken hata: {user_id}_{task_id}, {e}")
            return None
    
    async def _check_expired_tasks(self):
        """Süre aşımına uğramış görevleri kontrol et ve temizle"""
        try:
            while True:
                now = int(time.time())
                tasks_to_remove = []
                
                # Aktif görevleri kontrol et
                for task_key, task in self.active_tasks.items():
                    # Görev süresi dolmuş mu?
                    if task.expiry_time < now:
                        user_id, task_id = task_key.split("_", 1)
                        
                        logger.info(f"Görev süresi doldu: {task_key}")
                        
                        # Görevi durdur
                        await task.stop_listening()
                        
                        # Veritabanını güncelle
                        await self.db.update_task_status(user_id, task_id, "expired")
                        
                        # Temizlenecek görevlere ekle
                        tasks_to_remove.append(task_key)
                        
                        # Kullanıcıya bildir
                        try:
                            await self.bot.send_message(
                                int(user_id),
                                f"⏰ Üzgünüz, '{task_id}' ID'li görevin süresi doldu ve tamamlanamadı."
                            )
                        except Exception as e:
                            logger.error(f"Süre aşımı bildirimi gönderilirken hata: {task_key}, {e}")
                
                # Temizlenecek görevleri kaldır
                for task_key in tasks_to_remove:
                    self.active_tasks.pop(task_key, None)
                
                # 5 dakika bekle
                await asyncio.sleep(300)
                
        except asyncio.CancelledError:
            logger.info("Görev süre aşımı kontrol döngüsü durduruldu.")
        except Exception as e:
            logger.error(f"Görev süre aşımı kontrolü sırasında hata: {e}")
    
    async def stop(self):
        """Görev yöneticisini durdur"""
        logger.info("Görev yöneticisi durduruluyor...")
        
        # Tüm aktif görevleri durdur
        for task_key, task in list(self.active_tasks.items()):
            try:
                await task.stop_listening()
            except Exception as e:
                logger.error(f"Görev durdurulurken hata: {task_key}, {e}")
        
        # Süre aşımı kontrol döngüsünü durdur
        if self._expiry_check_task:
            self._expiry_check_task.cancel()
            try:
                await self._expiry_check_task
            except asyncio.CancelledError:
                pass
            
        # Aktif görevleri temizle
        self.active_tasks.clear()
        
        logger.info("Görev yöneticisi durduruldu.") 