import { Router } from 'express';
import User from '../models/user';
import { generateToken } from '../utils/jwtUtils';
import { auth, AuthRequest } from '../middleware/authMiddleware';

const authRouter = Router();

// Telegram kimlik doğrulama
authRouter.post('/telegram', async (req, res) => {
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
        isShowcu: false,
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
      if (username) user.username = username;
      if (firstName) user.firstName = firstName;
      if (lastName) user.lastName = lastName;
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

// Kullanıcı bilgisi doğrulama
authRouter.get('/me', auth, async (req: AuthRequest, res) => {
  try {
    const user = req.user;
    
    if (!user) {
      return res.status(404).json({ error: 'Kullanıcı bulunamadı' });
    }
    
    // Kullanıcı seviyesini hesapla
    const level = Math.floor(user.xp / 100) + 1;
    
    res.json({
      user: {
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
        walletAddress: user.wallet?.tonAddress || '',
        completedTasks: user.completedTasks || [],
        pendingTasks: user.pendingTasks || []
      }
    });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// Cihaz bilgisi kaydet
authRouter.post('/device', auth, async (req: AuthRequest, res) => {
  try {
    const { deviceId, deviceType, fcmToken } = req.body;
    const userId = req.user.telegramId;
    
    // Gelecekte bildirimler için FCM token kaydetmek üzere yapı
    
    res.json({
      message: 'Cihaz bilgisi kaydedildi',
      success: true
    });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

export { authRouter }; 