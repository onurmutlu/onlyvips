import React, { useEffect, useState } from 'react';
import { Card, Button, Input, Upload, message, Modal, Form, Select, Spin } from 'antd';
import { PlusOutlined, UploadOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { useContent } from '../hooks/useContent';
import { storageService } from '../services';
import { formatCurrency } from '../utils/format';

const { TextArea } = Input;
const { Option } = Select;

interface ContentFormData {
  title: string;
  description: string;
  mediaType: 'image' | 'video' | 'audio';
  isPremium: boolean;
  price: number;
}

const Content: React.FC = () => {
  const { contents, loading, error, fetchContents, createContent, updateContent, deleteContent } = useContent();
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingContent, setEditingContent] = useState<string | null>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchContents();
  }, []);

  const handleUpload = async (file: File) => {
    try {
      const response = await storageService.uploadFile(file);
      return response.url;
    } catch (error) {
      message.error('Dosya yüklenirken bir hata oluştu');
      throw error;
    }
  };

  const handleSubmit = async (values: ContentFormData) => {
    try {
      if (editingContent) {
        await updateContent(editingContent, values);
        message.success('İçerik güncellendi');
      } else {
        await createContent(values);
        message.success('İçerik oluşturuldu');
      }
      setIsModalVisible(false);
      form.resetFields();
      setEditingContent(null);
    } catch (error) {
      message.error('Bir hata oluştu');
    }
  };

  const handleEdit = (content: any) => {
    setEditingContent(content.id);
    form.setFieldsValue(content);
    setIsModalVisible(true);
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteContent(id);
      message.success('İçerik silindi');
    } catch (error) {
      message.error('Bir hata oluştu');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Spin size="large" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Card className="w-full max-w-md">
          <div className="text-red-500 text-center">{error}</div>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold mb-2">İçeriklerim</h1>
          <p className="text-gray-500">İçeriklerinizi yönetin ve yeni içerikler ekleyin</p>
        </div>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => setIsModalVisible(true)}
        >
          Yeni İçerik
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {contents.map((content) => (
          <Card
            key={content.id}
            className="h-full"
            cover={
              <div className="aspect-video bg-gray-100 flex items-center justify-center">
                {content.mediaType === 'image' ? (
                  <img
                    src={content.mediaUrl}
                    alt={content.title}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="text-gray-400">
                    {content.mediaType === 'video' ? 'Video' : 'Ses'}
                  </div>
                )}
              </div>
            }
            actions={[
              <Button
                key="edit"
                type="text"
                icon={<EditOutlined />}
                onClick={() => handleEdit(content)}
              />,
              <Button
                key="delete"
                type="text"
                danger
                icon={<DeleteOutlined />}
                onClick={() => handleDelete(content.id)}
              />,
            ]}
          >
            <Card.Meta
              title={content.title}
              description={
                <div>
                  <p className="mb-2">{content.description}</p>
                  <div className="flex justify-between items-center">
                    <span className={`px-2 py-1 rounded ${
                      content.isPremium ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'
                    }`}>
                      {content.isPremium ? 'Premium' : 'Ücretsiz'}
                    </span>
                    {content.isPremium && (
                      <span className="font-semibold">{formatCurrency(content.price)}</span>
                    )}
                  </div>
                </div>
              }
            />
          </Card>
        ))}
      </div>

      <Modal
        title={editingContent ? 'İçerik Düzenle' : 'Yeni İçerik'}
        open={isModalVisible}
        onCancel={() => {
          setIsModalVisible(false);
          form.resetFields();
          setEditingContent(null);
        }}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            name="title"
            label="Başlık"
            rules={[{ required: true, message: 'Lütfen başlık girin' }]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            name="description"
            label="Açıklama"
            rules={[{ required: true, message: 'Lütfen açıklama girin' }]}
          >
            <TextArea rows={4} />
          </Form.Item>

          <Form.Item
            name="mediaType"
            label="Medya Türü"
            rules={[{ required: true, message: 'Lütfen medya türü seçin' }]}
          >
            <Select>
              <Option value="image">Görsel</Option>
              <Option value="video">Video</Option>
              <Option value="audio">Ses</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="mediaUrl"
            label="Medya"
            rules={[{ required: true, message: 'Lütfen medya yükleyin' }]}
          >
            <Upload
              customRequest={async ({ file, onSuccess, onError }) => {
                try {
                  const url = await handleUpload(file as File);
                  form.setFieldValue('mediaUrl', url);
                  onSuccess?.('ok');
                } catch (error) {
                  onError?.(error as Error);
                }
              }}
              showUploadList={false}
            >
              <Button icon={<UploadOutlined />}>Yükle</Button>
            </Upload>
          </Form.Item>

          <Form.Item
            name="isPremium"
            label="Premium İçerik"
            valuePropName="checked"
          >
            <Select>
              <Option value={false}>Ücretsiz</Option>
              <Option value={true}>Premium</Option>
            </Select>
          </Form.Item>

          <Form.Item
            noStyle
            shouldUpdate={(prevValues, currentValues) =>
              prevValues.isPremium !== currentValues.isPremium
            }
          >
            {({ getFieldValue }) =>
              getFieldValue('isPremium') ? (
                <Form.Item
                  name="price"
                  label="Fiyat"
                  rules={[{ required: true, message: 'Lütfen fiyat girin' }]}
                >
                  <Input type="number" min={0} step={0.01} />
                </Form.Item>
              ) : null
            }
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" className="w-full">
              {editingContent ? 'Güncelle' : 'Oluştur'}
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Content; 