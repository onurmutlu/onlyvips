// backend-api/app/routes/creator-panel.ts
import express from 'express';
import { authenticate, authorizeCreator } from '../middleware/auth';
import { CreatorPanelController } from '../controllers/creator-panel';
import { upload } from '../middleware/upload';

const router = express.Router();
const controller = new CreatorPanelController();

// Şovcu paneline giriş
router.post('/login', controller.login);

// Şovcunun içeriklerini getir
router.get('/content', authenticate, authorizeCreator, controller.getCreatorContent);

// Yeni içerik oluştur
router.post('/content', 
  authenticate, 
  authorizeCreator, 
  upload.fields([
    { name: 'thumbnail', maxCount: 1 },
    { name: 'mediaFile', maxCount: 1 }
  ]), 
  controller.createContent
);

// İçerik güncelle
router.put('/content/:id', 
  authenticate, 
  authorizeCreator, 
  upload.fields([
    { name: 'thumbnail', maxCount: 1 },
    { name: 'mediaFile', maxCount: 1 }
  ]), 
  controller.updateContent
);

// İçerik sil
router.delete('/content/:id', authenticate, authorizeCreator, controller.deleteContent);

// Şovcu paketi oluştur
router.post('/packages', authenticate, authorizeCreator, controller.createPackage);

// Şovcu paketini güncelle
router.put('/packages/:id', authenticate, authorizeCreator, controller.updatePackage);

// Şovcu paketini sil
router.delete('/packages/:id', authenticate, authorizeCreator, controller.deletePackage);

// Şovcu istatistiklerini getir
router.get('/statistics', authenticate, authorizeCreator, controller.getStatistics);

// Şovcu abonelerini getir
router.get('/subscribers', authenticate, authorizeCreator, controller.getSubscribers);

// Şovcu gelirlerini getir
router.get('/earnings', authenticate, authorizeCreator, controller.getEarnings);

export default router;