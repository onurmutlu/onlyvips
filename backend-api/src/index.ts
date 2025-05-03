import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import mongoose from 'mongoose';
import { contentRouter } from './routes/content';
import { packageRouter } from './routes/packages';
import { analyticsRouter } from './routes/analytics';
import { authRouter } from './routes/auth';
import { taskRouter } from './routes/tasks';
import { walletRouter } from './routes/wallet';
import { profileRouter } from './routes/profile';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';

dotenv.config();

const app = express();
const port = process.env.PORT || 8000;
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/onlyvips';

// MongoDB bağlantısı
mongoose
  .connect(MONGODB_URI)
  .then(() => console.log('MongoDB bağlantısı başarılı'))
  .catch((err) => console.error('MongoDB bağlantı hatası:', err));

// Güvenlik middleware'leri
app.use(helmet());
app.use(
  rateLimit({
    windowMs: 15 * 60 * 1000, // 15 dakika
    max: 100, // IP başına sınır
    standardHeaders: true,
    legacyHeaders: false,
  })
);

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.use('/api/content', contentRouter);
app.use('/api/packages', packageRouter);
app.use('/api/analytics', analyticsRouter);
app.use('/api/auth', authRouter);
app.use('/api/tasks', taskRouter);
app.use('/api/wallet', walletRouter);
app.use('/api/profile', profileRouter);

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Route not found' });
});

// Error handler
app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error(err.stack);
  res.status(err.status || 500).json({
    error: {
      message: err.message || 'Internal Server Error',
      status: err.status || 500
    }
  });
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
}); 