import mongoose, { Document, Schema } from 'mongoose';
import bcrypt from 'bcrypt';

export interface IUser extends Document {
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
  wallet: {
    tonAddress?: string;
    balance: number;
  };
  completedTasks: number[];
  pendingTasks: number[];
  vipPackages: {
    packageId: mongoose.Types.ObjectId;
    purchaseDate: Date;
    expiryDate: Date;
    active: boolean;
  }[];
  createdAt: Date;
  updatedAt: Date;
  comparePassword(candidatePassword: string): Promise<boolean>;
}

const UserSchema: Schema = new Schema(
  {
    telegramId: { type: String, required: true, unique: true },
    username: { type: String },
    firstName: { type: String },
    lastName: { type: String },
    profilePhoto: { type: String },
    isShowcu: { type: Boolean, default: false },
    isAdmin: { type: Boolean, default: false },
    xp: { type: Number, default: 0 },
    badges: { type: [String], default: [] },
    stars: { type: Number, default: 0 },
    wallet: {
      tonAddress: { type: String },
      balance: { type: Number, default: 0 },
    },
    completedTasks: { type: [Number], default: [] },
    pendingTasks: { type: [Number], default: [] },
    vipPackages: [
      {
        packageId: { type: Schema.Types.ObjectId, ref: 'Package' },
        purchaseDate: { type: Date },
        expiryDate: { type: Date },
        active: { type: Boolean, default: true },
      },
    ],
  },
  { timestamps: true }
);

// Şifre karşılaştırma methodu - JWT token doğrulaması için
UserSchema.methods.comparePassword = async function (
  candidatePassword: string
): Promise<boolean> {
  try {
    return await bcrypt.compare(candidatePassword, this.password);
  } catch (error) {
    throw error;
  }
};

export default mongoose.model<IUser>('User', UserSchema); 