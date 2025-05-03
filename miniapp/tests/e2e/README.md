# OnlyVips End-to-End (E2E) Testleri

Bu klasör, OnlyVips MiniApp için Playwright kullanılarak yazılmış end-to-end testleri içerir.

## 📋 Test Senaryoları

Aşağıdaki özellikler test kapsamındadır:

1. **Ayarlar Sayfası**
   - Ayarlar formunu doldurma ve kaydetme 
   - Kayıt sonrası verilerin kalıcılığını doğrulama

2. **Mesaj İşlemleri**
   - Yeni mesaj oluşturma ve gönderme
   - Dashboard'da mesajları listeleme
   - Mesaj güncelleme
   - Mesaj silme

3. **Log Yönetimi**
   - Log sayfasının yüklenmesi
   - Filtreleme ve sıralama özellikleri
   - Log detaylarını görüntüleme

## 🛠️ Kurulum ve Çalıştırma

Testleri yerel ortamınızda çalıştırmak için:

```bash
# Bağımlılıkları yükle
npm install

# Playwright tarayıcılarını yükle
npx playwright install

# Tüm testleri çalıştır
npm run test:e2e

# Sadece belirli bir test dosyasını çalıştır
npx playwright test tests/settings.spec.ts

# Debug modunda çalıştır
npm run test:e2e:debug
```

## 📊 CI/CD Entegrasyonu

E2E testleri, GitHub Actions workflow'ları aracılığıyla PR kontrollerinde ve CI pipeline'da otomatik olarak çalıştırılır. Test sonuçları GitHub Actions üzerinde artifact olarak kaydedilir ve incelenebilir.

## 🧪 Test Yapısı

- `playwright.config.ts`: Test çalıştırma ortamı yapılandırması
- `tests/*.spec.ts`: Test senaryoları
- `.auth/`: Oturum bilgileri (gitignore'da listelenir) 