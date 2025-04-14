import { useEffect, useState } from "react";

export default function App() {
  const [uid, setUid] = useState("demo123"); // fallback UID
  const [telegramUserData, setTelegramUserData] = useState(null);
  const [viralTasks, setViralTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [userProfile, setUserProfile] = useState(null);
  const [activeTab, setActiveTab] = useState("tasks"); // "tasks" veya "profile"
  const [pendingTasks, setPendingTasks] = useState([]);
  
  // API'den görevleri çek
  const fetchTasks = async () => {
    try {
      setLoading(true);
      const response = await fetch(import.meta.env.VITE_API_URL + "/tasks/list");
      const data = await response.json();
      setViralTasks(data.tasks || []);
      setLoading(false);
    } catch (error) {
      console.error("Görevler çekilemedi:", error);
      // Hataya karşılık fallback veriler
      setViralTasks([
        {'id': 1, 'title': 'Yeni üye davet et', 'reward': '🎖️ Rozet'}, 
        {'id': 2, 'title': "DM'den tanıtım mesajı gönder", 'reward': '+15 XP'}, 
        {'id': 3, 'title': '5 farklı grupta botu paylaş', 'reward': '+20 XP'}
      ]);
      setLoading(false);
    }
  };
  
  // Kullanıcı profilini çek
  const fetchUserProfile = async () => {
    try {
      const response = await fetch(import.meta.env.VITE_API_URL + "/profile/" + uid);
      const data = await response.json();
      setUserProfile(data);
      
      // Bekleyen görevleri ayarla
      if (data.pending_tasks) {
        setPendingTasks(data.pending_tasks);
      }
    } catch (error) {
      console.error("Profil çekilemedi:", error);
    }
  };
  
  // Görev tamamla fonksiyonu 
  const completeTask = async (taskId) => {
    try {
      // Kullanıcı doğrulama verilerini hazırla
      const verificationData = {};
      
      // Görev tipine göre ek veriler ekle
      const task = viralTasks.find(t => t.id === taskId);
      if (task) {
        if (task.verification_type === "message_forward") {
          verificationData.source = "dm"; 
          verificationData.timestamp = Date.now();
        } else if (task.verification_type === "bot_mention") {
          verificationData.username = telegramUserData?.username || uid;
        }
      }
      
      const response = await fetch(import.meta.env.VITE_API_URL + "/task/complete", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          user_id: uid,
          task_id: taskId,
          verification_data: verificationData
        })
      });
      const data = await response.json();
      
      // Başarılı tamamlama
      if (data.status === "ok") {
        alert("🎉 " + data.message);
        // Kullanıcı bilgilerini güncelle
        if (data.user) {
          setUserProfile(data.user);
          if (data.user.pending_tasks) {
            setPendingTasks(data.user.pending_tasks);
          }
        } else {
          fetchUserProfile(); // Kullanıcı bilgileri dönmediyse tekrar çek
        }
      } 
      // Bekleyen doğrulama
      else if (data.status === "pending") {
        alert("⏳ " + data.message);
        // Bekleyen görevlere ekle
        if (data.user && data.user.pending_tasks) {
          setPendingTasks(data.user.pending_tasks);
        } else if (!pendingTasks.includes(taskId)) {
          setPendingTasks([...pendingTasks, taskId]);
        }
        
        // Kullanıcı bilgilerini güncelle
        if (data.user) {
          setUserProfile(data.user);
        }
      }
      // Uyarı mesajı (zaten tamamlanmış vb.)
      else if (data.status === "warning") {
        alert("⚠️ " + data.message);
      }
      // Hata mesajı
      else {
        alert("❌ Hata: " + (data.error || "Bilinmeyen bir hata oluştu"));
      }
    } catch (error) {
      console.error("Görev tamamlanamadı:", error);
      alert("❌ Bağlantı hatası: Sunucuya erişilemiyor.");
    }
  };
  
  useEffect(() => {
    if (typeof window !== "undefined" && window.Telegram && window.Telegram?.WebApp) {

      const tg = window.Telegram.WebApp;
      tg.ready();
      tg.expand();

      const user = window.Telegram.WebApp.initDataUnsafe?.user;
      if (user) {
        console.log("✅ Telegram UID:", user.id);
        setUid(user.id.toString());
      } else {
        console.warn("⚠️ Telegram initData gelmedi. Demo UID kullanılacak.");
      }


  
      const telegramUser = tg.initDataUnsafe?.user;
     
      if (telegramUser) {
        setTelegramUserData(telegramUser);
        setUid(telegramUser.id.toString()); // UID string olarak kullanılır
      } else {
        console.warn("⚠️ Telegram initData gelmedi, demo123 kullanılacak.");
      }
      // Konumu backend'e gönder
      if ("geolocation" in navigator && telegramUser?.id) {
        navigator.geolocation.getCurrentPosition(
          (pos) => {
            fetch(import.meta.env.VITE_API_URL + "/location/report", {
              method: "POST",
              headers: {
                "Content-Type": "application/json"
              },
              body: JSON.stringify({
                user_id: telegramUser.id,
                username: telegramUser.username,
                latitude: pos.coords.latitude,
                longitude: pos.coords.longitude
              })
            }).then(() => {
              console.log("📍 Konum başarıyla gönderildi.");
            });
          },
          (err) => console.warn("📍 Konum alınamadı:", err)
        );
      }
    } else {
      console.warn("🚫 Telegram WebApp context not available (muhtemelen tarayıcıda test ediyorsun)");
    }
    
    // Görevleri ve kullanıcı profilini çek
    fetchTasks();
    fetchUserProfile();
  }, [uid]);
  
  // Tab değiştirme işlevi
  const toggleTab = (tab) => {
    setActiveTab(tab);
    if (tab === "profile") {
      fetchUserProfile(); // Profil sekmesine geçince profil bilgilerini güncelle
    }
  };
  
  // Görev durumunu belirle (tamamlanmış, bekliyor, yapılmadı)
  const getTaskStatus = (taskId) => {
    if (!userProfile) return "incomplete";
    
    if (userProfile.completed_tasks?.includes(taskId)) {
      return "completed";
    }
    
    if (pendingTasks.includes(taskId)) {
      return "pending";
    }
    
    return "incomplete";
  };
  
  return (
    <main className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-gray-800 text-white flex flex-col items-center p-6 font-sans overflow-hidden">
      <h1 className="text-4xl font-bold mb-4 text-center text-gradient bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 bg-clip-text text-transparent animate-fade-in">
        🚀 OnlyVips Görev Merkezi
      </h1>

      {/* Navigasyon tabları */}
      <div className="flex mb-6 bg-white/5 backdrop-blur-lg rounded-full p-1 w-full max-w-md">
        <button 
          className={`flex-1 py-2 px-4 rounded-full text-center transition-all 
            ${activeTab === "tasks" ? "bg-gradient-to-r from-pink-500 to-indigo-500 text-white" : "text-gray-100 hover:text-white bg-black/20"}`}
          onClick={() => toggleTab("tasks")}
        >
          📋 Görevler
        </button>
        <button 
          className={`flex-1 py-2 px-4 rounded-full text-center transition-all 
            ${activeTab === "profile" ? "bg-gradient-to-r from-pink-500 to-indigo-500 text-white" : "text-gray-100 hover:text-white bg-black/20"}`}
          onClick={() => toggleTab("profile")}
        >
          👤 Profilim
        </button>
      </div>

      {/* Görevler Tab */}
      {activeTab === "tasks" && (
        <div className="w-full max-w-md bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6 shadow-xl animate-fade-in-up">
          <h2 className="text-xl font-semibold mb-4 text-white flex items-center gap-2">
            📋 Viral Görevler
          </h2>
          {loading ? (
            <div className="text-center py-10">Görevler yükleniyor...</div>
          ) : (
            <div className="space-y-3">
              {viralTasks.map((task, idx) => {
                const taskStatus = getTaskStatus(task.id);
                
                return (
                  <div
                    key={idx}
                    className={`bg-black/30 border border-white/10 rounded-xl p-4 shadow-sm animate-fade-in hover:scale-[1.01] transition-all duration-300 cursor-pointer relative ${
                      taskStatus === "completed" ? "border-emerald-500/50" : 
                      taskStatus === "pending" ? "border-yellow-500/50" : ""
                    }`}
                    onClick={() => completeTask(task.id)}
                  >
                    <div className="text-white font-semibold">📌 {task.title}</div>
                    <div className="text-sm text-emerald-400">Ödül: {task.reward}</div>
                    
                    {taskStatus === "incomplete" && (
                      <div className="text-xs text-gray-400 mt-2">Tamamlamak için tıkla 👆</div>
                    )}
                    
                    {/* Tamamlandı işareti */}
                    {taskStatus === "completed" && (
                      <div className="absolute top-2 right-2 bg-emerald-500 text-xs text-white px-2 py-1 rounded-full">
                        ✓ Tamamlandı
                      </div>
                    )}
                    
                    {/* Beklemede işareti */}
                    {taskStatus === "pending" && (
                      <div className="absolute top-2 right-2 bg-yellow-500 text-xs text-white px-2 py-1 rounded-full flex items-center gap-1">
                        <span className="animate-pulse">⌛</span> Doğrulanıyor
                      </div>
                    )}
                    
                    {/* Doğrulama bilgisi */}
                    {task.verification_required && taskStatus === "incomplete" && (
                      <div className="mt-2 text-xs text-gray-500 flex items-center gap-1">
                        <span>🔍</span> Doğrulama gerekir: {getVerificationText(task.verification_type)}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Profil Tab */}
      {activeTab === "profile" && (
        <div className="w-full max-w-md bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6 shadow-xl animate-fade-in-up">
          <h2 className="text-xl font-semibold mb-6 text-white flex items-center gap-2">
            👤 Kullanıcı Profili
          </h2>
          
          {!userProfile ? (
            <div className="text-center py-10">Profil yükleniyor...</div>
          ) : (
            <div className="space-y-6">
              {/* Kullanıcı bilgileri */}
              <div className="flex items-center gap-4">
                <div className="bg-gradient-to-br from-pink-500 to-indigo-500 w-16 h-16 rounded-full flex items-center justify-center text-2xl">
                  {userProfile.username?.charAt(0)?.toUpperCase() || "?"}
                </div>
                <div>
                  <h3 className="text-lg font-semibold">{userProfile.username || uid}</h3>
                  <p className="text-gray-300">ID: {uid}</p>
                </div>
              </div>
              
              {/* XP ve Seviye */}
              <div className="bg-black/30 border border-white/10 rounded-xl p-4">
                <h3 className="text-md font-medium mb-2">🌟 XP ve Seviye</h3>
                <div className="flex items-center gap-3">
                  <div className="text-2xl font-bold text-emerald-400">{userProfile.xp || 0}</div>
                  <div className="text-sm">XP</div>
                  <div className="h-6 w-px bg-white/20 mx-2"></div>
                  <div className="text-2xl font-bold text-yellow-400">{Math.floor((userProfile.xp || 0) / 100) + 1}</div>
                  <div className="text-sm">Seviye</div>
                </div>
                
                {/* İlerleme çubuğu */}
                <div className="mt-3 h-2 bg-gray-700 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-emerald-400 to-emerald-600"
                    style={{width: `${(userProfile.xp % 100)}%`}}
                  ></div>
                </div>
                <div className="mt-1 text-xs text-gray-400">
                  Bir sonraki seviyeye: {100 - (userProfile.xp % 100)} XP
                </div>
              </div>
              
              {/* Rozetler */}
              <div className="bg-black/30 border border-white/10 rounded-xl p-4">
                <h3 className="text-md font-medium mb-2">🎖️ Rozetlerim</h3>
                
                {userProfile.badges && userProfile.badges.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {userProfile.badges.map((badge, idx) => (
                      <div key={idx} className="bg-gradient-to-r from-amber-500 to-yellow-600 text-white text-xs px-3 py-1 rounded-full">
                        {badge}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-gray-400 text-sm">Henüz rozet kazanmadınız.</div>
                )}
              </div>
              
              {/* Bekleyen Görevler */}
              {pendingTasks.length > 0 && (
                <div className="bg-black/30 border border-yellow-500/20 rounded-xl p-4">
                  <h3 className="text-md font-medium mb-2">⌛ Bekleyen Görevler</h3>
                  <div className="space-y-2">
                    {pendingTasks.map((taskId) => {
                      const task = viralTasks.find(t => t.id === taskId);
                      return task ? (
                        <div key={taskId} className="bg-black/20 rounded p-2 text-sm">
                          <div className="font-medium">{task.title}</div>
                          <div className="text-xs text-yellow-400">Doğrulama bekleniyor...</div>
                        </div>
                      ) : null;
                    })}
                  </div>
                  <div className="mt-3 text-xs text-gray-400">
                    Görevlerin doğrulanmasını bekleyin. Bazı görevler birkaç dakika içinde otomatik doğrulanır.
                  </div>
                </div>
              )}
              
              {/* Tamamlanan görevler istatistiği */}
              <div className="bg-black/30 border border-white/10 rounded-xl p-4">
                <h3 className="text-md font-medium mb-2">📊 İstatistikler</h3>
                <div className="flex gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-400">{userProfile.completed_tasks?.length || 0}</div>
                    <div className="text-xs text-gray-400">Tamamlanan</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-yellow-400">{pendingTasks.length}</div>
                    <div className="text-xs text-gray-400">Bekleyen</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-400">{viralTasks.length}</div>
                    <div className="text-xs text-gray-400">Toplam Görev</div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      <footer className="mt-6 text-xs text-gray-500 text-center animate-fade-in-down">
        Görevleri tamamla, XP ve rozet kazan 💫<br />
        Star'lar sadece satın alınabilir ve VIP özelliklerde kullanılır.
      </footer>
    </main>
  );
}

// Doğrulama türünü anlaşılır metne çevir
function getVerificationText(verificationType) {
  const texts = {
    "invite_tracker": "Davet bağlantısı takibi",
    "message_forward": "Mesaj yönlendirme kontrolü",
    "bot_mention": "Bot etiketleme kontrolü",
    "deeplink_track": "Link tıklanma takibi",
    "pin_check": "Sabitlenmiş mesaj kontrolü",
    "post_share": "Gönderi paylaşım kontrolü",
    "share_count": "Paylaşım sayısı kontrolü",
    "referral": "Referans bağlantısı takibi"
  };
  
  return texts[verificationType] || "Manuel doğrulama";
}
