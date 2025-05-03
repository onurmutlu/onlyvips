# Common-Modules

Bu paket, OnlyVips ekosistemi içindeki tüm frontend ve backend projeleri arasında paylaşılan ortak kodları içerir.

## 📋 İçerik

- TypeScript tiplemeleri
- API istek fonksiyonları
- Yardımcı işlevler

## 🚀 Kurulum

Bu modül otomatik olarak monorepo yapısı içinde yüklenir. Herhangi bir ek kurulum gerekmez.

Eğer doğrudan geliştirme yapmak isterseniz:

```bash
cd common-modules
yarn install
```

## 📦 Yapı

```
common-modules/
├── src/
│   ├── api/           # API istekleri için ortak fonksiyonlar
│   │   ├── auth.ts    # Kimlik doğrulama
│   │   ├── content.ts # İçerik API'leri
│   │   ├── index.ts   # API yapılandırması
│   │   └── packages.ts # Paketler API'si
│   ├── types/         # TypeScript tipleri
│   │   └── index.ts   # Model tiplemeleri
│   ├── utils/         # Yardımcı fonksiyonlar
│   │   └── index.ts   # Genel yardımcı fonksiyonlar
│   └── index.ts       # Ana dışa aktarma dosyası
├── package.json
└── tsconfig.json
```

## 🔄 Kullanım

### Diğer Projelerde Kullanımı

Paketi kullanan diğer projelerde (miniapp, showcu-panel, backend-api), aşağıdaki şekilde import edebilirsiniz:

```typescript
// Tipleri içe aktarma
import { User, Content, Package, Task } from 'onlyvips-common';

// API fonksiyonlarını içe aktarma
import { telegramAuth, getContentList, getPackageDetail } from 'onlyvips-common';

// Yardımcı fonksiyonları içe aktarma
import { formatDate, formatPrice, calculateUserLevel } from 'onlyvips-common';
```

### API Kullanım Örnekleri

#### Kimlik Doğrulama

```typescript
import { telegramAuth } from 'onlyvips-common';

const login = async (telegramData) => {
  try {
    const { token, user } = await telegramAuth({
      telegramId: '123456789',
      username: 'username',
      firstName: 'Ad',
      lastName: 'Soyad'
    });
    
    // Token'ı sakla
    localStorage.setItem('auth_token', token);
    
    return user;
  } catch (error) {
    console.error('Giriş hatası:', error);
  }
};
```

#### İçerik Listeleme

```typescript
import { getContentList } from 'onlyvips-common';

const fetchContents = async () => {
  try {
    const { contents, pagination } = await getContentList({
      page: 1,
      limit: 10,
      category: 'populer',
      isPremium: true
    });
    
    return contents;
  } catch (error) {
    console.error('İçerik yükleme hatası:', error);
    return [];
  }
};
```

### Tip Kullanımı

```typescript
import { User, Content } from 'onlyvips-common';

// Kullanıcı nesnesi oluşturma
const user: User = {
  telegramId: '123456789',
  username: 'username',
  firstName: 'Ad',
  lastName: 'Soyad',
  profilePhoto: 'https://example.com/photo.jpg',
  isShowcu: false,
  isAdmin: false,
  xp: 100,
  badges: ['Yeni Üye'],
  stars: 50
};

// İçerik işleme
const renderContent = (content: Content) => {
  return (
    <div>
      <h3>{content.title}</h3>
      <p>{content.description}</p>
      {content.isPremium && <span>Premium</span>}
    </div>
  );
};
```

## 🧪 Build ve Test

Build için:

```bash
yarn build
```

Lint kontrolü için:

```bash
yarn lint
```

## 📝 Tip Tanımları

Bu paket şu tipleri içerir:

- `User`: Kullanıcı bilgileri
- `Content`: İçerik modeli
- `Package`: VIP paket modeli
- `Task`: Görev modeli

## 🔄 API Endpointleri

API modülü şu endpoint gruplama fonksiyonları içerir:

- `auth`: Kimlik doğrulama API'leri
- `content`: İçerik yönetimi API'leri
- `packages`: VIP paket API'leri

## 🔧 Yardımcı Fonksiyonlar

Aşağıdaki yardımcı fonksiyonlar mevcuttur:

- `formatDate`: Tarih formatlar 
- `formatPrice`: Fiyat formatlar
- `calculateUserLevel`: XP'ye göre kullanıcı seviyesi hesaplar
- `getMediaTypeIcon`: İçerik tipine göre ikon döndürür

## 🛠️ Geliştirme

Yeni bir tip eklemek için:
```typescript
// src/types/index.ts
export interface NewFeature {
  id: string;
  name: string;
  // ... diğer alanlar
}
```

Yeni bir API fonksiyonu eklemek için:
```typescript
// src/api/feature.ts
import api from './index';

export const getFeature = async (id: string) => {
  const response = await api.get(`/api/features/${id}`);
  return response.data;
};

// src/api/index.ts'den dışa aktarın
export * from './feature';
```

## 📄 Lisans

© 2024 SiyahKare. Tüm hakları saklıdır.
