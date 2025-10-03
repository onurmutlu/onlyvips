#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Task API - Görev API Modülü
FastAPI tabanlı görev yönetim API'si
"""

import logging
import datetime
import time
from typing import Dict, List, Optional, Any, Union
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Veri modelleri
class TaskComplete(BaseModel):
    user_id: str
    task_id: str
    completed_at: Optional[datetime.datetime] = None

class TaskResponse(BaseModel):
    success: bool
    message: str
    task_id: Optional[str] = None
    rewards: Optional[Dict[str, Any]] = None

app = FastAPI(title="Flirt-Bot Task API", version="1.0.0")

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API bağlamı
class APIContext:
    def __init__(self):
        self.task_manager = None
        self.db_manager = None
        self.user_manager = None

api_context = APIContext()

def setup_api(task_manager, db_manager, user_manager=None):
    """API'yi oluştur ve yapılandır"""
    api_context.task_manager = task_manager
    api_context.db_manager = db_manager
    api_context.user_manager = user_manager
    logger.info("Task API yapılandırıldı")
    return app

def get_task_manager():
    """Task Manager bağımlılığını sağla"""
    if api_context.task_manager is None:
        raise HTTPException(status_code=503, detail="Task Manager henüz başlatılmadı")
    return api_context.task_manager

def get_db_manager():
    """Database Manager bağımlılığını sağla"""
    if api_context.db_manager is None:
        raise HTTPException(status_code=503, detail="Database Manager henüz başlatılmadı")
    return api_context.db_manager

def get_user_manager():
    """User Manager bağımlılığını sağla"""
    if api_context.user_manager is None:
        raise HTTPException(status_code=503, detail="User Manager henüz başlatılmadı")
    return api_context.user_manager

@app.post("/api/task-complete", response_model=TaskResponse)
async def complete_task(
    data: TaskComplete,
    task_manager=Depends(get_task_manager),
    db_manager=Depends(get_db_manager)
):
    """
    Görev tamamlandı bildirimini işle
    Bu endpoint kullanıcının bir görevi tamamladığını bildirir ve ödüllerini verir
    """
    try:
        # Görev ID'yi doğrula
        task_details = await task_manager.get_task_details(data.user_id, data.task_id)
        if not task_details:
            raise HTTPException(status_code=404, detail=f"Görev bulunamadı: {data.task_id}")
            
        # Görev zaten tamamlanmış mı kontrol et
        if task_details.get("status") == "completed":
            return TaskResponse(
                success=False,
                message="Bu görev zaten tamamlanmış",
                task_id=data.task_id
            )
            
        # Görevi tamamla
        success = await task_manager.verify_task(data.user_id, data.task_id, True)
        if not success:
            return TaskResponse(
                success=False,
                message="Görev tamamlanamadı. Doğrulama hatası.",
                task_id=data.task_id
            )
            
        # Görev tamamlama zamanını kaydet
        completion_time = data.completed_at or datetime.datetime.now()
        await db_manager.update_task_completion_time(
            data.user_id, 
            data.task_id, 
            completion_time.isoformat()
        )
        
        # Kullanıcıya XP ve token ödüllerini ver
        rewards = await task_manager.award_task_rewards(data.user_id, data.task_id)
        
        # Günlük log dosyasına yaz
        log_entry = f"{completion_time.strftime('%Y-%m-%d %H:%M:%S')} | {data.user_id} | {data.task_id} | SUCCESS"
        await db_manager.append_task_log(log_entry)
        
        return TaskResponse(
            success=True,
            message="Görev başarıyla tamamlandı",
            task_id=data.task_id,
            rewards=rewards
        )
        
    except Exception as e:
        logger.error(f"Görev tamamlama hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks/{user_id}", response_model=List[Dict[str, Any]])
async def get_user_tasks(
    user_id: str,
    task_manager=Depends(get_task_manager)
):
    """Kullanıcının görevlerini getir"""
    try:
        tasks = await task_manager.get_user_tasks(user_id)
        return tasks
    except Exception as e:
        logger.error(f"Kullanıcı görevleri alınırken hata: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks/status/{user_id}/{task_id}")
