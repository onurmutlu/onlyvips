import mongoose, { Document, Schema } from 'mongoose';

export interface IContent extends Document {
  title: string;
  description: string;
  mediaUrl: string;
  thumbnailUrl?: string;
  mediaType: 'image' | 'video' | 'audio' | 'text' | 'collection';
  contentCategory: string;
  tags: string[];
  isPremium: boolean;
  price: number;
  ownerId: string; // Telegram ID of the showcu
  totalViews: number;
  totalLikes: number;
  requiredPackageId?: mongoose.Types.ObjectId;
  createdAt: Date;
  updatedAt: Date;
}

const ContentSchema: Schema = new Schema(
  {
    title: { type: String, required: true },
    description: { type: String, required: true },
    mediaUrl: { type: String, required: true },
    thumbnailUrl: { type: String },
    mediaType: { 
      type: String, 
      required: true, 
      enum: ['image', 'video', 'audio', 'text', 'collection'] 
    },
    contentCategory: { type: String, required: true },
    tags: { type: [String], default: [] },
    isPremium: { type: Boolean, default: false },
    price: { type: Number, default: 0 },
    ownerId: { type: String, required: true },
    totalViews: { type: Number, default: 0 },
    totalLikes: { type: Number, default: 0 },
    requiredPackageId: { type: Schema.Types.ObjectId, ref: 'Package' },
  },
  { timestamps: true }
);

// İçerik indeksleri oluştur
ContentSchema.index({ tags: 1 });
ContentSchema.index({ ownerId: 1 });
ContentSchema.index({ contentCategory: 1 });
ContentSchema.index({ title: 'text', description: 'text', tags: 'text' });

export default mongoose.model<IContent>('Content', ContentSchema); 