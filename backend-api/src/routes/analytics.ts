import { Router } from 'express';
import { auth, AuthRequest, requireShowcu } from '../middleware/authMiddleware';
import Content from '../models/content';
import User from '../models/user';
import Package from '../models/package';

const analyticsRouter = Router();

// Get dashboard analytics (for showcus)
analyticsRouter.get('/dashboard', auth, requireShowcu, async (req: AuthRequest, res) => {
  try {
    const userId = req.user.telegramId;
    
    // Son 30 günlük tarih
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    
    // Toplam içerik sayısı
    const totalContent = await Content.countDocuments({ ownerId: userId });
    
    // Toplam görüntüleme
    const contents = await Content.find({ ownerId: userId });
    const totalViews = contents.reduce((sum, content) => sum + content.totalViews, 0);
    const totalLikes = contents.reduce((sum, content) => sum + content.totalLikes, 0);
    
    // Toplam paket sayısı
    const totalPackages = await Package.countDocuments({ ownerId: userId });
    
    // Kullanıcıları bul ve VIP paketleri say
    const allUsers = await User.find({ 'vipPackages.active': true });
    
    // Bu şovcuya ait paketlerin ID'lerini al
    const packageIds = (await Package.find({ ownerId: userId })).map(p => p._id.toString());
    
    // Aboneleri say
    let totalSubscribers = 0;
    
    for (const user of allUsers) {
      // Kullanıcının aktif aboneliklerini kontrol et
      const hasActiveSubscription = user.vipPackages.some(
        sub => sub.active && packageIds.includes(sub.packageId.toString())
      );
      
      if (hasActiveSubscription) {
        totalSubscribers++;
      }
    }
    
    // Son 7 günlük görüntüleme verileri (line chart için)
    const viewsData = [];
    for (let i = 6; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      date.setHours(0, 0, 0, 0);
      
      const nextDate = new Date(date);
      nextDate.setDate(nextDate.getDate() + 1);
      
      // Bu tarihe ait görüntülemeleri saymak için gerçek veritabanı sorgusu gerekir
      // Şimdilik rastgele veri üretiyoruz
      viewsData.push({
        date: date.toISOString().slice(0, 10),
        views: Math.floor(Math.random() * 100)
      });
    }
    
    // En çok görüntülenen içerikler
    const topContents = await Content.find({ ownerId: userId })
      .sort({ totalViews: -1 })
      .limit(5);
    
    res.json({
      totalContent,
      totalViews,
      totalLikes,
      totalPackages,
      totalSubscribers,
      viewsData,
      topContents: topContents.map(content => ({
        id: content._id,
        title: content.title,
        mediaType: content.mediaType,
        thumbnailUrl: content.thumbnailUrl || content.mediaUrl,
        views: content.totalViews,
        likes: content.totalLikes
      }))
    });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// Get content analytics
analyticsRouter.get('/content/:id', auth, async (req: AuthRequest, res) => {
  try {
    const { id } = req.params;
    const userId = req.user.telegramId;
    
    // İçeriği bul
    const content = await Content.findById(id);
    
    if (!content) {
      return res.status(404).json({ error: 'İçerik bulunamadı' });
    }
    
    // İçerik sahibi olup olmadığını kontrol et
    if (content.ownerId !== userId && !req.user.isAdmin) {
      return res.status(403).json({ error: 'Bu içeriğin analitiğini görme yetkiniz yok' });
    }
    
    // Son 7 günlük görüntüleme verileri (daha gerçekçi analitik için ayrı bir model gerekebilir)
    const viewsData = [];
    for (let i = 6; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      
      viewsData.push({
        date: date.toISOString().slice(0, 10),
        views: Math.floor(Math.random() * 50)
      });
    }
    
    res.json({
      content: {
        id: content._id,
        title: content.title,
        description: content.description,
        mediaType: content.mediaType,
        createdAt: content.createdAt
      },
      stats: {
        totalViews: content.totalViews,
        totalLikes: content.totalLikes,
        viewsData
      }
    });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// Get package analytics
analyticsRouter.get('/package/:id', auth, async (req: AuthRequest, res) => {
  try {
    const { id } = req.params;
    const userId = req.user.telegramId;
    
    // Paketi bul
    const packageItem = await Package.findById(id);
    
    if (!packageItem) {
      return res.status(404).json({ error: 'Paket bulunamadı' });
    }
    
    // Paket sahibi olup olmadığını kontrol et
    if (packageItem.ownerId !== userId && !req.user.isAdmin) {
      return res.status(403).json({ error: 'Bu paketin analitiğini görme yetkiniz yok' });
    }
    
    // Aboneleri bul
    const users = await User.find({ 
      'vipPackages.packageId': id, 
      'vipPackages.active': true 
    });
    
    // Abonelik başlangıç tarihlerine göre veri oluştur
    const subscriptionData = [];
    for (let i = 6; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      date.setHours(0, 0, 0, 0);
      
      const nextDate = new Date(date);
      nextDate.setDate(nextDate.getDate() + 1);
      
      // Bu tarih aralığında başlayan abonelikleri say
      // Gerçek uygulama için timestamp kayıtları gerekir
      subscriptionData.push({
        date: date.toISOString().slice(0, 10),
        subscriptions: Math.floor(Math.random() * 10)
      });
    }
    
    res.json({
      package: {
        id: packageItem._id,
        name: packageItem.name,
        price: packageItem.price,
        duration: packageItem.duration,
        createdAt: packageItem.createdAt
      },
      stats: {
        totalSubscribers: users.length,
        activeSubscribers: users.length,
        revenue: users.length * packageItem.price,
        subscriptionData
      }
    });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// Get global platform stats (admin only)
analyticsRouter.get('/admin/global', auth, async (req: AuthRequest, res) => {
  try {
    // Admin kontrolü
    if (!req.user.isAdmin) {
      return res.status(403).json({ error: 'Yetkisiz erişim' });
    }
    
    // Toplam kullanıcı sayısı
    const totalUsers = await User.countDocuments();
    
    // Toplam şovcu sayısı
    const totalShowcus = await User.countDocuments({ isShowcu: true });
    
    // Toplam içerik sayısı
    const totalContent = await Content.countDocuments();
    
    // Toplam paket sayısı
    const totalPackages = await Package.countDocuments();
    
    // Son 7 günlük kullanıcı kayıt verileri
    const registrationData = [];
    for (let i = 6; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      date.setHours(0, 0, 0, 0);
      
      const nextDate = new Date(date);
      nextDate.setDate(nextDate.getDate() + 1);
      
      const count = await User.countDocuments({
        createdAt: { $gte: date, $lt: nextDate }
      });
      
      registrationData.push({
        date: date.toISOString().slice(0, 10),
        count
      });
    }
    
    res.json({
      totalUsers,
      totalShowcus,
      totalContent,
      totalPackages,
      registrationData
    });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

export { analyticsRouter }; 