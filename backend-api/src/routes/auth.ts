import { Router } from 'express';
import jwt from 'jsonwebtoken';

const authRouter = Router();

// Login
authRouter.post('/login', (req, res) => {
  const { username, password } = req.body;

  // Örnek kullanıcı doğrulama
  if (username === 'admin' && password === 'admin') {
    const token = jwt.sign(
      { userId: '1', username: 'admin' },
      'your-secret-key',
      { expiresIn: '1h' }
    );

    res.json({
      token,
      user: {
        id: '1',
        username: 'admin',
        email: 'admin@example.com',
      },
    });
  } else {
    res.status(401).json({ message: 'Geçersiz kullanıcı adı veya şifre' });
  }
});

// Register
authRouter.post('/register', (req, res) => {
  const { username, email, password } = req.body;

  // Örnek kullanıcı oluşturma
  const token = jwt.sign(
    { userId: '2', username },
    'your-secret-key',
    { expiresIn: '1h' }
  );

  res.status(201).json({
    token,
    user: {
      id: '2',
      username,
      email,
    },
  });
});

// Get current user
authRouter.get('/me', (req, res) => {
  const token = req.headers.authorization?.split(' ')[1];

  if (!token) {
    return res.status(401).json({ message: 'Token bulunamadı' });
  }

  try {
    const decoded = jwt.verify(token, 'your-secret-key');
    res.json({
      id: decoded.userId,
      username: decoded.username,
      email: 'user@example.com',
    });
  } catch (error) {
    res.status(401).json({ message: 'Geçersiz token' });
  }
});

export { authRouter }; 