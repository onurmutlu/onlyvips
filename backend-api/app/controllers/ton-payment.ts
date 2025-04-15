import { Request, Response } from 'express';
import TonWeb from 'tonweb';
import { DbService } from '../services/db';
import { PaymentService } from '../services/payment';

export class TonPaymentController {
  private dbService: DbService;
  private paymentService: PaymentService;
  private tonWeb: typeof TonWeb;
  
  constructor() {
    this.dbService = new DbService();
    this.paymentService = new PaymentService();
    this.tonWeb = new TonWeb(new TonWeb.HttpProvider('https://toncenter.com/api/v2/jsonRPC'));
  }
  
  // TON ile ödeme başlat
  initiateTonPayment = async (req: Request, res: Response) => {
    try {
      const { userId, amount, itemType, itemId } = req.body;
      
      if (!userId || !amount || amount <= 0) {
        return res.status(400).json({
          success: false,
          message: 'Geçersiz kullanıcı veya miktar'
        });
      }
      
      // Ödeme kaydı oluştur
      const paymentId = await this.paymentService.createPayment({
        userId,
        amount,
        currency: 'TON',
        status: 'pending',
        itemType, // 'star', 'package', 'content' olabilir
        itemId
      });
      
      // Ödeme alıcı cüzdan adresi
      const receiverAddress = process.env.TON_WALLET_ADDRESS;
      
      // Ödeme URL'ini oluştur
      const tonPayUrl = `ton://transfer/${receiverAddress}?amount=${amount * 1000000000}&text=payment_id:${paymentId}`;
      
      // QR kod verisi
      const qrData = tonPayUrl;
      
      return res.status(200).json({
        success: true,
        data: {
          paymentId,
          tonPayUrl,
          qrData,
          expiresAt: Date.now() + 30 * 60 * 1000 // 30 dakika geçerli
        }
      });
    } catch (error) {
      console.error('TON ödeme hatası:', error);
      return res.status(500).json({
        success: false,
        message: 'TON ödeme başlatılırken bir hata oluştu'
      });
    }
  };
  
  // Ödeme durumunu kontrol et
  checkPaymentStatus = async (req: Request, res: Response) => {
    try {
      const { paymentId } = req.params;
      
      // Ödeme kaydını getir
      const payment = await this.paymentService.getPayment(paymentId);
      
      if (!payment) {
        return res.status(404).json({
          success: false,
          message: 'Ödeme bulunamadı'
        });
      }
      
      // Ödeme zaten tamamlanmış mı?
      if (payment.status === 'completed') {
        return res.status(200).json({
          success: true,
          data: {
            status: payment.status,
            updatedAt: payment.updatedAt
          }
        });
      }
      
      // TON Explorer üzerinden işlemi kontrol et
      const transactions = await this.tonWeb.getTransactions(process.env.TON_WALLET_ADDRESS, 10);
      
      // İşlem ID içeren mesajı ara
      const matchingTx = transactions.find(tx => 
        tx.in_msg.message && tx.in_msg.message.includes(`payment_id:${paymentId}`)
      );
      
      if (matchingTx) {
        // İşlemi tamamla
        await this.paymentService.completePayment(paymentId, matchingTx.transaction_id);
        
        // İşlemin tipine göre (Star, paket, vb.) ilgili servisi çağır
        if (payment.itemType === 'star') {
          await this.paymentService.addStarsToUser(payment.userId, payment.amount);
        } else if (payment.itemType === 'package') {
          await this.paymentService.activateUserPackage(payment.userId, payment.itemId);
        }
        
        return res.status(200).json({
          success: true,
          data: {
            status: 'completed',
            transactionId: matchingTx.transaction_id,
            updatedAt: new Date()
          }
        });
      }
      
      // İşlem bulunamadı, hala bekliyor
      return res.status(200).json({
        success: true,
        data: {
          status: 'pending',
          updatedAt: payment.updatedAt
        }
      });
      
    } catch (error) {
      console.error('Ödeme kontrol hatası:', error);
      return res.status(500).json({
        success: false,
        message: 'Ödeme durumu kontrol edilirken bir hata oluştu'
      });
    }
  };
  
  // Para çekme işlemi başlat
  initiateWithdrawal = async (req: Request, res: Response) => {
    try {
      const { userId, amount, walletAddress } = req.body;
      
      if (!userId || !amount || amount <= 0 || !walletAddress) {
        return res.status(400).json({
          success: false,
          message: 'Geçersiz parametreler'
        });
      }
      
      // Kullanıcının bakiyesini kontrol et
      const userBalance = await this.paymentService.getUserBalance(userId);
      
      if (userBalance < amount) {
        return res.status(400).json({
          success: false,
          message: 'Yetersiz bakiye'
        });
      }
      
      // Para çekme kaydı oluştur
      const withdrawalId = await this.paymentService.createWithdrawal({
        userId,
        amount,
        currency: 'TON',
        status: 'pending',
        walletAddress
      });
      
      // Yönetici onayına gönder (gerçek uygulamada)
      
      return res.status(200).json({
        success: true,
        data: {
          withdrawalId,
          status: 'pending',
          createdAt: new Date()
        }
      });
    } catch (error) {
      console.error('Para çekme hatası:', error);
      return res.status(500).json({
        success: false,
        message: 'Para çekme işlemi başlatılırken bir hata oluştu'
      });
    }
  };
}