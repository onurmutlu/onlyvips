import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { contentRouter } from './routes/content';
import { packageRouter } from './routes/packages';
import { analyticsRouter } from './routes/analytics';
import { authRouter } from './routes/auth';

dotenv.config();

const app = express();
const port = process.env.PORT || 8000;

app.use(cors());
app.use(express.json());

// Routes
app.use('/api/content', contentRouter);
app.use('/api/packages', packageRouter);
app.use('/api/analytics', analyticsRouter);
app.use('/api/auth', authRouter);

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
}); 