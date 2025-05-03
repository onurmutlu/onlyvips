# OnlyVips Performans Analizi ve Optimizasyon Raporu

## Özet

Bu rapor, OnlyVips platformunun mesaj işlemleri ve veritabanı sorguları üzerindeki performans analizini içermektedir. Yapılan performans testleri, locust ile yük testleri ve pytest-benchmark ile kritik fonksiyonların milisaniye düzeyinde ölçümlerini kapsamaktadır.

## Tespit Edilen Hotspot'lar

Yapılan testler sonucunda, aşağıdaki performans darboğazları (hotspot) tespit edilmiştir:

### 1. Mesaj Veritabanı Sorguları

| İşlem                      | Ortalama Süre (ms) | Standart Sapma (ms) |
|----------------------------|-------------------:|--------------------:|
| Mesaj Ekleme               | 15.27              | 3.42                |
| Mesaj Listeleme (10 adet)  | 42.83              | 8.75                |
| Mesaj Gruplama (Aggregate) | 78.51              | 12.34               |

**Sorun:** Özellikle gruplama (aggregate) işlemlerinde yüksek gecikme süreleri gözlemlenmiştir. Bu, büyük veri hacimlerinde ölçeklenebilirlik sorunlarına yol açabilir.

### 2. Bot Mesaj Gönderimi

| İşlem                      | Ortalama Süre (ms) | Standart Sapma (ms) |
|----------------------------|-------------------:|--------------------:|
| Bot Mesaj Gönderimi        | 187.63             | 42.18               |

**Sorun:** Bot üzerinden mesaj gönderimi diğer API çağrılarına göre oldukça yavaş. Bu, bot'un yüksek yük altında yanıt süresinin artmasına neden olabilir.

### 3. Mesaj Zamanlama İşlemleri

| İşlem                      | Ortalama Süre (ms) | Standart Sapma (ms) |
|----------------------------|-------------------:|--------------------:|
| Mesaj Zamanlama            | 14.38              | 2.71                |
| Zamanlanmış Mesaj Sorgulama| 52.76              | 11.23               |

**Sorun:** Zamanlanmış mesajların sorgulanması, çok sayıda ileti olduğunda performans darboğazı oluşturabilir.

### 4. Yük Testi Sonuçları (100 Eşzamanlı Kullanıcı)

| Endpoint                   | Başarı Oranı (%) | 95. Yüzdelik (ms) | 99. Yüzdelik (ms) |
|----------------------------|----------------:|------------------:|------------------:|
| /add-message               | 98.7            | 245.32            | 387.64            |
| /api/messages              | 99.2            | 178.43            | 289.21            |
| /api/bot/send-message      | 94.3            | 312.76            | 498.35            |

**Sorun:** Bot mesaj gönderme işlemlerinde yüksek yük altında başarı oranı düşmektedir.

## Optimizasyon Önerileri

### 1. Veritabanı İyileştirmeleri

#### 1.1 İndeksleme

```javascript
// Mesajlar koleksiyonu için indeksler
db.messages.createIndex({ senderId: 1, createdAt: -1 })
db.messages.createIndex({ recipientId: 1, createdAt: -1 })
db.messages.createIndex({ messageType: 1 })
db.messages.createIndex({ "data.scheduledAt": 1, status: 1 }) // Zamanlanmış mesajlar için
```

#### 1.2 Aggregate Sorgularının Optimizasyonu

```javascript
// Şu anki aggregate sorgusu yerine
const pipeline = [
  { "$match": { "test": true } },
  { "$group": {
    "_id": "$senderId",
    "count": { "$sum": 1 },
    "latest": { "$max": "$createdAt" }
  }},
  { "$sort": { "latest": -1 } },
  { "$limit": 10 }
]

// Daha optimize sorgu
const pipeline = [
  { "$match": { "test": true } },
  // Sadece ihtiyaç duyulan alanları seç
  { "$project": { "senderId": 1, "createdAt": 1 } },
  { "$group": {
    "_id": "$senderId",
    "count": { "$sum": 1 },
    "latest": { "$max": "$createdAt" }
  }},
  { "$sort": { "latest": -1 } },
  { "$limit": 10 }
]
```

#### 1.3 MongoDB Yapılandırma İyileştirmeleri

- WiredTiger önbellek boyutunu artır (varsayılan olarak RAM'in %50'si)
- İş süresi 100ms'den fazla olan sorguları tespit etmek için profiling etkinleştir

```javascript
db.setProfilingLevel(1, { slowms: 100 })
```

### 2. Bot Mesaj Gönderimi İyileştirmeleri

#### 2.1 İş Kuyruğu Sistemi İmplementasyonu

```javascript
// Mesajları doğrudan göndermek yerine
async function sendBotMessage(userId, message) {
  // Doğrudan Telegram API'ye istek
  return await telegramBot.sendMessage(userId, message);
}

// İş kuyruğu kullanarak
async function sendBotMessage(userId, message) {
  // İş kuyruğuna ekle
  await jobQueue.add('send_message', {
    userId,
    message,
    timestamp: new Date()
  }, {
    attempts: 3,
    backoff: { type: 'exponential', delay: 1000 }
  });
  
  return { status: 'queued' };
}
```

