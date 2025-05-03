# Güvenlik Politikası

## Desteklenen Versiyonlar

Şu anda aktif olarak güvenlik güncellemeleri alan versiyonlar:

| Versiyon | Destekleniyor            |
| -------- | ------------------------ |
| 0.7.x    | :white_check_mark:       |
| 0.6.x    | :white_check_mark:       |
| < 0.6.0  | :x:                      |

## Güvenlik Açığını Bildirme

OnlyVips uygulamasında bir güvenlik açığı keşfettiyseniz, lütfen aşağıdaki adımları izleyerek güvenli bir şekilde bildiriniz:

1. **Açık bildirimi**: Güvenlik açığını `security@onlyvips.xyz` adresine e-posta ile bildirin.
2. **Açıklama**: Açığın nasıl tetiklendiğini, etkisini ve mümkünse bir düzeltme önerisi içeren detaylı bir açıklama ekleyin.
3. **İletişim**: Ek bilgiler sorabilmemiz için iletişim bilgilerinizi paylaşın.

## Güvenlik Açığı Bildirimi Süreci

1. Bildiriminiz 48 saat içinde ekibimiz tarafından incelenecek ve durum hakkında size bilgi verilecektir.
2. Açığın geçerliliği onaylandıktan sonra, düzeltme çalışmaları başlatılacaktır.
3. Düzeltme yayınlandığında, katkınız için teşekkür edilecek ve izniniz varsa kredi verilecektir.
4. Kritik açıklar için, düzeltme hazır olana kadar gizlilik korunacaktır.

## Güvenlik Önlemleri

OnlyVips ekibi olarak, aşağıdaki güvenlik uygulamalarını kullanıyoruz:

- **JWT Token Yönetimi**: Güvenli yetkilendirme ve kimlik doğrulama
- **Input Validasyonu**: Tüm kullanıcı girdilerinin doğrulanması 
- **Rate Limiting**: API isteklerinin hız sınırlaması
- **Helmet ve Güvenlik Başlıkları**: Express uygulamalarında koruma
- **Düzenli Güncellemeler**: Tüm bağımlılıkların güncel tutulması (Dependabot ile)
- **CORS Koruması**: Kaynaklar arası istek güvenlik kontrolleri
- **MongoDB Injection Koruması**: ORM kullanımı ile injection saldırıları engelleme

## Kredi

Güvenlik açıklarını sorumlu bir şekilde bildiren araştırmacılara teşekkür eder ve iznine bağlı olarak CHANGELOG.md dosyasında kredi veririz.

---

© 2024 SiyahKare. Tüm hakları saklıdır. 