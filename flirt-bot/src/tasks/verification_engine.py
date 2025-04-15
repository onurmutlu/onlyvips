#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Verification Engine - Görev Doğrulama Motoru
Görevlerin doğrulanması, izlenmesi ve yönetilmesi için temel sınıf
"""

import logging
import json
import os
import time
from typing import Dict, List, Optional, Any, Type

logger = logging.getLogger(__name__)

class VerificationEngine:
    """
    Görev doğrulama motoru.
    Tüm görevleri takip eder ve durumlarını yönetir.
    """
    
    def __init__(self, bot, db_path: str = "data/tasks.json"):
        """
        VerificationEngine yapıcısı
        
        Args:
            bot: Bot istemcisi
            db_path: Görev veritabanı yolu
        """
        self.bot = bot
        self.db_path = db_path
        self.tasks = {}  # user_id_task_id -> task
        self.active_tasks_by_user = {}  # user_id -> {task_id: task}
        self.plugin_registry = {}  # task_type -> task_class
        
        # Veritabanı dizinini oluştur
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Önceki görevleri yükle
        self._load_tasks()
        
        logger.info(f"Doğrulama motoru başlatıldı. Veritabanı: {db_path}")
    
    def register_plugin(self, task_type: str, task_class):
        """
        Görev eklentisini kaydet
        
        Args:
            task_type: Görev tipi (benzersiz isim)
            task_class: Görev sınıfı (BaseTask'tan türetilmiş)
        """
        self.plugin_registry[task_type] = task_class
        logger.info(f"Görev eklentisi kaydedildi: {task_type}")
    
    async def create_task(self, user_id: str, task_type: str, **kwargs):
        """
        Yeni görev oluştur
        
        Args:
            user_id: Kullanıcı ID'si
            task_type: Görev tipi
            **kwargs: Görev sınıfına geçirilecek ek parametreler
            
        Returns:
            Oluşturulan görev veya None (hata durumunda)
        """
        if task_type not in self.plugin_registry:
            logger.error(f"Bilinmeyen görev tipi: {task_type}")
            return None
        
        # Kullanıcının aynı tipte aktif bir görevi var mı kontrol et
        user_tasks = self.active_tasks_by_user.get(user_id, {})
        for task in user_tasks.values():
            if task.__class__.__name__ == task_type and task.is_active:
                logger.warning(f"Kullanıcının zaten aktif bir {task_type} görevi var: {user_id}")
                return None
        
        # Yeni görev ID'si oluştur
        task_id = f"{int(time.time())}_{task_type}"
        
        try:
            # Görevi oluştur
            task_class = self.plugin_registry[task_type]
            task = task_class(
                user_id=user_id,
                task_id=task_id,
                expiry_time=int(time.time()) + 24*60*60,  # 24 saat
                verification_engine=self,
                bot=self.bot,
                **kwargs
            )
            
            # Görevi başlat
            task.start_listening()
            
            # Görevi kaydet
            task_key = f"{user_id}_{task_id}"
            self.tasks[task_key] = task
            
            if user_id not in self.active_tasks_by_user:
                self.active_tasks_by_user[user_id] = {}
            self.active_tasks_by_user[user_id][task_id] = task
            
            # Veritabanını güncelle
            self._save_tasks()
            
            logger.info(f"Yeni görev oluşturuldu: {task_key}")
            return task
            
        except Exception as e:
            logger.error(f"Görev oluşturma hatası: {e}")
            return None
    
    async def verify_task(self, user_id: str, task_id: str):
        """
        Görevi doğrula
        
        Args:
            user_id: Kullanıcı ID'si
            task_id: Görev ID'si
            
        Returns:
            bool: Doğrulama sonucu
        """
        task_key = f"{user_id}_{task_id}"
        if task_key not in self.tasks:
            logger.warning(f"Doğrulama için görev bulunamadı: {task_key}")
            return False
        
        task = self.tasks[task_key]
        
        if task.is_completed:
            logger.debug(f"Görev zaten tamamlanmış: {task_key}")
            return True
            
        if task.is_expired():
            logger.debug(f"Görevin süresi dolmuş: {task_key}")
            await self.expire_task(user_id, task_id)
            return False
        
        # Görevi tamamlandı olarak işaretle
        task.is_completed = True
        task.stop_listening()
        
        # Veritabanını güncelle
        self._save_tasks()
        
        logger.info(f"Görev doğrulandı: {task_key}")
        return True
    
    async def expire_task(self, user_id: str, task_id: str):
        """
        Görevin süresini dolur
        
        Args:
            user_id: Kullanıcı ID'si
            task_id: Görev ID'si
        """
        task_key = f"{user_id}_{task_id}"
        if task_key not in self.tasks:
            return
        
        task = self.tasks[task_key]
        task.is_active = False
        task.stop_listening()
        
        # Veritabanını güncelle
        self._save_tasks()
        
        logger.info(f"Görevin süresi doldu: {task_key}")
    
    def get_active_tasks(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Kullanıcının aktif görevlerini getir
        
        Args:
            user_id: Kullanıcı ID'si (None ise tüm görevler)
            
        Returns:
            List[Dict]: Aktif görevlerin listesi
        """
        active_tasks = []
        
        if user_id:
            # Sadece belirli bir kullanıcının görevleri
            user_tasks = self.active_tasks_by_user.get(user_id, {})
            for task in user_tasks.values():
                if task.is_active and not task.is_expired():
                    active_tasks.append(task.to_dict())
        else:
            # Tüm görevler
            for task in self.tasks.values():
                if task.is_active and not task.is_expired():
                    active_tasks.append(task.to_dict())
        
        return active_tasks
    
    def _load_tasks(self):
        """Görevleri veritabanından yükle"""
        if not os.path.exists(self.db_path):
            return
        
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                tasks_data = json.load(f)
                
            # Burada sadece metaverileri yüklüyoruz
            # Gerçek görev nesneleri uygulamanın yeniden başlatılmasında
            # yeniden oluşturulmalıdır
            logger.info(f"{len(tasks_data)} görev yüklendi")
                
        except Exception as e:
            logger.error(f"Görevleri yükleme hatası: {e}")
    
    def _save_tasks(self):
        """Görevleri veritabanına kaydet"""
        try:
            tasks_data = {}
            for task_key, task in self.tasks.items():
                tasks_data[task_key] = task.to_dict()
                
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(tasks_data, f, ensure_ascii=False, indent=2)
                
            logger.debug(f"{len(tasks_data)} görev kaydedildi")
                
        except Exception as e:
            logger.error(f"Görevleri kaydetme hatası: {e}") 