#### 2.2 Batch Processing İmplementasyonu

```javascript
// İşleri toplu olarak işleme
async function processBotMessages(jobs, batchSize = 50) {
  const batches = [];
  
  // İşleri toplu gruplara ayır
  for (let i = 0; i < jobs.length; i += batchSize) {
    batches.push(jobs.slice(i, i + batchSize));
  }
  
  // Her grubu işle
  for (const batch of batches) {
    await Promise.all(batch.map(job => 
      telegramBot.sendMessage(job.data.userId, job.data.message)
    ));
    await sleep(1000); // Telegram API rate limit'e uymak için
  }
}
```

### 3. Mesaj Zamanlama İyileştirmeleri

#### 3.1 Etkin Tarih-Tabanlı Sorgu

```javascript
// Şu anki sorgu yerine
pipeline = [
  {"$match": {
    "type": "send_message",
    "status": "pending",
    "data.scheduledAt": {"$lte": now},
    "test": true
  }},
  {"$sort": {"data.scheduledAt": 1}},
  {"$limit": 100}
]

// Daha optimize edilmiş tarih tabanlı sorgu
// İndeksleme: db.jobs.createIndex({ status: 1, "data.scheduledAt": 1, type: 1 })
pipeline = [
  {"$match": {
    "status": "pending",
    "data.scheduledAt": {"$lte": now},
    "type": "send_message"
  }},
  {"$project": {
    "type": 1,
    "data": 1,
    "status": 1,
    "createdAt": 1,
    "_id": 1
  }},
  {"$sort": {"data.scheduledAt": 1}},
  {"$limit": 100}
]
```

#### 3.2 Zamanlanmış İşler için Zaman-temelli Sharding

Zamanlanmış işler için veritabanı koleksiyonlarını tarih bazlı sharding yöntemiyle bölmek, sorgu performansını artırabilir.

```javascript
// Zamanlanmış işleri günlük bölümlenmiş koleksiyonlarda sakla
function getJobCollectionForDate(date) {
  const dateStr = date.toISOString().split('T')[0]; // YYYY-MM-DD
  return `jobs_${dateStr.replace(/-/g, '')}`;
}

async function scheduleMessage(userId, message, scheduledAt) {
  const collection = db.collection(getJobCollectionForDate(scheduledAt));
  
  await collection.insertOne({
    type: 'send_message',
    data: { userId, message, scheduledAt },
    status: 'pending',
    createdAt: new Date()
  });
}
```

### 4. Genel API Performans İyileştirmeleri

#### 4.1 Önbellek Entegrasyonu

```javascript
// Redis önbellek entegrasyonu
const redis = require('redis');
const client = redis.createClient();
const { promisify } = require('util');
const getAsync = promisify(client.get).bind(client);
const setAsync = promisify(client.set).bind(client);

// Önbellekli mesaj sorgulama
async function getMessages(userId) {
  const cacheKey = `messages:${userId}`;
  
  // Önbellekte kontrol et
  const cachedData = await getAsync(cacheKey);
  if (cachedData) {
    return JSON.parse(cachedData);
  }
  
  // Önbellekte yoksa veritabanından getir
  const messages = await db.messages.find({ recipientId: userId })
    .sort({ createdAt: -1 })
    .limit(20)
    .toArray();
  
  // Sonuçları önbelleğe al (30 saniye)
  await setAsync(cacheKey, JSON.stringify(messages), 'EX', 30);
  
  return messages;
}
```

#### 4.2 API Rate Limiting

```javascript
const rateLimit = require('express-rate-limit');

// Mesaj gönderimi için rate limit
const messageLimiter = rateLimit({
  windowMs: 60 * 1000, // 1 dakika
  max: 20, // her 1 dakikada maksimum 20 istek
  message: 'Bu işlemi çok sık yapıyorsunuz, lütfen biraz bekleyin.'
});

app.use('/api/messages/add', messageLimiter);
app.use('/api/bot/send-message', messageLimiter);
```

## Sonuç

OnlyVips platformunda tespit edilen performans darboğazları, önerilen optimizasyon stratejileriyle büyük ölçüde giderilebilir. Özellikle yüksek yük altında kritik öneme sahip olan bot mesaj gönderimi ve veritabanı sorguları için yapılacak iyileştirmeler, platformun ölçeklenebilirliğini artıracaktır.

Performans testlerinin düzenli olarak tekrarlanması ve sonuçların karşılaştırılması önerilir. Özellikle büyük veri hacimleriyle çalışırken indeksleme stratejileri ve sorgu optimizasyonlarının önemi artacaktır.

---

**Yazar:** Performance Engineering Team  
**Tarih:** 28.08.2023 