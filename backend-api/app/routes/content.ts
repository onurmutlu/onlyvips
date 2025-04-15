// backend-api/app/routes/content.ts
import express from 'express';
import { authenticate } from '../middleware/auth';
import { ContentController } from '../controllers/content';

const router = express.Router();
const controller = new ContentController();

// Kategorileri getir
router.get('/categories', controller.getCategories);

// Öne çıkan içerikleri getir
router.get('/featured', controller.getFeatured);

// En son eklenen içerikleri getir
router.get('/latest', controller.getLatest);

// İçerik detaylarını getir
router.get('/:id', controller.getDetails);

// İçeriği beğen
router.post('/:id/like', authenticate, controller.likeContent);

// İçeriğe yorum ekle
router.post('/:id/comment', authenticate, controller.addComment);

// İçerik ara
router.get('/search', controller.search);

// Kategoriye göre filtrele
router.get('/filter', controller.filterByCategory);

export default router;