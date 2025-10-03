"""
MongoDB Veritabanı
Prodüksiyon ve ölçeklenebilir uygulama için MongoDB implementasyonu
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from bson import ObjectId
import motor.motor_asyncio
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from app.core.db_interface import DatabaseInterface
from app.core.config import settings

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

class MongoDBDatabase(DatabaseInterface):
    """
    MongoDB veritabanı implementasyonu
    """
    
    def __init__(self):
        self.logger = logging.getLogger("mongodb-db")
        self.client = None
        self.db = None
        
        # Bağlantı kurma
        self._setup_connection()
    
    def _setup_connection(self):
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
            
            # Veritabanı referansı
            self.db = self.client[settings.DB_NAME]
            
            # Bağlantıyı test et (senkron client ile)
            sync_client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
            sync_client.admin.command('ping')
            sync_client.close()
            
            self.logger.info(f"MongoDB bağlantısı başarılı: {settings.DB_HOST}:{settings.DB_PORT}, DB: {settings.DB_NAME}")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            self.logger.error(f"MongoDB bağlantı hatası: {str(e)}")
            raise ConnectionError(f"MongoDB bağlantısı kurulamadı: {str(e)}")
    
    async def setup_indexes(self):
        """MongoDB dizinlerini oluştur"""
        try:
            # Kullanıcı koleksiyonu için indeksler
            await self.db.users.create_index("username", unique=True)
            await self.db.users.create_index("telegram_id", unique=True, sparse=True)
            
            # Görev koleksiyonu için indeksler
            await self.db.tasks.create_index("task_id", unique=True)
            await self.db.tasks.create_index("task_type")
            
            # Doğrulama koleksiyonu için indeksler
            await self.db.verifications.create_index("verification_key", unique=True)
            await self.db.verifications.create_index("user_id")
            await self.db.verifications.create_index("status")
            
            # Görev tamamlama koleksiyonu için indeksler
            await self.db.task_completions.create_index("user_id")
            await self.db.task_completions.create_index("task_id")
            await self.db.task_completions.create_index("completed_at")
            
            # Metrik koleksiyonu için indeksler
            await self.db.metrics.create_index("timestamp")
            await self.db.metrics.create_index("endpoint")
            
            # Log koleksiyonu için indeksler
            await self.db.logs.create_index("timestamp")
            await self.db.logs.create_index("user_id")
            
            self.logger.info("MongoDB indeksler başarıyla oluşturuldu")
        except Exception as e:
            self.logger.error(f"İndeks oluşturma hatası: {str(e)}")
    
    # Kullanıcı İşlemleri
    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Kullanıcı bilgilerini getir"""
        try:
            # Farklı şekillerde arama yapalım
            if len(user_id) == 24 and all(c in '0123456789abcdef' for c in user_id.lower()):
                # ObjectId olabilir
                query = {"$or": [{"_id": ObjectId(user_id)}, {"username": user_id}]}
            else:
                # Kullanıcı adı
                query = {"username": user_id}
                
            user = await self.db.users.find_one(query)
            if user:
                return normalize_mongodb_doc(user)
            return None
        except Exception as e:
            self.logger.error(f"Kullanıcı getirme hatası: {str(e)}")
            return None
    
    async def get_user_by_telegram_id(self, telegram_id: str) -> Optional[Dict[str, Any]]:
        """Telegram ID'ye göre kullanıcı bilgilerini getir"""
        try:
            user = await self.db.users.find_one({"telegram_id": telegram_id})
            if user:
                return normalize_mongodb_doc(user)
            return None
        except Exception as e:
            self.logger.error(f"Telegram ID ile kullanıcı getirme hatası: {str(e)}")
            return None
    
    async def save_user(self, user_id: str, user_data: Dict[str, Any]) -> bool:
        """Kullanıcı bilgilerini kaydet"""
        try:
            # _id alanını kontrol et
            if "_id" not in user_data and "id" in user_data:
                try:
                    user_data["_id"] = ObjectId(user_data["id"])
                    del user_data["id"]
                except:
                    pass
                    
            # Kullanıcı ID için query oluştur
            query = {"username": user_id}
            
            # Mevcut kullanıcıyı kontrol et
            existing_user = await self.db.users.find_one(query)
            
            if existing_user:
                # Güncelle
                result = await self.db.users.update_one(
                    query, {"$set": user_data}
                )
                return result.modified_count > 0
            else:
                # Yeni oluştur
                user_data["username"] = user_id
                user_data["created_at"] = datetime.now()
                result = await self.db.users.insert_one(user_data)
                return bool(result.inserted_id)
        except Exception as e:
            self.logger.error(f"Kullanıcı kaydetme hatası: {str(e)}")
            return False
    
    async def update_user(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Kullanıcı bilgilerini güncelle"""
        try:
            updates["updated_at"] = datetime.now()
            result = await self.db.users.update_one(
                {"username": user_id},
                {"$set": updates}
            )
            return result.modified_count > 0
        except Exception as e:
            self.logger.error(f"Kullanıcı güncelleme hatası: {str(e)}")
            return False
    
    # Görev İşlemleri
    async def get_task(self, task_id: Union[str, int]) -> Optional[Dict[str, Any]]:
        """Görev bilgilerini getir"""
        try:
            # ID'nin türüne göre sorgu oluştur
            if isinstance(task_id, int) or (isinstance(task_id, str) and task_id.isdigit()):
                # Sayısal ID
                query = {"$or": [{"task_id": int(task_id)}, {"id": int(task_id)}]}
            else:
                # String ID veya ObjectId
                query = {"$or": [{"_id": parse_object_id(task_id)}, {"task_id": task_id}]}
                
            task = await self.db.tasks.find_one(query)
            if task:
                return normalize_mongodb_doc(task)
            return None
        except Exception as e:
            self.logger.error(f"Görev getirme hatası: {str(e)}")
            return None
    
    async def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Tüm görevleri getir"""
        try:
            tasks = []
            cursor = self.db.tasks.find({})
            async for task in cursor:
                tasks.append(normalize_mongodb_doc(task))
            return tasks
        except Exception as e:
            self.logger.error(f"Tüm görevleri getirme hatası: {str(e)}")
            return []
    
    async def save_task(self, task_id: Union[str, int], task_data: Dict[str, Any]) -> bool:
        """Görev bilgilerini kaydet"""
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
            existing_task = await self.db.tasks.find_one({"task_id": task_id})
            
            if existing_task:
                # Güncelle
                result = await self.db.tasks.update_one(
                    {"task_id": task_id},
                    {"$set": task_data}
                )
                return result.modified_count > 0
            else:
                # Yeni oluştur
                task_data["created_at"] = datetime.now()
                result = await self.db.tasks.insert_one(task_data)
                return bool(result.inserted_id)
        except Exception as e:
            self.logger.error(f"Görev kaydetme hatası: {str(e)}")
            return False
    
    # Görev Doğrulama İşlemleri
    async def get_verification(self, verification_key: str) -> Optional[Dict[str, Any]]:
        """Doğrulama kaydını getir"""
        try:
            verification = await self.db.verifications.find_one({"verification_key": verification_key})
            if verification:
                return normalize_mongodb_doc(verification)
            return None
        except Exception as e:
            self.logger.error(f"Doğrulama getirme hatası: {str(e)}")
            return None
    
    async def save_verification(self, verification_key: str, verification_data: Dict[str, Any]) -> bool:
        """Doğrulama kaydını kaydet"""
        try:
            # verification_key'i ekle
            verification_data["verification_key"] = verification_key
            
            # Güncelleme/ekleme zamanını ekle
            verification_data["updated_at"] = datetime.now()
            
            # Mevcut doğrulamayı kontrol et
            existing_verification = await self.db.verifications.find_one({"verification_key": verification_key})
            
            if existing_verification:
                # Güncelle
                result = await self.db.verifications.update_one(
                    {"verification_key": verification_key},
                    {"$set": verification_data}
                )
                return result.modified_count > 0
            else:
                # Yeni oluştur
                verification_data["created_at"] = datetime.now()
                result = await self.db.verifications.insert_one(verification_data)
                return bool(result.inserted_id)
        except Exception as e:
            self.logger.error(f"Doğrulama kaydetme hatası: {str(e)}")
            return False
    
    async def get_pending_verifications(self) -> List[Dict[str, Any]]:
        """Bekleyen tüm doğrulamaları getir"""
        try:
            verifications = []
            cursor = self.db.verifications.find({"status": "pending"})
            async for verification in cursor:
                verifications.append(normalize_mongodb_doc(verification))
            return verifications
        except Exception as e:
            self.logger.error(f"Bekleyen doğrulamaları getirme hatası: {str(e)}")
            return []
    
    # Görev Tamamlama İşlemleri
    async def get_completed_tasks(self, user_id: str) -> List[Union[str, int]]:
        """Kullanıcının tamamladığı görevleri getir"""
        try:
            user = await self.db.users.find_one({"username": user_id})
            if user:
                return user.get("completed_tasks", [])
            return []
        except Exception as e:
            self.logger.error(f"Tamamlanan görevleri getirme hatası: {str(e)}")
            return []
    
    async def complete_task(self, user_id: str, task_id: Union[str, int]) -> bool:
        """Görevi tamamla olarak işaretle"""
        try:
            # Kullanıcıyı bul ve completed_tasks listesine ekle
            result = await self.db.users.update_one(
                {"username": user_id},
                {"$addToSet": {"completed_tasks": task_id}}
            )
            return result.modified_count > 0
        except Exception as e:
            self.logger.error(f"Görev tamamlama hatası: {str(e)}")
            return False
    
    async def save_task_completion(self, completion_data: Dict[str, Any]) -> bool:
        """Görev tamamlama kaydını kaydet"""
        try:
            # Zaman damgası ekle
            if "completed_at" not in completion_data:
                completion_data["completed_at"] = datetime.now().isoformat()
                
            # Kaydı ekle
            result = await self.db.task_completions.insert_one(completion_data)
            return bool(result.inserted_id)
        except Exception as e:
            self.logger.error(f"Görev tamamlama kaydı hatası: {str(e)}")
            return False
    
    # Rozet İşlemleri
    async def get_all_badges(self) -> List[Dict[str, Any]]:
        """Tüm rozetleri getir"""
        try:
            badges = []
            cursor = self.db.badges.find({})
            async for badge in cursor:
                badges.append(normalize_mongodb_doc(badge))
            return badges
        except Exception as e:
            self.logger.error(f"Rozetleri getirme hatası: {str(e)}")
            return []
    
    async def add_badge_to_user(self, user_id: str, badge_id: str) -> bool:
        """Kullanıcıya rozet ekle"""
        try:
            # Kullanıcıyı bul ve rozet ekle
            result = await self.db.users.update_one(
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
            self.logger.error(f"Rozet ekleme hatası: {str(e)}")
            return False
    
    # Loglama
    async def add_log(self, log_data: Dict[str, Any]) -> bool:
        """Log ekle"""
        try:
            # Zaman damgası ekle
            log_data["timestamp"] = datetime.now()
            
            # Logu ekle
            result = await self.db.logs.insert_one(log_data)
            return bool(result.inserted_id)
        except Exception as e:
            self.logger.error(f"Log ekleme hatası: {str(e)}")
            return False
    
    # Metrik
    async def add_metric(self, metric_data: Dict[str, Any]) -> bool:
        """Metrik ekle"""
        try:
            # Zaman damgası ekle
            metric_data["timestamp"] = datetime.now()
            
            # Metriği ekle
            result = await self.db.metrics.insert_one(metric_data)
            return bool(result.inserted_id)
        except Exception as e:
            self.logger.error(f"Metrik ekleme hatası: {str(e)}")
            return False
    
    # İstatistik İşlemleri
    async def get_task_stats(self) -> Dict[str, Any]:
        """Görev istatistiklerini getir"""
        try:
            # Temel metrikleri hazırla
            user_count = await self.db.users.count_documents({})
            task_count = await self.db.tasks.count_documents({})
            
            # Görev bazında tamamlanma sayıları
            task_completions = {}
            
            # Tüm görevleri al
            cursor = self.db.tasks.find({})
            async for task in cursor:
                task_id = task.get("task_id", str(task["_id"]))
                task_completions[task_id] = await self.db.task_completions.count_documents({"task_id": task_id})
            
            # Genel istatistikler
            total_completions = await self.db.task_completions.count_documents({})
            
            # Son 24 saatteki tamamlamalar
            yesterday = datetime.now() - timedelta(days=1)
            recent_completions = await self.db.task_completions.count_documents({
                "completed_at": {"$gte": yesterday.isoformat()}
            })
            
            # Sonuçları birleştir
            stats = {
                "total_users": user_count,
                "total_tasks": task_count,
                "total_completions": total_completions,
                "recent_completions": recent_completions,
                "task_completions": task_completions
            }
            
            return stats
        except Exception as e:
            self.logger.error(f"İstatistik getirme hatası: {str(e)}")
            return {
                "total_users": 0,
                "total_tasks": 0,
                "total_completions": 0,
                "recent_completions": 0,
                "task_completions": {}
            }
    
    # Günlük Limit Sıfırlama
    async def reset_daily_task_limits(self, today: str) -> int:
        """Günlük görev limitlerini sıfırla ve etkilenen kullanıcı sayısını döndür"""
        try:
            # Kullanıcılardaki daily_attempts alanını filtrele
            counter = 0
            
            # Tüm kullanıcıları getir
            cursor = self.db.users.find({"daily_attempts": {"$exists": True}})
            
            async for user in cursor:
                if "daily_attempts" in user:
                    # Sadece bugünkü kayıtları tut
                    new_daily_attempts = {}
                    for key, value in user["daily_attempts"].items():
                        if today in key:
                            new_daily_attempts[key] = value
                    
                    # Kullanıcıyı güncelle
                    result = await self.db.users.update_one(
                        {"_id": user["_id"]},
                        {"$set": {"daily_attempts": new_daily_attempts}}
                    )
                    
                    if result.modified_count > 0:
                        counter += 1
            
            return counter
        except Exception as e:
            self.logger.error(f"Günlük limit sıfırlama hatası: {str(e)}")
            return 0 