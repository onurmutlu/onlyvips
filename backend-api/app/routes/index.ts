// backend-api/app/routes/index.ts
import express from 'express';
import contentRoutes from './content';
import creatorRoutes from './creators';
import userRoutes from './users';
import packageRoutes from './packages';
import paymentRoutes from './payments';
import creatorPanelRoutes from './creator-panel';

const router = express.Router();

// API rotalarını tanımla
router.use('/content', contentRoutes);
router.use('/creators', creatorRoutes);
router.use('/users', userRoutes);
router.use('/packages', packageRoutes);
router.use('/payments', paymentRoutes);
router.use('/creator-panel', creatorPanelRoutes);

// Ana API rotası için bilgi
router.get('/', (req, res) => {
  res.json({
    name: 'OnlyVips API',
    version: '0.7.0',
    endpoints: [
      '/content',
      '/creators',
      '/users',
      '/packages',
      '/payments',
      '/creator-panel'
    ]
  });
});

export default router;