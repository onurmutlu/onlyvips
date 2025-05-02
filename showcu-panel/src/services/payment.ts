import { api } from './api';

export interface Payment {
  id: string;
  userId: string;
  packageId: string;
  amount: number;
  currency: string;
  status: 'pending' | 'completed' | 'failed' | 'refunded';
  paymentMethod: 'ton' | 'credit_card' | 'bank_transfer';
  transactionId?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface CreatePaymentData {
  packageId: string;
  paymentMethod: 'ton' | 'credit_card' | 'bank_transfer';
  amount: number;
  currency: string;
}

export const paymentService = {
  getAll: async (): Promise<Payment[]> => {
    const { data } = await api.get('/api/payments');
    return data;
  },

  getById: async (id: string): Promise<Payment> => {
    const { data } = await api.get(`/api/payments/${id}`);
    return data;
  },

  create: async (data: CreatePaymentData): Promise<Payment> => {
    const { data: createdPayment } = await api.post('/api/payments', data);
    return createdPayment;
  },

  verify: async (id: string): Promise<Payment> => {
    const { data } = await api.post(`/api/payments/${id}/verify`);
    return data;
  },

  refund: async (id: string): Promise<Payment> => {
    const { data } = await api.post(`/api/payments/${id}/refund`);
    return data;
  },

  getHistory: async (userId: string): Promise<Payment[]> => {
    const { data } = await api.get(`/api/payments/history/${userId}`);
    return data;
  },

  getByUserId: async (userId: string): Promise<Payment[]> => {
    const { data } = await api.get(`/api/payments/user/${userId}`);
    return data;
  },

  getByPackageId: async (packageId: string): Promise<Payment[]> => {
    const { data } = await api.get(`/api/payments/package/${packageId}`);
    return data;
  },

  getAnalytics: async (startDate: string, endDate: string): Promise<any> => {
    const { data } = await api.get('/api/payments/analytics', {
      params: { startDate, endDate }
    });
    return data;
  }
}; 