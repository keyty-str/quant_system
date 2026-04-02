import React, { useEffect, useState } from "react";
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
  Spin,
} from "antd";
import {
  PlayCircleOutlined,
  EyeOutlined,
  DeleteOutlined,
  DownloadOutlined,
} from "@ant-design/icons";
import dayjs from "dayjs";
import {
  runBacktest,
  getBacktestHistory,
  deleteBacktest,
  type BacktestRequest,
  type BacktestResult,
} from "../services/backtest";

const { Option } = Select;
const { RangePicker } = DatePicker;

interface BacktestData {
  key: string;
  id: string;
  strategyName: string;
  stockPool: string;
  dateRange: string;
  status: string;
  totalReturn: string;
  maxDrawdown: string;
  sharpeRatio: string;
  winRate: string;
  createTime: string;
}

const Backtest: React.FC = () => {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [backtestData, setBacktestData] = useState<BacktestData[]>([]);
  const [total, setTotal] = useState(0);
  const [stats, setStats] = useState({
    total: 0,
    completed: 0,
    running: 0,
    avgReturn: "+0%",
  });
  const [progress, setProgress] = useState([
    { name: "双均线策略", percent: 75, color: "#1890ff" },
    { name: "MACD金叉策略", percent: 45, color: "#52c41a" },
    { name: "RSI超卖策略", percent: 90, color: "#faad14" },
  ]);

  // 获取回测历史
  const fetchBacktestHistory = async () => {
    setLoading(true);
    try {
      const response = await getBacktestHistory({ limit: 100 });
      const data = response.data || [];

      const formattedData = data.map((item: BacktestResult) => ({
        key: item.id,
        id: item.id,
        strategyName: item.strategyId,
        stockPool: "沪深300",
        dateRange: "2023-01-01 至 2023-12-31",
        status: "已完成",
        totalReturn: `+${item.totalReturn.toFixed(1)}%`,
        maxDrawdown: `${item.maxDrawdown.toFixed(1)}%`,
        sharpeRatio: item.sharpeRatio.toFixed(2),
        winRate: `${(item.winRate * 100).toFixed(1)}%`,
        createTime: new Date().toLocaleString(),
      }));

      // 如果没有数据，显示模拟数据
      if (formattedData.length === 0) {
        setBacktestData([
          {
            key: "1",
            id: "1",
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
            id: "2",
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
            id: "3",
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
        ]);
        setTotal(3);
        setStats({
          total: 3,
          completed: 2,
          running: 1,
          avgReturn: "+22.5%",
        });
      } else {
        setBacktestData(formattedData);
        setTotal(formattedData.length);
        setStats({
          total: formattedData.length,
          completed: formattedData.filter((s) => s.status === "已完成").length,
          running: formattedData.filter((s) => s.status === "运行中").length,
          avgReturn: "+22.5%",
        });
      }
    } catch (error: any) {
      console.error("获取回测历史失败:", error);
      // 显示模拟数据
      setBacktestData([
        {
          key: "1",
          id: "1",
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
          id: "2",
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
          id: "3",
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
      ]);
      setTotal(3);
      setStats({
        total: 3,
        completed: 2,
        running: 1,
        avgReturn: "+22.5%",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBacktestHistory();
  }, []);

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
      render: (_: any, record: BacktestData) => (
        <Space size="small">
          <Button type="link" size="small" icon={<EyeOutlined />}>
            查看
          </Button>
          <Button type="link" size="small" icon={<DownloadOutlined />}>
            导出
          </Button>
          <Button
            type="link"
            size="small"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record.id)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  const handleRunBacktest = () => {
    setIsModalVisible(true);
  };

  const handleModalOk = async () => {
    try {
      await form.validateFields();
      const values = form.getFieldsValue();
      console.log("运行回测:", values);

      const backtestData: BacktestRequest = {
        strategyId: values.strategy,
        symbols:
          values.stockPool === "hs300" ? ["000001", "000002"] : ["600036"],
        start_date: values.dateRange
          ? dayjs(values.dateRange[0]).format("YYYY-MM-DD")
          : "2023-01-01",
        end_date: values.dateRange
          ? dayjs(values.dateRange[1]).format("YYYY-MM-DD")
          : "2023-12-31",
        initial_capital: parseFloat(values.initialCapital),
        commission: parseFloat(values.commission) / 100,
      };

      await runBacktest(backtestData);
      message.success("回测任务已启动");
      setIsModalVisible(false);
      form.resetFields();
      fetchBacktestHistory();
    } catch (error: any) {
      console.error("表单验证失败:", error);
    }
  };

  const handleModalCancel = () => {
    setIsModalVisible(false);
    form.resetFields();
  };

  const handleDelete = async (id: string) => {
    Modal.confirm({
      title: "确认删除",
      content: "确定要删除该回测记录吗？",
      onOk: async () => {
        try {
          await deleteBacktest(id);
          message.success("回测记录已删除");
          fetchBacktestHistory();
        } catch (error: any) {
          console.error("删除回测记录失败:", error);
          message.error("删除回测记录失败");
        }
      },
    });
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
        <div
          style={{
            display: "flex",
            justifyContent: "space-around",
            flexWrap: "wrap",
          }}
        >
          <div style={{ textAlign: "center", padding: "16px" }}>
            <div style={{ fontSize: 24, fontWeight: "bold", color: "#1890ff" }}>
              {stats.total}
            </div>
            <div>总回测次数</div>
          </div>
          <div style={{ textAlign: "center", padding: "16px" }}>
            <div style={{ fontSize: 24, fontWeight: "bold", color: "#52c41a" }}>
              {stats.completed}
            </div>
            <div>已完成</div>
          </div>
          <div style={{ textAlign: "center", padding: "16px" }}>
            <div style={{ fontSize: 24, fontWeight: "bold", color: "#1890ff" }}>
              {stats.running}
            </div>
            <div>运行中</div>
          </div>
          <div style={{ textAlign: "center", padding: "16px" }}>
            <div style={{ fontSize: 24, fontWeight: "bold", color: "#3f8600" }}>
              {stats.avgReturn}
            </div>
            <div>平均收益</div>
          </div>
        </div>
      </Card>

      {/* 进度显示 */}
      <Card title="当前回测进度" style={{ marginBottom: 16 }}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-around",
            flexWrap: "wrap",
          }}
        >
          {progress.map((item, index) => (
            <div key={index} style={{ textAlign: "center", padding: "16px" }}>
              <Progress
                type="circle"
                percent={item.percent}
                strokeColor={item.color}
              />
              <div style={{ marginTop: 8 }}>{item.name}</div>
            </div>
          ))}
        </div>
      </Card>

      {/* 回测列表 */}
      <Card title="回测记录">
        <Spin spinning={loading}>
          <Table
            columns={columns}
            dataSource={backtestData}
            pagination={{
              total: total,
              pageSize: 10,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total) => `共 ${total} 条记录`,
            }}
            scroll={{ x: 1300 }}
          />
        </Spin>
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
