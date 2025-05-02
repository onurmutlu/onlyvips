import React, { useState, useEffect } from 'react';
import { Table, Button, Space, message, Popconfirm } from 'antd';
import { PlusOutlined, EyeOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { contentService } from '../services/content';
import ContentModal from '../components/content/ContentModal';
import { useNavigate } from 'react-router-dom';

const MyContents: React.FC = () => {
  const [contents, setContents] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [selectedContent, setSelectedContent] = useState<any>(null);
  const navigate = useNavigate();

  const fetchContents = async () => {
    setLoading(true);
    try {
      const data = await contentService.getAll();
      setContents(data);
    } catch (error) {
      message.error('İçerikler yüklenirken bir hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchContents();
  }, []);

  const handleView = (content: any) => {
    navigate(`/content/${content.id}`);
  };

  const handleEdit = (content: any) => {
    setSelectedContent(content);
    setModalVisible(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await contentService.delete(id);
      message.success('İçerik başarıyla silindi');
      fetchContents();
    } catch (error) {
      message.error('İçerik silinirken bir hata oluştu');
    }
  };

  const columns = [
    {
      title: 'Başlık',
      dataIndex: 'title',
      key: 'title',
    },
    {
      title: 'Tür',
      dataIndex: 'mediaType',
      key: 'mediaType',
      render: (type: string) => type === 'image' ? 'Fotoğraf' : 'Video',
    },
    {
      title: 'Görüntülenme',
      dataIndex: 'views',
      key: 'views',
    },
    {
      title: 'Fiyat (TON)',
      dataIndex: 'price',
      key: 'price',
    },
    {
      title: 'İşlemler',
      key: 'actions',
      render: (_: any, record: any) => (
        <Space size="middle">
          <Button
            type="text"
            icon={<EyeOutlined />}
            onClick={() => handleView(record)}
          />
          <Button
            type="text"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          />
          <Popconfirm
            title="İçeriği silmek istediğinizden emin misiniz?"
            onConfirm={() => handleDelete(record.id)}
            okText="Evet"
            cancelText="Hayır"
          >
            <Button type="text" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-white">İçeriklerim</h1>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => {
            setSelectedContent(null);
            setModalVisible(true);
          }}
        >
          Yeni İçerik
        </Button>
      </div>

      <div className="bg-gray-800 rounded-lg p-6 backdrop-blur-lg bg-opacity-50">
        <Table
          columns={columns}
          dataSource={contents}
          loading={loading}
          rowKey="id"
          className="[&_.ant-table-thead>tr>th]:bg-gray-700 [&_.ant-table-tbody>tr>td]:bg-gray-800 [&_.ant-table-tbody>tr:hover>td]:bg-gray-700"
        />
      </div>

      <ContentModal
        visible={modalVisible}
        onClose={() => setModalVisible(false)}
        onSuccess={fetchContents}
        content={selectedContent}
      />
    </div>
  );
};

export default MyContents; 