import { Request, Response, NextFunction } from 'express';
import { verifyToken, extractToken } from '../utils/jwtUtils';
import User from '../models/user';

// Middleware'de gerekli parametreleri eklemek için interface genişletme
export interface AuthRequest extends Request {
  user?: any;
}

// Token doğrulama middleware'i
export const auth = async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const bearerToken = req.headers.authorization;
    const token = extractToken(bearerToken);
    const decoded = verifyToken(token);

    // Kullanıcıyı veritabanında kontrol et
    const user = await User.findOne({ telegramId: decoded.userId });
    if (!user) {
      return res.status(401).json({ message: 'Kimlik doğrulama başarısız - kullanıcı bulunamadı' });
    }

    // Request nesnesine kullanıcı bilgisini ekle
    req.user = user;
    next();
  } catch (error: any) {
    res.status(401).json({ message: `Kimlik doğrulama başarısız: ${error.message}` });
  }
};

// Şovcu rolü kontrolü
export const requireShowcu = (req: AuthRequest, res: Response, next: NextFunction) => {
  if (!req.user || !req.user.isShowcu) {
    return res.status(403).json({ message: 'Bu işlem için şovcu rolü gerekli' });
  }
  next();
}; 