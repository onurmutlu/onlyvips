import React, { useState } from 'react';
import { Modal, Form, Input, Select, Upload, Button, message } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import { contentService } from '../../services/content';

interface ContentModalProps {
  visible: boolean;
  onClose: () => void;
  onSuccess: () => void;
  content?: any;
}

const ContentModal: React.FC<ContentModalProps> = ({
  visible,
  onClose,
  onSuccess,
  content,
}) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [fileList, setFileList] = useState<any[]>([]);

  const handleSubmit = async (values: any) => {
    setLoading(true);
    try {
      if (content) {
        await contentService.update(content.id, values);
        message.success('İçerik başarıyla güncellendi');
      } else {
        await contentService.create(values);
        message.success('İçerik başarıyla oluşturuldu');
      }
      onSuccess();
      onClose();
    } catch (error) {
      message.error('Bir hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const normFile = (e: any) => {
    if (Array.isArray(e)) {
      return e;
    }
    return e?.fileList;
  };

  return (
    <Modal
      title={content ? 'İçeriği Düzenle' : 'Yeni İçerik'}
      open={visible}
      onCancel={onClose}
      footer={null}
      className="[&_.ant-modal-content]:bg-gray-800 [&_.ant-modal-header]:bg-transparent [&_.ant-modal-title]:text-white"
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={content}
      >
        <Form.Item
          name="title"
          label="Başlık"
          rules={[{ required: true, message: 'Lütfen başlık giriniz' }]}
        >
          <Input className="bg-gray-700 border-gray-600 text-white" />
        </Form.Item>

        <Form.Item
          name="description"
          label="Açıklama"
          rules={[{ required: true, message: 'Lütfen açıklama giriniz' }]}
        >
          <Input.TextArea
            rows={4}
            className="bg-gray-700 border-gray-600 text-white"
          />
        </Form.Item>

        <Form.Item
          name="mediaType"
          label="İçerik Türü"
          rules={[{ required: true, message: 'Lütfen içerik türü seçiniz' }]}
        >
          <Select className="bg-gray-700 border-gray-600 text-white">
            <Select.Option value="image">Fotoğraf</Select.Option>
            <Select.Option value="video">Video</Select.Option>
          </Select>
        </Form.Item>

        <Form.Item
          name="mediaUrl"
          label="Medya"
          valuePropName="fileList"
          getValueFromEvent={normFile}
          rules={[{ required: true, message: 'Lütfen medya yükleyiniz' }]}
        >
          <Upload
            listType="picture"
            maxCount={1}
            onChange={({ fileList }) => setFileList(fileList)}
          >
            <Button icon={<UploadOutlined />}>Yükle</Button>
          </Upload>
        </Form.Item>

        <Form.Item
          name="price"
          label="Fiyat (TON)"
          rules={[{ required: true, message: 'Lütfen fiyat giriniz' }]}
        >
          <Input
            type="number"
            min={0}
            className="bg-gray-700 border-gray-600 text-white"
          />
        </Form.Item>

        <Form.Item>
          <div className="flex justify-end space-x-2">
            <Button onClick={onClose}>İptal</Button>
            <Button type="primary" htmlType="submit" loading={loading}>
              {content ? 'Güncelle' : 'Oluştur'}
            </Button>
          </div>
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default ContentModal; 