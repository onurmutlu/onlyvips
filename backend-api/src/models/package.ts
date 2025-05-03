import mongoose, { Document, Schema } from 'mongoose';

export interface IPackage extends Document {
  name: string;
  description: string;
  price: number;
  duration: number; // days
  features: string[];
  ownerId: string; // Telegram ID of the showcu
  createdAt: Date;
  updatedAt: Date;
}

const PackageSchema: Schema = new Schema(
  {
    name: { type: String, required: true },
    description: { type: String, required: true },
    price: { type: Number, required: true },
    duration: { type: Number, required: true }, // days
    features: { type: [String], default: [] },
    ownerId: { type: String, required: true },
  },
  { timestamps: true }
);

export default mongoose.model<IPackage>('Package', PackageSchema); 