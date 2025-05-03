import api from './index';
import { Package } from '../types';

export interface PackageListParams {
  page?: number;
  limit?: number;
  ownerId?: string;
}

export interface PackageListResponse {
  packages: Package[];
  pagination: {
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  };
}

export interface PackageDetailResponse {
  package: Package;
  owner: {
    telegramId: string;
    username?: string;
    firstName?: string;
    lastName?: string;
    profilePhoto?: string;
  } | null;
}

export interface SubscriptionResponse {
  message: string;
  subscription: {
    packageId: string;
    packageName: string;
    purchaseDate: string;
    expiryDate: string;
    active: boolean;
  };
}

// Paket listesi al
export const getPackageList = async (params: PackageListParams = {}): Promise<PackageListResponse> => {
  const response = await api.get<PackageListResponse>('/api/packages', { params });
  return response.data;
};

// Paket detayı al
export const getPackageDetail = async (id: string): Promise<PackageDetailResponse> => {
  const response = await api.get<PackageDetailResponse>(`/api/packages/${id}`);
  return response.data;
};

// Paket oluştur
export const createPackage = async (packageData: Partial<Package>): Promise<{ package: Package }> => {
  const response = await api.post<{ package: Package }>('/api/packages', packageData);
  return response.data;
};

// Paketi güncelle
export const updatePackage = async (id: string, packageData: Partial<Package>): Promise<{ package: Package }> => {
  const response = await api.put<{ package: Package }>(`/api/packages/${id}`, packageData);
  return response.data;
};

// Paketi sil
export const deletePackage = async (id: string): Promise<{ message: string }> => {
  const response = await api.delete<{ message: string }>(`/api/packages/${id}`);
  return response.data;
};

// Pakete abone ol
export const subscribeToPackage = async (id: string, transactionHash: string): Promise<SubscriptionResponse> => {
  const response = await api.post<SubscriptionResponse>(`/api/packages/${id}/subscribe`, { transactionHash });
  return response.data;
}; 