# OnlyVips Production Rollout Planı

Bu doküman, OnlyVips platformunun production ortamına güvenli ve verimli bir şekilde dağıtımı için adımları, stratejileri ve en iyi uygulamaları açıklar.

## İçindekiler

1. [Canary Release Stratejisi](#canary-release-stratejisi)
2. [Rollback Prosedürü](#rollback-prosedürü)
3. [Smoke Test Procedürü](#smoke-test-prosedürü)
4. [Hızlı Deployment Rehberi](#hızlı-deployment-rehberi)
5. [İzleme ve Alerting](#i̇zleme-ve-alerting)

## Canary Release Stratejisi

Canary deployment, yeni sürümün önce küçük bir kullanıcı grubuna (trafik yüzdesine) sunulmasıyla risk azaltılmasını sağlar.

### Canary Release Akışı

1. **Hazırlık**: Yeni versiyon hazırlanır ve imajlar oluşturulur
2. **Kısmi Deployment**: Trafiğin %10'u yeni versiyona yönlendirilir
3. **İzleme Süresi**: 30 dakika boyunca performans ve hata metrikleri izlenir
4. **Karar**: İzleme sonuçlarına bağlı olarak tam rollout veya rollback yapılır
5. **Tam Rollout**: Sorun yoksa, tüm trafik yeni versiyona geçirilir

### Canary Deployment Komutları

```bash
# Kubernetes/Helm ile Canary Deployment
./scripts/canary-deploy.sh

# veya Docker Compose ile
cd docker-config
docker-compose -f docker-compose.yml -f docker-compose.canary.yml up -d
```

## Rollback Prosedürü

Deployment sonrası sorun tespit edilirse, hızlı bir şekilde önceki kararlı sürüme geri dönmek kritik önem taşır.

### Rollback Komutları

```bash
# Kubernetes/Helm ile otomatik rollback
./scripts/rollback.sh [revizyon numarası]

# Docker Compose ile rollback
cd docker-config
docker-compose down
# Önceki imajlara geçiş
docker tag onlyvips/backend-api:previous onlyvips/backend-api:latest
docker tag onlyvips/miniapp:previous onlyvips/miniapp:latest
docker tag onlyvips/showcu-panel:previous onlyvips/showcu-panel:latest
docker tag onlyvips/flirt-bot:previous onlyvips/flirt-bot:latest
# Servisleri başlat
docker-compose up -d
```

## Smoke Test Prosedürü

Deployment sonrası temel fonksiyonaliteyi doğrulamak için smoke testleri çalıştırılmalıdır.

### Smoke Test Akışı

1. Tüm servislerin durumunu kontrol et (Kubernetes pod'ları veya Docker container'ları)
2. Temel API ve servis health check'lerini doğrula
3. User authentication ve temel iş akışlarını test et
4. Sonuçları değerlendir ve gerekirse rollback yap

### Smoke Test Komutları

```bash
# Otomatik smoke testleri çalıştır
./scripts/smoke-test.sh

# Test başarısızsa, rollback yapılabilir
./scripts/rollback.sh
```

## Hızlı Deployment Rehberi

"2 Dakikada Prod'a Al" adımları:

1. **Ortam Hazırlığı**:
   ```bash
   cd /path/to/OnlyVips
   git pull origin main
   ```

2. **Deployment Başlat**:
   ```bash
   # Tüm deployment süreci için tek komut
   ./scripts/launch.sh
   ```

3. **Deployment Onayı ve İzleme**:
   ```bash
   # Kubernetes için
   kubectl get pods -n default -w
   
   # Docker için
   docker-compose ps
   docker-compose logs -f
   ```

4. **Sorun Durumunda Rollback**:
   ```bash
   ./scripts/rollback.sh
   ```

## İzleme ve Alerting

### Metrik İzleme

- **Prometheus/Grafana**: http://metrics.onlyvips.xyz
- **Kritik Metrikler**:
  - CPU/Memory kullanımı
  - API yanıt süreleri
  - Hata oranları
  - Kullanıcı işlem hacimleri

### Alerting

- Slack kanalı: #onlyvips-alerts
- On-call rotasyonu: Trello board'da tanımlanmıştır
- Escalation prosedürü: PagerDuty üzerinden yönetilir

## Ek Kaynaklar

- [OnlyVips Mimari Dokümanı](./README.md)
- [Deployments Trello Board](https://trello.com/onlyvips-deployments)
- [Incident Response Playbook](./SECURITY.md)

---

**NOT**: Bu doküman canlı bir kaynaktır ve her release ile güncellenir. Sorun ya da önerileriniz için: devops@onlyvips.xyz 