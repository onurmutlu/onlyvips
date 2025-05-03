# OnlyVips Güvenlik Politikası

Bu belge, OnlyVips projesi için güvenlik politikalarını ve prosedürlerini açıklar.

## 🔐 Secret Yönetimi

OnlyVips projesi artık aşağıdaki secret yönetimi çözümlerini kullanmaktadır:

- **HashiCorp Vault**: Üretim ortamında birincil secret depolama çözümü
- **AWS SSM Parameter Store**: AWS ortamında alternatif secret yönetimi çözümü
- **GitHub Secrets**: CI/CD pipeline'ı için
- **Vercel Secrets**: Frontend dağıtımları için

## 🔄 Secret Rotation

Secret'lar aşağıdaki koşullarda rotasyona tabi tutulmalıdır:

1. Her 90 günde bir rutin olarak
2. Bir ekip üyesi ayrıldığında
3. Potansiyel bir güvenlik ihlali şüphesi olduğunda

## 📃 Git History'den Secret Temizleme

Eski secret'lar, GitHub depo geçmişinden BFG Repo-Cleaner kullanılarak temizlenmiştir. Eğer yeni bir temizlik gerekirse:

### BFG Repo-Cleaner ile Secret Temizleme Adımları

1. BFG Repo-Cleaner'ı indirin:

```bash
wget https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar -O bfg.jar
```

2. Deponun bir kopyasını oluşturun:

```bash
git clone --mirror git@github.com:SiyahKare/OnlyVips.git OnlyVips-mirror
```

3. Silinecek secret'ları bir metin dosyasında tanımlayın:

```bash
# secrets.txt
JWT_SECRET=your-jwt-secret
TELEGRAM_API_ID=12345
TELEGRAM_API_HASH=abcdef123456
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
```

4. BFG ile secret'ları kaldırın:

```bash
java -jar bfg.jar --replace-text secrets.txt OnlyVips-mirror
```

5. Depoyu temizleyin ve GitHub'a push edin:

```bash
cd OnlyVips-mirror
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push
```

## 🔒 Güvenli Geliştirme Yönergeleri

1. **Hiçbir secret değeri asla:**
   - Doğrudan kod tabanına ekleme
   - Yorumlara ekleme
   - Commit mesajlarına ekleme
   - GitHub Issues veya PR'lara ekleme

2. **Secret değerleri her zaman:**
   - HashiCorp Vault, AWS SSM veya diğer secure secret store'a ekleyin
   - `.env.example` dosyalarında yalnızca yapı örnekleri sağlayın, gerçek değerleri değil
   - Secret değerlerini aktif bir şekilde rotate edin

3. **Yeni bir secret ekleme:**
   - Secret'ı Vault veya SSM'ye ekleyin
   - GitHub Actions secret olarak ekleyin
   - Gerekirse Vercel secret olarak ekleyin
   - Kod tabanında referans ekleyin

## 🛡️ Güvenlik Açığı Bildirme

Bir güvenlik açığı keşfederseniz, lütfen e-posta ile [security@onlyvips.xyz](mailto:security@onlyvips.xyz) adresine bildirin. Tüm güvenlik açıkları ciddiye alınacaktır.

## 📊 Güvenlik Denetimleri

OnlyVips kod tabanı şu güvenlik denetimlerine tabi tutulur:

1. Otomatik dependency scanner (her PR'da ve haftalık)
2. Kod güvenlik analizi
3. Düzenli olarak 3. taraf penetrasyon testleri

---

© 2024 SiyahKare. Tüm hakları saklıdır. 