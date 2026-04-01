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
  DatePicker,
  Progress,
  message,
} from "antd";
import {
  PlayCircleOutlined,
  EyeOutlined,
  DeleteOutlined,
  DownloadOutlined,
} from "@ant-design/icons";

const { Option } = Select;
const { RangePicker } = DatePicker;

const Backtest: React.FC = () => {
  const [isModalVisible, setIsModalVisible] = React.useState(false);
  const [form] = Form.useForm();

  // 模拟回测数据
  const backtestData = [
    {
      key: "1",
      strategyName: "双均线策略",
      stockPool: "沪深300",
      dateRange: "2023-01-01 至 2023-12-31",
      status: "已完成",
      totalReturn: "+25.6%",
      maxDrawdown: "-8.2%",
      sharpeRatio: "1.85",
      winRate: "68.5%",
      createTime: "2024-01-15 10:30",
    },
    {
      key: "2",
      strategyName: "MACD金叉策略",
      stockPool: "中证500",
      dateRange: "2023-06-01 至 2023-12-31",
      status: "运行中",
      totalReturn: "+18.3%",
      maxDrawdown: "-6.5%",
      sharpeRatio: "1.62",
      winRate: "65.2%",
      createTime: "2024-01-16 14:20",
    },
    {
      key: "3",
      strategyName: "RSI超卖策略",
      stockPool: "创业板指",
      dateRange: "2023-03-01 至 2023-12-31",
      status: "已完成",
      totalReturn: "+32.1%",
      maxDrawdown: "-12.3%",
      sharpeRatio: "2.15",
      winRate: "72.8%",
      createTime: "2024-01-17 09:15",
    },
  ];

  const columns = [
    {
      title: "策略名称",
      dataIndex: "strategyName",
      key: "strategyName",
      width: 120,
    },
    {
      title: "股票池",
      dataIndex: "stockPool",
      key: "stockPool",
      width: 100,
    },
    {
      title: "回测区间",
      dataIndex: "dateRange",
      key: "dateRange",
      width: 180,
    },
    {
      title: "状态",
      dataIndex: "status",
      key: "status",
      width: 80,
      render: (status: string) => (
        <Tag color={status === "已完成" ? "green" : "blue"}>{status}</Tag>
      ),
    },
    {
      title: "总收益",
      dataIndex: "totalReturn",
      key: "totalReturn",
      width: 80,
      render: (value: string) => (
        <span style={{ color: value.startsWith("+") ? "#3f8600" : "#cf1322" }}>
          {value}
        </span>
      ),
    },
    {
      title: "最大回撤",
      dataIndex: "maxDrawdown",
      key: "maxDrawdown",
      width: 80,
      render: (value: string) => (
        <span style={{ color: "#cf1322" }}>{value}</span>
      ),
    },
    {
      title: "夏普比率",
      dataIndex: "sharpeRatio",
      key: "sharpeRatio",
      width: 80,
    },
    {
      title: "胜率",
      dataIndex: "winRate",
      key: "winRate",
      width: 80,
    },
    {
      title: "创建时间",
      dataIndex: "createTime",
      key: "createTime",
      width: 150,
    },
    {
      title: "操作",
      key: "action",
      width: 150,
      render: (_, record) => (
        <Space size="small">
          <Button type="link" size="small" icon={<EyeOutlined />}>
            查看
          </Button>
          <Button type="link" size="small" icon={<DownloadOutlined />}>
            导出
          </Button>
          <Button type="link" size="small" danger icon={<DeleteOutlined />}>
            删除
          </Button>
        </Space>
      ),
    },
  ];

  const handleRunBacktest = () => {
    setIsModalVisible(true);
  };

  const handleModalOk = () => {
    form.validateFields().then((values) => {
      console.log("运行回测:", values);
      message.success("回测任务已启动");
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
      <h1>回测系统</h1>

      {/* 操作栏 */}
      <Card style={{ marginBottom: 16 }}>
        <Space>
          <Button
            type="primary"
            icon={<PlayCircleOutlined />}
            onClick={handleRunBacktest}
          >
            运行回测
          </Button>
          <Button>批量回测</Button>
          <Button>回测报告</Button>
        </Space>
      </Card>

      {/* 回测统计 */}
      <Card style={{ marginBottom: 16 }}>
        <div style={{ display: "flex", justifyContent: "space-around" }}>
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: 24, fontWeight: "bold", color: "#1890ff" }}>
              15
            </div>
            <div>总回测次数</div>
          </div>
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: 24, fontWeight: "bold", color: "#52c41a" }}>
              12
            </div>
            <div>已完成</div>
          </div>
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: 24, fontWeight: "bold", color: "#1890ff" }}>
              3
            </div>
            <div>运行中</div>
          </div>
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: 24, fontWeight: "bold", color: "#3f8600" }}>
              +22.5%
            </div>
            <div>平均收益</div>
          </div>
        </div>
      </Card>

      {/* 进度显示 */}
      <Card title="当前回测进度" style={{ marginBottom: 16 }}>
        <div style={{ display: "flex", justifyContent: "space-around" }}>
          <div style={{ textAlign: "center" }}>
            <Progress type="circle" percent={75} strokeColor="#1890ff" />
            <div style={{ marginTop: 8 }}>双均线策略</div>
          </div>
          <div style={{ textAlign: "center" }}>
            <Progress type="circle" percent={45} strokeColor="#52c41a" />
            <div style={{ marginTop: 8 }}>MACD金叉策略</div>
          </div>
          <div style={{ textAlign: "center" }}>
            <Progress type="circle" percent={90} strokeColor="#faad14" />
            <div style={{ marginTop: 8 }}>RSI超卖策略</div>
          </div>
        </div>
      </Card>

      {/* 回测列表 */}
      <Card title="回测记录">
        <Table
          columns={columns}
          dataSource={backtestData}
          pagination={{
            total: 20,
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`,
          }}
          scroll={{ x: 1200 }}
        />
      </Card>

      {/* 运行回测弹窗 */}
      <Modal
        title="运行回测"
        open={isModalVisible}
        onOk={handleModalOk}
        onCancel={handleModalCancel}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="strategy"
            label="选择策略"
            rules={[{ required: true, message: "请选择策略" }]}
          >
            <Select placeholder="请选择策略">
              <Option value="strategy1">双均线策略</Option>
              <Option value="strategy2">MACD金叉策略</Option>
              <Option value="strategy3">RSI超卖策略</Option>
            </Select>
          </Form.Item>
          <Form.Item
            name="stockPool"
            label="股票池"
            rules={[{ required: true, message: "请选择股票池" }]}
          >
            <Select placeholder="请选择股票池">
              <Option value="hs300">沪深300</Option>
              <Option value="zz500">中证500</Option>
              <Option value="cyb">创业板指</Option>
              <Option value="all">全部A股</Option>
            </Select>
          </Form.Item>
          <Form.Item
            name="dateRange"
            label="回测区间"
            rules={[{ required: true, message: "请选择回测区间" }]}
          >
            <RangePicker style={{ width: "100%" }} />
          </Form.Item>
          <Form.Item
            name="initialCapital"
            label="初始资金"
            rules={[{ required: true, message: "请输入初始资金" }]}
          >
            <Input placeholder="请输入初始资金" type="number" />
          </Form.Item>
          <Form.Item
            name="commission"
            label="手续费率"
            rules={[{ required: true, message: "请输入手续费率" }]}
          >
            <Input placeholder="请输入手续费率" suffix="%" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Backtest;
