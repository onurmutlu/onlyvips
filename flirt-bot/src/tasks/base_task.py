#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Base Task - Temel Görev Sınıfı
Tüm görev tipleri için temel sınıf.
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class BaseTask(ABC):
    """
    Görev doğrulama için temel sınıf.
    Tüm görev tipleri bu sınıftan türetilmelidir.
    """
    
    def __init__(
        self,
        user_id: str,
        task_id: str,
        expiry_time: int,
        verification_engine,
        bot,
        **kwargs
    ):
        """
        BaseTask yapıcısı
        
        Args:
            user_id: Kullanıcı ID'si
            task_id: Görev ID'si
            expiry_time: Görevin geçerlilik süresi (Unix timestamp)
            verification_engine: Görev doğrulama motoru referansı
            bot: Bot istemci referansı
            **kwargs: Alt sınıflar için ek parametreler
        """
        self.user_id = user_id
        self.task_id = task_id
        self.expiry_time = expiry_time
        self.creation_time = int(time.time())
        self.verification_engine = verification_engine
        self.bot = bot
        
        # Görev durumu
        self.is_active = True
        self.is_completed = False
        
        # Alt sınıflar için özel değişkenler
        self.details = kwargs
        
        logger.info(f"Görev oluşturuldu: {self.user_id}_{self.task_id}")
    
    def is_expired(self) -> bool:
        """
        Görevin süresinin dolup dolmadığını kontrol et
        
        Returns:
            bool: Görevin süresi dolduysa True, aksi halde False
        """
        return int(time.time()) > self.expiry_time
    
    @abstractmethod
    async def start_listening(self):
        """
        Görev için olay dinlemeyi başlat.
        Bu metot, göreve özgü olay dinleyicilerini kaydetmelidir.
        """
        pass
    
    @abstractmethod
    async def stop_listening(self):
        """
        Görev için olay dinlemeyi durdur.
        Bu metot, start_listening'de kaydedilen dinleyicileri kaldırmalıdır.
        """
        pass
    
    @abstractmethod
    async def verify_manually(self, admin_id: str) -> bool:
        """
        Görevi manuel olarak doğrula (yönetici tarafından)
        
        Args:
            admin_id: Yönetici ID'si
            
        Returns:
            bool: Doğrulama başarılı ise True, aksi halde False
        """
        pass
    
    async def cancel(self):
        """
        Görevi iptal et
        """
        if not self.is_active:
            return
            
        self.is_active = False
        await self.stop_listening()
        
        logger.info(f"Görev iptal edildi: {self.user_id}_{self.task_id}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Görevi sözlük olarak döndür (JSON serileştirme için)
        
        Returns:
            Dict[str, Any]: Görev verisi
        """
        return {
            "user_id": self.user_id,
            "task_id": self.task_id,
            "task_type": self.__class__.__name__,
            "creation_time": self.creation_time,
            "expiry_time": self.expiry_time,
            "is_active": self.is_active,
            "is_completed": self.is_completed,
            "details": self.details
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], verification_engine, bot):
        """
        Sözlükten görev oluştur
        
        Args:
            data: Görev verisi
            verification_engine: Görev doğrulama motoru
            bot: Bot istemcisi
            
        Returns:
            BaseTask: Oluşturulan görev
        """
        task = cls(
            user_id=data["user_id"],
            task_id=data["task_id"],
            expiry_time=data["expiry_time"],
            verification_engine=verification_engine,
            bot=bot,
            **data.get("details", {})
        )
        
        # Durum bilgilerini ayarla
        task.creation_time = data["creation_time"]
        task.is_active = data["is_active"]
        task.is_completed = data["is_completed"]
        
        return task 