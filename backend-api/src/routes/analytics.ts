import { Router } from 'express';

const analyticsRouter = Router();

// Get overview analytics
analyticsRouter.get('/overview', (req, res) => {
  res.json({
    totalViews: 1000,
    totalSubscribers: 100,
    totalRevenue: 1000,
    activeSubscribers: 50,
    averageViewDuration: 120,
    topContent: [
      {
        id: '1',
        title: 'En Çok İzlenen İçerik',
        views: 500,
        revenue: 500,
      },
    ],
  });
});

// Get revenue analytics
analyticsRouter.get('/revenue', (req, res) => {
  const { startDate, endDate } = req.query;
  res.json({
    totalRevenue: 1000,
    dailyRevenue: [
      { date: '2024-04-01', revenue: 100 },
      { date: '2024-04-02', revenue: 200 },
      { date: '2024-04-03', revenue: 300 },
    ],
    subscriptionRevenue: 800,
    contentRevenue: 200,
  });
});

// Get content analytics
analyticsRouter.get('/content', (req, res) => {
  res.json([
    {
      id: '1',
      title: 'İçerik 1',
      views: 500,
      likes: 100,
      comments: 50,
      revenue: 500,
    },
  ]);
});

export { analyticsRouter }; 