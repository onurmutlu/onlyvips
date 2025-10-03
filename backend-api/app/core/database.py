"""
Veritabanı bağlantı modülü
"""

import os
import json
from typing import Dict, List, Any, Optional, Union
import logging
from datetime import datetime
import asyncio
import motor.motor_asyncio
from bson import ObjectId
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from app.core.config import settings
from app.utils.logger import app_logger
from app.core.db_interface import DatabaseInterface
from app.core.memory_db import MemoryDatabase
from app.core.mongodb_db import MongoDBDatabase, normalize_mongodb_doc, parse_object_id

# In-memory veritabanı (örnek olarak)
memory_db = {
    "users": {},
    "tasks": {},
    "badges": {},
    "metrics": [],
    "logs": []
}

# ObjectId dönüştürücü
def parse_object_id(id_value: Union[str, int]) -> Union[ObjectId, str, int]:
    """
    ID değerini MongoDB ObjectId'ye dönüştürür veya orijinal değeri döndürür
    """
    if isinstance(id_value, str) and len(id_value) == 24 and all(c in '0123456789abcdef' for c in id_value.lower()):
        try:
            return ObjectId(id_value)
        except:
            pass
    return id_value

# MongoDB sonuçlarını JSON'a çevirilebilir formata dönüştürme
def normalize_mongodb_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    MongoDB belgesindeki ObjectId'leri string'e dönüştürür ve _id alanını id olarak yeniden adlandırır
    """
    if not doc:
        return {}
        
    result = {}
    for key, value in doc.items():
        # ObjectId dönüştürme
        if key == '_id':
            result['id'] = str(value)
        else:
            # İç içe sözlükler ve listeler için rekürsif işlem
            if isinstance(value, dict):
                result[key] = normalize_mongodb_doc(value)
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                result[key] = [normalize_mongodb_doc(item) for item in value]
            else:
                result[key] = value
    
    return result

# Basit DB sınıfı - MongoDB implementasyonu
class Database:
    def __init__(self):
        self.provider = settings.DB_PROVIDER
        self.db = memory_db  # Varsayılan değer
        self.logger = logging.getLogger("onlyvips-db")
        self.client = None
        
        # Provider'a göre bağlantı
        if self.provider == "memory":
            self.logger.info("Bellek tabanlı veritabanı kullanılıyor (veriler kalıcı değil)")
            self._load_sample_data()
        elif self.provider == "mongodb":
            self._setup_mongodb()
        else:
            self.logger.error(f"Desteklenmeyen veritabanı sağlayıcısı: {self.provider}")
            raise ValueError(f"Desteklenmeyen veritabanı sağlayıcısı: {self.provider}")
    
    def _setup_mongodb(self):
        """MongoDB bağlantısı kur"""
        try:
            self.logger.info("MongoDB bağlantısı başlatılıyor...")
            
            # Connection string oluştur
            if settings.DB_URL:
                mongo_url = settings.DB_URL
            else:
                auth_part = f"{settings.DB_USER}:{settings.DB_PASSWORD}@" if settings.DB_USER else ""
                mongo_url = f"mongodb://{auth_part}{settings.DB_HOST}:{settings.DB_PORT}"
                
            # Async client
            self.client = motor.motor_asyncio.AsyncIOMotorClient(
                mongo_url, 
                serverSelectionTimeoutMS=5000
            )
            
            # Senkron client (test için)
            sync_client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
            
            # Bağlantıyı test et
            sync_client.admin.command('ping')
            
            # Veritabanı referansı
            self.db = self.client[settings.DB_NAME]
            
            self.logger.info(f"MongoDB bağlantısı başarılı: {settings.DB_HOST}:{settings.DB_PORT}, DB: {settings.DB_NAME}")
            
            # Koleksiyonlar
            self.users_collection = self.db.users
            self.tasks_collection = self.db.tasks
            self.badges_collection = self.db.badges
            self.metrics_collection = self.db.metrics
            self.logs_collection = self.db.logs
            
            # Dizinleri ayarla
            asyncio.create_task(self._setup_indexes())
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            self.logger.error(f"MongoDB bağlantı hatası: {str(e)}")
            self.logger.warning("Bellek tabanlı veritabanına geri dönülüyor...")
            self.provider = "memory"
            self._load_sample_data()

    async def _setup_indexes(self):
        """MongoDB dizinlerini oluştur"""
        if self.provider != "mongodb":
            return
            
        try:
            # Kullanıcı koleksiyonu için indeksler
            await self.users_collection.create_index("username", unique=True)
            await self.users_collection.create_index("telegram_id", unique=True, sparse=True)
            
            # Görev koleksiyonu için indeksler
            await self.tasks_collection.create_index("task_id", unique=True)
            await self.tasks_collection.create_index("task_type")
            
            # Metrik koleksiyonu için indeksler
            await self.metrics_collection.create_index("timestamp")
            await self.metrics_collection.create_index("endpoint")
            
            # Log koleksiyonu için indeksler
            await self.logs_collection.create_index("timestamp")
            await self.logs_collection.create_index("user_id")
            
            self.logger.info("MongoDB indeksler başarıyla oluşturuldu")
        except Exception as e:
            self.logger.error(f"İndeks oluşturma hatası: {str(e)}")
    
    def _load_sample_data(self) -> None:
        """Örnek veri yükleme - Sadece bellek modunda çalışır"""
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
                "demo": {"username": "demo", "xp": 100, "badges": ["starter"], "completed_tasks": [1, 2]},
                "admin": {"username": "admin", "xp": 999, "badges": ["admin", "star"], "completed_tasks": [1, 2, 3, 4, 5]}
            }
            
            self.logger.info("Örnek kullanıcı verileri yüklendi")
                
        except Exception as e:
            self.logger.error(f"Örnek veri yüklenirken hata: {str(e)}")
    
    # Kullanıcı işlemleri
    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Kullanıcı bilgilerini getir"""
        if self.provider == "memory":
            return self.db["users"].get(user_id)
        elif self.provider == "mongodb":
            if len(user_id) == 24 and all(c in '0123456789abcdef' for c in user_id.lower()):
                # ObjectId olabilir
                query = {"$or": [{"_id": ObjectId(user_id)}, {"username": user_id}, {"telegram_id": user_id}]}
            else:
                # Kullanıcı adı veya telegram_id
                query = {"$or": [{"username": user_id}, {"telegram_id": user_id}]}
                
            user = await self.users_collection.find_one(query)
            if user:
                return normalize_mongodb_doc(user)
            return None
    
    async def save_user(self, user_id: str, user_data: Dict[str, Any]) -> bool:
        """Kullanıcı bilgilerini kaydet"""
        if self.provider == "memory":
            self.db["users"][user_id] = user_data
            return True
        elif self.provider == "mongodb":
            # _id alanını kontrol et
            if "_id" not in user_data and "id" in user_data:
                try:
                    user_data["_id"] = ObjectId(user_data["id"])
                    del user_data["id"]
                except:
                    pass
                    
            try:
                # Kullanıcı ID için query oluştur
                query = {"username": user_id}
                
                # Mevcut kullanıcıyı kontrol et
                existing_user = await self.users_collection.find_one(query)
                
                if existing_user:
                    # Güncelle
                    result = await self.users_collection.update_one(
                        query, {"$set": user_data}
                    )
                    return result.modified_count > 0
                else:
                    # Yeni oluştur
                    user_data["username"] = user_id
                    user_data["created_at"] = datetime.now()
                    result = await self.users_collection.insert_one(user_data)
                    return bool(result.inserted_id)
            except Exception as e:
                self.logger.error(f"Kullanıcı kaydedilirken hata: {str(e)}")
                return False
    
    async def update_user(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Kullanıcı bilgilerini güncelle"""
        if self.provider == "memory":
            if user_id in self.db["users"]:
                self.db["users"][user_id].update(updates)
                return True
            return False
        elif self.provider == "mongodb":
            try:
                result = await self.users_collection.update_one(
                    {"username": user_id},
                    {"$set": updates}
                )
                return result.modified_count > 0
            except Exception as e:
                self.logger.error(f"Kullanıcı güncellenirken hata: {str(e)}")
                return False
    
    # Görev işlemleri
    async def get_task(self, task_id: Union[str, int]) -> Optional[Dict[str, Any]]:
        """Görev bilgilerini getir"""
        if self.provider == "memory":
            return self.db["tasks"].get(task_id)
        elif self.provider == "mongodb":
            try:
                # ID'nin türüne göre sorgu oluştur
                query = {"$or": [{"_id": parse_object_id(task_id)}, {"task_id": task_id}]}
                task = await self.tasks_collection.find_one(query)
                if task:
                    return normalize_mongodb_doc(task)
                return None
            except Exception as e:
                self.logger.error(f"Görev çekilirken hata: {str(e)}")
                return None
    
    async def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Tüm görevleri getir"""
        if self.provider == "memory":
            return list(self.db["tasks"].values())
        elif self.provider == "mongodb":
            try:
                tasks = []
                cursor = self.tasks_collection.find({})
                async for task in cursor:
                    tasks.append(normalize_mongodb_doc(task))
                return tasks
            except Exception as e:
                self.logger.error(f"Görevler çekilirken hata: {str(e)}")
                return []
    
    async def save_task(self, task_id: Union[str, int], task_data: Dict[str, Any]) -> bool:
        """Görev bilgilerini kaydet"""
        if self.provider == "memory":
            self.db["tasks"][task_id] = task_data
            return True
        elif self.provider == "mongodb":
            try:
                # Eğer task_id task_data içinde yoksa ekle
                if "task_id" not in task_data:
                    task_data["task_id"] = task_id
                
                # _id alanını kontrol et
                if "_id" not in task_data and "id" in task_data:
                    try:
                        task_data["_id"] = ObjectId(task_data["id"])
                        del task_data["id"]
                    except:
                        pass
                
                # Güncelleme/ekleme zamanını ekle
                task_data["updated_at"] = datetime.now()
                
                # Mevcut görevi kontrol et
                existing_task = await self.tasks_collection.find_one({"task_id": task_id})
                
                if existing_task:
                    # Güncelle
                    result = await self.tasks_collection.update_one(
                        {"task_id": task_id},
                        {"$set": task_data}
                    )
                    return result.modified_count > 0
                else:
                    # Yeni oluştur
                    task_data["created_at"] = datetime.now()
                    result = await self.tasks_collection.insert_one(task_data)
                    return bool(result.inserted_id)
            except Exception as e:
                self.logger.error(f"Görev kaydedilirken hata: {str(e)}")
                return False
    
    # Görev tamamlama işlemleri
    async def get_completed_tasks(self, user_id: str) -> List[Union[str, int]]:
        """Kullanıcının tamamladığı görevleri getir"""
        if self.provider == "memory":
            user = self.db["users"].get(user_id, {})
            return user.get("completed_tasks", [])
        elif self.provider == "mongodb":
            try:
                user = await self.users_collection.find_one({"username": user_id})
                if user:
                    return user.get("completed_tasks", [])
                return []
            except Exception as e:
                self.logger.error(f"Tamamlanan görevler çekilirken hata: {str(e)}")
                return []
    
    async def complete_task(self, user_id: str, task_id: Union[str, int]) -> bool:
        """Görevi tamamla olarak işaretle"""
        if self.provider == "memory":
            if user_id in self.db["users"]:
                user = self.db["users"][user_id]
                if "completed_tasks" not in user:
                    user["completed_tasks"] = []
                if task_id not in user["completed_tasks"]:
                    user["completed_tasks"].append(task_id)
                return True
            return False
        elif self.provider == "mongodb":
            try:
                # Kullanıcıyı bul ve completed_tasks listesine ekle
                result = await self.users_collection.update_one(
                    {"username": user_id},
                    {"$addToSet": {"completed_tasks": task_id}}
                )
                
                # Ayrıca tamamlama zamanını kaydet
                completion_record = {
                    "user_id": user_id,
                    "task_id": task_id,
                    "completed_at": datetime.now()
                }
                await self.db.task_completions.insert_one(completion_record)
                
                return result.modified_count > 0
            except Exception as e:
                self.logger.error(f"Görev tamamlanırken hata: {str(e)}")
                return False
    
    # Loglama
    async def add_log(self, log_data: Dict[str, Any]) -> bool:
        """Log ekle"""
        if self.provider == "memory":
            log_data["timestamp"] = datetime.now().isoformat()
            self.db["logs"].append(log_data)
            return True
        elif self.provider == "mongodb":
            try:
                log_data["timestamp"] = datetime.now()
                result = await self.logs_collection.insert_one(log_data)
                return bool(result.inserted_id)
            except Exception as e:
                print(f"Log kaydedilirken hata: {str(e)}")  # Loglama mekanizması kullanılamaz olabilir
                return False
    
    # Metrik
    async def add_metric(self, metric_data: Dict[str, Any]) -> bool:
        """Metrik ekle"""
        if self.provider == "memory":
            metric_data["timestamp"] = datetime.now().isoformat()
            self.db["metrics"].append(metric_data)
            return True
        elif self.provider == "mongodb":
            try:
                metric_data["timestamp"] = datetime.now()
                result = await self.metrics_collection.insert_one(metric_data)
                return bool(result.inserted_id)
            except Exception as e:
                self.logger.error(f"Metrik kaydedilirken hata: {str(e)}")
                return False
    
    # Rozet/badge işlemleri
    async def get_all_badges(self) -> List[Dict[str, Any]]:
        """Tüm rozetleri getir"""
        if self.provider == "memory":
            return list(self.db.get("badges", {}).values())
        elif self.provider == "mongodb":
            try:
                badges = []
                cursor = self.badges_collection.find({})
                async for badge in cursor:
                    badges.append(normalize_mongodb_doc(badge))
                return badges
            except Exception as e:
                self.logger.error(f"Rozetler çekilirken hata: {str(e)}")
                return []
    
    async def add_badge_to_user(self, user_id: str, badge_id: str) -> bool:
        """Kullanıcıya rozet ekle"""
        if self.provider == "memory":
            if user_id in self.db["users"]:
                user = self.db["users"][user_id]
                if "badges" not in user:
                    user["badges"] = []
                if badge_id not in user["badges"]:
                    user["badges"].append(badge_id)
                return True
            return False
        elif self.provider == "mongodb":
            try:
                result = await self.users_collection.update_one(
                    {"username": user_id},
                    {"$addToSet": {"badges": badge_id}}
                )
                
                # Rozet atama kaydı
                badge_record = {
                    "user_id": user_id,
                    "badge_id": badge_id,
                    "awarded_at": datetime.now()
                }
                await self.db.badge_awards.insert_one(badge_record)
                
                return result.modified_count > 0
            except Exception as e:
                self.logger.error(f"Rozet eklenirken hata: {str(e)}")
                return False

class DatabaseFactory:
    """
    Veritabanı fabrika sınıfı - yapılandırmaya göre doğru veritabanı implementasyonunu döndürür
    """
    @staticmethod
    def get_database() -> DatabaseInterface:
        """
        Yapılandırmaya göre uygun veritabanı nesnesini döndürür
        """
        if settings.DB_PROVIDER == "memory":
            app_logger.info("Bellek tabanlı veritabanı kullanılıyor (veriler kalıcı değil)")
            return MemoryDatabase()
        elif settings.DB_PROVIDER == "mongodb":
            app_logger.info(f"MongoDB veritabanı kullanılıyor: {settings.DB_HOST}:{settings.DB_PORT}")
            return MongoDBDatabase()
        else:
            error_msg = f"Desteklenmeyen veritabanı sağlayıcısı: {settings.DB_PROVIDER}"
            app_logger.error(error_msg)
            raise ValueError(error_msg)

# Veritabanı bağlantısını oluştur
db = DatabaseFactory.get_database()

async def create_tables():
    """Veritabanı tablolarını oluştur"""
    if settings.DB_PROVIDER == "mongodb":
        try:
            app_logger.info("MongoDB koleksiyonları ve indekslerini hazırlıyor...")
            # MongoDB indeksleri oluştur
            if isinstance(db, MongoDBDatabase):
                await db.setup_indexes()
                
            app_logger.info("MongoDB koleksiyonları ve indeksleri hazır")
        except Exception as e:
            app_logger.error(f"MongoDB koleksiyon ve indeks hazırlama hatası: {str(e)}")
    else:
        app_logger.info("Bellek veritabanı kullanılıyor, tablo oluşturmaya gerek yok")

# Bağlantıyı kapat (uygulama kapanırken çağrılır)
async def close_connection():
    """Veritabanı bağlantısını kapat"""
    if settings.DB_PROVIDER == "mongodb" and isinstance(db, MongoDBDatabase) and db.client:
        db.client.close()
        app_logger.info("MongoDB bağlantısı kapatıldı") 