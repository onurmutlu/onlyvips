import express from 'express';
import { authenticate } from '../middleware/auth';
import { PaymentController } from '../controllers/payment';
import { TonPaymentController } from '../controllers/ton-payment';

const router = express.Router();
const paymentController = new PaymentController();
const tonPaymentController = new TonPaymentController();

// Star satın al
router.post('/stars', authenticate, paymentController.purchaseStars);

// Ödeme yöntemlerini getir
router.get('/methods', paymentController.getMethods);

// İşlem geçmişini getir
router.get('/history/:userId', authenticate, paymentController.getHistory);

// TON ödeme başlatma
router.post('/ton/initiate', authenticate, tonPaymentController.initiateTonPayment);

// TON ödeme durumunu kontrol et
router.get('/status/:paymentId', authenticate, tonPaymentController.checkPaymentStatus);

// Para çekme işlemi başlat (şovcular için)
router.post('/withdraw', authenticate, tonPaymentController.initiateWithdrawal);

export default router;