async def get_task_status(
    user_id: str,
    task_id: str,
    task_manager=Depends(get_task_manager)
):
    """Görev durumunu getir"""
    try:
        task = await task_manager.get_task_details(user_id, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Görev bulunamadı")
        return {
            "task_id": task_id,
            "status": task.get("status", "unknown"),
            "details": task
        }
    except Exception as e:
        logger.error(f"Görev durumu alınırken hata: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user/progress/{user_id}")
async def get_user_progress(
    user_id: str,
    db_manager=Depends(get_db_manager)
):
    """Kullanıcının ilerleme durumunu getir"""
    try:
        user_data = await db_manager.get_user_data(user_id)
        if not user_data:
            raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
            
        # Tamamlanan görevleri say
        completed_tasks = await db_manager.count_completed_tasks(user_id)
        
        return {
            "user_id": user_id,
            "xp": user_data.get("xp", 0),
            "tokens": user_data.get("tokens", 0),
            "completed_task_count": completed_tasks,
            "badges": user_data.get("badges", [])
        }
    except Exception as e:
        logger.error(f"Kullanıcı ilerleme durumu alınırken hata: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats/tasks")
async def get_task_stats(
    db_manager=Depends(get_db_manager)
):
    """Görev istatistiklerini getir"""
    try:
        stats = await db_manager.get_task_stats()
        return stats
    except Exception as e:
        logger.error(f"Görev istatistikleri alınırken hata: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/config", response_model=List[Dict[str, Any]])
async def get_tasks_config(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    JSON temelli görev yapılandırmasını döndürür.
    Bu görevler sistem tarafından dinamik olarak yüklenir.
    """
    try:
        # Örnek görev yapılandırmaları - Gerçek sistemde bir dosyadan veya veritabanından yüklenebilir
        tasks_config = [
            {
                "id": "join_channel",
                "title": "Kanala Katıl",
                "description": "Resmi telegram kanalımıza katılarak ödül kazanın",
                "type": "channel_join_v2",
                "reward": {
                    "xp": 10,
                    "token": 1
                },
                "params": {
                    "channel_id": "@onlyvips_channel"
                },
                "cooldown": 86400  # 24 saat (saniye cinsinden)
            },
            {
                "id": "send_message",
                "title": "Mesaj Gönder",
                "description": "Grubumuza mesaj göndererek ödül kazanın",
                "type": "message_send",
                "reward": {
                    "xp": 5,
                    "token": 1
                },
                "params": {
                    "chat_id": "@onlyvips_group",
                    "min_length": 10
                },
                "cooldown": 86400
            },
            {
                "id": "click_button",
                "title": "Butona Tıkla",
                "description": "Günlük ödül butonuna tıklayarak token kazanın",
                "type": "button_click",
                "reward": {
                    "xp": 3,
                    "token": 2
                },
                "params": {
                    "button_id": "daily_reward"
                },
                "cooldown": 86400
            },
            {
                "id": "vote_poll",
                "title": "Ankete Katıl",
                "description": "Topluluk anketine katılarak fikrini belirt",
                "type": "voting",
                "reward": {
                    "xp": 8,
                    "token": 1
                },
                "params": {
                    "poll_chat_id": "@onlyvips_channel",
                    "poll_message_id": 123
                },
                "cooldown": 604800  # 7 gün
            },
            {
                "id": "schedule_post",
                "title": "Zamanlanmış Mesaj",
                "description": "Belirli bir zamanda mesaj gönder",
                "type": "schedule_post",
                "reward": {
                    "xp": 15,
                    "token": 3
                },
                "params": {
                    "target_chat_id": "@onlyvips_events",
                    "schedule_timestamp": int(time.time()) + 3600,  # 1 saat sonra
                    "min_length": 20
                },
                "cooldown": 604800  # 7 gün
            },
            {
                "id": "emoji_reaction",
                "title": "Emoji Tepkisi Ver",
                "description": "Duyuru mesajına emoji tepkisi ver",
                "type": "emoji_reaction",
                "reward": {
                    "xp": 5,
                    "token": 1
                },
                "params": {
                    "target_chat_id": "@onlyvips_channel",
                    "target_message_id": 456,
                    "target_emoji": "👍"
                },
                "cooldown": 86400
            },
            {
                "id": "group_join_message",
                "title": "Gruba Katıl ve Mesaj Gönder",
                "description": "Yeni grubumuza katıl ve kendini tanıt",
                "type": "group_join_message",
                "reward": {
                    "xp": 20,
                    "token": 3
                },
                "params": {
                    "group_username": "@onlyvips_community",
                    "min_length": 30
                },
                "cooldown": 2592000  # 30 gün
            }
        ]
        
        # Kullanıcı bazında görevleri filtreleme veya özelleştirme yapılabilir
        # Örneğin, user_level'e göre farklı görevler sunulabilir
        
        return tasks_config
    except Exception as e:
        logger.error(f"Görev yapılandırması alınırken hata: {e}")
        raise HTTPException(status_code=500, detail="Görev yapılandırması alınamadı")

# API başlatma ve servis etme kodu burada olmayacak
# Bu dosya sadece FastAPI app'ini tanımlar, ayrı bir dosyada çalıştırılır 