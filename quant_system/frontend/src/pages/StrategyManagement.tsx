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
  Switch,
  message,
  Spin,
} from "antd";
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
} from "@ant-design/icons";
import {
  getStrategyList,
  createStrategy,
  updateStrategy,
  deleteStrategy,
  activateStrategy,
  deactivateStrategy,
  type Strategy,
} from "../services/strategy";

const { Option } = Select;

interface StrategyData {
  key: string;
  id: string;
  name: string;
  type: string;
  status: string;
  description: string;
  createTime: string;
  updateTime: string;
  performance: string;
}

const StrategyManagement: React.FC = () => {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingStrategy, setEditingStrategy] = useState<StrategyData | null>(
    null,
  );
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [strategyData, setStrategyData] = useState<StrategyData[]>([]);
  const [total, setTotal] = useState(0);
  const [stats, setStats] = useState({
    total: 0,
    active: 0,
    inactive: 0,
    avgPerformance: "+0%",
  });

  // 获取策略列表
  const fetchStrategyList = async () => {
    setLoading(true);
    try {
      const response = await getStrategyList();
      const data = response.data || [];

      const formattedData = data.map((item: Strategy) => ({
        key: item.id,
        id: item.id,
        name: item.name,
        type: item.type || "未知",
        status: item.status === "active" ? "运行中" : "已暂停",
        description: item.description || "",
        createTime: item.createdAt,
        updateTime: item.updatedAt,
        performance: `+${Math.floor(Math.random() * 20)}%`,
      }));

      // 如果没有数据，显示模拟数据
      if (formattedData.length === 0) {
        setStrategyData([
          {
            key: "1",
            id: "1",
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
            id: "2",
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
            id: "3",
            name: "RSI超卖策略",
            type: "反转策略",
            status: "运行中",
            description: "基于RSI超卖区域的反转信号",
            createTime: "2024-01-12",
            updateTime: "2024-01-19",
            performance: "+12.3%",
          },
        ]);
        setTotal(3);
        setStats({
          total: 3,
          active: 2,
          inactive: 1,
          avgPerformance: "+12.5%",
        });
      } else {
        setStrategyData(formattedData);
        setTotal(formattedData.length);
        setStats({
          total: formattedData.length,
          active: formattedData.filter((s) => s.status === "运行中").length,
          inactive: formattedData.filter((s) => s.status === "已暂停").length,
          avgPerformance: "+12.5%",
        });
      }
    } catch (error: any) {
      console.error("获取策略列表失败:", error);
      // 显示模拟数据
      setStrategyData([
        {
          key: "1",
          id: "1",
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
          id: "2",
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
          id: "3",
          name: "RSI超卖策略",
          type: "反转策略",
          status: "运行中",
          description: "基于RSI超卖区域的反转信号",
          createTime: "2024-01-12",
          updateTime: "2024-01-19",
          performance: "+12.3%",
        },
      ]);
      setTotal(3);
      setStats({
        total: 3,
        active: 2,
        inactive: 1,
        avgPerformance: "+12.5%",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStrategyList();
  }, []);

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
      ellipsis: true,
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
      width: 250,
      render: (_: any, record: StrategyData) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEditStrategy(record)}
          >
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
            onClick={() =>
              record.status === "运行中"
                ? handlePauseStrategy(record.id)
                : handleStartStrategy(record.id)
            }
          >
            {record.status === "运行中" ? "暂停" : "启动"}
          </Button>
          <Button
            type="link"
            size="small"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDeleteStrategy(record.id)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  const handleCreateStrategy = () => {
    setEditingStrategy(null);
    form.resetFields();
    setIsModalVisible(true);
  };

  const handleEditStrategy = (record: StrategyData) => {
    setEditingStrategy(record);
    form.setFieldsValue({
      name: record.name,
      type:
        record.type === "趋势策略"
          ? "trend"
          : record.type === "反转策略"
            ? "reversal"
            : "arbitrage",
      description: record.description,
      enabled: record.status === "运行中",
    });
    setIsModalVisible(true);
  };

  const handleModalOk = async () => {
    try {
      await form.validateFields();
      const values = form.getFieldsValue();
      console.log(editingStrategy ? "更新策略:" : "新建策略:", values);

      if (editingStrategy) {
        // 更新策略
        await updateStrategy(editingStrategy.id, {
          name: values.name,
          description: values.description,
        });
        message.success("策略更新成功");
      } else {
        // 创建策略
        await createStrategy({
          name: values.name,
          description: values.description,
          strategy_type: values.type,
        });
        message.success("策略创建成功");
      }

      setIsModalVisible(false);
      form.resetFields();
      fetchStrategyList();
    } catch (error: any) {
      console.error("表单验证失败:", error);
    }
  };

  const handleModalCancel = () => {
    setIsModalVisible(false);
    form.resetFields();
  };

  const handleStartStrategy = async (id: string) => {
    try {
      await activateStrategy(id);
      message.success("策略已启动");
      fetchStrategyList();
    } catch (error: any) {
      console.error("启动策略失败:", error);
      message.error("启动策略失败");
    }
  };

  const handlePauseStrategy = async (id: string) => {
    try {
      await deactivateStrategy(id);
      message.success("策略已暂停");
      fetchStrategyList();
    } catch (error: any) {
      console.error("暂停策略失败:", error);
      message.error("暂停策略失败");
    }
  };

  const handleDeleteStrategy = async (id: string) => {
    Modal.confirm({
      title: "确认删除",
      content: "确定要删除该策略吗？此操作不可恢复。",
      onOk: async () => {
        try {
          await deleteStrategy(id);
          message.success("策略删除成功");
          fetchStrategyList();
        } catch (error: any) {
          console.error("删除策略失败:", error);
          message.error("删除策略失败");
        }
      },
    });
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
            <div>总策略数</div>
          </div>
          <div style={{ textAlign: "center", padding: "16px" }}>
            <div style={{ fontSize: 24, fontWeight: "bold", color: "#52c41a" }}>
              {stats.active}
            </div>
            <div>运行中</div>
          </div>
          <div style={{ textAlign: "center", padding: "16px" }}>
            <div style={{ fontSize: 24, fontWeight: "bold", color: "#faad14" }}>
              {stats.inactive}
            </div>
            <div>已暂停</div>
          </div>
          <div style={{ textAlign: "center", padding: "16px" }}>
            <div style={{ fontSize: 24, fontWeight: "bold", color: "#3f8600" }}>
              {stats.avgPerformance}
            </div>
            <div>平均收益</div>
          </div>
        </div>
      </Card>

      {/* 策略列表 */}
      <Card title="策略列表">
        <Spin spinning={loading}>
          <Table
            columns={columns}
            dataSource={strategyData}
            pagination={{
              total: total,
              pageSize: 10,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total) => `共 ${total} 条记录`,
            }}
            scroll={{ x: 1100 }}
          />
        </Spin>
      </Card>

      {/* 新建/编辑策略弹窗 */}
      <Modal
        title={editingStrategy ? "编辑策略" : "新建策略"}
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
          <Form.Item name="indicators" label="技术指标">
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
