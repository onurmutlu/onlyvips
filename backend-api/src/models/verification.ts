import mongoose, { Document, Schema } from 'mongoose';

export interface IVerification extends Document {
  userId: string; // Telegram ID
  taskId: number;
  verificationType: string;
  verificationData: any;
  requestTime: Date;
  verified: boolean;
  completedAt?: Date;
  createdAt: Date;
  updatedAt: Date;
}

const VerificationSchema: Schema = new Schema(
  {
    userId: { type: String, required: true },
    taskId: { type: Number, required: true },
    verificationType: { type: String, required: true },
    verificationData: { type: Schema.Types.Mixed },
    requestTime: { type: Date, default: Date.now },
    verified: { type: Boolean, default: false },
    completedAt: { type: Date },
  },
  { timestamps: true }
);

// Composite index for userId and taskId
VerificationSchema.index({ userId: 1, taskId: 1 }, { unique: true });

export default mongoose.model<IVerification>('Verification', VerificationSchema); 