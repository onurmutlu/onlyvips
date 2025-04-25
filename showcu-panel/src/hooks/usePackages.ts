import { create } from 'zustand';
import { packageService } from '../services';

interface Package {
  id: string;
  name: string;
  description: string;
  price: number;
  duration: number;
  features: string[];
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

interface PackagesState {
  packages: Package[];
  loading: boolean;
  error: string | null;
  fetchPackages: () => Promise<void>;
  createPackage: (data: {
    name: string;
    description: string;
    price: number;
    duration: number;
    features: string[];
  }) => Promise<void>;
  updatePackage: (id: string, data: Partial<Package>) => Promise<void>;
  deletePackage: (id: string) => Promise<void>;
}

export const usePackages = create<PackagesState>((set) => ({
  packages: [],
  loading: false,
  error: null,
  fetchPackages: async () => {
    try {
      set({ loading: true, error: null });
      const packages = await packageService.getAll();
      set({ packages, loading: false });
    } catch (error) {
      set({ error: (error as Error).message, loading: false });
    }
  },
  createPackage: async (data) => {
    try {
      set({ loading: true, error: null });
      const newPackage = await packageService.create(data);
      set((state) => ({
        packages: [...state.packages, newPackage],
        loading: false
      }));
    } catch (error) {
      set({ error: (error as Error).message, loading: false });
    }
  },
  updatePackage: async (id, data) => {
    try {
      set({ loading: true, error: null });
      const updatedPackage = await packageService.update(id, data);
      set((state) => ({
        packages: state.packages.map((pkg) =>
          pkg.id === id ? updatedPackage : pkg
        ),
        loading: false
      }));
    } catch (error) {
      set({ error: (error as Error).message, loading: false });
    }
  },
  deletePackage: async (id) => {
    try {
      set({ loading: true, error: null });
      await packageService.delete(id);
      set((state) => ({
        packages: state.packages.filter((pkg) => pkg.id !== id),
        loading: false
      }));
    } catch (error) {
      set({ error: (error as Error).message, loading: false });
    }
  }
})); 