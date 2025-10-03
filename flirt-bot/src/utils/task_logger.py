#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Task Logger - Görev Logları
Görev tamamlama, başarısızlık ve istatistik loglarını yöneten modül
"""

import os
import json
import time
import logging
import datetime
import sqlite3
import asyncio
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)

class TaskLogger:
    """Görev loglarını ve istatistiklerini yönetir."""
    
    def __init__(self, log_dir: str = "./logs", db_path: str = "./logs/tasks.db"):
        """
        TaskLogger yapıcısı
        
        Args:
            log_dir: Log dosyalarının kaydedileceği dizin
            db_path: SQLite veritabanı dosyasının yolu
        """
        self.log_dir = log_dir
        self.db_path = db_path
        
        # Log dizinini oluştur
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        # Log dosyaları
        self.completion_log_path = os.path.join(log_dir, "task_completions.log")
        self.stats_json_path = os.path.join(log_dir, "task_stats.json")
        
        # Veritabanı bağlantısı
        self._connection = None
        self._lock = asyncio.Lock()
        
        # İstatistikler
        self.stats = self._load_stats()
        
        # Veritabanı tabloları oluştur
        self._init_db()
        
        logger.info(f"TaskLogger başlatıldı: {log_dir}")
    
    def _init_db(self):
        """Veritabanı tablolarını oluştur"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Görev logları tablosu
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER NOT NULL,
                user_id TEXT NOT NULL,
                task_id TEXT NOT NULL,
                task_type TEXT NOT NULL,
                status TEXT NOT NULL,
                details TEXT
            )
            ''')
            
            # Görev istatistikleri tablosu
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_stats (
                task_type TEXT PRIMARY KEY,
                total_attempts INTEGER DEFAULT 0,
                successful_attempts INTEGER DEFAULT 0,
                failed_attempts INTEGER DEFAULT 0,
                unique_users INTEGER DEFAULT 0,
                last_updated INTEGER NOT NULL
            )
            ''')
            
            # Günlük görev limitleri tablosu
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_task_limits (
                user_id TEXT NOT NULL,
                task_type TEXT NOT NULL,
                day_date TEXT NOT NULL,
                count INTEGER DEFAULT 1,
                PRIMARY KEY (user_id, task_type, day_date)
            )
            ''')
            
            conn.commit()
            logger.info("Veritabanı tabloları oluşturuldu")
            
        except Exception as e:
            logger.error(f"Veritabanı oluşturulurken hata: {e}")
    
    def _get_connection(self):
        """SQLite bağlantısını döndür"""
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path)
        return self._connection
    
    def _load_stats(self) -> Dict[str, Dict[str, int]]:
        """İstatistikleri dosyadan yükle"""
        try:
            if os.path.exists(self.stats_json_path):
                with open(self.stats_json_path, "r") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"İstatistikler yüklenirken hata: {e}")
            return {}
    
    def _save_stats(self):
        """İstatistikleri dosyaya kaydet"""
        try:
            with open(self.stats_json_path, "w") as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            logger.error(f"İstatistikler kaydedilirken hata: {e}")
    
    async def log_task_completion(
        self,
        user_id: str,
        task_id: str,
        task_type: str,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Görev tamamlama logunu ekle
        
        Args:
            user_id: Kullanıcı ID'si
            task_id: Görev ID'si
            task_type: Görev tipi
            status: Durum (completed, failed, expired)
            details: Ek detaylar (opsiyonel)
        """
        timestamp = int(time.time())
        formatted_time = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        
        # Text log dosyasına yaz
        log_line = f"{formatted_time} | {user_id} | {task_id} | {task_type} | {status}"
        
        try:
            with open(self.completion_log_path, "a") as f:
                f.write(log_line + "\n")
        except Exception as e:
            logger.error(f"Log dosyasına yazılırken hata: {e}")
        
        # Veritabanına ekle
        try:
            async with self._lock:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                # Log ekle
                cursor.execute(
                    "INSERT INTO task_logs (timestamp, user_id, task_id, task_type, status, details) VALUES (?, ?, ?, ?, ?, ?)",
                    (timestamp, user_id, task_id, task_type, status, json.dumps(details) if details else None)
                )
                
                # İstatistikleri güncelle
                cursor.execute(
                    """
                    INSERT INTO task_stats (task_type, total_attempts, successful_attempts, failed_attempts, unique_users, last_updated)
                    VALUES (?, 1, ?, ?, 1, ?)
                    ON CONFLICT(task_type) DO UPDATE SET
                        total_attempts = total_attempts + 1,
                        successful_attempts = successful_attempts + CASE WHEN ? = 'completed' THEN 1 ELSE 0 END,
                        failed_attempts = failed_attempts + CASE WHEN ? = 'failed' OR ? = 'expired' THEN 1 ELSE 0 END,
                        last_updated = ?
                    """,
                    (
                        task_type,
                        1 if status == "completed" else 0,
                        1 if status in ["failed", "expired"] else 0,
                        timestamp,
                        status, status, status,
                        timestamp
                    )
                )
                
                # Benzersiz kullanıcıları güncelle (her görev tipi için ayrı tutuluyor)
                cursor.execute(
                    """
                    SELECT COUNT(DISTINCT user_id) FROM task_logs WHERE task_type = ?
                    """,
                    (task_type,)
                )
                unique_users = cursor.fetchone()[0]
                
                cursor.execute(
                    """
                    UPDATE task_stats SET unique_users = ? WHERE task_type = ?
                    """,
                    (unique_users, task_type)
                )
                
                conn.commit()
                
                # Ayrıca yerel istatistikleri de güncelle
                if task_type not in self.stats:
                    self.stats[task_type] = {
                        "total_attempts": 0,
                        "successful_attempts": 0,
                        "failed_attempts": 0,
                        "unique_users": 0
                    }
                
                self.stats[task_type]["total_attempts"] += 1
                
                if status == "completed":
                    self.stats[task_type]["successful_attempts"] += 1
                elif status in ["failed", "expired"]:
                    self.stats[task_type]["failed_attempts"] += 1
                
                self.stats[task_type]["unique_users"] = unique_users
                
                # İstatistikleri JSON dosyasına kaydet
                self._save_stats()
                
                logger.debug(f"Görev logu eklendi: {log_line}")
                
        except Exception as e:
            logger.error(f"Veritabanı logu eklenirken hata: {e}")
    
    async def check_daily_limit(self, user_id: str, task_type: str, limit: int = 1) -> bool:
        """
        Kullanıcının günlük görev limitini kontrol et
        
        Args:
            user_id: Kullanıcı ID'si
            task_type: Görev tipi
            limit: Günlük limit (varsayılan: 1)
            
        Returns:
            bool: Kullanıcı limiti aşmadıysa True, aştıysa False
        """
        try:
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            
            async with self._lock:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                # Kullanıcının bugün bu görev tipindeki tamamlama sayısını al
                cursor.execute(
                    "SELECT count FROM daily_task_limits WHERE user_id = ? AND task_type = ? AND day_date = ?",
                    (user_id, task_type, today)
                )
                
                result = cursor.fetchone()
                
                if not result:
                    # Kullanıcı bugün bu görevi hiç yapmamış
                    return True
                
                count = result[0]
                
                # Limite ulaşıldı mı kontrol et
                return count < limit
                
        except Exception as e:
            logger.error(f"Günlük limit kontrolünde hata: {e}")
            # Hata durumunda kullanıcıyı engellemek yerine devam etmesine izin ver
            return True
    
    async def increment_daily_limit(self, user_id: str, task_type: str):
        """
        Kullanıcının günlük görev sayacını artır
        
        Args:
            user_id: Kullanıcı ID'si
            task_type: Görev tipi
        """
        try:
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            
            async with self._lock:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                # Sayacı güncelle veya yeni kayıt ekle
                cursor.execute(
                    """
                    INSERT INTO daily_task_limits (user_id, task_type, day_date, count)
                    VALUES (?, ?, ?, 1)
                    ON CONFLICT(user_id, task_type, day_date) DO UPDATE SET
                        count = count + 1
                    """,
                    (user_id, task_type, today)
                )
                
                conn.commit()
                
                logger.debug(f"Günlük limit artırıldı: {user_id}, {task_type}, {today}")
                
        except Exception as e:
            logger.error(f"Günlük limit artırılırken hata: {e}")
    
    async def reset_daily_limits(self):
        """
        Tüm kullanıcılar için günlük limitleri sıfırla.
        Bu metod gece yarısı bir planlayıcı tarafından çağrılabilir.
        """
        try:
            yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            
            async with self._lock:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                # Dünkü ve daha eski kayıtları temizle
                cursor.execute(
                    "DELETE FROM daily_task_limits WHERE day_date <= ?",
                    (yesterday,)
                )
                
                conn.commit()
                
                logger.info(f"Günlük limitler sıfırlandı, temizlenen tarih: {yesterday} ve öncesi")
                
        except Exception as e:
            logger.error(f"Günlük limitler sıfırlanırken hata: {e}")
    
    async def get_user_progress(self, user_id: str) -> Dict[str, Any]:
        """
        Kullanıcının görev ilerleme durumunu getir
        
        Args:
            user_id: Kullanıcı ID'si
            
        Returns:
            Dict: Kullanıcının ilerleme istatistikleri
        """
        try:
            async with self._lock:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                # Tamamlanan görev sayısı
                cursor.execute(
                    "SELECT COUNT(*) FROM task_logs WHERE user_id = ? AND status = 'completed'",
                    (user_id,)
                )
                completed_tasks = cursor.fetchone()[0]
                
                # Toplam XP (her görev 10 XP olarak varsayalım, gerçek sistemde ödül tablosundan alınabilir)
                xp = completed_tasks * 10
                
                # Toplam Token (her görev 1 Token olarak varsayalım, gerçek sistemde ödül tablosundan alınabilir)
                token = completed_tasks * 1
                
                # Görev tiplerine göre tamamlama sayıları
                cursor.execute(
                    """
                    SELECT task_type, COUNT(*) FROM task_logs 
                    WHERE user_id = ? AND status = 'completed'
                    GROUP BY task_type
                    """,
                    (user_id,)
                )
                task_type_counts = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Son 7 gündeki ilerleme
                seven_days_ago = int(time.time()) - (7 * 24 * 3600)
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM task_logs 
                    WHERE user_id = ? AND status = 'completed' AND timestamp >= ?
                    """,
                    (user_id, seven_days_ago)
                )
                last_week_tasks = cursor.fetchone()[0]
                
                return {
                    "user_id": user_id,
                    "completed_tasks": completed_tasks,
                    "xp": xp,
                    "token": token,
                    "task_types": task_type_counts,
                    "last_week_tasks": last_week_tasks
                }
                
        except Exception as e:
            logger.error(f"Kullanıcı ilerleme durumu alınırken hata: {e}")
            return {
                "user_id": user_id,
                "completed_tasks": 0,
                "xp": 0,
                "token": 0,
                "task_types": {},
                "last_week_tasks": 0
            }
    
    async def get_task_stats(self) -> Dict[str, Dict[str, int]]:
        """
        Tüm görev tiplerinin istatistiklerini getir
        
        Returns:
            Dict: Görev tiplerinin istatistikleri
        """
        try:
            async with self._lock:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                cursor.execute(
                    """
                    SELECT task_type, total_attempts, successful_attempts, failed_attempts, unique_users
                    FROM task_stats
                    """
                )
                
                stats = {}
                for row in cursor.fetchall():
                    stats[row[0]] = {
                        "total_attempts": row[1],
                        "successful_attempts": row[2],
                        "failed_attempts": row[3],
                        "unique_users": row[4]
                    }
                
                return stats
                
        except Exception as e:
            logger.error(f"Görev istatistikleri alınırken hata: {e}")
            return self.stats  # Hata durumunda yerel kopyayı döndür
    
    def close(self):
        """Veritabanı bağlantısını kapat"""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("TaskLogger veritabanı bağlantısı kapatıldı") 