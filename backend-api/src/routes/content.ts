import { Router } from 'express';
import { auth, AuthRequest, requireShowcu } from '../middleware/authMiddleware';
import Content from '../models/content';
import User from '../models/user';
import mongoose from 'mongoose';

const contentRouter = Router();

// Get all content (with filters)
contentRouter.get('/', async (req, res) => {
  try {
    const { 
      category, 
      showcuId, 
      isPremium, 
      search,
      page = 1, 
      limit = 20 
    } = req.query;
    
    // Filtre kriterleri oluştur
    const filter: any = {};
    
    if (category) filter.contentCategory = category;
    if (showcuId) filter.ownerId = showcuId;
    if (isPremium !== undefined) filter.isPremium = isPremium === 'true';
    
    // Metin araması
    if (search) {
      filter.$text = { $search: search as string };
    }
    
    // Sayfalama
    const skip = (Number(page) - 1) * Number(limit);
    
    // İçerikleri getir
    const contents = await Content.find(filter)
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(Number(limit));
    
    // Toplam sayfa sayısını hesapla
    const total = await Content.countDocuments(filter);
    const totalPages = Math.ceil(total / Number(limit));
    
    res.json({
      contents,
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

// Get content by ID
contentRouter.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    // ID geçerliliğini kontrol et
    if (!mongoose.Types.ObjectId.isValid(id)) {
      return res.status(400).json({ error: 'Geçersiz içerik ID' });
    }
    
    const content = await Content.findById(id);
    
    if (!content) {
      return res.status(404).json({ error: 'İçerik bulunamadı' });
    }
    
    // İçerik görüntüleme sayısını artır
    content.totalViews += 1;
    await content.save();
    
    // Şovcu bilgilerini ekle
    const owner = await User.findOne({ telegramId: content.ownerId });
    
    res.json({
      content,
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

// Create content (only for showcus)
contentRouter.post('/', auth, requireShowcu, async (req: AuthRequest, res) => {
  try {
    const contentData = req.body;
    const ownerId = req.user.telegramId;
    
    // Gerekli alanları kontrol et
    if (!contentData.title || !contentData.description || !contentData.mediaUrl || !contentData.mediaType) {
      return res.status(400).json({ error: 'Başlık, açıklama, medya URL ve medya tipi gereklidir' });
    }
    
    // Yeni içerik oluştur
    const newContent = new Content({
      ...contentData,
      ownerId,
      totalViews: 0,
      totalLikes: 0
    });
    
    await newContent.save();
    
    res.status(201).json({
      message: 'İçerik başarıyla oluşturuldu',
      content: newContent
    });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// Update content (only for content owner)
contentRouter.put('/:id', auth, async (req: AuthRequest, res) => {
  try {
    const { id } = req.params;
    const contentData = req.body;
    const userId = req.user.telegramId;
    
    // ID geçerliliğini kontrol et
    if (!mongoose.Types.ObjectId.isValid(id)) {
      return res.status(400).json({ error: 'Geçersiz içerik ID' });
    }
    
    // İçeriği bul
    const content = await Content.findById(id);
    
    if (!content) {
      return res.status(404).json({ error: 'İçerik bulunamadı' });
    }
    
    // İçerik sahibi olup olmadığını kontrol et
    if (content.ownerId !== userId) {
      return res.status(403).json({ error: 'Bu içeriği düzenleme yetkiniz yok' });
    }
    
    // İçeriği güncelle (ownerId'yi koruyarak)
    const updatedContent = await Content.findByIdAndUpdate(
      id,
      { ...contentData, ownerId: content.ownerId },
      { new: true }
    );
    
    res.json({
      message: 'İçerik başarıyla güncellendi',
      content: updatedContent
    });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// Delete content (only for content owner)
contentRouter.delete('/:id', auth, async (req: AuthRequest, res) => {
  try {
    const { id } = req.params;
    const userId = req.user.telegramId;
    
    // ID geçerliliğini kontrol et
    if (!mongoose.Types.ObjectId.isValid(id)) {
      return res.status(400).json({ error: 'Geçersiz içerik ID' });
    }
    
    // İçeriği bul
    const content = await Content.findById(id);
    
    if (!content) {
      return res.status(404).json({ error: 'İçerik bulunamadı' });
    }
    
    // İçerik sahibi olup olmadığını kontrol et
    if (content.ownerId !== userId && !req.user.isAdmin) {
      return res.status(403).json({ error: 'Bu içeriği silme yetkiniz yok' });
    }
    
    // İçeriği sil
    await Content.findByIdAndDelete(id);
    
    res.status(200).json({
      message: 'İçerik başarıyla silindi'
    });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// Like content
contentRouter.post('/:id/like', auth, async (req: AuthRequest, res) => {
  try {
    const { id } = req.params;
    
    // ID geçerliliğini kontrol et
    if (!mongoose.Types.ObjectId.isValid(id)) {
      return res.status(400).json({ error: 'Geçersiz içerik ID' });
    }
    
    // İçeriği bul
    const content = await Content.findById(id);
    
    if (!content) {
      return res.status(404).json({ error: 'İçerik bulunamadı' });
    }
    
    // Beğeni sayısını artır
    content.totalLikes += 1;
    await content.save();
    
    res.json({
      message: 'İçerik beğenildi',
      totalLikes: content.totalLikes
    });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// Get content categories
contentRouter.get('/categories/list', async (req, res) => {
  try {
    // Mevcut içerik kategorilerini getir (veritabanından benzersiz kategorileri sorgula)
    const categories = await Content.distinct('contentCategory');
    
    res.json({ categories });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// Get showcase content (featured content)
contentRouter.get('/featured/list', async (req, res) => {
  try {
    // Öne çıkan içerikleri getir (en çok görüntülenen, premium olan ilk 5)
    const featuredContent = await Content.find({ isPremium: true })
      .sort({ totalViews: -1, createdAt: -1 })
      .limit(5);
    
    res.json({ featuredContent });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

export { contentRouter }; 