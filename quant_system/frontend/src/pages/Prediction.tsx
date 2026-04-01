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
  ThunderboltOutlined,
  FireOutlined,
  RiseOutlined,
  FallOutlined,
  ReloadOutlined,
  DownloadOutlined,
} from "@ant-design/icons";
import ReactECharts from "echarts-for-react";

const { Option } = Select;

const Prediction: React.FC = () => {
  // 模拟热门板块预测数据
  const hotSectorData = [
    {
      key: "1",
      rank: 1,
      sectorName: "人工智能",
      score: 95.2,
      trend: "up",
      change: "+5.2%",
      confidence: "高",
      reason: "政策支持，技术突破",
    },
    {
      key: "2",
      rank: 2,
      sectorName: "新能源汽车",
      score: 92.8,
      trend: "up",
      change: "+3.8%",
      confidence: "高",
      reason: "销量增长，市场扩大",
    },
    {
      key: "3",
      rank: 3,
      sectorName: "半导体",
      score: 89.5,
      trend: "down",
      change: "-1.2%",
      confidence: "中",
      reason: "周期性调整，等待机会",
    },
    {
      key: "4",
      rank: 4,
      sectorName: "生物医药",
      score: 87.3,
      trend: "up",
      change: "+2.1%",
      confidence: "中",
      reason: "创新药突破，研发进展",
    },
    {
      key: "5",
      rank: 5,
      sectorName: "光伏产业",
      score: 85.1,
      trend: "down",
      change: "-2.3%",
      confidence: "中",
      reason: "产能过剩，价格竞争",
    },
  ];

  const columns = [
    {
      title: "排名",
      dataIndex: "rank",
      key: "rank",
      width: 80,
      render: (rank: number) => (
        <span
          style={{ fontWeight: "bold", color: rank <= 3 ? "#1890ff" : "#666" }}
        >
          {rank}
        </span>
      ),
    },
    {
      title: "板块名称",
      dataIndex: "sectorName",
      key: "sectorName",
      width: 120,
    },
    {
      title: "热度评分",
      dataIndex: "score",
      key: "score",
      width: 100,
      render: (score: number) => (
        <span
          style={{
            color:
              score >= 90 ? "#52c41a" : score >= 80 ? "#1890ff" : "#faad14",
          }}
        >
          {score}
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
      title: "置信度",
      dataIndex: "confidence",
      key: "confidence",
      width: 80,
      render: (confidence: string) => (
        <Tag color={confidence === "高" ? "green" : "orange"}>{confidence}</Tag>
      ),
    },
    {
      title: "预测理由",
      dataIndex: "reason",
      key: "reason",
      width: 200,
    },
  ];

  // 热门板块分布图表配置
  const sectorChartOption = {
    title: {
      text: "热门板块热度分布",
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
      data: ["人工智能", "新能源汽车", "半导体", "生物医药", "光伏产业"],
      axisLabel: {
        rotate: 45,
      },
    },
    yAxis: {
      type: "value",
      name: "热度评分",
    },
    series: [
      {
        name: "热度评分",
        type: "bar",
        data: [95.2, 92.8, 89.5, 87.3, 85.1],
        itemStyle: {
          color: (params: any) => {
            const colors = [
              "#52c41a",
              "#1890ff",
              "#faad14",
              "#722ed1",
              "#eb2f96",
            ];
            return colors[params.dataIndex];
          },
        },
      },
    ],
  };

  // 预测准确度趋势图表配置
  const accuracyChartOption = {
    title: {
      text: "预测准确度趋势",
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
      name: "准确度(%)",
      min: 0,
      max: 100,
    },
    series: [
      {
        name: "预测准确度",
        type: "line",
        data: [72, 75, 78, 82, 85, 88, 90, 92, 89, 91, 93, 95],
        smooth: true,
        itemStyle: {
          color: "#1890ff",
        },
        areaStyle: {
          color: "rgba(24, 144, 255, 0.1)",
        },
      },
    ],
  };

  return (
    <div>
      <h1>预测系统</h1>

      {/* 操作栏 */}
      <Card style={{ marginBottom: 16 }}>
        <Space>
          <Button type="primary" icon={<ThunderboltOutlined />}>
            生成预测
          </Button>
          <Button icon={<ReloadOutlined />}>刷新数据</Button>
          <Button icon={<DownloadOutlined />}>导出报告</Button>
          <Select defaultValue="1m" style={{ width: 120 }}>
            <Option value="1w">1周</Option>
            <Option value="1m">1月</Option>
            <Option value="3m">3月</Option>
          </Select>
        </Space>
      </Card>

      {/* 预测统计 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总预测次数"
              value={156}
              prefix={<ThunderboltOutlined />}
              valueStyle={{ color: "#1890ff" }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="准确次数"
              value={142}
              prefix={<FireOutlined />}
              valueStyle={{ color: "#52c41a" }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="准确率"
              value={91.0}
              precision={1}
              suffix="%"
              valueStyle={{ color: "#3f8600" }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="平均收益"
              value={12.5}
              precision={1}
              suffix="%"
              valueStyle={{ color: "#52c41a" }}
            />
          </Card>
        </Col>
      </Row>

      {/* 图表区域 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={12}>
          <Card title="热门板块热度分布">
            <ReactECharts option={sectorChartOption} style={{ height: 300 }} />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="预测准确度趋势">
            <ReactECharts
              option={accuracyChartOption}
              style={{ height: 300 }}
            />
          </Card>
        </Col>
      </Row>

      {/* 热门板块排名 */}
      <Card title="热门板块预测排名" style={{ marginBottom: 16 }}>
        <Table
          columns={columns}
          dataSource={hotSectorData}
          pagination={false}
          size="small"
        />
      </Card>

      {/* 预测详情 */}
      <Row gutter={16}>
        <Col span={12}>
          <Card title="预测详情">
            <div style={{ marginBottom: 16 }}>
              <h4>人工智能板块</h4>
              <Progress percent={95.2} strokeColor="#52c41a" />
              <p>基于政策支持和技术突破，预计未来1个月将有5.2%的涨幅</p>
            </div>
            <div style={{ marginBottom: 16 }}>
              <h4>新能源汽车板块</h4>
              <Progress percent={92.8} strokeColor="#1890ff" />
              <p>销量增长和市场扩大，预计未来1个月将有3.8%的涨幅</p>
            </div>
            <div>
              <h4>半导体板块</h4>
              <Progress percent={89.5} strokeColor="#faad14" />
              <p>周期性调整中，建议观望等待机会</p>
            </div>
          </Card>
        </Col>
        <Col span={12}>
          <Card title="预测建议">
            <div style={{ marginBottom: 16 }}>
              <h4>推荐配置</h4>
              <ul>
                <li>人工智能板块：建议配置20-30%仓位</li>
                <li>新能源汽车：建议配置15-25%仓位</li>
                <li>生物医药：建议配置10-20%仓位</li>
              </ul>
            </div>
            <div>
              <h4>风险提示</h4>
              <ul>
                <li>市场波动风险：注意控制仓位</li>
                <li>政策变化风险：关注政策动向</li>
                <li>技术风险：注意技术面变化</li>
              </ul>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Prediction;
