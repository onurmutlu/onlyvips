import { useEffect } from "react";

export default function Home() {
  useEffect(() => {
    if (typeof window !== "undefined" && window.Telegram?.WebApp) {
      window.Telegram.WebApp.ready();
    }
  }, []);

  const handleStart = () => {
    if (typeof window !== "undefined" && window.Telegram?.WebApp) {
      window.Telegram.WebApp.sendData("gorev-baslat");
    }
  };

  return (
    <main className="relative min-h-screen bg-gradient-to-br from-black via-gray-900 to-gray-800 text-white flex flex-col items-center justify-center p-4 sm:p-6 font-sans overflow-hidden">
      <div class="absolute inset-0 z-0 animate-pulse pointer-events-none">
        <div class="absolute top-10 left-10 w-2 h-2 bg-yellow-400 rounded-full blur-md animate-ping"></div>
        <div class="absolute bottom-20 right-16 w-3 h-3 bg-pink-400 rounded-full blur-sm animate-ping"></div>
        <div class="absolute top-1/2 left-1/2 w-1.5 h-1.5 bg-white rounded-full blur-md animate-ping"></div>
      </div>

      <h1 class="z-10 text-4xl font-bold mb-6 tracking-wide text-gradient bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 bg-clip-text text-transparent animate-fade-in text-center">
        ✨ OnlyVips MiniApp ✨
      </h1>

      <div class="z-10 mb-4 flex space-x-2 animate-fade-in-up">
        {[1, 2, 3].map((n) => (
          <img
            key={n}
            src={`https://i.pravatar.cc/100?img=${n + 20}`}
            alt="avatar"
            class="w-10 h-10 rounded-full border-2 border-pink-500 shadow-md"
          />
        ))}
      </div>

      <div class="z-10 w-full max-w-md backdrop-blur-sm bg-white/5 border border-white/10 rounded-2xl shadow-xl p-6 animate-fade-in-up">
        <h2 class="text-2xl font-semibold mb-4 text-white flex items-center gap-2">
          <img src="/badge.png" class="w-6 h-6" alt="Rozet" /> Stars Görev Sistemi
        </h2>

        <div class="space-y-4 mb-6">
          {["DM Gönder", "Yeni Üye Davet Et", "Yorum Yap"].map((task, index) => (
            <div
              key={index}
              class="bg-black/30 border border-white/10 rounded-xl p-4 shadow-md animate-fade-in hover:scale-105 transition-all duration-300"
            >
              <div class="text-white font-semibold">📌 {task}</div>
              <div class="text-sm text-gray-400">Bu görevi tamamla ve 5 Stars kazan ✨</div>
            </div>
          ))}
        </div>

        <button
          onClick={handleStart}
          class="w-full text-lg bg-gradient-to-r from-pink-500 to-purple-600 hover:brightness-110 text-white font-bold py-3 px-5 rounded-xl shadow-md transition-all duration-300 transform hover:scale-105"
        >
          🚀 Göreve Başla
        </button>
      </div>

      <footer class="z-10 mt-8 text-xs text-gray-400 animate-fade-in-down">
        @OnlyVips | MiniApp Arayüzü 💫
      </footer>
    </main>
  );
}
