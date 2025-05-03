# OnlyVips CI/CD Yapılandırması

Bu belge, OnlyVips monorepo'sunun CI/CD (Sürekli Entegrasyon/Sürekli Dağıtım) yapılandırmasını açıklar.

## 🚀 Genel Bakış

OnlyVips projesi için CI/CD pipeline'ı aşağıdaki bileşenlerden oluşur:

1. **Pull Request Kontrolleri**: Her PR'ın kalite standartlarını karşıladığını doğrulama
2. **CI Pipeline**: Ana dallara (main, develop) push'lar için derleme ve test
3. **CD Pipeline**: Main dalına başarılı push'lar için otomatik dağıtım

## 🔄 PR Kontrolleri

Her pull request'in aşağıdaki koşulları karşılaması gerekir:

- Linter kontrollerinden geçmesi
- Test kapsamının en az %80 olması
- Tüm testlerin başarılı olması

PR kontrollerini değerlendirmek için `.github/workflows/pr-check.yml` workflow'u kullanılır.

## 🔧 CI Pipeline

`ci-cd.yml` workflow'u, üç paralel işi çalıştırır:

1. **Frontend İşi**:
   - Yarn ile bağımlılıkları yükler
   - Linter kontrolü yapar
   - Miniapp ve Showcu Panel için build işlemi gerçekleştirir
   - Test kapsamını doğrular

2. **Backend İşi**:
   - Poetry ile Python bağımlılıklarını yükler
   - Ruff ile kod kalitesini kontrol eder
   - API testlerini çalıştırır
   - Test kapsamını doğrular
   - Main dalına push'larda Docker image'ını oluşturur ve Docker Hub'a gönderir

3. **Bot İşi**:
   - Poetry ile Python bağımlılıklarını yükler
   - Testleri çalıştırır ve kapsamı doğrular
   - Main dalına push'larda GitHub Container Registry'ye image gönderir

## 📦 CD Pipeline

CI pipeline'ı başarılı olduğunda ve main dalı üzerine push yapıldığında, CD pipeline'ı şunları yapar:

1. **Frontend Dağıtımı**:
   - Vercel CLI ile miniapp ve showcu-panel'i dağıtır

2. **Backend Dağıtımı**:
   - Docker Hub'a gönderilen image'lar otomatik olarak sunuculara dağıtılır

## 🔐 Ortam Değişkenleri ve Sırlar

Tüm gizli değerler ve ortam değişkenleri GitHub Secrets olarak saklanır ve workflow dosyalarında referans alınır:

```yaml
env:
  VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
  MONGODB_URI: ${{ secrets.MONGODB_URI }}
  JWT_SECRET: ${{ secrets.JWT_SECRET }}
  # ... diğer değişkenler
```

## 📊 Test Kapsamı Kontrolü

Test kapsamını değerlendirmek için şu adımlar izlenir:

1. Jest ile frontend testleri ve kapsamı
2. Pytest ile backend ve bot testleri ve kapsamı
3. %80'in altında kapsam varsa PR reddedilir

```bash
# Frontend kapsamı örneği
yarn workspace miniapp test --coverage

# Backend kapsamı örneği
poetry run pytest --cov=app --cov-report=xml
```

## 🔄 Dependabot Entegrasyonu

Bağımlılıkları güncel tutmak için Dependabot kullanılır:

- Her hafta bağımlılık güncellemeleri için PR'lar oluşturur
- CI kontrollerini otomatik olarak çalıştırır
- Başarılı olanlar için onay gerektirmez

## 📜 CI/CD Kontrol Listesi

PR ve merge işlemleri için kontrol listesi:

- [ ] Linter kontrollerinden geçiyor mu?
- [ ] Test kapsamı %80'in üzerinde mi?
- [ ] Tüm testler başarılı mı?
- [ ] Değişiklikler belgelenmiş mi?
- [ ] Security.md'de gerekli güncellemeler yapılmış mı?

## 🛠️ CI/CD Sorun Giderme

Sık karşılaşılan sorunların çözümleri:

1. **Linter Hataları**: Yerel olarak `yarn lint` veya `ruff check .` çalıştırın
2. **Test Hataları**: Tek bir test çalıştırarak hataları izole edin
3. **Coverage Sorunları**: Yeterli test eklendiğinden emin olun
4. **Docker Build Hataları**: Dockerfile'ları yerel olarak test edin

---

© 2024 SiyahKare. Tüm hakları saklıdır. 