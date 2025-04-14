from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from profile import router as profile_router, users_db
import time


app = FastAPI()

# CORS ayarı
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://arayis-evreni.siyahkare.com", "https://*.vercel.app", "http://localhost:5173", "http://localhost:4173", "http://localhost:4174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profile_router)


# Sahte görev verisi
TASKS = [
    {"id": 1, "title": "Yeni üye davet et", "reward": "🎖️ Rozet", "reward_type": "badge", "reward_value": "Davetçi", "verification_type": "invite_tracker", "verification_required": True},
    {"id": 2, "title": "DM'den tanıtım mesajı gönder", "reward": "+15 XP", "reward_type": "xp", "reward_value": 15, "verification_type": "message_forward", "verification_required": True},
    {"id": 3, "title": "5 farklı grupta botu paylaş", "reward": "+20 XP", "reward_type": "xp", "reward_value": 20, "verification_type": "bot_mention", "verification_required": True},
    {"id": 4, "title": "Show linkini arkadaşlarına yolla", "reward": "+10 XP", "reward_type": "xp", "reward_value": 10, "verification_type": "deeplink_track", "verification_required": True},
    {"id": 5, "title": "Grubuna MiniApp linkini sabitle", "reward": "🎖️ Rozet", "reward_type": "badge", "reward_value": "VIP Tanıtıcı", "verification_type": "pin_check", "verification_required": True},
    {"id": 6, "title": "VIP tanıtım postunu 3 grupta paylaş", "reward": "+25 XP", "reward_type": "xp", "reward_value": 25, "verification_type": "post_share", "verification_required": True},
    {"id": 7, "title": "Görev çağrısını 10 kişiye gönder", "reward": "+30 XP", "reward_type": "xp", "reward_value": 30, "verification_type": "share_count", "verification_required": True},
    {"id": 8, "title": "Botu kullanan bir arkadaş davet et", "reward": "+10 XP", "reward_type": "xp", "reward_value": 10, "verification_type": "referral", "verification_required": True},
]

# Bekleyen görev doğrulamaları
PENDING_VERIFICATIONS = {}

@app.get("/tasks/list")
def get_tasks():
    return {"tasks": TASKS}

@app.post("/location/report")
async def report_location(req: Request):
    data = await req.json()
    print("📍 Konum bildirildi:", data)
    return {"status": "ok"}

