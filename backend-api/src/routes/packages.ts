import { Router } from 'express';

const packageRouter = Router();

// Get all packages
packageRouter.get('/', (req, res) => {
  res.json([
    {
      id: '1',
      name: 'Bronze Paket',
      description: 'Temel özellikler',
      price: 9.99,
      duration: 30,
      features: ['Özellik 1', 'Özellik 2'],
      createdAt: new Date(),
      updatedAt: new Date(),
    },
  ]);
});

// Get package by ID
packageRouter.get('/:id', (req, res) => {
  const { id } = req.params;
  res.json({
    id,
    name: 'Bronze Paket',
    description: 'Temel özellikler',
    price: 9.99,
    duration: 30,
    features: ['Özellik 1', 'Özellik 2'],
    createdAt: new Date(),
    updatedAt: new Date(),
  });
});

// Create package
packageRouter.post('/', (req, res) => {
  const packageData = req.body;
  res.status(201).json({
    ...packageData,
    id: '2',
    createdAt: new Date(),
    updatedAt: new Date(),
  });
});

// Update package
packageRouter.put('/:id', (req, res) => {
  const { id } = req.params;
  const packageData = req.body;
  res.json({
    ...packageData,
    id,
    updatedAt: new Date(),
  });
});

// Delete package
packageRouter.delete('/:id', (req, res) => {
  const { id } = req.params;
  res.status(204).send();
});

export { packageRouter }; 