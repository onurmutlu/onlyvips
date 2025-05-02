import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Button, Space, Table, message } from 'antd';
import { TonConnectButton } from '@tonconnect/ui-react';
import { walletService } from '../services/wallet';

const WalletPage: React.FC = () => {
  const [balance, setBalance] = useState<{ TON: number; AJX: number }>({ TON: 0, AJX: 0 });
  const [transactions, setTransactions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [balanceData, transactionsData] = await Promise.all([
        walletService.getBalance(),
        walletService.getTransactionHistory()
      ]);
      setBalance(balanceData);
      setTransactions(transactionsData);
    } catch (error) {
      message.error('Veriler yüklenirken bir hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      title: 'İşlem ID',
      dataIndex: 'id',
      key: 'id',
    },
    {
      title: 'Tür',
      dataIndex: 'type',
      key: 'type',
      render: (type: string) => type === 'deposit' ? 'Yatırma' : 'Çekme',
    },
    {
      title: 'Miktar',
      dataIndex: 'amount',
      key: 'amount',
      render: (amount: number, record: any) => `${amount} ${record.currency}`,
    },
    {
      title: 'Durum',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const statusMap: Record<string, { color: string; text: string }> = {
          pending: { color: 'orange', text: 'Beklemede' },
          completed: { color: 'green', text: 'Tamamlandı' },
          failed: { color: 'red', text: 'Başarısız' },
        };
        const { color, text } = statusMap[status] || { color: 'default', text: status };
        return <span style={{ color }}>{text}</span>;
      },
    },
    {
      title: 'Tarih',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (timestamp: Date) => new Date(timestamp).toLocaleString(),
    },
  ];

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Card 
            title="Cüzdan Bağlantısı"
            className="bg-gray-800 border-gray-700"
          >
            <Space direction="vertical" style={{ width: '100%' }}>
              <TonConnectButton />
            </Space>
          </Card>
        </Col>

        <Col span={12}>
          <Card className="bg-gray-800 border-gray-700">
            <Statistic
              title="TON Bakiyesi"
              value={balance.TON}
              precision={2}
              suffix="TON"
              valueStyle={{ color: '#fff' }}
            />
          </Card>
        </Col>

        <Col span={12}>
          <Card className="bg-gray-800 border-gray-700">
            <Statistic
              title="AJX Bakiyesi"
              value={balance.AJX}
              precision={2}
              suffix="AJX"
              valueStyle={{ color: '#fff' }}
            />
          </Card>
        </Col>

        <Col span={24}>
          <Card 
            title="İşlem Geçmişi"
            className="bg-gray-800 border-gray-700"
          >
            <Table
              columns={columns}
              dataSource={transactions}
              loading={loading}
              rowKey="id"
              pagination={{
                pageSize: 10,
                showSizeChanger: true,
                showTotal: (total) => `Toplam ${total} işlem`,
              }}
              className="[&_.ant-table-thead>tr>th]:bg-transparent [&_.ant-table-thead>tr>th]:text-white/60 [&_.ant-table-tbody>tr>td]:bg-transparent [&_.ant-table-tbody>tr:hover>td]:bg-white/5"
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default WalletPage; 