// backend-api/app/routes/creators.ts
import express from 'express';
import { authenticate } from '../middleware/auth';
import { CreatorController } from '../controllers/creator';

const router = express.Router();
const controller = new CreatorController();

// Tüm şovcuları getir
router.get('/', controller.getAll);

// Popüler şovcuları getir
router.get('/popular', controller.getPopular);

// Şovcu profilini getir
router.get('/:id', controller.getProfile);

// Şovcu içeriklerini getir
router.get('/:id/content', controller.getContent);

// Şovcuya abone ol
router.post('/:id/subscribe', authenticate, controller.subscribe);

// Şovcu ara
router.get('/search', controller.search);

export default router;