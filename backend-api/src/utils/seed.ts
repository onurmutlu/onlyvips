import mongoose from 'mongoose';
import dotenv from 'dotenv';
import User from '../models/user';
import Task from '../models/task';
import Content from '../models/content';
import Package from '../models/package';
import logger from './logger';

dotenv.config();

const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/onlyvips';

// Test veritabanı doldurma fonksiyonu
const seedDatabase = async () => {
  try {
    // MongoDB'ye bağlan
    await mongoose.connect(MONGODB_URI);
    logger.info('MongoDB bağlantısı kuruldu');

    // Mevcut verileri temizle (dikkatli kullanın!)
    if (process.env.NODE_ENV === 'development') {
      await Task.deleteMany({});
      logger.info('Görev koleksiyonu temizlendi');
    }

    // Görev verilerini yükle
    const tasks = [
      {
        id: 1,
        title: 'Yeni üye davet et',
        description: 'Arkadaşlarını OnlyVips\'e davet et ve ödül kazan',
        reward: '🎖️ Rozet',
        rewardType: 'badge',
        rewardValue: 'Davetçi',
        verificationType: 'invite_tracker',
        verificationRequired: true,
        isActive: true
      },
      {
        id: 2,
        title: 'DM\'den tanıtım mesajı gönder',
        description: 'Bota özel mesaj göndererek tanıtım yap',
        reward: '+15 XP',
        rewardType: 'xp',
        rewardValue: 15,
        verificationType: 'message_forward',
        verificationRequired: true,
        isActive: true
      },
      {
        id: 3,
        title: '5 farklı grupta botu paylaş',
        description: 'Telegram gruplarında botu paylaş',
        reward: '+20 XP',
        rewardType: 'xp',
        rewardValue: 20,
        verificationType: 'bot_mention',
        verificationRequired: true,
        isActive: true
      },
      {
        id: 4,
        title: 'Show linkini arkadaşlarına yolla',
        description: 'Özel davet linkini paylaş',
        reward: '+10 XP',
        rewardType: 'xp',
        rewardValue: 10,
        verificationType: 'deeplink_track',
        verificationRequired: true,
        isActive: true
      },
      {
        id: 5,
        title: 'Grubuna MiniApp linkini sabitle',
        description: 'Grubuna VIP içerik linkini sabitle',
        reward: '🎖️ Rozet',
        rewardType: 'badge',
        rewardValue: 'VIP Tanıtıcı',
        verificationType: 'pin_check',
        verificationRequired: true,
        isActive: true
      },
      {
        id: 6,
        title: 'VIP tanıtım postunu 3 grupta paylaş',
        description: 'Tanıtım postunu farklı gruplarda paylaş',
        reward: '+25 XP',
        rewardType: 'xp',
        rewardValue: 25,
        verificationType: 'post_share',
        verificationRequired: true,
        isActive: true
      },
      {
        id: 7,
        title: 'Görev çağrısını 10 kişiye gönder',
        description: 'Arkadaşlarını davet et',
        reward: '+30 XP',
        rewardType: 'xp',
        rewardValue: 30,
        verificationType: 'share_count',
        verificationRequired: true,
        isActive: true
      },
      {
        id: 8,
        title: 'Botu kullanan bir arkadaş davet et',
        description: 'Arkadaşını davet et',
        reward: '+10 XP',
        rewardType: 'xp',
        rewardValue: 10,
        verificationType: 'referral',
        verificationRequired: true,
        isActive: true
      }
    ];

    // Görevleri kaydet
    await Task.insertMany(tasks);
    logger.info(`${tasks.length} görev oluşturuldu`);

    // Eğer test için başka veriler eklemek isterseniz buraya ekleyebilirsiniz
    // Örnek admin kullanıcısı
    if (process.env.CREATE_ADMIN === 'true') {
      const adminUser = new User({
        telegramId: '12345678',
        username: 'admin',
        firstName: 'Admin',
        lastName: 'User',
        profilePhoto: 'https://example.com/admin.jpg',
        isShowcu: true,
        isAdmin: true,
        xp: 1000,
        badges: ['Admin', 'VIP Tanıtıcı', 'İçerik Üreticisi'],
        stars: 500,
        wallet: {
          tonAddress: 'EQDrjaLahXc1HQoXHJAzVfSF6KVkfHzy3yuCYYnMfwieTd_3',
          balance: 100
        },
        completedTasks: [1, 2, 3, 4, 5],
        pendingTasks: []
      });

      // Mevcut admin kullanıcısını kontrol et
      const existingAdmin = await User.findOne({ telegramId: '12345678' });
      if (!existingAdmin) {
        await adminUser.save();
        logger.info('Admin kullanıcısı oluşturuldu');
      } else {
        logger.info('Admin kullanıcısı zaten mevcut');
      }
    }

    logger.info('Veritabanı başarıyla dolduruldu');
  } catch (error) {
    logger.error('Veritabanı doldurma hatası:', error);
  } finally {
    // Bağlantıyı kapat
    await mongoose.disconnect();
    logger.info('MongoDB bağlantısı kapatıldı');
  }
};

// Eğer bu dosya doğrudan çalıştırılırsa, seed işlemini başlat
if (require.main === module) {
  seedDatabase()
    .then(() => {
      logger.info('Seed işlemi tamamlandı');
      process.exit(0);
    })
    .catch((error) => {
      logger.error('Seed işlemi sırasında hata oluştu:', error);
      process.exit(1);
    });
}

export default seedDatabase; 