from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS ayarı
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sahte görev verisi
TASKS = [
    {"id": 1, "title": "Yeni üye davet et", "reward": "🎖️ Rozet"},
    {"id": 2, "title": "DM'den tanıtım mesajı gönder", "reward": "+15 XP"},
    {"id": 3, "title": "5 farklı grupta botu paylaş", "reward": "+20 XP"},
    {"id": 4, "title": "Show linkini arkadaşlarına yolla", "reward": "+10 XP"},
    {"id": 5, "title": "Grubuna MiniApp linkini sabitle", "reward": "🎖️ Rozet"},
    {"id": 6, "title": "VIP tanıtım postunu 3 grupta paylaş", "reward": "+25 XP"},
    {"id": 7, "title": "Görev çağrısını 10 kişiye gönder", "reward": "+30 XP"},
    {"id": 8, "title": "Botu kullanan bir arkadaş davet et", "reward": "+10 XP"},
]

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
    print("✅ Görev tamamlandı:", data)
    return {"message": "XP veya rozet verildi", "status": "ok"}