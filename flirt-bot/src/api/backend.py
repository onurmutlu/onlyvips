#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Backend API Module - Backend API istemcisi
Bu modül backend API ile iletişimi sağlar
"""

import logging
import requests
import json
import asyncio
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger(__name__)

class BackendAPI:
    """Backend API istemcisi"""
    
    def __init__(self, api_url: str, admin_key: str):
        self.api_url = api_url
        self.admin_key = admin_key
        self.session = requests.Session()
        self.cache = {}
        self.last_check = 0
    
    async def get_tasks(self) -> List[Dict[str, Any]]:
        """Tüm görevleri getir"""
        try:
            response = await self._request('get', '/tasks/list')
            return response.get("tasks", [])
        except Exception as e:
            logger.error(f"Görevler alınırken hata: {e}")
            return []
    
    async def get_task(self, task_id: Union[str, int]) -> Optional[Dict[str, Any]]:
        """Belirli bir görevi getir"""
        tasks = await self.get_tasks()
        for task in tasks:
            if str(task.get("id")) == str(task_id):
                return task
        return None
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Kullanıcı profilini getir"""
        try:
            response = await self._request('get', f'/profile/{user_id}')
            return response
        except Exception as e:
            logger.error(f"Kullanıcı profili alınırken hata: {e}")
            
            # Kullanıcı bulunamadı mı diye kontrol et (404)
            if hasattr(e, 'status_code') and e.status_code == 404:
                # Kullanıcı yoksa oluşturmayı dene
                logger.info(f"Kullanıcı {user_id} bulunamadı, oluşturulmaya çalışılıyor")
                return await self.create_user(user_id)
            return None
    
    async def create_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Yeni kullanıcı oluştur"""
        try:
            response = await self._request('post', '/profile/create', data={"user_id": user_id})
            logger.info(f"Yeni kullanıcı oluşturuldu: {user_id}")
            return response
        except Exception as e:
            logger.error(f"Kullanıcı oluşturulurken hata: {e}")
            return None
    
    async def complete_task(self, user_id: str, task_id: Union[str, int], verification_data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Görev tamamla"""
        try:
            data = {
                "user_id": user_id,
                "task_id": task_id,
                "verification_data": verification_data or {}
            }
            response = await self._request('post', '/task/complete', data=data)
            return response
        except Exception as e:
            logger.error(f"Görev tamamlanırken hata: {e}")
            return None
    
    async def verify_task(self, user_id: str, task_id: Union[str, int], verified: bool = True) -> bool:
        """Görevi doğrula (admin)"""
        try:
            data = {
                "user_id": user_id,
                "task_id": task_id,
                "verified": verified,
                "admin_key": self.admin_key
            }
            await self._request('post', '/admin/verify-task', data=data)
            logger.info(f"Görev doğrulandı: {user_id} için görev {task_id}")
            return True
        except Exception as e:
            logger.error(f"Görev doğrulanırken hata: {e}")
            return False
    
    async def get_pending_tasks(self) -> Dict[str, Dict[str, Any]]:
        """Bekleyen görevleri getir (admin)"""
        try:
            response = await self._request('get', '/admin/pending-verifications', params={"admin_key": self.admin_key})
            return response.get("pending_verifications", {})
        except Exception as e:
            logger.error(f"Bekleyen görevler alınırken hata: {e}")
            return {}
    
    async def add_xp(self, user_id: str, amount: int) -> bool:
        """Kullanıcıya XP ekle"""
        try:
            data = {"user_id": user_id, "amount": amount}
            await self._request('post', '/profile/add-xp', data=data)
            logger.info(f"XP eklendi: {user_id} için {amount} XP")
            return True
        except Exception as e:
            logger.error(f"XP eklenirken hata: {e}")
            return False
    
    async def add_badge(self, user_id: str, badge_name: str) -> bool:
        """Kullanıcıya rozet ekle"""
        try:
            data = {"user_id": user_id, "badge": badge_name}
            await self._request('post', '/profile/add-badge', data=data)
            logger.info(f"Rozet eklendi: {user_id} için {badge_name}")
            return True
        except Exception as e:
            logger.error(f"Rozet eklenirken hata: {e}")
            return False
    
    async def check_daily_task(self, user_id: str) -> bool:
        """Kullanıcının günlük görev alıp almadığını kontrol et"""
        try:
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            response = await self._request('get', f'/daily-task/check/{user_id}', params={"date": today})
            return response.get("has_received", False)
        except Exception as e:
            logger.error(f"Günlük görev kontrolünde hata: {e}")
            return False
    
    async def set_daily_task(self, user_id: str, task: Dict[str, Any]) -> bool:
        """Kullanıcıya günlük görev ata"""
        try:
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            data = {
                "user_id": user_id,
                "date": today,
                "task": task
            }
            await self._request('post', '/daily-task/set', data=data)
            return True
        except Exception as e:
            logger.error(f"Günlük görev atama hatası: {e}")
            return False
    
    async def expire_task(self, user_id: str, task_id: Union[str, int]) -> bool:
        """Görevi süresi doldu olarak işaretle"""
        try:
            data = {
                "user_id": user_id,
                "task_id": task_id,
                "status": "EXPIRED",
                "admin_key": self.admin_key
            }
            await self._request('post', '/admin/update-task-status', data=data)
            logger.info(f"Görev süresi doldu olarak işaretlendi: {user_id} için görev {task_id}")
            return True
        except Exception as e:
            logger.error(f"Görev süresi doldu işaretlenirken hata: {e}")
            return False
    
    async def _request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """API isteği gönder"""
        url = f"{self.api_url}{endpoint}"
        
        # Loop içinde olduğumuz için asenkron yapılandırılmış bir istek yap
        loop = asyncio.get_event_loop()
        
        try:
            if method.lower() == 'get':
                response = await loop.run_in_executor(
                    None, 
                    lambda: self.session.get(url, params=params, timeout=10)
                )
            elif method.lower() == 'post':
                response = await loop.run_in_executor(
                    None, 
                    lambda: self.session.post(url, json=data, params=params, timeout=10)
                )
            else:
                raise ValueError(f"Desteklenmeyen HTTP metodu: {method}")
            
            response.raise_for_status()  # HTTP hatalarını yükselt
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API isteği başarısız: {e}")
            raise 