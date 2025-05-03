import { Router } from 'express';
import { auth, AuthRequest } from '../middleware/authMiddleware';
import Task from '../models/task';
import User from '../models/user';
import Verification from '../models/verification';

const taskRouter = Router();

// Get all tasks
taskRouter.get('/', async (req, res) => {
  try {
    const tasks = await Task.find({ isActive: true });
    res.json({ tasks });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// Complete task
taskRouter.post('/complete', auth, async (req: AuthRequest, res) => {
  try {
    const { taskId, verificationData } = req.body;
    const userId = req.user.telegramId;

    // Görevi bul
    const task = await Task.findOne({ id: taskId, isActive: true });
    if (!task) {
      return res.status(404).json({ error: 'Görev bulunamadı', status: 'error' });
    }

    // Kullanıcıyı bul
    const user = await User.findOne({ telegramId: userId });
    if (!user) {
      return res.status(404).json({ error: 'Kullanıcı bulunamadı', status: 'error' });
    }

    // Görev zaten tamamlanmış mı kontrol et
    if (user.completedTasks.includes(taskId)) {
      return res.status(400).json({ message: 'Bu görev zaten tamamlandı', status: 'warning' });
    }

    // Doğrulama gerekiyor mu kontrol et
    if (task.verificationRequired) {
      // Bekleyen doğrulama var mı kontrol et
      let verification = await Verification.findOne({ userId, taskId });
      
      if (verification) {
        // Doğrulama zaten var, durumunu kontrol et
        if (verification.verified) {
          // Görevi tamamlandı olarak işaretle
          if (user.pendingTasks.includes(taskId)) {
            user.pendingTasks = user.pendingTasks.filter(id => id !== taskId);
          }
          
          // Tamamlananlara ekle
          if (!user.completedTasks.includes(taskId)) {
            user.completedTasks.push(taskId);
          }
          
          // Ödülü ver
          const rewardMessage = await awardReward(user, task);
          await user.save();
          
          // Doğrulama tamamlandı
          verification.completedAt = new Date();
          await verification.save();
          
          return res.json({ 
            message: rewardMessage, 
            status: 'ok', 
            user: {
              telegramId: user.telegramId,
              xp: user.xp,
              badges: user.badges,
              completedTasks: user.completedTasks,
              pendingTasks: user.pendingTasks
            }
          });
        } else {
          // Doğrulama hala bekliyor
          return res.json({
            message: 'Görevin doğrulanması bekleniyor',
            status: 'pending',
            verificationType: task.verificationType,
            user: {
              telegramId: user.telegramId,
              xp: user.xp,
              badges: user.badges,
              completedTasks: user.completedTasks,
              pendingTasks: user.pendingTasks
            }
          });
        }
      }
      
      // Yeni bir doğrulama başlat
      verification = new Verification({
        userId,
        taskId,
        verificationType: task.verificationType,
        verificationData,
        requestTime: new Date(),
        verified: false
      });
      
      await verification.save();
      
      // Kullanıcının bekleyen görevlerine ekle
      if (!user.pendingTasks.includes(taskId)) {
        user.pendingTasks.push(taskId);
        await user.save();
      }
      
      // DEV ortamında test için bazı görevleri otomatik doğrula
      if (process.env.NODE_ENV === 'development' && [2, 4, 6].includes(taskId)) {
        verification.verified = true;
        await verification.save();
        return res.json({
          message: 'Test ortamında otomatik doğrulama yapıldı. Lütfen sayfayı yenileyin.',
          status: 'pending',
          verificationType: task.verificationType,
          user: {
            telegramId: user.telegramId,
            xp: user.xp,
            badges: user.badges,
            completedTasks: user.completedTasks,
            pendingTasks: user.pendingTasks
          }
        });
      }
      
      return res.json({
        message: `Görev doğrulanıyor. '${task.verificationType}' türünde doğrulama gerekiyor.`,
        status: 'pending',
        verificationType: task.verificationType,
        user: {
          telegramId: user.telegramId,
          xp: user.xp,
          badges: user.badges,
          completedTasks: user.completedTasks,
          pendingTasks: user.pendingTasks
        }
      });
    } else {
      // Doğrulama gerektirmeyen görevler için doğrudan tamamla
      if (!user.completedTasks.includes(taskId)) {
        user.completedTasks.push(taskId);
      }
      
      // Ödülü ver
      const rewardMessage = await awardReward(user, task);
      await user.save();
      
      return res.json({ 
        message: rewardMessage, 
        status: 'ok', 
        user: {
          telegramId: user.telegramId,
          xp: user.xp,
          badges: user.badges,
          completedTasks: user.completedTasks,
          pendingTasks: user.pendingTasks
        }
      });
    }
  } catch (error: any) {
    console.error('Görev tamamlama hatası:', error);
    res.status(500).json({ error: error.message, status: 'error' });
  }
});

// Admin task verification endpoint
taskRouter.post('/admin/verify', auth, async (req: AuthRequest, res) => {
  try {
    const { userId, taskId, verified } = req.body;
    
    // Admin kontrolü
    if (!req.user.isAdmin) {
      return res.status(403).json({ error: 'Yetkisiz erişim', status: 'error' });
    }
    
    // Doğrulamayı bul
    const verification = await Verification.findOne({ userId, taskId });
    if (!verification) {
      return res.status(404).json({ error: 'Bekleyen doğrulama bulunamadı', status: 'error' });
    }
    
    // Doğrulama durumunu güncelle
    verification.verified = verified;
    if (verified) {
      verification.completedAt = new Date();
    }
    await verification.save();
    
    return res.json({ message: 'Görev doğrulama durumu güncellendi', status: 'ok' });
  } catch (error: any) {
    res.status(500).json({ error: error.message, status: 'error' });
  }
});

// Helper function to award rewards
async function awardReward(user: any, task: any) {
  let rewardMessage = '';
  
  if (task.rewardType === 'xp') {
    user.xp += task.rewardValue;
    rewardMessage = `+${task.rewardValue} XP kazandın!`;
  } else if (task.rewardType === 'badge') {
    if (!user.badges.includes(task.rewardValue)) {
      user.badges.push(task.rewardValue);
    }
    rewardMessage = `'${task.rewardValue}' rozetini kazandın!`;
  } else if (task.rewardType === 'stars') {
    user.stars += task.rewardValue;
    rewardMessage = `+${task.rewardValue} Star kazandın!`;
  }
  
  return rewardMessage;
}

// Get all pending verifications (admin)
taskRouter.get('/admin/verifications', auth, async (req: AuthRequest, res) => {
  try {
    // Admin kontrolü
    if (!req.user.isAdmin) {
      return res.status(403).json({ error: 'Yetkisiz erişim', status: 'error' });
    }
    
    const verifications = await Verification.find({ verified: false, completedAt: null })
      .sort({ requestTime: -1 })
      .limit(100);
    
    res.json({ verifications });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

export { taskRouter }; 