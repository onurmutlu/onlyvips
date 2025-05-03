import { Router } from 'express';
import { auth, AuthRequest, requireShowcu } from '../middleware/authMiddleware';
import User from '../models/user';

const walletRouter = Router();

// Get user wallet
walletRouter.get('/', auth, async (req: AuthRequest, res) => {
  try {
    const userId = req.user.telegramId;
    const user = await User.findOne({ telegramId: userId });
    
    if (!user) {
      return res.status(404).json({ error: 'Kullanıcı bulunamadı' });
    }
    
    res.json({
      wallet: {
        tonAddress: user.wallet.tonAddress || '',
        balance: user.wallet.balance || 0
      }
    });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// Update TON address
walletRouter.put('/ton-address', auth, async (req: AuthRequest, res) => {
  try {
    const { tonAddress } = req.body;
    const userId = req.user.telegramId;
    
    if (!tonAddress) {
      return res.status(400).json({ error: 'TON adresi gerekli' });
    }
    
    // TON adres formatını kontrol et (basit doğrulama)
    const tonAddressRegex = /^[0-9a-zA-Z_-]{48}$/;
    if (!tonAddressRegex.test(tonAddress)) {
      return res.status(400).json({ error: 'Geçersiz TON adresi formatı' });
    }
    
    const user = await User.findOneAndUpdate(
      { telegramId: userId },
      { 'wallet.tonAddress': tonAddress },
      { new: true }
    );
    
    if (!user) {
      return res.status(404).json({ error: 'Kullanıcı bulunamadı' });
    }
    
    res.json({
      message: 'TON adresi güncellendi',
      wallet: {
        tonAddress: user.wallet.tonAddress,
        balance: user.wallet.balance
      }
    });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// Request withdrawal (for showcus)
walletRouter.post('/withdraw', auth, requireShowcu, async (req: AuthRequest, res) => {
  try {
    const { amount } = req.body;
    const userId = req.user.telegramId;
    
    if (!amount || amount <= 0) {
      return res.status(400).json({ error: 'Geçerli bir miktar gerekli' });
    }
    
    const user = await User.findOne({ telegramId: userId });
    
    if (!user) {
      return res.status(404).json({ error: 'Kullanıcı bulunamadı' });
    }
    
    if (!user.wallet.tonAddress) {
      return res.status(400).json({ error: 'Çekim yapmadan önce TON adresi eklemelisiniz' });
    }
    
    if (user.wallet.balance < amount) {
      return res.status(400).json({ error: 'Yetersiz bakiye' });
    }
    
    // TON çekim talebi oluştur (gerçek işlemler back-office panelinden yapılacak)
    // Burada sadece kullanıcının bakiyesini güncelliyoruz
    user.wallet.balance -= amount;
    await user.save();
    
    // Burada gerçek TON işlemi sistemi entegre edilecek
    
    res.json({
      message: `${amount} TON çekim talebi alındı. İşleminiz en kısa sürede gerçekleştirilecek.`,
      wallet: {
        tonAddress: user.wallet.tonAddress,
        balance: user.wallet.balance
      }
    });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// Purchase stars with TON
walletRouter.post('/purchase-stars', auth, async (req: AuthRequest, res) => {
  try {
    const { amount, transactionHash } = req.body;
    const userId = req.user.telegramId;
    
    if (!amount || amount <= 0) {
      return res.status(400).json({ error: 'Geçerli bir miktar gerekli' });
    }
    
    if (!transactionHash) {
      return res.status(400).json({ error: 'İşlem hash değeri gerekli' });
    }
    
    const user = await User.findOne({ telegramId: userId });
    
    if (!user) {
      return res.status(404).json({ error: 'Kullanıcı bulunamadı' });
    }
    
    // Bu bölümde gerçek TON işlemi doğrulanacak
    // Şimdilik test için otomatik olarak kabul ediyoruz
    const starsToAdd = amount * 10; // 1 TON = 10 Star
    
    user.stars += starsToAdd;
    await user.save();
    
    res.json({
      message: `${starsToAdd} Star satın alındı!`,
      stars: user.stars
    });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// Get transaction history (stub for now)
walletRouter.get('/transactions', auth, async (req: AuthRequest, res) => {
  try {
    // Örnek işlem geçmişi (gerçek veritabanı entegrasyonu gerekiyor)
    res.json({
      transactions: [
        {
          id: '1',
          type: 'deposit',
          amount: 10,
          status: 'completed',
          timestamp: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
        },
        {
          id: '2',
          type: 'purchase',
          amount: 5,
          itemName: 'VIP Paket',
          status: 'completed',
          timestamp: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000)
        }
      ]
    });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

export { walletRouter }; 