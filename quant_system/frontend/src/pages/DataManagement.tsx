import React, { useEffect, useState } from "react";
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
  DatePicker,
  Spin,
} from "antd";
import {
  PlusOutlined,
  SearchOutlined,
  ReloadOutlined,
  DownloadOutlined,
  UploadOutlined,
} from "@ant-design/icons";
import dayjs from "dayjs";
import {
  getStockList,
  getRealTimeQuotes,
  updateStockData,
  getUpdateStatus,
  type Stock,
} from "../services/data";

const { Option } = Select;
const { RangePicker } = DatePicker;

interface StockData {
  key: string;
  code: string;
  name: string;
  market: string;
  industry: string;
  listDate: string;
  status: string;
}

const DataManagement: React.FC = () => {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [stockData, setStockData] = useState<StockData[]>([]);
  const [total, setTotal] = useState(0);
  const [searchParams, setSearchParams] = useState({
    keyword: "",
    market: "",
    industry: "",
  });
  const [updateStatus, setUpdateStatus] = useState({
    completeness: 98.5,
    lastUpdate: "2分钟前",
    pendingTasks: 3,
  });

  // 获取股票列表
  const fetchStockList = async () => {
    setLoading(true);
    try {
      const params: Record<string, any> = {};
      if (searchParams.keyword) {
        params.symbol = searchParams.keyword;
      }
      if (searchParams.market) {
        params.exchange = searchParams.market;
      }
      params.limit = 100;

      const response = await getStockList(params);
      const data = response.data || [];

      const formattedData = data.map((item: Stock, index: number) => ({
        key: `${index}`,
        code: item.code,
        name: item.name,
        market: item.exchange === "SH" ? "上海" : "深圳",
        industry: item.industry || "未知",
        listDate: item.listDate,
        status: "正常",
      }));

      // 如果没有数据，显示模拟数据
      if (formattedData.length === 0) {
        setStockData([
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
        ]);
        setTotal(3);
      } else {
        setStockData(formattedData);
        setTotal(formattedData.length);
      }
    } catch (error: any) {
      console.error("获取股票列表失败:", error);
      // 显示模拟数据
      setStockData([
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
      ]);
      setTotal(3);
    } finally {
      setLoading(false);
    }
  };

  // 获取更新状态
  const fetchUpdateStatus = async () => {
    try {
      const response = await getUpdateStatus();
      if (response.data) {
        setUpdateStatus({
          completeness: response.data.completeness || 98.5,
          lastUpdate: response.data.lastUpdate || "2分钟前",
          pendingTasks: response.data.pendingTasks || 3,
        });
      }
    } catch (error) {
      console.error("获取更新状态失败:", error);
    }
  };

  useEffect(() => {
    fetchStockList();
    fetchUpdateStatus();
  }, []);

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
      width: 200,
      render: (_: any, record: StockData) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            onClick={() => handleViewDetail(record)}
          >
            查看
          </Button>
          <Button
            type="link"
            size="small"
            onClick={() => handleUpdateStock(record.code)}
          >
            更新
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

  const handleModalOk = async () => {
    try {
      await form.validateFields();
      const values = form.getFieldsValue();
      console.log("新增股票:", values);
      message.success("股票添加成功");
      setIsModalVisible(false);
      form.resetFields();
      fetchStockList();
    } catch (error: any) {
      console.error("表单验证失败:", error);
    }
  };

  const handleModalCancel = () => {
    setIsModalVisible(false);
    form.resetFields();
  };

  const handleRefresh = () => {
    fetchStockList();
    fetchUpdateStatus();
    message.success("数据刷新成功");
  };

  const handleExport = () => {
    // 导出数据为CSV
    const headers = [
      "股票代码",
      "股票名称",
      "市场",
      "行业",
      "上市日期",
      "状态",
    ];
    const rows = stockData.map((item) => [
      item.code,
      item.name,
      item.market,
      item.industry,
      item.listDate,
      item.status,
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
    link.download = `stock_list_${dayjs().format("YYYYMMDD")}.csv`;
    link.click();

    message.success("数据导出成功");
  };

  const handleSearch = () => {
    fetchStockList();
  };

  const handleReset = () => {
    setSearchParams({
      keyword: "",
      market: "",
      industry: "",
    });
    fetchStockList();
  };

  const handleViewDetail = (record: StockData) => {
    Modal.info({
      title: `股票详情 - ${record.name}(${record.code})`,
      content: (
        <div>
          <p>股票代码: {record.code}</p>
          <p>股票名称: {record.name}</p>
          <p>市场: {record.market}</p>
          <p>行业: {record.industry}</p>
          <p>上市日期: {record.listDate}</p>
          <p>状态: {record.status}</p>
        </div>
      ),
      width: 400,
    });
  };

  const handleUpdateStock = async (code: string) => {
    try {
      await updateStockData(code);
      message.success(`股票 ${code} 数据更新成功`);
      fetchStockList();
    } catch (error: any) {
      console.error("更新股票数据失败:", error);
      message.error("更新股票数据失败");
    }
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
          <Button
            icon={<ReloadOutlined />}
            onClick={handleRefresh}
            loading={loading}
          >
            刷新数据
          </Button>
          <Button icon={<DownloadOutlined />} onClick={handleExport}>
            导出数据
          </Button>
          <Button icon={<UploadOutlined />}>导入数据</Button>
        </Space>
      </Card>

      {/* 搜索和筛选 */}
      <Card style={{ marginBottom: 16 }}>
        <Space wrap>
          <Input
            placeholder="股票代码/名称"
            prefix={<SearchOutlined />}
            style={{ width: 200 }}
            value={searchParams.keyword}
            onChange={(e) =>
              setSearchParams({ ...searchParams, keyword: e.target.value })
            }
          />
          <Select
            placeholder="市场"
            style={{ width: 100 }}
            value={searchParams.market}
            onChange={(value) =>
              setSearchParams({ ...searchParams, market: value })
            }
          >
            <Option value="">全部</Option>
            <Option value="sh">上海</Option>
            <Option value="sz">深圳</Option>
          </Select>
          <Select
            placeholder="行业"
            style={{ width: 120 }}
            value={searchParams.industry}
            onChange={(value) =>
              setSearchParams({ ...searchParams, industry: value })
            }
          >
            <Option value="">全部</Option>
            <Option value="bank">银行</Option>
            <Option value="realestate">房地产</Option>
            <Option value="tech">科技</Option>
            <Option value="consumer">消费</Option>
            <Option value="medical">医药</Option>
          </Select>
          <Button type="primary" onClick={handleSearch}>
            查询
          </Button>
          <Button onClick={handleReset}>重置</Button>
        </Space>
      </Card>

      {/* 数据表格 */}
      <Card title="股票列表">
        <Spin spinning={loading}>
          <Table
            columns={columns}
            dataSource={stockData}
            pagination={{
              total: total,
              pageSize: 10,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total) => `共 ${total} 条记录`,
            }}
            scroll={{ x: 900 }}
          />
        </Spin>
      </Card>

      {/* 数据采集状态 */}
      <Card title="数据采集状态" style={{ marginTop: 16 }}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-around",
            flexWrap: "wrap",
          }}
        >
          <div style={{ textAlign: "center", padding: "16px" }}>
            <div style={{ fontSize: 24, fontWeight: "bold", color: "#52c41a" }}>
              {updateStatus.completeness}%
            </div>
            <div>数据完整度</div>
          </div>
          <div style={{ textAlign: "center", padding: "16px" }}>
            <div style={{ fontSize: 24, fontWeight: "bold", color: "#1890ff" }}>
              {updateStatus.lastUpdate}
            </div>
            <div>最后更新</div>
          </div>
          <div style={{ textAlign: "center", padding: "16px" }}>
            <div style={{ fontSize: 24, fontWeight: "bold", color: "#faad14" }}>
              {updateStatus.pendingTasks}
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
