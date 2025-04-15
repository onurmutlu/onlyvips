
# Flirt-Bot: OnlyVips Görev Doğrulama ve Yardımcı Botu

Flirt-Bot, OnlyVips platformu için görev doğrulama ve kullanıcı etkileşim botu olarak hizmet veren, Telethon tabanlı bir Telegram botudur. Hem bot tokeni ile hem de bir kullanıcı hesabı ile çalışabilir.

## 🌟 Özellikler

- **Görev Doğrulama**: Kullanıcıların tamamladığı görevleri otomatik olarak doğrular
- **Görev Dağıtma**: Kullanıcılara yeni görevler atayabilir
- **MiniApp Entegrasyonu**: Telegram MiniApp ile tam entegrasyon
- **GPT Entegrasyonu**: Flört tavsiyeleri ve sosyal ipuçları için OpenAI GPT desteği
- **Kullanıcı Profili**: Kullanıcı XP, rozetler ve görevleri görüntüleme
- **Günlük Görevler**: Kullanıcıya günlük görevler verebilme
- **Çeşitli Komutlar**: Yardım, profil, flört ipuçları vb. komutlar
- **GPT Kullanım Limitlemesi**: Maliyet optimizasyonu için akıllı kullanım sınırlamaları

## 🚀 Kurulum

1. Python 3.8+ yüklü olmalıdır

2. Bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

3. Örnek `.env` dosyasını kopyalayın:
   ```bash
   cp .env.example .env
   ```

4. `.env` dosyasını düzenleyin ve gerekli bilgileri girin:
   ```
   API_ID=your_telegram_api_id
   API_HASH=your_telegram_api_hash
   BOT_TOKEN=your_telegram_bot_token
   SESSION_STRING=optional_user_account_session_string
   BACKEND_API_URL=https://api.onlyvips.com
   OPENAI_API_KEY=your_openai_api_key
   OPENAI_MODEL=gpt-3.5-turbo-instruct
   GPT_MAX_USAGE_DAY=50
   GPT_MAX_TOKENS=250
   ```
   
   - Telegram API ID ve Hash: https://my.telegram.org/apps adresinden alabilirsiniz
   - Bot Token: @BotFather'dan oluşturun
   - (İsteğe bağlı ama önerilen) SESSION_STRING: Tüm mesajları görebilmek için kullanıcı hesabı session string'i
   - BackendAPI URL: Backend API'nizin URL'i
   - OpenAI API Key: Flört asistanı için (opsiyonel)

5. Eğer bir kullanıcı hesabı oturumu kullanmak istiyorsanız, session string'i oluşturun:
   ```bash
   python session_generator.py
   ```
   ve sonucu `.env` dosyasına kopyalayın.

## 💻 Çalıştırma

Botu başlatmak için:
```bash
python bot_listener.py
```

Üretim ortamında sürekli çalışma için supervisor yapılandırması:
```
[program:onlyvips-bot]
command=/path/to/venv/bin/python /path/to/flirt-bot/bot_listener.py
directory=/path/to/flirt-bot
autostart=true
autorestart=true
stderr_logfile=/var/log/onlyvips-bot.err.log
stdout_logfile=/var/log/onlyvips-bot.out.log
```

## 🤖 Bot Komutları

### Kullanıcı Komutları
- `/start` - Botu başlatır ve tanıtım mesajı gönderir
- `/help` veya `/yardim` - Yardım menüsünü gösterir
- `/gorev` - Yeni bir görev atar
- `/gorevlerim` - Tüm görevlerini görüntüle
- `/gunluk` - Günlük görev al
- `/profil` - Kullanıcı profilini gösterir
- `/flirt` - Flört koçu modunu başlatır veya rastgele bir flört ipucu verir
- `/agent [soru]` - Flört asistanı ile konuş
- `/flortcoach [soru]` - Flört koçundan tavsiye al
- `/rozet` - Kazanılan rozetleri gösterir
- `/match` - Benzer ilgi alanlarına sahip kişileri bul (yakında)
- `/miniapp` - MiniApp'e ulaşmak için buton gönderir
- `/tamamla [görev_id]` - Belirli bir görevi manuel olarak tamamlamak için

### Admin Komutları
- `/verify [user_id] [task_id]` - Belirli bir görevi manuel olarak doğrula (sadece yetkili adminler için)

## 📊 Görev Tipleri

Bot aşağıdaki tür görevleri otomatik olarak doğrulayabilir:

- `BotMentionTask` - Grup içinde botu etiketleme
- `ChannelJoinTask` - Kanala katılma görevi
- `GroupJoinTask` - Gruba katılma görevi
- `ForwardMessageTask` - Mesaj yönlendirme görevi
- `PostShareTask` - Gönderi paylaşma görevi
- `DeeplinkTrackTask` - Link paylaşma görevi
- `PinCheckTask` - Mesaj sabitleme görevi
- `MessageTask` - Mesaj gönderme görevi
- `ReferralTask` - Yeni üye daveti
- `InviteTrackerTask` - Kullanıcı davet etme görevi
- `ShareCountTask` - Belirli sayıda paylaşım yapma görevi

## 🔄 MiniApp Entegrasyonu

Bot, Telegram MiniApp ile tam entegrasyon içerir:

