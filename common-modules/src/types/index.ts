export interface User {
  telegramId: string;
  username?: string;
  firstName?: string;
  lastName?: string;
  profilePhoto?: string;
  isShowcu: boolean;
  isAdmin: boolean;
  xp: number;
  badges: string[];
  stars: number;
}

export interface Content {
  _id: string;
  title: string;
  description: string;
  mediaUrl: string;
  thumbnailUrl?: string;
  mediaType: 'image' | 'video' | 'audio' | 'text' | 'collection';
  contentCategory: string;
  tags: string[];
  isPremium: boolean;
  price: number;
  ownerId: string;
  totalViews: number;
  totalLikes: number;
  createdAt: string;
  updatedAt: string;
}

export interface Package {
  _id: string;
  name: string;
  description: string;
  price: number;
  duration: number;
  features: string[];
  ownerId: string;
  createdAt: string;
  updatedAt: string;
}

export interface Task {
  id: number;
  title: string;
  description?: string;
  reward: string;
  rewardType: 'xp' | 'badge' | 'stars';
  rewardValue: number | string;
  verificationType: string;
  verificationRequired: boolean;
  isActive: boolean;
} 