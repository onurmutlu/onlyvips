import { Router } from 'express';

const contentRouter = Router();

// Get all content
contentRouter.get('/', (req, res) => {
  res.json([
    {
      id: '1',
      title: 'Örnek İçerik 1',
      description: 'Bu bir örnek içeriktir',
      mediaUrl: 'https://example.com/media1.jpg',
      mediaType: 'image',
      isPremium: true,
      price: 9.99,
      createdAt: new Date(),
      updatedAt: new Date(),
    },
  ]);
});

// Get content by ID
contentRouter.get('/:id', (req, res) => {
  const { id } = req.params;
  res.json({
    id,
    title: 'Örnek İçerik',
    description: 'Bu bir örnek içeriktir',
    mediaUrl: 'https://example.com/media1.jpg',
    mediaType: 'image',
    isPremium: true,
    price: 9.99,
    createdAt: new Date(),
    updatedAt: new Date(),
  });
});

// Create content
contentRouter.post('/', (req, res) => {
  const content = req.body;
  res.status(201).json({
    ...content,
    id: '2',
    createdAt: new Date(),
    updatedAt: new Date(),
  });
});

// Update content
contentRouter.put('/:id', (req, res) => {
  const { id } = req.params;
  const content = req.body;
  res.json({
    ...content,
    id,
    updatedAt: new Date(),
  });
});

// Delete content
contentRouter.delete('/:id', (req, res) => {
  const { id } = req.params;
  res.status(204).send();
});

export { contentRouter }; 