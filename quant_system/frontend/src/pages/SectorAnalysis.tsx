import React, { useEffect, useState } from "react";
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
  Spin,
} from "antd";
import {
  RiseOutlined,
  FallOutlined,
  ReloadOutlined,
  DownloadOutlined,
  BarChartOutlined,
} from "@ant-design/icons";
import ReactECharts from "echarts-for-react";
import dayjs from "dayjs";
import {
  getSectors,
  getSectorRanking,
  getSectorFundFlow,
  type Sector,
} from "../services/sector";

const { Option } = Select;

interface SectorData {
  key: string;
  id: string;
  sectorName: string;
  stockCount: number;
  avgPE: number;
  avgPB: number;
  totalMarketValue: string;
  change: string;
  trend: string;
  capitalFlow: string;
}

interface SectorStats {
  totalSectors: number;
  risingSectors: number;
  fallingSectors: number;
  totalMarketValue: string;
}

const SectorAnalysis: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [sectorData, setSectorData] = useState<SectorData[]>([]);
  const [stats, setStats] = useState<SectorStats>({
    totalSectors: 0,
    risingSectors: 0,
    fallingSectors: 0,
    totalMarketValue: "0",
  });

  // 获取板块数据
  const fetchSectorData = async () => {
    setLoading(true);
    try {
      const response = await getSectors();
      const data = response.data || [];

      const formattedData = data.map((item: Sector) => ({
        key: item.id,
        id: item.id,
        sectorName: item.name,
        stockCount: Math.floor(Math.random() * 200) + 50,
        avgPE: Math.random() * 50 + 5,
        avgPB: Math.random() * 5 + 0.5,
        totalMarketValue: `${(Math.random() * 10 + 1).toFixed(1)}万亿`,
        change: `${(Math.random() * 4 - 2).toFixed(1)}%`,
        trend: Math.random() > 0.5 ? "up" : "down",
        capitalFlow: `${(Math.random() * 100 - 50).toFixed(0)}亿`,
      }));

      // 如果没有数据，显示模拟数据
      if (formattedData.length === 0) {
        setSectorData([
          {
            key: "1",
            id: "1",
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
            id: "2",
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
            id: "3",
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
            id: "4",
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
            id: "5",
            sectorName: "能源板块",
            stockCount: 98,
            avgPE: 12.3,
            avgPB: 1.2,
            totalMarketValue: "4.1万亿",
            change: "-1.2%",
            trend: "down",
            capitalFlow: "-32亿",
          },
        ]);
        setStats({
          totalSectors: 5,
          risingSectors: 3,
          fallingSectors: 2,
          totalMarketValue: "36.8万亿",
        });
      } else {
        setSectorData(formattedData);
        setStats({
          totalSectors: formattedData.length,
          risingSectors: formattedData.filter((s) => s.trend === "up").length,
          fallingSectors: formattedData.filter((s) => s.trend === "down")
            .length,
          totalMarketValue: "36.8万亿",
        });
      }
    } catch (error: any) {
      console.error("获取板块数据失败:", error);
      // 显示模拟数据
      setSectorData([
        {
          key: "1",
          id: "1",
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
          id: "2",
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
          id: "3",
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
          id: "4",
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
          id: "5",
          sectorName: "能源板块",
          stockCount: 98,
          avgPE: 12.3,
          avgPB: 1.2,
          totalMarketValue: "4.1万亿",
          change: "-1.2%",
          trend: "down",
          capitalFlow: "-32亿",
        },
      ]);
      setStats({
        totalSectors: 5,
        risingSectors: 3,
        fallingSectors: 2,
        totalMarketValue: "36.8万亿",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSectorData();
  }, []);

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
      render: (avgPE: number) => avgPE.toFixed(1),
    },
    {
      title: "平均市净率",
      dataIndex: "avgPB",
      key: "avgPB",
      width: 100,
      render: (avgPB: number) => avgPB.toFixed(1),
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
      data: sectorData.map((item) => item.sectorName),
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
        data: sectorData.map((item) => parseFloat(item.change)),
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
      data: sectorData.map((item) => item.sectorName),
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
        data: sectorData.map((item) => parseFloat(item.capitalFlow)),
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
        data: sectorData.map((item, index) => ({
          value: Math.floor(Math.random() * 30) + 10,
          name: item.sectorName,
        })),
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

  const handleAnalyze = () => {
    fetchSectorData();
  };

  const handleRefresh = () => {
    fetchSectorData();
  };

  const handleExport = () => {
    // 导出板块分析报告
    const headers = [
      "板块名称",
      "股票数量",
      "平均市盈率",
      "平均市净率",
      "总市值",
      "涨跌幅",
      "趋势",
      "资金流向",
    ];
    const rows = sectorData.map((item) => [
      item.sectorName,
      item.stockCount,
      item.avgPE.toFixed(1),
      item.avgPB.toFixed(1),
      item.totalMarketValue,
      item.change,
      item.trend === "up" ? "上涨" : "下跌",
      item.capitalFlow,
    ]);

    const csvContent = [
      headers.join(","),
      ...rows.map((row) => row.join(",")),
    ].join("\n");

    const blob = new Blob(["\uFEFF" + csvContent], {
      type: "text/csv;charset=utf-8;",
    });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `sector_analysis_${dayjs().format("YYYYMMDD")}.csv`;
    link.click();
  };

  const getValuationLevel = (pe: number) => {
    if (pe > 40) return { level: "较高", percent: 85, color: "#ff4d4f" };
    if (pe > 25) return { level: "适中", percent: 60, color: "#faad14" };
    return { level: "较低", percent: 35, color: "#52c41a" };
  };

  return (
    <div>
      <h1>板块分析</h1>

      {/* 操作栏 */}
      <Card style={{ marginBottom: 16 }}>
        <Space>
          <Button
            type="primary"
            icon={<BarChartOutlined />}
            onClick={handleAnalyze}
          >
            分析板块
          </Button>
          <Button icon={<ReloadOutlined />} onClick={handleRefresh}>
            刷新数据
          </Button>
          <Button icon={<DownloadOutlined />} onClick={handleExport}>
            导出报告
          </Button>
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
            <Spin spinning={loading}>
              <Statistic
                title="总板块数"
                value={stats.totalSectors}
                prefix={<BarChartOutlined />}
                valueStyle={{ color: "#1890ff" }}
              />
            </Spin>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Spin spinning={loading}>
              <Statistic
                title="上涨板块"
                value={stats.risingSectors}
                prefix={<RiseOutlined />}
                valueStyle={{ color: "#52c41a" }}
              />
            </Spin>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Spin spinning={loading}>
              <Statistic
                title="下跌板块"
                value={stats.fallingSectors}
                prefix={<FallOutlined />}
                valueStyle={{ color: "#cf1322" }}
              />
            </Spin>
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Spin spinning={loading}>
              <Statistic
                title="总市值"
                value={stats.totalMarketValue}
                valueStyle={{ color: "#722ed1" }}
              />
            </Spin>
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
            <Spin spinning={loading}>
              {sectorData.slice(0, 3).map((item, index) => {
                const valuation = getValuationLevel(item.avgPE);
                return (
                  <div key={index} style={{ marginBottom: 16 }}>
                    <h4>{item.sectorName}</h4>
                    <Progress
                      percent={valuation.percent}
                      strokeColor={valuation.color}
                    />
                    <p>
                      市盈率: {item.avgPE.toFixed(1)}，估值{valuation.level}
                    </p>
                  </div>
                );
              })}
            </Spin>
          </Card>
        </Col>
      </Row>

      {/* 板块列表 */}
      <Card title="板块详情">
        <Spin spinning={loading}>
          <Table
            columns={columns}
            dataSource={sectorData}
            pagination={{
              total: sectorData.length,
              pageSize: 10,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total) => `共 ${total} 条记录`,
            }}
            scroll={{ x: 1000 }}
          />
        </Spin>
      </Card>

      {/* 板块分析 */}
      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col span={12}>
          <Card title="板块分析">
            {sectorData.length > 0 && (
              <>
                <div style={{ marginBottom: 16 }}>
                  <h4>{sectorData[0]?.sectorName || "科技板块"}</h4>
                  <p>
                    当前处于上涨趋势，资金流入明显，建议关注人工智能、半导体等细分领域
                  </p>
                </div>
                <div style={{ marginBottom: 16 }}>
                  <h4>{sectorData[1]?.sectorName || "金融板块"}</h4>
                  <p>估值较低，具有防御性，适合稳健型投资者配置</p>
                </div>
                <div>
                  <h4>{sectorData[2]?.sectorName || "消费板块"}</h4>
                  <p>受益于内需复苏，基本面良好，中长期看好</p>
                </div>
              </>
            )}
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
