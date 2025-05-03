# OnlyVips Helm Chart

Bu Helm chart, OnlyVips platformunun Kubernetes üzerinde çalıştırılması için gerekli tüm bileşenleri içerir.

## Önkoşullar

- Kubernetes 1.20+
- Helm 3.0+
- PV (PersistentVolume) oluşturabilen dinamik depolama sağlayıcısı
- Ingress controller (NGINX Ingress Controller önerilir)
- Cert-manager (SSL sertifikaları için, isteğe bağlı)

## Bileşenler

Bu chart aşağıdaki bileşenleri içerir:

- Backend API (FastAPI)
- MiniApp (Telegram Mini App)
- Showcu Panel (Telegram Mini App yönetim paneli)
- Flirt Bot (Telegram bot)
- MongoDB (veritabanı)
- Redis (önbellek ve kuyruk)
- PostgreSQL (isteğe bağlı)

## Kurulum

### Hızlı Kurulum

```bash
# Helm repo ekle
helm repo add bitnami https://charts.bitnami.com/bitnami

# Değerleri özelleştirin
cp values.yaml my-values.yaml
# my-values.yaml'ı düzenleme...

# Chart'ı yükle
helm install onlyvips ./onlyvips-chart -f my-values.yaml
```

### Staging Ortamı Kurulumu

```bash
# Staging değerlerini özelleştirin
cp values.yaml staging-values.yaml
# staging-values.yaml'ı düzenleme...

# Secret değerleri için ayrı bir dosya oluşturun
cp values.yaml staging-secrets.yaml
# staging-secrets.yaml'ı düzenleme...

# Chart'ı staging namespace'e yükle
helm install staging onlyvips-chart/ --namespace staging --create-namespace -f staging-values.yaml -f staging-secrets.yaml
```

## Değerler

| Parametre | Açıklama | Varsayılan |
|-----------|----------|------------|
| `global.environment` | Uygulama ortamı | `production` |
| `global.telegram.apiId` | Telegram API ID | `""` |
| `global.telegram.apiHash` | Telegram API Hash | `""` |
| `global.telegram.botToken` | Telegram Bot Token | `""` |
| `backend.replicaCount` | Backend API replica sayısı | `2` |
| `backend.image.repository` | Backend Docker image repository | `onlyvips/backend-api` |
| `backend.image.tag` | Backend Docker image tag | `latest` |
| `miniapp.replicaCount` | MiniApp replica sayısı | `2` |
| `miniapp.image.repository` | MiniApp Docker image repository | `onlyvips/miniapp` |
| `miniapp.image.tag` | MiniApp Docker image tag | `latest` |
| `showcuPanel.replicaCount` | Showcu Panel replica sayısı | `2` |
| `showcuPanel.image.repository` | Showcu Panel Docker image repository | `onlyvips/showcu-panel` |
| `showcuPanel.image.tag` | Showcu Panel Docker image tag | `latest` |
| `flirtBot.replicaCount` | Flirt Bot replica sayısı | `1` |
| `flirtBot.image.repository` | Flirt Bot Docker image repository | `onlyvips/flirt-bot` |
| `flirtBot.image.tag` | Flirt Bot Docker image tag | `latest` |
| `persistence.enabled` | Kalıcı depolama kullanımı | `true` |
| `mongodb.enabled` | MongoDB etkinleştirme | `true` |
| `redis.enabled` | Redis etkinleştirme | `true` |
| `postgresql.enabled` | PostgreSQL etkinleştirme | `true` |

Tam değerler listesi için `values.yaml` dosyasına bakın.

## Bakım

### Yükseltme

```bash
helm upgrade onlyvips ./onlyvips-chart -f my-values.yaml
```

### Kaldırma

```bash
helm uninstall onlyvips
```

## Özelleştirme

### İngress

Varsayılan olarak, tüm servisler için (backend, miniapp, showcu-panel) ingress kaynakları oluşturulur. Kendi domain'lerinizi yapılandırmak için `values.yaml` dosyasında `*.ingress.hosts` değerlerini düzenleyin.

### Veritabanı

Varsayılan olarak MongoDB kullanılır. Eğer mevcut bir veritabanı kullanmak istiyorsanız, `mongodb.enabled` değerini `false` olarak ayarlayın ve kendi veritabanı bağlantı bilgilerinizi sağlayın.

### SSL

SSL için cert-manager kullanılır. SSL sertifikalarını yapılandırmak için `*.ingress.annotations` değerlerini düzenleyin.

## Troubleshooting

En yaygın sorunlar ve çözümleri:

1. **Pod'lar başlatılamıyor**: `kubectl describe pod <pod-name>` komutu ile sorunları kontrol edin.
2. **Veritabanı bağlantı hatası**: Secret değerlerini ve bağlantı bilgilerini kontrol edin.
3. **Ingress çalışmıyor**: Ingress controller'ın kurulu olduğundan emin olun ve ingress kaynağını kontrol edin.

## Lisans

Bu chart ve OnlyVips platformu özel lisans altındadır. Daha fazla bilgi için iletişime geçin. 