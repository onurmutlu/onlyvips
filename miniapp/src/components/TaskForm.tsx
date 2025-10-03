import React, { useState } from 'react';
import api from '../api/apiClient';
import '../styles/TaskForm.css';

interface TaskFormProps {
  creatorId: string;
  onSuccess?: () => void;
  onCancel?: () => void;
}

const TaskForm: React.FC<TaskFormProps> = ({ creatorId, onSuccess, onCancel }) => {
  const [title, setTitle] = useState('');
  const [taskType, setTaskType] = useState('follow');
  const [reward, setReward] = useState('10');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const taskTypes = [
    { id: 'follow', label: 'Takip' },
    { id: 'message', label: 'Mesaj' },
    { id: 'watch', label: 'İçerik İzleme' },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Ödül miktarını sayıya çevir
      const rewardAmount = parseInt(reward, 10);
      
      if (isNaN(rewardAmount) || rewardAmount <= 0) {
        throw new Error('Lütfen geçerli bir ödül miktarı girin');
      }

      // API isteği için veri
      const taskData = {
        creatorId,
        title,
        taskType,
        reward: rewardAmount
      };

      // Backend'e gönder
      const response = await api.creators.createTask(creatorId, taskData);

      if (!response.success) {
        throw new Error(response.error || 'Görev oluşturulurken bir hata oluştu');
      }

      // Başarılı olunca
      if (onSuccess) {
        onSuccess();
      }
      
      // Form alanlarını temizle
      setTitle('');
      setTaskType('follow');
      setReward('10');
      
    } catch (err: any) {
      setError(err.message || 'Bir hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="task-form">
      <h2>Yeni Görev Oluştur</h2>
      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="task-title">Görev Başlığı</label>
          <input
            id="task-title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Görev başlığı girin"
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="task-type">Görev Tipi</label>
          <select
            id="task-type"
            value={taskType}
            onChange={(e) => setTaskType(e.target.value)}
            required
          >
            {taskTypes.map(type => (
              <option key={type.id} value={type.id}>
                {type.label}
              </option>
            ))}
          </select>
        </div>
        
        <div className="form-group">
          <label htmlFor="task-reward">Ödül (Token Miktarı)</label>
          <input
            id="task-reward"
            type="number"
            min="1"
            step="1"
            value={reward}
            onChange={(e) => setReward(e.target.value)}
            placeholder="Token miktarı"
            required
          />
        </div>
        
        <div className="form-actions">
          <button 
            type="button" 
            onClick={onCancel}
            disabled={loading}
            className="cancel-button"
          >
            İptal
          </button>
          <button 
            type="submit" 
            disabled={loading}
            className="submit-button"
          >
            {loading ? 'Oluşturuluyor...' : 'Görev Oluştur'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default TaskForm; 