@app.post("/task/complete")
async def complete_task(req: Request):
    data = await req.json()
    user_id = str(data.get("user_id"))
    task_id = data.get("task_id")
    verification_data = data.get("verification_data", {})
    
    if not user_id or task_id is None:
        return {"error": "user_id ve task_id gerekli", "status": "error"}
    
    # Görevi bul
    task = None
    for t in TASKS:
        if t["id"] == task_id:
            task = t
            break
    
    if not task:
        return {"error": "Görev bulunamadı", "status": "error"}
    
    # Kullanıcı profili
    if user_id not in users_db:
        users_db[user_id] = {"username": user_id, "xp": 0, "badges": [], "completed_tasks": [], "pending_tasks": []}
    
    user = users_db[user_id]
    
    # Görev zaten tamamlanmış mı kontrol et
    if task_id in user.get("completed_tasks", []):
        return {"message": "Bu görev zaten tamamlanmış", "status": "warning"}
    
    # Doğrulama gerekiyor mu kontrol et
    if task.get("verification_required", True):
        # Eğer bu görev zaten doğrulamayı bekliyor mu kontrol et
        pending_verification_key = f"{user_id}_{task_id}"
        
        if pending_verification_key in PENDING_VERIFICATIONS:
            pending_info = PENDING_VERIFICATIONS[pending_verification_key]
            
            # Eğer doğrulama gerçekleşmişse
            if pending_info.get("verified", False):
                # Görev tamamlandı olarak işaretle
                if "pending_tasks" not in user:
                    user["pending_tasks"] = []
                
                # Bekleyenlerden kaldır
                if task_id in user["pending_tasks"]:
                    user["pending_tasks"].remove(task_id)
                
                # Tamamlananlara ekle
                if "completed_tasks" not in user:
                    user["completed_tasks"] = []
                user["completed_tasks"].append(task_id)
                
                # Ödülü ver
                reward_message = award_reward(user, task)
                
                # Doğrulama kayıtlarından temizle
                del PENDING_VERIFICATIONS[pending_verification_key]
                
                print(f"✅ Görev tamamlandı ve doğrulandı: {data} Ödül: {reward_message}")
                return {"message": reward_message, "status": "ok", "user": user}
            else:
                # Doğrulama hala bekleniyor
                elapsed_time = time.time() - pending_info.get("request_time", 0)
                
                # Eğer doğrulama 5 dakikadan uzun süredir bekliyorsa, iptal et
                if elapsed_time > 300:  # 5 dakika (300 saniye)
                    del PENDING_VERIFICATIONS[pending_verification_key]
                    if task_id in user.get("pending_tasks", []):
                        user["pending_tasks"].remove(task_id)
                    return {"message": "Doğrulama zaman aşımına uğradı, lütfen tekrar deneyin", "status": "error"}
                
                return {"message": "Görevin doğrulanması bekleniyor", "status": "pending", "user": user}
        
        # Yeni bir doğrulama başlat
        PENDING_VERIFICATIONS[pending_verification_key] = {
            "user_id": user_id,
            "task_id": task_id,
            "verification_type": task.get("verification_type", "manual"),
            "verification_data": verification_data,
            "request_time": time.time(),
            "verified": False
        }
        
        # Kullanıcının bekleyen görevlerine ekle
        if "pending_tasks" not in user:
            user["pending_tasks"] = []
        if task_id not in user["pending_tasks"]:
            user["pending_tasks"].append(task_id)
        
        print(f"🔍 Görev doğrulama başlatıldı: {user_id} için {task_id} görevi")
        
        # DEV/TEST ortamında otomatik doğrulama (gerçek ortamda bu kaldırılacak)
        if task_id in [2, 4, 6]:  # Test için bazı görevleri otomatik doğrula
            PENDING_VERIFICATIONS[pending_verification_key]["verified"] = True
            return await complete_task(req)  # Tekrar kendimizi çağır
        
        return {
            "message": f"Görev doğrulanıyor. '{task['verification_type']}' türünde doğrulama gerekiyor.",
            "status": "pending",
            "verification_type": task.get("verification_type"),
            "user": user
        }
    else:
        # Doğrulama gerektirmeyen görevler için doğrudan tamamla
        if "completed_tasks" not in user:
            user["completed_tasks"] = []
        user["completed_tasks"].append(task_id)
        
        # Ödülü ver
        reward_message = award_reward(user, task)
        
        print(f"✅ Görev tamamlandı (doğrulama gerekmez): {data} Ödül: {reward_message}")
        return {"message": reward_message, "status": "ok", "user": user}

def award_reward(user, task):
    """Kullanıcıya ödül ver ve mesajı döndür"""
    reward_message = ""
    if task["reward_type"] == "xp":
        user["xp"] += task["reward_value"]
        reward_message = f"+{task['reward_value']} XP kazandın!"
    elif task["reward_type"] == "badge":
        if task["reward_value"] not in user["badges"]:
            user["badges"].append(task["reward_value"])
        reward_message = f"'{task['reward_value']}' rozetini kazandın!"
    return reward_message

@app.post("/admin/verify-task")
async def admin_verify_task(req: Request):
    """Admin tarafında görev doğrulama endpoint'i"""
    data = await req.json()
    user_id = str(data.get("user_id"))
    task_id = data.get("task_id")
    verified = data.get("verified", True)
    admin_key = data.get("admin_key")
    
    # Admin key kontrolü
    if admin_key != "your-secret-admin-key":  # Gerçek uygulamada daha güvenli bir yöntem kullanın
        return {"error": "Yetkisiz erişim", "status": "error"}
    
    pending_verification_key = f"{user_id}_{task_id}"
    
    if pending_verification_key not in PENDING_VERIFICATIONS:
        return {"error": "Bekleyen doğrulama bulunamadı", "status": "error"}
    
    # Doğrulama durumunu güncelle
    PENDING_VERIFICATIONS[pending_verification_key]["verified"] = verified
    
    return {"message": "Görev doğrulama durumu güncellendi", "status": "ok"}

@app.get("/admin/pending-verifications")
async def get_pending_verifications(req: Request):
    """Admin tarafında bekleyen doğrulamaları listele"""
    admin_key = req.query_params.get("admin_key")
    
    # Admin key kontrolü
    if admin_key != "your-secret-admin-key":  # Gerçek uygulamada daha güvenli bir yöntem kullanın
        return {"error": "Yetkisiz erişim", "status": "error"}
    
    return {"pending_verifications": PENDING_VERIFICATIONS}