import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Table, Button, Space, Modal, message, Form, Input, Select, InputNumber, Upload } from 'antd';
import { EyeOutlined, EditOutlined, DeleteOutlined, PlusOutlined, UploadOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { contentService } from '../services/content';
import { Content } from '../services/content';

const { Option } = Select;

const ContentPage: React.FC = () => {
  const [contents, setContents] = useState<Content[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [selectedContent, setSelectedContent] = useState<Content | null>(null);
  const [form] = Form.useForm();
  const navigate = useNavigate();

  useEffect(() => {
    fetchContents();
  }, []);

  const fetchContents = async () => {
    try {
      setLoading(true);
      const data = await contentService.getAll();
      setContents(data);
    } catch (error) {
      message.error('İçerikler yüklenirken bir hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const handleView = (content: Content) => {
    navigate(`/content/${content.id}`);
  };

  const handleEdit = (content: Content) => {
    setSelectedContent(content);
    form.setFieldsValue(content);
    setIsModalVisible(true);
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

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();
      if (selectedContent) {
        await contentService.update(selectedContent.id, values);
        message.success('İçerik başarıyla güncellendi');
      } else {
        await contentService.create(values);
        message.success('İçerik başarıyla oluşturuldu');
      }
      setIsModalVisible(false);
      fetchContents();
    } catch (error) {
      message.error('İşlem sırasında bir hata oluştu');
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
      render: (type: string) => type === 'image' ? 'Resim' : 'Video',
    },
    {
      title: 'Görüntülenme',
      dataIndex: 'views',
      key: 'views',
      render: (views: number) => (
        <Statistic value={views} prefix={<EyeOutlined />} />
      ),
    },
    {
      title: 'Fiyat',
      dataIndex: 'price',
      key: 'price',
      render: (price: number) => `${price} TON`,
    },
    {
      title: 'İşlemler',
      key: 'actions',
      render: (_: any, record: Content) => (
        <Space>
          <Button
            type="primary"
            icon={<EyeOutlined />}
            onClick={() => handleView(record)}
          >
            Görüntüle
          </Button>
          <Button
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            Düzenle
          </Button>
          <Button
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record.id)}
          >
            Sil
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Card
            title="İçerik Yönetimi"
            extra={
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => setIsModalVisible(true)}
              >
                Yeni İçerik
              </Button>
            }
          >
            <Table
              columns={columns}
              dataSource={contents}
              loading={loading}
              rowKey="id"
              pagination={{
                pageSize: 10,
                showSizeChanger: true,
                showTotal: (total) => `Toplam ${total} içerik`,
              }}
            />
          </Card>
        </Col>
      </Row>

      <Modal
        title={selectedContent ? 'İçerik Düzenle' : 'Yeni İçerik'}
        open={isModalVisible}
        onOk={handleModalOk}
        onCancel={() => {
          setIsModalVisible(false);
          setSelectedContent(null);
          form.resetFields();
        }}
        width={800}
      >
        <Form
          form={form}
          layout="vertical"
        >
          <Form.Item
            name="title"
            label="Başlık"
            rules={[{ required: true, message: 'Lütfen başlık giriniz' }]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            name="description"
            label="Açıklama"
          >
            <Input.TextArea rows={4} />
          </Form.Item>

          <Form.Item
            name="mediaType"
            label="Medya Türü"
            rules={[{ required: true, message: 'Lütfen medya türü seçiniz' }]}
          >
            <Select>
              <Option value="image">Resim</Option>
              <Option value="video">Video</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="mediaUrl"
            label="Medya URL"
            rules={[{ required: true, message: 'Lütfen medya URL giriniz' }]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            name="isPremium"
            label="Premium İçerik"
            valuePropName="checked"
          >
            <Select>
              <Option value={true}>Evet</Option>
              <Option value={false}>Hayır</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="price"
            label="Fiyat (TON)"
            rules={[{ required: true, message: 'Lütfen fiyat giriniz' }]}
          >
            <InputNumber
              min={0}
              style={{ width: '100%' }}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ContentPage; 