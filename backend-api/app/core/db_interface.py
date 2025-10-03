"""
Veritabanı Arayüzü
Farklı veritabanı sağlayıcıları için ortak arayüz
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union


class DatabaseInterface(ABC):
    """
    Veritabanı sağlayıcıları için soyut temel sınıf.
    Bu arayüzü uygulayan tüm sınıflar bu metodları uygulamalıdır.
    """
    
    # Kullanıcı İşlemleri
    @abstractmethod
    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Kullanıcı bilgilerini getir"""
        pass
    
    @abstractmethod
    async def get_user_by_telegram_id(self, telegram_id: str) -> Optional[Dict[str, Any]]:
        """Telegram ID'ye göre kullanıcı bilgilerini getir"""
        pass
        
    @abstractmethod
    async def save_user(self, user_id: str, user_data: Dict[str, Any]) -> bool:
        """Kullanıcı bilgilerini kaydet"""
        pass
    
    @abstractmethod
    async def update_user(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Kullanıcı bilgilerini güncelle"""
        pass
    
    # Görev İşlemleri
    @abstractmethod
    async def get_task(self, task_id: Union[str, int]) -> Optional[Dict[str, Any]]:
        """Görev bilgilerini getir"""
        pass
    
    @abstractmethod
    async def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Tüm görevleri getir"""
        pass
    
    @abstractmethod
    async def save_task(self, task_id: Union[str, int], task_data: Dict[str, Any]) -> bool:
        """Görev bilgilerini kaydet"""
        pass
    
    # Görev Doğrulama İşlemleri
    @abstractmethod
    async def get_verification(self, verification_key: str) -> Optional[Dict[str, Any]]:
        """Doğrulama kaydını getir"""
        pass
    
    @abstractmethod
    async def save_verification(self, verification_key: str, verification_data: Dict[str, Any]) -> bool:
        """Doğrulama kaydını kaydet"""
        pass
    
    @abstractmethod
    async def get_pending_verifications(self) -> List[Dict[str, Any]]:
        """Bekleyen tüm doğrulamaları getir"""
        pass
    
    # Görev Tamamlama İşlemleri
    @abstractmethod
    async def get_completed_tasks(self, user_id: str) -> List[Union[str, int]]:
        """Kullanıcının tamamladığı görevleri getir"""
        pass
    
    @abstractmethod
    async def complete_task(self, user_id: str, task_id: Union[str, int]) -> bool:
        """Görevi tamamla olarak işaretle"""
        pass
    
    @abstractmethod
    async def save_task_completion(self, completion_data: Dict[str, Any]) -> bool:
        """Görev tamamlama kaydını kaydet"""
        pass
    
    # Rozet İşlemleri
    @abstractmethod
    async def get_all_badges(self) -> List[Dict[str, Any]]:
        """Tüm rozetleri getir"""
        pass
    
    @abstractmethod
    async def add_badge_to_user(self, user_id: str, badge_id: str) -> bool:
        """Kullanıcıya rozet ekle"""
        pass
    
    # Loglama
    @abstractmethod
    async def add_log(self, log_data: Dict[str, Any]) -> bool:
        """Log ekle"""
        pass
    
    # Metrik
    @abstractmethod
    async def add_metric(self, metric_data: Dict[str, Any]) -> bool:
        """Metrik ekle"""
        pass
    
    # İstatistik İşlemleri
    @abstractmethod
    async def get_task_stats(self) -> Dict[str, Any]:
        """Görev istatistiklerini getir"""
        pass
    
    # Günlük Limit Sıfırlama
    @abstractmethod
    async def reset_daily_task_limits(self, today: str) -> int:
        """Günlük görev limitlerini sıfırla ve etkilenen kullanıcı sayısını döndür"""
        pass 