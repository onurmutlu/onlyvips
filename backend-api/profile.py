from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()

users_db = {
    "demo123": {"username": "demo123", "xp": 85, "badges": ["Rozet-1", "Rozet-2"], "completed_tasks": [1, 3]},
    "onlyvips": {"username": "onlyvips", "xp": 30, "badges": [], "completed_tasks": []}
}

@router.get("/profile/{user_id}")
async def get_profile(user_id: str):
    user = users_db.get(user_id)
    if not user:
        # Kullanıcı yoksa yeni oluştur
        users_db[user_id] = {"username": user_id, "xp": 0, "badges": [], "completed_tasks": []}
        return users_db[user_id]
    return user

@router.post("/profile/add-xp")
async def add_xp(req: Request):
    data = await req.json()
    user_id = str(data.get("user_id"))
    xp_amount = data.get("xp", 0)
    
    if not user_id:
        return JSONResponse(status_code=400, content={"error": "user_id gerekli"})
        
    # Kullanıcı yoksa oluştur
    if user_id not in users_db:
        users_db[user_id] = {"username": user_id, "xp": 0, "badges": [], "completed_tasks": []}
    
    users_db[user_id]["xp"] += xp_amount
    return {"status": "ok", "new_xp": users_db[user_id]["xp"]}

@router.post("/profile/add-badge")
async def add_badge(req: Request):
    data = await req.json()
    user_id = str(data.get("user_id"))
    badge = data.get("badge")
    
    if not user_id or not badge:
        return JSONResponse(status_code=400, content={"error": "user_id ve badge gerekli"})
        
    # Kullanıcı yoksa oluştur
    if user_id not in users_db:
        users_db[user_id] = {"username": user_id, "xp": 0, "badges": [], "completed_tasks": []}
    
    if badge not in users_db[user_id]["badges"]:
        users_db[user_id]["badges"].append(badge)
        
    return {"status": "ok", "badges": users_db[user_id]["badges"]}

@router.get("/profile/completed-tasks/{user_id}")
async def get_completed_tasks(user_id: str):
    user = users_db.get(user_id)
    if not user:
        return JSONResponse(status_code=404, content={"error": "Kullanıcı bulunamadı"})
    return {"completed_tasks": user.get("completed_tasks", [])}
