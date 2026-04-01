import React from "react";
import {
  Card,
  Row,
  Col,
  Statistic,
  Progress,
  Table,
  Tag,
  Button,
  Space,
  Select,
  DatePicker,
} from "antd";
import {
  RiseOutlined,
  FallOutlined,
  ReloadOutlined,
  DownloadOutlined,
  BarChartOutlined,
} from "@ant-design/icons";
import ReactECharts from "echarts-for-react";

const { Option } = Select;

const SectorAnalysis: React.FC = () => {
  // 模拟板块数据
  const sectorData = [
    {
      key: "1",
      sectorName: "科技板块",
      stockCount: 256,
      avgPE: 45.2,
      avgPB: 3.8,
      totalMarketValue: "12.5万亿",
      change: "+2.3%",
      trend: "up",
      capitalFlow: "+125亿",
    },
    {
      key: "2",
      sectorName: "金融板块",
      stockCount: 128,
      avgPE: 8.5,
      avgPB: 0.9,
      totalMarketValue: "8.2万亿",
      change: "-0.8%",
      trend: "down",
      capitalFlow: "-45亿",
    },
    {
      key: "3",
      sectorName: "消费板块",
      stockCount: 189,
      avgPE: 32.1,
      avgPB: 4.2,
      totalMarketValue: "6.8万亿",
      change: "+1.5%",
      trend: "up",
      capitalFlow: "+78亿",
    },
    {
      key: "4",
      sectorName: "医药板块",
      stockCount: 167,
      avgPE: 28.5,
      avgPB: 3.5,
      totalMarketValue: "5.2万亿",
      change: "+0.9%",
      trend: "up",
      capitalFlow: "+52亿",
    },
    {
      key: "5",
      sectorName: "能源板块",
      stockCount: 98,
      avgPE: 12.3,
      avgPB: 1.2,
      totalMarketValue: "4.1万亿",
      change: "-1.2%",
      trend: "down",
      capitalFlow: "-32亿",
    },
  ];

  const columns = [
    {
      title: "板块名称",
      dataIndex: "sectorName",
      key: "sectorName",
      width: 120,
    },
    {
      title: "股票数量",
      dataIndex: "stockCount",
      key: "stockCount",
      width: 100,
    },
    {
      title: "平均市盈率",
      dataIndex: "avgPE",
      key: "avgPE",
      width: 100,
    },
    {
      title: "平均市净率",
      dataIndex: "avgPB",
      key: "avgPB",
      width: 100,
    },
    {
      title: "总市值",
      dataIndex: "totalMarketValue",
      key: "totalMarketValue",
      width: 120,
    },
    {
      title: "涨跌幅",
      dataIndex: "change",
      key: "change",
      width: 80,
      render: (change: string) => (
        <span style={{ color: change.startsWith("+") ? "#52c41a" : "#cf1322" }}>
          {change}
        </span>
      ),
    },
    {
      title: "趋势",
      dataIndex: "trend",
      key: "trend",
      width: 80,
      render: (trend: string) => (
        <Tag color={trend === "up" ? "green" : "red"}>
          {trend === "up" ? <RiseOutlined /> : <FallOutlined />}
          {trend === "up" ? "上涨" : "下跌"}
        </Tag>
      ),
    },
    {
      title: "资金流向",
      dataIndex: "capitalFlow",
      key: "capitalFlow",
      width: 100,
      render: (flow: string) => (
        <span style={{ color: flow.startsWith("+") ? "#52c41a" : "#cf1322" }}>
          {flow}
        </span>
      ),
    },
  ];

  // 板块涨跌幅图表配置
  const changeChartOption = {
    title: {
      text: "板块涨跌幅",
      left: "center",
    },
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "shadow",
      },
    },
    xAxis: {
      type: "category",
      data: ["科技板块", "金融板块", "消费板块", "医药板块", "能源板块"],
      axisLabel: {
        rotate: 45,
      },
    },
    yAxis: {
      type: "value",
      name: "涨跌幅(%)",
    },
    series: [
      {
        name: "涨跌幅",
        type: "bar",
        data: [2.3, -0.8, 1.5, 0.9, -1.2],
        itemStyle: {
          color: (params: any) => {
            return params.data >= 0 ? "#52c41a" : "#cf1322";
          },
        },
      },
    ],
  };

  // 资金流向图表配置
  const capitalFlowChartOption = {
    title: {
      text: "资金流向",
      left: "center",
    },
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "shadow",
      },
    },
    xAxis: {
      type: "category",
      data: ["科技板块", "金融板块", "消费板块", "医药板块", "能源板块"],
      axisLabel: {
        rotate: 45,
      },
    },
    yAxis: {
      type: "value",
      name: "资金流向(亿)",
    },
    series: [
      {
        name: "资金流向",
        type: "bar",
        data: [125, -45, 78, 52, -32],
        itemStyle: {
          color: (params: any) => {
            return params.data >= 0 ? "#52c41a" : "#cf1322";
          },
        },
      },
    ],
  };

  // 板块分布饼图配置
  const sectorDistributionOption = {
    title: {
      text: "板块市值分布",
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
        name: "市值分布",
        type: "pie",
        radius: "50%",
        data: [
          { value: 35, name: "科技板块" },
          { value: 25, name: "金融板块" },
          { value: 20, name: "消费板块" },
          { value: 15, name: "医药板块" },
          { value: 5, name: "能源板块" },
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

  return (
    <div>
      <h1>板块分析</h1>

      {/* 操作栏 */}
      <Card style={{ marginBottom: 16 }}>
        <Space>
          <Button type="primary" icon={<BarChartOutlined />}>
            分析板块
          </Button>
          <Button icon={<ReloadOutlined />}>刷新数据</Button>
          <Button icon={<DownloadOutlined />}>导出报告</Button>
          <Select defaultValue="1d" style={{ width: 120 }}>
            <Option value="1d">1天</Option>
            <Option value="1w">1周</Option>
            <Option value="1m">1月</Option>
          </Select>
        </Space>
      </Card>

      {/* 板块统计 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总板块数"
              value={8}
              prefix={<BarChartOutlined />}
              valueStyle={{ color: "#1890ff" }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="上涨板块"
              value={5}
              prefix={<RiseOutlined />}
              valueStyle={{ color: "#52c41a" }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="下跌板块"
              value={3}
              prefix={<FallOutlined />}
              valueStyle={{ color: "#cf1322" }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="总市值"
              value="36.8万亿"
              valueStyle={{ color: "#722ed1" }}
            />
          </Card>
        </Col>
      </Row>

      {/* 图表区域 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={12}>
          <Card title="板块涨跌幅">
            <ReactECharts option={changeChartOption} style={{ height: 300 }} />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="资金流向">
            <ReactECharts
              option={capitalFlowChartOption}
              style={{ height: 300 }}
            />
          </Card>
        </Col>
      </Row>

      {/* 板块分布 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={12}>
          <Card title="板块市值分布">
            <ReactECharts
              option={sectorDistributionOption}
              style={{ height: 300 }}
            />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="板块估值分析">
            <div style={{ marginBottom: 16 }}>
              <h4>科技板块</h4>
              <Progress percent={75} strokeColor="#1890ff" />
              <p>市盈率: 45.2，估值较高</p>
            </div>
            <div style={{ marginBottom: 16 }}>
              <h4>金融板块</h4>
              <Progress percent={35} strokeColor="#52c41a" />
              <p>市盈率: 8.5，估值较低</p>
            </div>
            <div>
              <h4>消费板块</h4>
              <Progress percent={60} strokeColor="#faad14" />
              <p>市盈率: 32.1，估值适中</p>
            </div>
          </Card>
        </Col>
      </Row>

      {/* 板块列表 */}
      <Card title="板块详情">
        <Table
          columns={columns}
          dataSource={sectorData}
          pagination={{
            total: 20,
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`,
          }}
          scroll={{ x: 1000 }}
        />
      </Card>

      {/* 板块分析 */}
      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col span={12}>
          <Card title="板块分析">
            <div style={{ marginBottom: 16 }}>
              <h4>科技板块</h4>
              <p>
                当前处于上涨趋势，资金流入明显，建议关注人工智能、半导体等细分领域
              </p>
            </div>
            <div style={{ marginBottom: 16 }}>
              <h4>金融板块</h4>
              <p>估值较低，具有防御性，适合稳健型投资者配置</p>
            </div>
            <div>
              <h4>消费板块</h4>
              <p>受益于内需复苏，基本面良好，中长期看好</p>
            </div>
          </Card>
        </Col>
        <Col span={12}>
          <Card title="投资建议">
            <div style={{ marginBottom: 16 }}>
              <h4>推荐配置</h4>
              <ul>
                <li>科技板块：建议配置25-35%仓位</li>
                <li>消费板块：建议配置20-30%仓位</li>
                <li>医药板块：建议配置15-25%仓位</li>
              </ul>
            </div>
            <div>
              <h4>风险提示</h4>
              <ul>
                <li>市场波动风险：注意控制仓位</li>
                <li>行业轮动风险：关注板块轮动节奏</li>
                <li>估值风险：避免追高估值板块</li>
              </ul>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default SectorAnalysis;