- **Otomatik Yönlendirme**: Görevler tamamlandığında kullanıcıya MiniApp butonu gönderilir
- **Kullanıcı Tanıma**: MiniApp'e geçişte kullanıcı kimliği otomatik olarak aktarılır
- **Çift Yönlü Doğrulama**: MiniApp veya bot üzerinden tamamlanan görevler her iki platformda da güncellenir
- **Kolay Erişim**: `/miniapp` komutu ile kullanıcılara doğrudan MiniApp erişimi sağlanır

## 📱 Backend API Entegrasyonu

Bot, OnlyVips Backend API ile entegre çalışır:

- **Profil Senkronizasyonu**: Kullanıcı profillerini otomatik olarak senkronize eder
- **Görev Takibi**: Tamamlanan ve bekleyen görevleri takip eder
- **Ödül Sistemi**: XP ve rozet kazanımlarını yönetir
- **Otomatik Doğrulama**: Görevleri API aracılığıyla doğrular

## 💰 GPT Kullanım Limitleri ve Maliyet Optimizasyonu

Bot, GPT çağrılarını `GPT_MAX_USAGE_DAY` değeri ile günlük olarak sınırlar ve her yanıt için `GPT_MAX_TOKENS` değeri kadar token kullanır. Bu limitler `.env` dosyasından ayarlanabilir.

Bot, GPT entegrasyonunu optimum şekilde kullanır:

- **Akıllı Kullanım**: Sadece gerektiğinde GPT API'si kullanılır
- **Hazır Cevaplar**: Yaygın sorular için hazır cevaplar kullanılarak API maliyeti azaltılır
- **Konu Analizi**: Mesaj içeriğine göre en uygun cevap tür ve yöntemi seçilir
- **Kullanım Limiti**: Kullanıcı başına günlük API kullanımı kontrol edilir
- **Daha Ucuz Model**: Maliyet düşürmek için `gpt-3.5-turbo-instruct` gibi daha ekonomik modeller kullanılır
- **Token Sınırlaması**: Yanıt başına token sayısı sınırlandırılmıştır

## 📁 Proje Yapısı

```
flirt-bot/
├── src/
│   ├── tasks/                 # Görev tipleri
│   │   ├── base_task.py       # Temel görev sınıfı
│   │   ├── task_factory.py    # Görev oluşturucu
│   │   └── task_types/        # Farklı görev tipleri
│   ├── utils/                 # Yardımcı fonksiyonlar
│   └── verification/          # Doğrulama altyapısı
├── data/
│   ├── tasks.json             # Görev şablonları
│   ├── users.json             # Kullanıcı verileri
│   └── flirt_tips.json        # Hazır flört ipuçları
├── bot_listener.py            # Ana bot dosyası
├── requirements.txt           # Proje bağımlılıkları
├── session_generator.py       # Session string oluşturucu
└── README.md                  # Bu dosya
```

## 🔧 Özelleştirme

- **Sistem Mesajları**: Bot mesajlarını `bot_listener.py` dosyasında ilgili fonksiyonlarda değiştirebilirsiniz
- **Görev Tipleri**: Yeni görev doğrulama türleri eklemek için `VERIFICATION_TYPES` sözlüğüne ekleyin
- **GPT Modeli**: OpenAI modeli veya sistem mesajlarını `/agent` ve `/flortcoach` fonksiyonlarında değiştirebilirsiniz
- **Günlük Görevler**: Günlük görevleri `daily_tasks` listesinde düzenleyebilirsiniz

## 🔍 Sorun Giderme ve Hata Ayıklama

- **"API hatası"**: API_ID, API_HASH ve BOT_TOKEN değerlerinin doğru olduğundan emin olun
- **"GPT entegrasyonu kullanılamıyor"**: OPENAI_API_KEY değerini kontrol edin
- **"Görev doğrulanamadı"**: SESSION_STRING'in geçerli olduğundan emin olun
- **"Bot mesajları görmüyor"**: Kullanıcı hesabına ihtiyaç duyar, SESSION_STRING'i kontrol edin
- **"MiniApp butonu görüntülenmiyor"**: Bot'un mesaj butonları gönderme iznini kontrol edin

Botun çalışması sırasında karşılaşılan sorunlar için logları kontrol edin:
```bash
tail -f logs/bot.log
```

## 📋 Deployment Kontrol Listesi

- [ ] Telegram API kimlik bilgileri doğru girildi
- [ ] OpenAI API anahtarı çalışıyor
- [ ] .env yapılandırması tamamlandı
- [ ] Görev tipleri test edildi
- [ ] GPT limitlemesi kontrol edildi
- [ ] Veritabanı yedekleme yapılandırıldı
- [ ] Supervisor servis yapılandırması tamamlandı
- [ ] Hata loglama sistemi aktif

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Daha fazla bilgi için `LICENSE` dosyasına bakın.

## 🔗 İlgili Projeler

- [OnlyVips MiniApp](https://github.com/yourusername/onlyvips-miniapp) - Telegram MiniApp
- [OnlyVips Backend](https://github.com/yourusername/onlyvips-backend) - Backend API
- [OnlyVips Showcu Panel](https://github.com/yourusername/onlyvips-showcu-panel) - İçerik Üretici Paneli
