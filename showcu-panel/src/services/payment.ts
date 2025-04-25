import api from './api';

interface Payment {
  id: string;
  userId: string;
  packageId: string;
  amount: number;
  currency: 'TON' | 'USD';
  status: 'pending' | 'completed' | 'failed';
  transactionHash?: string;
  createdAt: string;
  updatedAt: string;
}

interface CreatePaymentData {
  userId: string;
  packageId: string;
  amount: number;
  currency: 'TON' | 'USD';
}

export const paymentService = {
  async getAll() {
    const response = await api.get<Payment[]>('/payments');
    return response.data;
  },

  async getById(id: string) {
    const response = await api.get<Payment>(`/payments/${id}`);
    return response.data;
  },

  async create(data: CreatePaymentData) {
    const response = await api.post<Payment>('/payments', data);
    return response.data;
  },

  async update(id: string, data: Partial<CreatePaymentData>) {
    const response = await api.put<Payment>(`/payments/${id}`, data);
    return response.data;
  },

  async delete(id: string) {
    await api.delete(`/payments/${id}`);
  },

  async getByUserId(userId: string) {
    const response = await api.get(`/payments/user/${userId}`);
    return response.data;
  },

  async getByPackageId(packageId: string) {
    const response = await api.get(`/payments/package/${packageId}`);
    return response.data;
  },

  async getAnalytics(startDate: string, endDate: string) {
    const response = await api.get('/payments/analytics', {
      params: { startDate, endDate }
    });
    return response.data;
  }
}; 