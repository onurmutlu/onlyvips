import mongoose, { Document, Schema } from 'mongoose';

export interface ITask extends Document {
  id: number;
  title: string;
  description?: string;
  reward: string;
  rewardType: 'xp' | 'badge' | 'stars';
  rewardValue: number | string;
  verificationType: 'bot_mention' | 'channel_join' | 'group_join' | 'forward_message' | 
                    'post_share' | 'deeplink_track' | 'pin_check' | 'message' | 
                    'referral' | 'invite_tracker' | 'share_count' | 'manual' | 'none';
  verificationRequired: boolean;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

const TaskSchema: Schema = new Schema(
  {
    id: { type: Number, required: true, unique: true },
    title: { type: String, required: true },
    description: { type: String },
    reward: { type: String, required: true },
    rewardType: { 
      type: String, 
      required: true, 
      enum: ['xp', 'badge', 'stars']
    },
    rewardValue: { 
      type: Schema.Types.Mixed, 
      required: true 
    },
    verificationType: { 
      type: String, 
      required: true,
      enum: [
        'bot_mention', 'channel_join', 'group_join', 'forward_message',
        'post_share', 'deeplink_track', 'pin_check', 'message',
        'referral', 'invite_tracker', 'share_count', 'manual', 'none'
      ]
    },
    verificationRequired: { type: Boolean, default: true },
    isActive: { type: Boolean, default: true },
  },
  { timestamps: true }
);

export default mongoose.model<ITask>('Task', TaskSchema); 