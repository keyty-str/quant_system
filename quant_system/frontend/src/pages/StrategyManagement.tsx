import React from "react";
import {
  Card,
  Table,
  Button,
  Space,
  Tag,
  Modal,
  Form,
  Input,
  Select,
  Switch,
  message,
} from "antd";
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
} from "@ant-design/icons";

const { Option } = Select;

const StrategyManagement: React.FC = () => {
  const [isModalVisible, setIsModalVisible] = React.useState(false);
  const [form] = Form.useForm();

  // 模拟策略数据
  const strategyData = [
    {
      key: "1",
      name: "双均线策略",
      type: "趋势策略",
      status: "运行中",
      description: "基于短期和长期均线的交叉信号",
      createTime: "2024-01-15",
      updateTime: "2024-01-20",
      performance: "+15.2%",
    },
    {
      key: "2",
      name: "MACD金叉策略",
      type: "趋势策略",
      status: "已暂停",
      description: "基于MACD指标的金叉信号",
      createTime: "2024-01-10",
      updateTime: "2024-01-18",
      performance: "+8.5%",
    },
    {
      key: "3",
      name: "RSI超卖策略",
      type: "反转策略",
      status: "运行中",
      description: "基于RSI超卖区域的反转信号",
      createTime: "2024-01-12",
      updateTime: "2024-01-19",
      performance: "+12.3%",
    },
  ];

  const columns = [
    {
      title: "策略名称",
      dataIndex: "name",
      key: "name",
      width: 150,
    },
    {
      title: "策略类型",
      dataIndex: "type",
      key: "type",
      width: 100,
      render: (type: string) => (
        <Tag color={type === "趋势策略" ? "blue" : "green"}>{type}</Tag>
      ),
    },
    {
      title: "状态",
      dataIndex: "status",
      key: "status",
      width: 100,
      render: (status: string) => (
        <Tag color={status === "运行中" ? "green" : "orange"}>{status}</Tag>
      ),
    },
    {
      title: "描述",
      dataIndex: "description",
      key: "description",
      width: 200,
    },
    {
      title: "收益",
      dataIndex: "performance",
      key: "performance",
      width: 100,
      render: (performance: string) => (
        <span
          style={{ color: performance.startsWith("+") ? "#3f8600" : "#cf1322" }}
        >
          {performance}
        </span>
      ),
    },
    {
      title: "创建时间",
      dataIndex: "createTime",
      key: "createTime",
      width: 120,
    },
    {
      title: "更新时间",
      dataIndex: "updateTime",
      key: "updateTime",
      width: 120,
    },
    {
      title: "操作",
      key: "action",
      width: 200,
      render: (_, record) => (
        <Space size="small">
          <Button type="link" size="small" icon={<EditOutlined />}>
            编辑
          </Button>
          <Button
            type="link"
            size="small"
            icon={
              record.status === "运行中" ? (
                <PauseCircleOutlined />
              ) : (
                <PlayCircleOutlined />
              )
            }
          >
            {record.status === "运行中" ? "暂停" : "启动"}
          </Button>
          <Button type="link" size="small" danger icon={<DeleteOutlined />}>
            删除
          </Button>
        </Space>
      ),
    },
  ];

  const handleCreateStrategy = () => {
    setIsModalVisible(true);
  };

  const handleModalOk = () => {
    form.validateFields().then((values) => {
      console.log("新建策略:", values);
      message.success("策略创建成功");
      setIsModalVisible(false);
      form.resetFields();
    });
  };

  const handleModalCancel = () => {
    setIsModalVisible(false);
    form.resetFields();
  };

  return (
    <div>
      <h1>策略管理</h1>

      {/* 操作栏 */}
      <Card style={{ marginBottom: 16 }}>
        <Space>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleCreateStrategy}
          >
            新建策略
          </Button>
          <Button>导入策略</Button>
          <Button>导出策略</Button>
        </Space>
      </Card>

      {/* 策略统计 */}
      <Card style={{ marginBottom: 16 }}>
        <div style={{ display: "flex", justifyContent: "space-around" }}>
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: 24, fontWeight: "bold", color: "#1890ff" }}>
              8
            </div>
            <div>总策略数</div>
          </div>
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: 24, fontWeight: "bold", color: "#52c41a" }}>
              5
            </div>
            <div>运行中</div>
          </div>
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: 24, fontWeight: "bold", color: "#faad14" }}>
              3
            </div>
            <div>已暂停</div>
          </div>
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: 24, fontWeight: "bold", color: "#3f8600" }}>
              +12.5%
            </div>
            <div>平均收益</div>
          </div>
        </div>
      </Card>

      {/* 策略列表 */}
      <Card title="策略列表">
        <Table
          columns={columns}
          dataSource={strategyData}
          pagination={{
            total: 10,
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`,
          }}
          scroll={{ x: 1000 }}
        />
      </Card>

      {/* 新建策略弹窗 */}
      <Modal
        title="新建策略"
        open={isModalVisible}
        onOk={handleModalOk}
        onCancel={handleModalCancel}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="name"
            label="策略名称"
            rules={[{ required: true, message: "请输入策略名称" }]}
          >
            <Input placeholder="请输入策略名称" />
          </Form.Item>
          <Form.Item
            name="type"
            label="策略类型"
            rules={[{ required: true, message: "请选择策略类型" }]}
          >
            <Select placeholder="请选择策略类型">
              <Option value="trend">趋势策略</Option>
              <Option value="reversal">反转策略</Option>
              <Option value="arbitrage">套利策略</Option>
              <Option value="momentum">动量策略</Option>
            </Select>
          </Form.Item>
          <Form.Item
            name="description"
            label="策略描述"
            rules={[{ required: true, message: "请输入策略描述" }]}
          >
            <Input.TextArea rows={4} placeholder="请输入策略描述" />
          </Form.Item>
          <Form.Item
            name="indicators"
            label="技术指标"
            rules={[{ required: true, message: "请选择技术指标" }]}
          >
            <Select mode="multiple" placeholder="请选择技术指标">
              <Option value="ma">移动平均线</Option>
              <Option value="macd">MACD</Option>
              <Option value="rsi">RSI</Option>
              <Option value="boll">布林带</Option>
              <Option value="kdj">KDJ</Option>
            </Select>
          </Form.Item>
          <Form.Item name="enabled" label="是否启用" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default StrategyManagement;
