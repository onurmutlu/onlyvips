import { Router } from 'express';
import { auth, AuthRequest } from '../middleware/authMiddleware';
import User from '../models/user';
import Content from '../models/content';
import { generateToken } from '../utils/jwtUtils';

const profileRouter = Router();

// Telegram ile giriş/kayıt
profileRouter.post('/telegram-auth', async (req, res) => {
  try {
    const { telegramId, username, firstName, lastName, photoUrl } = req.body;
    
    if (!telegramId) {
      return res.status(400).json({ error: 'Telegram ID gerekli' });
    }
    
    // Kullanıcıyı bul veya oluştur
    let user = await User.findOne({ telegramId });
    
    if (!user) {
      // Yeni kullanıcı oluştur
      user = new User({
        telegramId,
        username,
        firstName,
        lastName,
        profilePhoto: photoUrl,
        xp: 0,
        badges: [],
        stars: 0,
        wallet: { balance: 0 },
        completedTasks: [],
        pendingTasks: []
      });
      
      await user.save();
    } else {
      // Mevcut kullanıcıyı güncelle
      user.username = username || user.username;
      user.firstName = firstName || user.firstName;
      user.lastName = lastName || user.lastName;
      if (photoUrl) user.profilePhoto = photoUrl;
      
      await user.save();
    }
    
    // JWT token oluştur
    const token = generateToken(user.telegramId);
    
    res.json({
      token,
      user: {
        telegramId: user.telegramId,
        username: user.username,
        firstName: user.firstName,
        lastName: user.lastName,
        profilePhoto: user.profilePhoto,
        isShowcu: user.isShowcu,
        xp: user.xp,
        badges: user.badges,
        stars: user.stars
      }
    });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// Kullanıcı profil bilgilerini getir
profileRouter.get('/', auth, async (req: AuthRequest, res) => {
  try {
    const user = req.user;
    
    if (!user) {
      return res.status(404).json({ error: 'Kullanıcı bulunamadı' });
    }
    
    // Kullanıcı görevlerini ve seviye bilgilerini hesapla
    const level = Math.floor(user.xp / 100) + 1;
    const completedTaskCount = user.completedTasks.length;
    const pendingTaskCount = user.pendingTasks.length;
    
    res.json({
      profile: {
        telegramId: user.telegramId,
        username: user.username,
        firstName: user.firstName,
        lastName: user.lastName,
        profilePhoto: user.profilePhoto,
        isShowcu: user.isShowcu,
        xp: user.xp,
        level,
        badges: user.badges,
        stars: user.stars,
        stats: {
          completedTasks: completedTaskCount,
          pendingTasks: pendingTaskCount
        }
      }
    });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// Şovcu profil bilgilerini getir
profileRouter.get('/showcu/:showcuId', async (req, res) => {
  try {
    const { showcuId } = req.params;
    
    const showcu = await User.findOne({ telegramId: showcuId, isShowcu: true });
    
    if (!showcu) {
      return res.status(404).json({ error: 'Şovcu bulunamadı' });
    }
    
    // Şovcunun içerik sayılarını ve paket bilgilerini hesapla
    const contentCount = await Content.countDocuments({ ownerId: showcuId });
    const premiumContentCount = await Content.countDocuments({ ownerId: showcuId, isPremium: true });
    
    res.json({
      profile: {
        telegramId: showcu.telegramId,
        username: showcu.username,
        firstName: showcu.firstName,
        lastName: showcu.lastName,
        profilePhoto: showcu.profilePhoto,
        badges: showcu.badges,
        stats: {
          totalContent: contentCount,
          premiumContent: premiumContentCount
        }
      }
    });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// Şovcu olma başvurusu
profileRouter.post('/become-showcu', auth, async (req: AuthRequest, res) => {
  try {
    const userId = req.user.telegramId;
    
    const user = await User.findOne({ telegramId: userId });
    
    if (!user) {
      return res.status(404).json({ error: 'Kullanıcı bulunamadı' });
    }
    
    if (user.isShowcu) {
      return res.status(400).json({ error: 'Zaten şovcu rolüne sahipsiniz' });
    }
    
    // Şovcu başvurusu (şimdilik otomatik onaylıyoruz)
    user.isShowcu = true;
    await user.save();
    
    res.json({
      message: 'Şovcu rolü başarıyla etkinleştirildi',
      isShowcu: true
    });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// Rozet bilgisi
profileRouter.get('/badges', async (req, res) => {
  try {
    // Sabit rozet listesi (gerçek uygulamada veritabanından çekilebilir)
    const badges = [
      { id: 'Davetçi', name: 'Davetçi', description: 'Yeni üye davet ettin', icon: '🎖️' },
      { id: 'VIP Tanıtıcı', name: 'VIP Tanıtıcı', description: 'MiniApp linkini gruba sabitledin', icon: '🏆' },
      { id: 'İçerik Üreticisi', name: 'İçerik Üreticisi', description: 'İlk içeriğini oluşturdun', icon: '🌟' },
      { id: 'Premium Üye', name: 'Premium Üye', description: 'VIP pakete abone oldun', icon: '💎' },
    ];
    
    res.json({ badges });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

export { profileRouter }; 