"""
Görev Yönetim Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status, Body
from typing import List, Dict, Any, Optional
import json
from datetime import datetime, timedelta

from app.core.config import settings
from app.core.database import db
from app.utils.logger import app_logger, log_task_completion
from app.core.auth import (
    User, 
    get_current_user_from_any, 
    get_active_user,
    get_user_with_permission
)

router = APIRouter()

# Örnek görev verileri (gerçek uygulamada veritabanından gelir)
TASKS = [
    {
        "id": 1,
        "title": "Telegram Botunu Başlat",
        "description": "OnlyVips Flirt-Bot'u başlatmak için /start komutunu gönderin",
        "reward_type": "xp",
        "reward_value": 5,
        "verification_type": "automatic",
        "verification_required": True,
        "max_daily_attempts": 1,
        "task_type": "start_command"
    },
    {
        "id": 2,
        "title": "Kanala Katıl",
        "description": "OnlyVips resmi kanalına katılın",
        "reward_type": "xp",
        "reward_value": 10,
        "verification_type": "join_channel",
        "verification_required": True,
        "channel_id": "@onlyvips_channel",
        "max_daily_attempts": 1,
        "task_type": "join_channel"
    },
    {
        "id": 3,
        "title": "Emoji Tepkisi Gönder",
        "description": "Kanaldaki son mesaja 👍 emoji tepkisi gönderin",
        "reward_type": "xp",
        "reward_value": 5,
        "verification_type": "emoji_reaction",
        "verification_required": True,
        "required_emoji": "👍",
        "channel_id": "@onlyvips_channel",
        "max_daily_attempts": 3,
        "task_type": "emoji_reaction"
    },
    {
        "id": 4,
        "title": "Gruba Katıl ve Mesaj Gönder",
        "description": "OnlyVips grubuna katılın ve kendinizi tanıtan bir mesaj gönderin",
        "reward_type": "badge",
        "reward_value": "Sosyal Kelebek",
        "verification_type": "group_join_message",
        "verification_required": True,
        "group_id": "@onlyvips_group",
        "max_daily_attempts": 1,
        "task_type": "group_join_message"
    },
    {
        "id": 5,
        "title": "Inline Butona Tıkla",
        "description": "Flirt-Bot'un gönderdiği inline butona tıklayın",
        "reward_type": "xp",
        "reward_value": 5,
        "verification_type": "inline_button",
        "verification_required": True,
        "max_daily_attempts": 1,
        "task_type": "inline_button_click"
    },
    {
        "id": 6,
        "title": "Mesaj İletme",
        "description": "Bir kanaldan mesaj iletme",
        "reward_type": "xp",
        "reward_value": 5,
        "verification_type": "forward_message",
        "verification_required": True,
        "source_channel_id": "@onlyvips_channel",
        "max_daily_attempts": 2,
        "task_type": "forward_message"
    }
]

# Basit kullanıcı veritabanı (gerçek uygulamada veritabanına taşınır)
USERS_DB = {}

# Doğrulama bekleyen görevler
PENDING_VERIFICATIONS = {}

@router.get("/list")
async def get_tasks(current_user: User = Depends(get_current_user_from_any)):
    """Tüm görevleri listele"""
    try:
        tasks = await db.get_all_tasks()
        return {"tasks": tasks, "status": "success"}
    except Exception as e:
        app_logger.error(f"Görev listesi alınırken hata: {str(e)}")
        raise HTTPException(status_code=500, detail="Görev listesi alınamadı")

@router.get("/user/{user_id}")
async def get_user_tasks(
    user_id: str,
    current_user: User = Depends(get_current_user_from_any)
):
    """Kullanıcı görevlerini ve ilerleme durumunu getir"""
    try:
        # Farklı bir kullanıcının bilgilerini görüntüleme yetkisi
        if user_id != current_user.id and current_user.role not in ["admin", "moderator", "showcu", "system"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Başka bir kullanıcının görevlerini görüntüleme yetkiniz yok"
            )
        
        # Kullanıcı bilgilerini al
        user_data = await db.get_user(user_id)
        
        if not user_data:
            # Kullanıcı yoksa oluştur
            user_data = {
                "username": user_id, 
                "xp": 0, 
                "badges": [], 
                "completed_tasks": [], 
                "pending_tasks": [],
                "daily_attempts": {}
            }
            await db.save_user(user_id, user_data)
        
        # Tüm görevleri al
        all_tasks = await db.get_all_tasks()
        
        # Kullanıcının tamamladığı görevleri al
        completed_tasks = user_data.get("completed_tasks", [])
        pending_tasks = user_data.get("pending_tasks", [])
        
        # Görevlerin durumunu ekleyelim
        tasks_with_status = []
        today = datetime.now().strftime("%Y-%m-%d")
        
        for task in all_tasks:
            task_copy = task.copy()
            task_id = task.get("id")
            
            # Görev durumunu belirleyelim
            if task_id in completed_tasks:
                task_copy["status"] = "completed"
            elif task_id in pending_tasks:
                task_copy["status"] = "pending"
            else:
                task_copy["status"] = "available"
                
            # Günlük deneme sayısını kontrol edelim
            daily_attempts_key = f"{task_id}_{today}"
            daily_attempts = user_data.get("daily_attempts", {}).get(daily_attempts_key, 0)
            
            task_copy["daily_attempts"] = daily_attempts
            task_copy["max_attempts_reached"] = daily_attempts >= task.get("max_daily_attempts", 1)
            
            tasks_with_status.append(task_copy)
        
        # Kullanıcı bilgilerini format
        user_info = {
            "user_id": user_id,
            "xp": user_data.get("xp", 0),
            "badges": user_data.get("badges", []),
            "completed_tasks_count": len(completed_tasks),
            "pending_tasks_count": len(pending_tasks)
        }
        
        return {
            "user_info": user_info,
            "tasks": tasks_with_status,
            "status": "success"
        }
    
    except HTTPException:
        # HTTP hataları doğrudan yeniden fırlat
        raise
    except Exception as e:
        app_logger.error(f"Kullanıcı görevleri alınırken hata: {str(e)}")
        raise HTTPException(status_code=500, detail="Kullanıcı görevleri alınamadı")

@router.post("/complete")
async def complete_task(
    request: Request,
    current_user: User = Depends(get_current_user_from_any)
):
    """Görev tamamlama bildirimi"""
    try:
        data = await request.json()
        
        # Kullanıcı ID kontrolü
        user_id = data.get("user_id")
        
        # Kullanıcı kendi adına veya sistem rolü işlem yapabilir
        if user_id != current_user.id and current_user.role not in ["admin", "system"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Başka bir kullanıcı için görev tamamlama yetkiniz yok"
            )
        
        task_id = data.get("task_id")
        verification_data = data.get("verification_data", {})
        
        if not user_id or task_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user_id ve task_id gerekli"
            )
        
        # Görev nesnesini bulalım
        task = await db.get_task(task_id)
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Geçersiz task_id"
            )
        
        # Kullanıcı yoksa oluşturalım
        user_data = await db.get_user(user_id)
        
        if not user_data:
            user_data = {
                "username": user_id, 
                "xp": 0, 
                "badges": [], 
                "completed_tasks": [], 
                "pending_tasks": [],
                "daily_attempts": {}
            }
            await db.save_user(user_id, user_data)
        
        # Zaten tamamladıysa bildirelim
        if task_id in user_data.get("completed_tasks", []):
            return {"message": "Bu görev zaten tamamlandı", "status": "success"}
        
        # Günlük deneme sayısını kontrol edelim
        today = datetime.now().strftime("%Y-%m-%d")
        daily_attempts_key = f"{task_id}_{today}"
        
        if "daily_attempts" not in user_data:
            user_data["daily_attempts"] = {}
            
        daily_attempts = user_data.get("daily_attempts", {}).get(daily_attempts_key, 0)
        
        if daily_attempts >= task.get("max_daily_attempts", 1):
            return {"error": "Bu görev için günlük deneme limitine ulaştınız", "status": "error"}
        
        # Deneme sayısını artıralım
        user_data["daily_attempts"][daily_attempts_key] = daily_attempts + 1
        
        # Kullanıcı verilerini güncelle
        await db.save_user(user_id, user_data)
        
        # Doğrulama gerekiyorsa
        if task.get("verification_required", True):
            # Benzersiz doğrulama anahtarı oluştur
            pending_verification_key = f"{user_id}_{task_id}"
            
            # Doğrulama nesnesini saklayalım
            verification_record = {
                "user_id": user_id,
                "task_id": task_id,
                "verification_data": verification_data,
                "timestamp": datetime.now().isoformat(),
                "status": "pending"
            }
            
            # Veritabanına kaydet
            await db.save_verification(pending_verification_key, verification_record)
            
            # Bekleyen görevlere ekleyelim
            if "pending_tasks" not in user_data:
                user_data["pending_tasks"] = []
            
            # Zaten beklemedeyse tekrar eklemeyelim
            if task_id not in user_data["pending_tasks"]:
                user_data["pending_tasks"].append(task_id)
                await db.save_user(user_id, user_data)
            
            app_logger.info(f"Görev doğrulama başlatıldı: {user_id} için {task_id} görevi")
            
            # Doğrulama tipine göre otomatik doğrulama yapalım
            if task.get("verification_type") in ["automatic", "start_command", "inline_button"]:
                # Burada basit bir simülasyon, gerçekte farklı doğrulama tipleri için özel işlemler olacak
                verification_data = {
                    "user_id": user_id,
                    "task_id": task_id,
                    "status": "approved"
                }
                return await verify_task(verification_data)
            
            return {
                "message": f"Görev doğrulanıyor. '{task.get('verification_type')}' türünde doğrulama gerekiyor.",
                "status": "pending",
                "verification_type": task.get("verification_type"),
                "pending_verification_id": pending_verification_key
            }
        
        # Doğrulama gerekmiyorsa doğrudan tamamla
        await complete_task_for_user(user_id, task_id, task)
        
        return {
            "message": f"Görev tamamlandı!",
            "status": "success",
            "user_xp": user_data.get("xp", 0) + task.get("reward_value", 0) if task.get("reward_type") == "xp" else user_data.get("xp", 0),
            "badges": user_data.get("badges", []) + [task.get("reward_value")] if task.get("reward_type") == "badge" and task.get("reward_value") not in user_data.get("badges", []) else user_data.get("badges", [])
        }
        
    except HTTPException:
        # HTTP hataları doğrudan yeniden fırlat
        raise
    except Exception as e:
        app_logger.error(f"Görev tamamlama hatası: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Görev tamamlanamadı: {str(e)}")

@router.post("/verify")
async def verify_task(
    data: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_user_with_permission("tasks:verify"))
):
    """Görev doğrulama (bot veya admin tarafından)"""
    try:
        user_id = data.get("user_id")
        task_id = data.get("task_id")
        status = data.get("status", "approved")  # approved veya rejected
        
        if not user_id or task_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user_id ve task_id gerekli"
            )
        
        # Kullanıcıyı kontrol et
        user_data = await db.get_user(user_id)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kullanıcı bulunamadı"
            )
        
        # Doğrulama anahtarını oluştur
        pending_verification_key = f"{user_id}_{task_id}"
        
        # Bekleyen doğrulama var mı kontrol et
        verification = await db.get_verification(pending_verification_key)
        
        if not verification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bekleyen doğrulama bulunamadı"
            )
        
        # Görev nesnesini bul
        task = await db.get_task(task_id)
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Geçersiz task_id"
            )
        
        # Doğrulama durumuna göre işlem yap
        if status == "approved":
            # Görevi tamamla
            result = await complete_task_for_user(user_id, task_id, task)
            
            # Doğrulama kaydını güncelle
            verification["status"] = "approved"
            verification["approved_by"] = current_user.username
            verification["approved_at"] = datetime.now().isoformat()
            
            await db.save_verification(pending_verification_key, verification)
            
            # Log kaydı
            log_task_completion(user_id, task_id, "SUCCESS", {
                "verifier": current_user.username,
                "verification_type": task.get("verification_type")
            })
            
            return {
                "message": f"Görev doğrulandı! {result.get('reward_message', '')}",
                "status": "success",
                "user_xp": result.get("user_xp", 0),
                "badges": result.get("badges", [])
            }
        else:  # rejected
            # Bekleyen görevlerden çıkar
            if "pending_tasks" in user_data and task_id in user_data["pending_tasks"]:
                user_data["pending_tasks"].remove(task_id)
                await db.save_user(user_id, user_data)
            
            # Doğrulama kaydını güncelle
            verification["status"] = "rejected"
            verification["rejected_by"] = current_user.username
            verification["rejected_at"] = datetime.now().isoformat()
            
            await db.save_verification(pending_verification_key, verification)
            
            # Log kaydı
            log_task_completion(user_id, task_id, "REJECTED", {
                "verifier": current_user.username,
                "verification_type": task.get("verification_type")
            })
            
            return {
                "message": "Görev doğrulanamadı.",
                "status": "rejected"
            }
    
    except HTTPException:
        # HTTP hataları doğrudan yeniden fırlat
        raise
    except Exception as e:
        app_logger.error(f"Görev doğrulama hatası: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Görev doğrulanamadı: {str(e)}")

@router.get("/pending")
async def get_pending_tasks(
    current_user: User = Depends(get_user_with_permission("tasks:verify"))
):
    """Doğrulama bekleyen tüm görevleri getir (admin panel için)"""
    try:
        pending_list = await db.get_pending_verifications()
        
        # 24 saatten eski olanları filtrele
        now = datetime.now()
        filtered_pending = []
        
        for verification in pending_list:
            # Timestamp'i kontrol et
            if "timestamp" in verification:
                try:
                    verification_time = datetime.fromisoformat(verification["timestamp"])
                    if now - verification_time <= timedelta(hours=24):
                        filtered_pending.append(verification)
                except (ValueError, TypeError):
                    # Geçersiz zaman formatı, yine de listeye ekle
                    filtered_pending.append(verification)
            else:
                # Timestamp yoksa yine de ekle
                filtered_pending.append(verification)
        
        return {"pending_tasks": filtered_pending, "status": "success"}
    except Exception as e:
        app_logger.error(f"Bekleyen görevler alınırken hata: {str(e)}")
        raise HTTPException(status_code=500, detail="Bekleyen görevler alınamadı")

@router.get("/reset-daily")
async def reset_daily_limits(
    current_user: User = Depends(get_user_with_permission("tasks:reset"))
):
    """Günlük limitleri sıfırla (günde bir kez çalıştırılır)"""
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        counter = await db.reset_daily_task_limits(today)
        
        # Log kaydı
        app_logger.info(f"Günlük limitler sıfırlandı: {counter} kullanıcı etkilendi")
        
        return {"message": f"{counter} kullanıcı için günlük limitler temizlendi", "status": "success"}
    except Exception as e:
        app_logger.error(f"Günlük limitler sıfırlanırken hata: {str(e)}")
        raise HTTPException(status_code=500, detail="Günlük limitler sıfırlanamadı")

@router.post("/assign-badge")
async def assign_badge(
    data: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_user_with_permission("badges:assign"))
):
    """Kullanıcıya rozet ata"""
    try:
        user_id = data.get("user_id")
        badge_id = data.get("badge_id")
        
        if not user_id or not badge_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user_id ve badge_id gerekli"
            )
        
        # Kullanıcıyı kontrol et
        user = await db.get_user(user_id)
        
        if not user:
            # Kullanıcı yoksa oluştur
            user = {
                "username": user_id, 
                "xp": 0, 
                "badges": [], 
                "completed_tasks": []
            }
            await db.save_user(user_id, user)
        
        # Rozeti ekle
        result = await db.add_badge_to_user(user_id, badge_id)
        
        if result:
            # Log kaydı
            app_logger.info(f"Rozet atandı: {user_id} kullanıcısına {badge_id} rozeti")
            
            return {"message": f"'{badge_id}' rozeti başarıyla eklendi", "status": "success"}
        else:
            return {"message": "Bu rozet zaten kullanıcıda var", "status": "success"}
    except Exception as e:
        app_logger.error(f"Rozet atama hatası: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Rozet atanamadı: {str(e)}")

@router.get("/stats")
async def get_task_stats(
    current_user: User = Depends(get_user_with_permission("tasks:read"))
):
    """Görev istatistiklerini getir"""
    try:
        stats = await db.get_task_stats()
        return {"stats": stats, "status": "success"}
    except Exception as e:
        app_logger.error(f"Görev istatistikleri alınırken hata: {str(e)}")
        raise HTTPException(status_code=500, detail="Görev istatistikleri alınamadı")

# Yardımcı Fonksiyonlar
async def complete_task_for_user(user_id: str, task_id: Any, task: Dict[str, Any]) -> Dict[str, Any]:
    """Kullanıcı için görevi tamamla ve ödülleri dağıt"""
    # Kullanıcı verisini al
    user_data = await db.get_user(user_id)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı bulunamadı"
        )
    
    # Bekleyen görevlerden çıkar
    if "pending_tasks" in user_data and task_id in user_data["pending_tasks"]:
        user_data["pending_tasks"].remove(task_id)
    
    # Tamamlanan görevlere ekle
    if "completed_tasks" not in user_data:
        user_data["completed_tasks"] = []
    
    if task_id not in user_data["completed_tasks"]:
        user_data["completed_tasks"].append(task_id)
    
    # Ödül ver
    reward_message = await _award_reward(user_data, task)
    
    # Kullanıcı verilerini güncelle
    await db.save_user(user_id, user_data)
    
    # Tamamlama zamanını kaydet
    completion_data = {
        "user_id": user_id,
        "task_id": task_id,
        "completed_at": datetime.now().isoformat(),
        "reward_type": task.get("reward_type"),
        "reward_value": task.get("reward_value")
    }
    
    await db.save_task_completion(completion_data)
    
    # Log kaydı
    log_task_completion(user_id, task_id, "COMPLETED", {
        "xp": task.get("reward_value") if task.get("reward_type") == "xp" else 0,
        "badge": task.get("reward_value") if task.get("reward_type") == "badge" else None
    })
    
    return {
        "reward_message": reward_message,
        "user_xp": user_data.get("xp", 0),
        "badges": user_data.get("badges", [])
    }

async def _award_reward(user: Dict[str, Any], task: Dict[str, Any]) -> str:
    """Görev tamamlama ödülünü ver ve ödül mesajını döndür"""
    reward_message = ""
    
    if task["reward_type"] == "xp":
        if "xp" not in user:
            user["xp"] = 0
        user["xp"] += task["reward_value"]
        reward_message = f"+{task['reward_value']} XP kazandın!"
    
    elif task["reward_type"] == "badge":
        if "badges" not in user:
            user["badges"] = []
        if task["reward_value"] not in user["badges"]:
            user["badges"].append(task["reward_value"])
        reward_message = f"'{task['reward_value']}' rozetini kazandın!"
    
    return reward_message 