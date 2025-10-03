"""
Bellek Tabanlı Veritabanı
Geliştirme, test ve demo amaçlı kullanılan in-memory veritabanı
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

from app.core.db_interface import DatabaseInterface
from app.core.config import settings

# In-memory veritabanı
MEMORY_DB = {
    "users": {},
    "tasks": {},
    "badges": {},
    "verifications": {},
    "task_completions": [],
    "metrics": [],
    "logs": []
}

class MemoryDatabase(DatabaseInterface):
    """
    Bellek tabanlı veritabanı implementasyonu
    """
    
    def __init__(self):
        self.db = MEMORY_DB
        self.logger = logging.getLogger("memory-db")
        self._load_sample_data()
    
    def _load_sample_data(self) -> None:
        """Örnek veri yükle"""
        try:
            # Örnek görev verileri
            task_data_path = os.path.join(os.path.dirname(__file__), "../config/tasks.json")
            
            if os.path.exists(task_data_path):
                with open(task_data_path, 'r', encoding='utf-8') as f:
                    tasks_data = json.load(f)
                
                # Görevleri ID'ye göre indeksle
                for task in tasks_data:
                    self.db["tasks"][task["id"]] = task
                
                self.logger.info(f"{len(tasks_data)} görev örnek veriden yüklendi")
            else:
                self.logger.warning(f"Örnek görev verisi bulunamadı: {task_data_path}")
                
            # Örnek kullanıcı verileri
            self.db["users"] = {
                "demo": {
                    "username": "demo", 
                    "xp": 100, 
                    "badges": ["starter"], 
                    "completed_tasks": [1, 2],
                    "telegram_id": "123456789"
                },
                "admin": {
                    "username": "admin", 
                    "xp": 999, 
                    "badges": ["admin", "star"], 
                    "completed_tasks": [1, 2, 3, 4, 5],
                    "role": "admin",
                    "is_active": True,
                    "password_hash": "admin_password"  # Demo amaçlı, gerçek ortamda hash kullanılmalı
                }
            }
            
            # Örnek rozetler
            self.db["badges"] = {
                "starter": {
                    "id": "starter",
                    "name": "Yeni Başlayan",
                    "description": "OnlyVips'e hoş geldiniz!",
                    "icon": "🌟"
                },
                "admin": {
                    "id": "admin",
                    "name": "Yönetici",
                    "description": "Site yöneticisi",
                    "icon": "⚙️"
                },
                "star": {
                    "id": "star",
                    "name": "Yıldız",
                    "description": "VIP üye",
                    "icon": "🌠"
                }
            }
            
            self.logger.info("Örnek veriler yüklendi")
                
        except Exception as e:
            self.logger.error(f"Örnek veri yüklenirken hata: {str(e)}")
    
    # Kullanıcı İşlemleri
    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Kullanıcı bilgilerini getir"""
        return self.db["users"].get(user_id)
    
    async def get_user_by_telegram_id(self, telegram_id: str) -> Optional[Dict[str, Any]]:
        """Telegram ID'ye göre kullanıcı bilgilerini getir"""
        for user_id, user_data in self.db["users"].items():
            if user_data.get("telegram_id") == telegram_id:
                return user_data
        return None
    
    async def save_user(self, user_id: str, user_data: Dict[str, Any]) -> bool:
        """Kullanıcı bilgilerini kaydet"""
        self.db["users"][user_id] = user_data
        return True
    
    async def update_user(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Kullanıcı bilgilerini güncelle"""
        if user_id in self.db["users"]:
            self.db["users"][user_id].update(updates)
            return True
        return False
    
    # Görev İşlemleri
    async def get_task(self, task_id: Union[str, int]) -> Optional[Dict[str, Any]]:
        """Görev bilgilerini getir"""
        return self.db["tasks"].get(task_id)
    
    async def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Tüm görevleri getir"""
        return list(self.db["tasks"].values())
    
    async def save_task(self, task_id: Union[str, int], task_data: Dict[str, Any]) -> bool:
        """Görev bilgilerini kaydet"""
        self.db["tasks"][task_id] = task_data
        return True
    
    # Görev Doğrulama İşlemleri
    async def get_verification(self, verification_key: str) -> Optional[Dict[str, Any]]:
        """Doğrulama kaydını getir"""
        return self.db["verifications"].get(verification_key)
    
    async def save_verification(self, verification_key: str, verification_data: Dict[str, Any]) -> bool:
        """Doğrulama kaydını kaydet"""
        self.db["verifications"][verification_key] = verification_data
        return True
    
    async def get_pending_verifications(self) -> List[Dict[str, Any]]:
        """Bekleyen tüm doğrulamaları getir"""
        return [v for k, v in self.db["verifications"].items() 
                if v.get("status") == "pending"]
    
    # Görev Tamamlama İşlemleri
    async def get_completed_tasks(self, user_id: str) -> List[Union[str, int]]:
        """Kullanıcının tamamladığı görevleri getir"""
        user = self.db["users"].get(user_id, {})
        return user.get("completed_tasks", [])
    
    async def complete_task(self, user_id: str, task_id: Union[str, int]) -> bool:
        """Görevi tamamla olarak işaretle"""
        if user_id in self.db["users"]:
            user = self.db["users"][user_id]
            if "completed_tasks" not in user:
                user["completed_tasks"] = []
            if task_id not in user["completed_tasks"]:
                user["completed_tasks"].append(task_id)
            return True
        return False
    
    async def save_task_completion(self, completion_data: Dict[str, Any]) -> bool:
        """Görev tamamlama kaydını kaydet"""
        self.db["task_completions"].append(completion_data)
        return True
    
    # Rozet İşlemleri
    async def get_all_badges(self) -> List[Dict[str, Any]]:
        """Tüm rozetleri getir"""
        return list(self.db["badges"].values())
    
    async def add_badge_to_user(self, user_id: str, badge_id: str) -> bool:
        """Kullanıcıya rozet ekle"""
        if user_id in self.db["users"]:
            user = self.db["users"][user_id]
            if "badges" not in user:
                user["badges"] = []
            if badge_id not in user["badges"]:
                user["badges"].append(badge_id)
            return True
        return False
    
    # Loglama
    async def add_log(self, log_data: Dict[str, Any]) -> bool:
        """Log ekle"""
        log_data["timestamp"] = datetime.now().isoformat()
        self.db["logs"].append(log_data)
        return True
    
    # Metrik
    async def add_metric(self, metric_data: Dict[str, Any]) -> bool:
        """Metrik ekle"""
        metric_data["timestamp"] = datetime.now().isoformat()
        self.db["metrics"].append(metric_data)
        return True
    
    # İstatistik İşlemleri
    async def get_task_stats(self) -> Dict[str, Any]:
        """Görev istatistiklerini getir"""
        stats = {
            "total_users": len(self.db["users"]),
            "total_tasks": len(self.db["tasks"]),
            "task_completions": {}
        }
        
        # Görev bazında tamamlanma sayıları
        for task_id in self.db["tasks"]:
            stats["task_completions"][task_id] = 0
        
        # Kullanıcıların tamamladığı görevleri say
        for user_id, user_data in self.db["users"].items():
            for task_id in user_data.get("completed_tasks", []):
                if task_id in stats["task_completions"]:
                    stats["task_completions"][task_id] += 1
        
        return stats
    
    # Günlük Limit Sıfırlama
    async def reset_daily_task_limits(self, today: str) -> int:
        """Günlük görev limitlerini sıfırla ve etkilenen kullanıcı sayısını döndür"""
        counter = 0
        
        for user_id, user_data in self.db["users"].items():
            if "daily_attempts" in user_data:
                # Sadece bugünkü kayıtları tut
                new_daily_attempts = {}
                for key, value in user_data["daily_attempts"].items():
                    if today in key:
                        new_daily_attempts[key] = value
                
                user_data["daily_attempts"] = new_daily_attempts
                counter += 1
        
        return counter 