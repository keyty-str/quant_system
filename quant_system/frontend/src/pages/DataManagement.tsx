import React from "react";
import {
  Card,
  Table,
  Button,
  Input,
  Select,
  Space,
  Tag,
  Modal,
  Form,
  message,
} from "antd";
import {
  PlusOutlined,
  SearchOutlined,
  ReloadOutlined,
  DownloadOutlined,
} from "@ant-design/icons";

const { Option } = Select;

const DataManagement: React.FC = () => {
  const [isModalVisible, setIsModalVisible] = React.useState(false);
  const [form] = Form.useForm();

  // 模拟股票数据
  const stockData = [
    {
      key: "1",
      code: "000001",
      name: "平安银行",
      market: "深圳",
      industry: "银行",
      listDate: "1991-04-03",
      status: "正常",
    },
    {
      key: "2",
      code: "000002",
      name: "万科A",
      market: "深圳",
      industry: "房地产",
      listDate: "1991-01-29",
      status: "正常",
    },
    {
      key: "3",
      code: "600036",
      name: "招商银行",
      market: "上海",
      industry: "银行",
      listDate: "2002-04-09",
      status: "正常",
    },
  ];

  const columns = [
    {
      title: "股票代码",
      dataIndex: "code",
      key: "code",
      width: 100,
    },
    {
      title: "股票名称",
      dataIndex: "name",
      key: "name",
      width: 120,
    },
    {
      title: "市场",
      dataIndex: "market",
      key: "market",
      width: 80,
      render: (market: string) => (
        <Tag color={market === "上海" ? "blue" : "green"}>{market}</Tag>
      ),
    },
    {
      title: "行业",
      dataIndex: "industry",
      key: "industry",
      width: 100,
    },
    {
      title: "上市日期",
      dataIndex: "listDate",
      key: "listDate",
      width: 120,
    },
    {
      title: "状态",
      dataIndex: "status",
      key: "status",
      width: 80,
      render: (status: string) => (
        <Tag color={status === "正常" ? "green" : "red"}>{status}</Tag>
      ),
    },
    {
      title: "操作",
      key: "action",
      width: 150,
      render: () => (
        <Space size="small">
          <Button type="link" size="small">
            查看
          </Button>
          <Button type="link" size="small">
            编辑
          </Button>
          <Button type="link" size="small" danger>
            删除
          </Button>
        </Space>
      ),
    },
  ];

  const handleAddStock = () => {
    setIsModalVisible(true);
  };

  const handleModalOk = () => {
    form.validateFields().then((values) => {
      console.log("新增股票:", values);
      message.success("股票添加成功");
      setIsModalVisible(false);
      form.resetFields();
    });
  };

  const handleModalCancel = () => {
    setIsModalVisible(false);
    form.resetFields();
  };

  const handleRefresh = () => {
    message.success("数据刷新成功");
  };

  const handleExport = () => {
    message.success("数据导出成功");
  };

  return (
    <div>
      <h1>数据管理</h1>

      {/* 操作栏 */}
      <Card style={{ marginBottom: 16 }}>
        <Space>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleAddStock}
          >
            添加股票
          </Button>
          <Button icon={<ReloadOutlined />} onClick={handleRefresh}>
            刷新数据
          </Button>
          <Button icon={<DownloadOutlined />} onClick={handleExport}>
            导出数据
          </Button>
        </Space>
      </Card>

      {/* 搜索和筛选 */}
      <Card style={{ marginBottom: 16 }}>
        <Space>
          <Input
            placeholder="股票代码/名称"
            prefix={<SearchOutlined />}
            style={{ width: 200 }}
          />
          <Select placeholder="市场" style={{ width: 100 }}>
            <Option value="sh">上海</Option>
            <Option value="sz">深圳</Option>
          </Select>
          <Select placeholder="行业" style={{ width: 120 }}>
            <Option value="bank">银行</Option>
            <Option value="realestate">房地产</Option>
            <Option value="tech">科技</Option>
          </Select>
          <Button type="primary">查询</Button>
          <Button>重置</Button>
        </Space>
      </Card>

      {/* 数据表格 */}
      <Card title="股票列表">
        <Table
          columns={columns}
          dataSource={stockData}
          pagination={{
            total: 100,
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`,
          }}
          scroll={{ x: 800 }}
        />
      </Card>

      {/* 数据采集状态 */}
      <Card title="数据采集状态" style={{ marginTop: 16 }}>
        <div style={{ display: "flex", justifyContent: "space-around" }}>
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: 24, fontWeight: "bold", color: "#52c41a" }}>
              98.5%
            </div>
            <div>数据完整度</div>
          </div>
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: 24, fontWeight: "bold", color: "#1890ff" }}>
              2分钟前
            </div>
            <div>最后更新</div>
          </div>
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: 24, fontWeight: "bold", color: "#faad14" }}>
              3
            </div>
            <div>待采集任务</div>
          </div>
        </div>
      </Card>

      {/* 添加股票弹窗 */}
      <Modal
        title="添加股票"
        open={isModalVisible}
        onOk={handleModalOk}
        onCancel={handleModalCancel}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="code"
            label="股票代码"
            rules={[{ required: true, message: "请输入股票代码" }]}
          >
            <Input placeholder="请输入股票代码" />
          </Form.Item>
          <Form.Item
            name="name"
            label="股票名称"
            rules={[{ required: true, message: "请输入股票名称" }]}
          >
            <Input placeholder="请输入股票名称" />
          </Form.Item>
          <Form.Item
            name="market"
            label="市场"
            rules={[{ required: true, message: "请选择市场" }]}
          >
            <Select placeholder="请选择市场">
              <Option value="sh">上海</Option>
              <Option value="sz">深圳</Option>
            </Select>
          </Form.Item>
          <Form.Item
            name="industry"
            label="行业"
            rules={[{ required: true, message: "请选择行业" }]}
          >
            <Select placeholder="请选择行业">
              <Option value="bank">银行</Option>
              <Option value="realestate">房地产</Option>
              <Option value="tech">科技</Option>
              <Option value="consumer">消费</Option>
              <Option value="medical">医药</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default DataManagement;
