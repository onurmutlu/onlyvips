import { Router } from 'express';
import { auth, AuthRequest, requireShowcu } from '../middleware/authMiddleware';
import Package from '../models/package';
import User from '../models/user';
import mongoose from 'mongoose';

const packageRouter = Router();

// Get all packages (with filters)
packageRouter.get('/', async (req, res) => {
  try {
    const { 
      ownerId, 
      page = 1, 
      limit = 20 
    } = req.query;
    
    // Filtre kriterleri oluştur
    const filter: any = {};
    
    if (ownerId) filter.ownerId = ownerId;
    
    // Sayfalama
    const skip = (Number(page) - 1) * Number(limit);
    
    // Paketleri getir
    const packages = await Package.find(filter)
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(Number(limit));
    
    // Toplam sayfa sayısını hesapla
    const total = await Package.countDocuments(filter);
    const totalPages = Math.ceil(total / Number(limit));
    
    res.json({
      packages,
      pagination: {
        total,
        page: Number(page),
        limit: Number(limit),
        totalPages
      }
    });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// Get package by ID
packageRouter.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    // ID geçerliliğini kontrol et
    if (!mongoose.Types.ObjectId.isValid(id)) {
      return res.status(400).json({ error: 'Geçersiz paket ID' });
    }
    
    const packageItem = await Package.findById(id);
    
    if (!packageItem) {
      return res.status(404).json({ error: 'Paket bulunamadı' });
    }
    
    // Şovcu bilgilerini ekle
    const owner = await User.findOne({ telegramId: packageItem.ownerId });
    
    res.json({
      package: packageItem,
      owner: owner ? {
        telegramId: owner.telegramId,
        username: owner.username,
        firstName: owner.firstName,
        lastName: owner.lastName,
        profilePhoto: owner.profilePhoto
      } : null
    });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// Create package (only for showcus)
packageRouter.post('/', auth, requireShowcu, async (req: AuthRequest, res) => {
  try {
    const packageData = req.body;
    const ownerId = req.user.telegramId;
    
    // Gerekli alanları kontrol et
    if (!packageData.name || !packageData.description || !packageData.price || !packageData.duration) {
      return res.status(400).json({ error: 'İsim, açıklama, fiyat ve süre gereklidir' });
    }
    
    // Yeni paket oluştur
    const newPackage = new Package({
      ...packageData,
      ownerId
    });
    
    await newPackage.save();
    
    res.status(201).json({
      message: 'Paket başarıyla oluşturuldu',
      package: newPackage
    });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// Update package (only for package owner)
packageRouter.put('/:id', auth, async (req: AuthRequest, res) => {
  try {
    const { id } = req.params;
    const packageData = req.body;
    const userId = req.user.telegramId;
    
    // ID geçerliliğini kontrol et
    if (!mongoose.Types.ObjectId.isValid(id)) {
      return res.status(400).json({ error: 'Geçersiz paket ID' });
    }
    
    // Paketi bul
    const packageItem = await Package.findById(id);
    
    if (!packageItem) {
      return res.status(404).json({ error: 'Paket bulunamadı' });
    }
    
    // Paket sahibi olup olmadığını kontrol et
    if (packageItem.ownerId !== userId) {
      return res.status(403).json({ error: 'Bu paketi düzenleme yetkiniz yok' });
    }
    
    // Paketi güncelle (ownerId'yi koruyarak)
    const updatedPackage = await Package.findByIdAndUpdate(
      id,
      { ...packageData, ownerId: packageItem.ownerId },
      { new: true }
    );
    
    res.json({
      message: 'Paket başarıyla güncellendi',
      package: updatedPackage
    });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// Delete package (only for package owner)
packageRouter.delete('/:id', auth, async (req: AuthRequest, res) => {
  try {
    const { id } = req.params;
    const userId = req.user.telegramId;
    
    // ID geçerliliğini kontrol et
    if (!mongoose.Types.ObjectId.isValid(id)) {
      return res.status(400).json({ error: 'Geçersiz paket ID' });
    }
    
    // Paketi bul
    const packageItem = await Package.findById(id);
    
    if (!packageItem) {
      return res.status(404).json({ error: 'Paket bulunamadı' });
    }
    
    // Paket sahibi olup olmadığını kontrol et
    if (packageItem.ownerId !== userId && !req.user.isAdmin) {
      return res.status(403).json({ error: 'Bu paketi silme yetkiniz yok' });
    }
    
    // Paketi sil
    await Package.findByIdAndDelete(id);
    
    res.status(200).json({
      message: 'Paket başarıyla silindi'
    });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// Subscribe to package
packageRouter.post('/:id/subscribe', auth, async (req: AuthRequest, res) => {
  try {
    const { id } = req.params;
    const { transactionHash } = req.body;
    const userId = req.user.telegramId;
    
    // ID geçerliliğini kontrol et
    if (!mongoose.Types.ObjectId.isValid(id)) {
      return res.status(400).json({ error: 'Geçersiz paket ID' });
    }
    
    // Paketi bul
    const packageItem = await Package.findById(id);
    
    if (!packageItem) {
      return res.status(404).json({ error: 'Paket bulunamadı' });
    }
    
    // Kullanıcıyı bul
    const user = await User.findOne({ telegramId: userId });
    
    if (!user) {
      return res.status(404).json({ error: 'Kullanıcı bulunamadı' });
    }
    
    // Kullanıcının bu pakete zaten abone olup olmadığını kontrol et
    const existingSub = user.vipPackages.find(
      p => p.packageId.toString() === id && p.active
    );
    
    if (existingSub) {
      return res.status(400).json({ error: 'Bu pakete zaten abonesiniz' });
    }
    
    // Ödeme doğrulaması burada eklenir (TON işlem hash doğrulama)
    // Şimdilik test için otomatik olarak kabul ediyoruz
    
    // Abonelik süresi hesapla
    const purchaseDate = new Date();
    const expiryDate = new Date(purchaseDate);
    expiryDate.setDate(expiryDate.getDate() + packageItem.duration);
    
    // Abonelik ekle
    user.vipPackages.push({
      packageId: new mongoose.Types.ObjectId(id),
      purchaseDate,
      expiryDate,
      active: true
    });
    
    await user.save();
    
    res.json({
      message: `${packageItem.name} paketine başarıyla abone oldunuz!`,
      subscription: {
        packageId: id,
        packageName: packageItem.name,
        purchaseDate,
        expiryDate,
        active: true
      }
    });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// Get user subscriptions
packageRouter.get('/subscriptions/list', auth, async (req: AuthRequest, res) => {
  try {
    const userId = req.user.telegramId;
    
    // Kullanıcıyı bul
    const user = await User.findOne({ telegramId: userId });
    
    if (!user) {
      return res.status(404).json({ error: 'Kullanıcı bulunamadı' });
    }
    
    // Aktif abonelikleri filtrele ve detayları ekle
    const subscriptions = [];
    
    for (const sub of user.vipPackages) {
      // Paket bilgilerini getir
      const packageItem = await Package.findById(sub.packageId);
      
      if (packageItem) {
        subscriptions.push({
          packageId: sub.packageId,
          packageName: packageItem.name,
          packageDescription: packageItem.description,
          ownerId: packageItem.ownerId,
          purchaseDate: sub.purchaseDate,
          expiryDate: sub.expiryDate,
          active: sub.active
        });
      }
    }
    
    res.json({ subscriptions });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

export { packageRouter }; 