import { api } from './api';

export interface TonPayment {
  id: string;
  userId: string;
  amount: number;
  status: 'pending' | 'completed' | 'failed';
  transactionHash: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface CreateTonPaymentData {
  amount: number;
  userId: string;
}

export const tonService = {
  createPayment: async (data: CreateTonPaymentData): Promise<TonPayment> => {
    const { data: payment } = await api.post('/api/ton/payments', data);
    return payment;
  },

  verifyPayment: async (transactionHash: string): Promise<TonPayment> => {
    const { data } = await api.post(`/api/ton/payments/verify`, { transactionHash });
    return data;
  },

  getBalance: async (): Promise<number> => {
    const { data } = await api.get('/api/ton/balance');
    return data.balance;
  },

  withdraw: async (amount: number, address: string): Promise<string> => {
    const { data } = await api.post('/api/ton/withdraw', { amount, address });
    return data.transactionHash;
  }
}; 