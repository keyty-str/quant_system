import React, { useEffect, useState } from "react";
import {
  Card,
  Row,
  Col,
  Statistic,
  Table,
  Tag,
  Spin,
  Alert,
  Progress,
} from "antd";
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  DollarOutlined,
  LineChartOutlined,
  PieChartOutlined,
  BarChartOutlined,
} from "@ant-design/icons";
import ReactECharts from "echarts-for-react";
import { getStockList, getStrategyList } from "../services";
import useStore from "../store";

interface Position {
  key: string;
  code: string;
  name: string;
  quantity: number;
  cost: number;
  current: number;
  profit: number;
  profitRate: number;
}

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [positions, setPositions] = useState<Position[]>([]);
  const [stats, setStats] = useState({
    totalAssets: 1258632.5,
    todayProfit: 12563.2,
    holdingCount: 15,
    winRate: 68.5,
  });
  const setSystemStatus = useStore((state) => state.setSystemStatus);
  const systemStatus = useStore((state) => state.systemStatus);

  useEffect(() => {
    fetchDashboardData();
    checkSystemHealth();
  }, []);

  const checkSystemHealth = async () => {
    try {
      const API_BASE_URL =
        import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
      const response = await fetch(`${API_BASE_URL}/health`);
      const data = await response.json();
      setSystemStatus({
        backendConnected: data.status === "healthy",
        mongodbConnected: data.services?.mongodb || false,
        redisConnected: data.services?.redis || false,
        lastCheck: new Date().toISOString(),
      });
    } catch (error) {
      console.error("Health check failed:", error);
      setSystemStatus({
        backendConnected: false,
        lastCheck: new Date().toISOString(),
      });
    }
  };

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      // 获取股票列表
      const stockData = await getStockList({ limit: 20 });
      if (stockData?.data?.stocks) {
        // 模拟持仓数据（实际应该从后端获取持仓信息）
        const mockPositions: Position[] = [
          {
            key: "1",
            code: "000001",
            name: "平安银行",
            quantity: 1000,
            cost: 12.5,
            current: 13.2,
            profit: 700,
            profitRate: 5.6,
          },
          {
            key: "2",
            code: "000002",
            name: "万科A",
            quantity: 500,
            cost: 18.3,
            current: 17.8,
            profit: -250,
            profitRate: -2.7,
          },
          {
            key: "3",
            code: "600036",
            name: "招商银行",
            quantity: 800,
            cost: 35.2,
            current: 36.5,
            profit: 1040,
            profitRate: 3.7,
          },
        ];
        setPositions(mockPositions);
      }

      // 获取策略状态
      const strategyData = await getStrategyList();
      if (strategyData?.data) {
        // 更新策略相关状态
      }
    } catch (error) {
      console.error("Failed to fetch dashboard data:", error);
    } finally {
      setLoading(false);
    }
  };

  const statsData = [
    {
      title: "总资产",
      value: stats.totalAssets,
      precision: 2,
      prefix: <DollarOutlined />,
      suffix: "元",
      valueStyle: { color: "#3f8600" },
    },
    {
      title: "今日收益",
      value: stats.todayProfit,
      precision: 2,
      prefix:
        stats.todayProfit >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />,
      suffix: "元",
      valueStyle: { color: stats.todayProfit >= 0 ? "#3f8600" : "#cf1322" },
    },
    {
      title: "持仓股票",
      value: stats.holdingCount,
      prefix: <LineChartOutlined />,
      suffix: "只",
    },
    {
      title: "胜率",
      value: stats.winRate,
      precision: 1,
      prefix: <PieChartOutlined />,
      suffix: "%",
    },
  ];

  const positionColumns = [
    {
      title: "股票代码",
      dataIndex: "code",
      key: "code",
    },
    {
      title: "股票名称",
      dataIndex: "name",
      key: "name",
    },
    {
      title: "持仓数量",
      dataIndex: "quantity",
      key: "quantity",
    },
    {
      title: "成本价",
      dataIndex: "cost",
      key: "cost",
      render: (value: number) => value.toFixed(2),
    },
    {
      title: "当前价",
      dataIndex: "current",
      key: "current",
      render: (value: number) => value.toFixed(2),
    },
    {
      title: "盈亏",
      dataIndex: "profit",
      key: "profit",
      render: (value: number) => (
        <span style={{ color: value >= 0 ? "#3f8600" : "#cf1322" }}>
          {value >= 0 ? "+" : ""}
          {value.toFixed(2)}
        </span>
      ),
    },
    {
      title: "盈亏比例",
      dataIndex: "profitRate",
      key: "profitRate",
      render: (value: number) => (
        <Tag color={value >= 0 ? "green" : "red"}>
          {value >= 0 ? "+" : ""}
          {value.toFixed(2)}%
        </Tag>
      ),
    },
  ];

  const profitChartOption = {
    title: {
      text: "收益曲线",
      left: "center",
    },
    tooltip: {
      trigger: "axis",
    },
    xAxis: {
      type: "category",
      data: [
        "1月",
        "2月",
        "3月",
        "4月",
        "5月",
        "6月",
        "7月",
        "8月",
        "9月",
        "10月",
        "11月",
        "12月",
      ],
    },
    yAxis: {
      type: "value",
      name: "收益率(%)",
    },
    series: [
      {
        name: "策略收益",
        type: "line",
        data: [2.5, 3.2, 1.8, 4.5, 3.8, 5.2, 4.8, 6.1, 5.5, 7.2, 6.8, 8.5],
        smooth: true,
        itemStyle: {
          color: "#1890ff",
        },
      },
      {
        name: "基准收益",
        type: "line",
        data: [1.2, 1.5, 0.8, 2.1, 1.9, 2.5, 2.2, 3.1, 2.8, 3.5, 3.2, 4.2],
        smooth: true,
        itemStyle: {
          color: "#999",
        },
      },
    ],
  };

  const sectorChartOption = {
    title: {
      text: "板块分布",
      left: "center",
    },
    tooltip: {
      trigger: "item",
      formatter: "{a} <br/>{b}: {c} ({d}%)",
    },
    legend: {
      orient: "vertical",
      left: "left",
    },
    series: [
      {
        name: "板块分布",
        type: "pie",
        radius: "50%",
        data: [
          { value: 35, name: "金融" },
          { value: 25, name: "科技" },
          { value: 20, name: "消费" },
          { value: 15, name: "医药" },
          { value: 5, name: "其他" },
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: "rgba(0, 0, 0, 0.5)",
          },
        },
      },
    ],
  };

  if (loading) {
    return (
      <div style={{ textAlign: "center", padding: 50 }}>
        <Spin size="large" tip="加载数据中..." />
      </div>
    );
  }

  return (
    <div>
      <h1>仪表板</h1>

      {/* 系统状态提示 */}
      <Alert
        message={
          <span>
            系统状态:{" "}
            {systemStatus.backendConnected ? (
              <Tag color="green">正常</Tag>
            ) : (
              <Tag color="red">异常</Tag>
            )}{" "}
            | MongoDB:{" "}
            {systemStatus.mongodbConnected ? (
              <Tag color="green">已连接</Tag>
            ) : (
              <Tag color="red">未连接</Tag>
            )}{" "}
            | Redis:{" "}
            {systemStatus.redisConnected ? (
              <Tag color="green">已连接</Tag>
            ) : (
              <Tag color="red">未连接</Tag>
            )}
          </span>
        }
        type="info"
        showIcon
        style={{ marginBottom: 24 }}
      />

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        {statsData.map((item, index) => (
          <Col span={6} key={index}>
            <Card>
              <Statistic
                title={item.title}
                value={item.value}
                precision={item.precision}
                prefix={item.prefix}
                suffix={item.suffix}
                valueStyle={item.valueStyle}
              />
            </Card>
          </Col>
        ))}
      </Row>

      {/* 图表区域 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={16}>
          <Card title="收益曲线">
            <ReactECharts option={profitChartOption} style={{ height: 300 }} />
          </Card>
        </Col>
        <Col span={8}>
          <Card title="板块分布">
            <ReactECharts option={sectorChartOption} style={{ height: 300 }} />
          </Card>
        </Col>
      </Row>

      {/* 持仓表格 */}
      <Card title="当前持仓">
        <Table
          columns={positionColumns}
          dataSource={positions}
          pagination={false}
          size="small"
        />
      </Card>

      {/* 策略状态 */}
      <Row gutter={16} style={{ marginTop: 24 }}>
        <Col span={8}>
          <Card title="策略状态">
            <div style={{ textAlign: "center" }}>
              <Progress type="circle" percent={75} format={() => "运行中"} />
              <p style={{ marginTop: 16 }}>策略运行正常</p>
            </div>
          </Card>
        </Col>
        <Col span={8}>
          <Card title="今日信号">
            <div style={{ textAlign: "center" }}>
              <Progress
                type="circle"
                percent={3}
                strokeColor="#52c41a"
                format={() => "3个"}
              />
              <p style={{ marginTop: 16 }}>买入信号</p>
            </div>
          </Card>
        </Col>
        <Col span={8}>
          <Card title="风险控制">
            <div style={{ textAlign: "center" }}>
              <Progress
                type="circle"
                percent={85}
                strokeColor="#faad14"
                format={() => "正常"}
              />
              <p style={{ marginTop: 16 }}>风险可控</p>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
