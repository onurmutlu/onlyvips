import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Button, Tag, Statistic, Space, message } from 'antd';
import { ArrowLeftOutlined, EyeOutlined, DollarOutlined, LockOutlined } from '@ant-design/icons';
import { contentService } from '../services/content';

const ContentDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [content, setContent] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState<any>(null);

  useEffect(() => {
    fetchContent();
    fetchAnalytics();
  }, [id]);

  const fetchContent = async () => {
    try {
      const data = await contentService.getById(id!);
      setContent(data);
    } catch (error) {
      message.error('İçerik yüklenirken bir hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const data = await contentService.getAnalytics(id!);
      setAnalytics(data);
    } catch (error) {
      message.error('Analiz verileri yüklenirken bir hata oluştu');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-indigo-900 text-white flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  if (!content) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-indigo-900 text-white flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-4xl font-bold mb-4">İçerik Bulunamadı</h1>
          <Button
            type="primary"
            onClick={() => navigate('/content')}
            className="bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 border-0"
          >
            Geri Dön
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-indigo-900 text-white">
      <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))]"></div>
      
      <div className="container mx-auto px-4 py-8 relative z-10">
        <Button
          type="text"
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate('/content')}
          className="mb-8 text-white/60 hover:text-white"
        >
          Geri Dön
        </Button>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <Card className="bg-white/5 backdrop-blur-lg border-0 shadow-xl mb-8">
              {content.mediaType === 'image' ? (
                <img
                  src={content.mediaUrl}
                  alt={content.title}
                  className="w-full h-auto rounded-lg"
                />
              ) : (
                <video
                  src={content.mediaUrl}
                  controls
                  className="w-full rounded-lg"
                />
              )}
            </Card>

            <Card className="bg-white/5 backdrop-blur-lg border-0 shadow-xl">
              <h1 className="text-3xl font-bold mb-4">{content.title}</h1>
              <p className="text-white/60 mb-6">{content.description}</p>
              
              <div className="flex flex-wrap gap-4 mb-6">
                <Tag color={content.mediaType === 'image' ? 'blue' : 'purple'}>
                  {content.mediaType === 'image' ? 'Fotoğraf' : 'Video'}
                </Tag>
                <Tag color={content.isPremium ? 'gold' : 'green'}>
                  {content.isPremium ? 'Premium' : 'Ücretsiz'}
                </Tag>
                {content.isPremium && (
                  <Tag color="purple" icon={<DollarOutlined />}>
                    {content.price} TON
                  </Tag>
                )}
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <Statistic
                  title="Görüntülenme"
                  value={analytics?.views || 0}
                  prefix={<EyeOutlined />}
                  valueStyle={{ color: '#fff' }}
                  className="text-white"
                />
                <Statistic
                  title="Kazanç"
                  value={analytics?.revenue || 0}
                  prefix={<DollarOutlined />}
                  suffix="TON"
                  valueStyle={{ color: '#fff' }}
                  className="text-white"
                />
                <Statistic
                  title="Satın Alma"
                  value={analytics?.purchases || 0}
                  prefix={<LockOutlined />}
                  valueStyle={{ color: '#fff' }}
                  className="text-white"
                />
                <Statistic
                  title="Beğeni"
                  value={analytics?.likes || 0}
                  valueStyle={{ color: '#fff' }}
                  className="text-white"
                />
              </div>
            </Card>
          </div>

          <div>
            <Card className="bg-white/5 backdrop-blur-lg border-0 shadow-xl">
              <h2 className="text-xl font-bold mb-4">İçerik Detayları</h2>
              
              <div className="space-y-4">
                <div>
                  <p className="text-white/60">Oluşturulma Tarihi</p>
                  <p className="font-medium">
                    {new Date(content.createdAt).toLocaleDateString('tr-TR')}
                  </p>
                </div>
                
                <div>
                  <p className="text-white/60">Son Güncelleme</p>
                  <p className="font-medium">
                    {new Date(content.updatedAt).toLocaleDateString('tr-TR')}
                  </p>
                </div>

                <div>
                  <p className="text-white/60">İçerik ID</p>
                  <p className="font-medium">{content.id}</p>
                </div>

                <div>
                  <p className="text-white/60">Medya URL</p>
                  <p className="font-medium break-all">{content.mediaUrl}</p>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ContentDetail; 