import { api } from './api';

export interface Task {
  id: string;
  title: string;
  taskType: 'follow' | 'message' | 'watch';
  reward: number;
  createdAt: string;
  completionCount: number;
  isActive: boolean;
  creatorId: string;
}

export interface CreateTaskData {
  title: string;
  taskType: 'follow' | 'message' | 'watch';
  reward: number;
}

export const taskService = {
  getAll: async (): Promise<Task[]> => {
    const { data } = await api.get('/api/tasks');
    return data;
  },
  
  getCreatorTasks: async (creatorId: string): Promise<Task[]> => {
    const { data } = await api.get(`/api/creators/${creatorId}/tasks`);
    return data;
  },

  getById: async (id: string): Promise<Task> => {
    const { data } = await api.get(`/api/tasks/${id}`);
    return data;
  },
  
  getTaskCompletions: async (taskId: string) => {
    const { data } = await api.get(`/api/tasks/${taskId}/completions`);
    return data;
  },

  create: async (data: CreateTaskData): Promise<Task> => {
    const { data: response } = await api.post('/api/tasks', data);
    return response;
  },

  update: async (id: string, data: Partial<CreateTaskData>): Promise<Task> => {
    const { data: response } = await api.put(`/api/tasks/${id}`, data);
    return response;
  },

  toggleStatus: async (id: string, isActive: boolean): Promise<Task> => {
    const { data: response } = await api.patch(`/api/tasks/${id}/status`, { isActive });
    return response;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/api/tasks/${id}`);
  },
}; 