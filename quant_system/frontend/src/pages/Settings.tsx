import React from "react";
import {
  Card,
  Form,
  Input,
  Button,
  Switch,
  Select,
  InputNumber,
  Divider,
  message,
  Row,
  Col,
} from "antd";
import {
  SaveOutlined,
  ReloadOutlined,
  UserOutlined,
  LockOutlined,
  BellOutlined,
  DatabaseOutlined,
} from "@ant-design/icons";

const { Option } = Select;

const Settings: React.FC = () => {
  const [form] = Form.useForm();

  const handleSave = () => {
    form.validateFields().then((values) => {
      console.log("保存设置:", values);
      message.success("设置保存成功");
    });
  };

  const handleReset = () => {
    form.resetFields();
    message.info("设置已重置");
  };

  return (
    <div>
      <h1>系统设置</h1>

      {/* 操作栏 */}
      <Card style={{ marginBottom: 16 }}>
        <Button
          type="primary"
          icon={<SaveOutlined />}
          onClick={handleSave}
          style={{ marginRight: 8 }}
        >
          保存设置
        </Button>
        <Button icon={<ReloadOutlined />} onClick={handleReset}>
          重置设置
        </Button>
      </Card>

      <Row gutter={16}>
        <Col span={12}>
          {/* 用户设置 */}
          <Card
            title="用户设置"
            icon={<UserOutlined />}
            style={{ marginBottom: 16 }}
          >
            <Form form={form} layout="vertical">
              <Form.Item
                name="username"
                label="用户名"
                rules={[{ required: true, message: "请输入用户名" }]}
              >
                <Input placeholder="请输入用户名" />
              </Form.Item>
              <Form.Item
                name="email"
                label="邮箱"
                rules={[{ required: true, message: "请输入邮箱" }]}
              >
                <Input placeholder="请输入邮箱" />
              </Form.Item>
              <Form.Item name="phone" label="手机号">
                <Input placeholder="请输入手机号" />
              </Form.Item>
            </Form>
          </Card>

          {/* 安全设置 */}
          <Card
            title="安全设置"
            icon={<LockOutlined />}
            style={{ marginBottom: 16 }}
          >
            <Form form={form} layout="vertical">
              <Form.Item
                name="currentPassword"
                label="当前密码"
                rules={[{ required: true, message: "请输入当前密码" }]}
              >
                <Input.Password placeholder="请输入当前密码" />
              </Form.Item>
              <Form.Item
                name="newPassword"
                label="新密码"
                rules={[{ required: true, message: "请输入新密码" }]}
              >
                <Input.Password placeholder="请输入新密码" />
              </Form.Item>
              <Form.Item
                name="confirmPassword"
                label="确认密码"
                rules={[{ required: true, message: "请确认密码" }]}
              >
                <Input.Password placeholder="请确认密码" />
              </Form.Item>
              <Form.Item
                name="twoFactor"
                label="双因素认证"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
            </Form>
          </Card>

          {/* 通知设置 */}
          <Card
            title="通知设置"
            icon={<BellOutlined />}
            style={{ marginBottom: 16 }}
          >
            <Form form={form} layout="vertical">
              <Form.Item
                name="emailNotification"
                label="邮件通知"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
              <Form.Item
                name="smsNotification"
                label="短信通知"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
              <Form.Item
                name="pushNotification"
                label="推送通知"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
              <Form.Item name="notificationFrequency" label="通知频率">
                <Select placeholder="请选择通知频率">
                  <Option value="realtime">实时</Option>
                  <Option value="daily">每日</Option>
                  <Option value="weekly">每周</Option>
                </Select>
              </Form.Item>
            </Form>
          </Card>
        </Col>

        <Col span={12}>
          {/* 交易设置 */}
          <Card title="交易设置" style={{ marginBottom: 16 }}>
            <Form form={form} layout="vertical">
              <Form.Item
                name="defaultCapital"
                label="默认资金"
                rules={[{ required: true, message: "请输入默认资金" }]}
              >
                <InputNumber
                  placeholder="请输入默认资金"
                  style={{ width: "100%" }}
                  formatter={(value) =>
                    `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ",")
                  }
                  parser={(value) => value!.replace(/\$\s?|(,*)/g, "")}
                />
              </Form.Item>
              <Form.Item
                name="maxPosition"
                label="最大仓位"
                rules={[{ required: true, message: "请输入最大仓位" }]}
              >
                <InputNumber
                  placeholder="请输入最大仓位"
                  style={{ width: "100%" }}
                  min={0}
                  max={100}
                  formatter={(value) => `${value}%`}
                  parser={(value) => value!.replace("%", "")}
                />
              </Form.Item>
              <Form.Item
                name="stopLoss"
                label="止损比例"
                rules={[{ required: true, message: "请输入止损比例" }]}
              >
                <InputNumber
                  placeholder="请输入止损比例"
                  style={{ width: "100%" }}
                  min={0}
                  max={100}
                  formatter={(value) => `${value}%`}
                  parser={(value) => value!.replace("%", "")}
                />
              </Form.Item>
              <Form.Item
                name="takeProfit"
                label="止盈比例"
                rules={[{ required: true, message: "请输入止盈比例" }]}
              >
                <InputNumber
                  placeholder="请输入止盈比例"
                  style={{ width: "100%" }}
                  min={0}
                  max={100}
                  formatter={(value) => `${value}%`}
                  parser={(value) => value!.replace("%", "")}
                />
              </Form.Item>
              <Form.Item
                name="commission"
                label="手续费率"
                rules={[{ required: true, message: "请输入手续费率" }]}
              >
                <InputNumber
                  placeholder="请输入手续费率"
                  style={{ width: "100%" }}
                  min={0}
                  max={1}
                  step={0.01}
                  formatter={(value) => `${value}%`}
                  parser={(value) => value!.replace("%", "")}
                />
              </Form.Item>
            </Form>
          </Card>

          {/* 数据设置 */}
          <Card
            title="数据设置"
            icon={<DatabaseOutlined />}
            style={{ marginBottom: 16 }}
          >
            <Form form={form} layout="vertical">
              <Form.Item name="dataUpdateInterval" label="数据更新间隔">
                <Select placeholder="请选择数据更新间隔">
                  <Option value="1">1分钟</Option>
                  <Option value="5">5分钟</Option>
                  <Option value="15">15分钟</Option>
                  <Option value="30">30分钟</Option>
                  <Option value="60">1小时</Option>
                </Select>
              </Form.Item>
              <Form.Item name="dataRetentionDays" label="数据保留天数">
                <InputNumber
                  placeholder="请输入数据保留天数"
                  style={{ width: "100%" }}
                  min={30}
                  max={3650}
                />
              </Form.Item>
              <Form.Item
                name="autoBackup"
                label="自动备份"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
              <Form.Item name="backupFrequency" label="备份频率">
                <Select placeholder="请选择备份频率">
                  <Option value="daily">每日</Option>
                  <Option value="weekly">每周</Option>
                  <Option value="monthly">每月</Option>
                </Select>
              </Form.Item>
            </Form>
          </Card>

          {/* 界面设置 */}
          <Card title="界面设置" style={{ marginBottom: 16 }}>
            <Form form={form} layout="vertical">
              <Form.Item name="theme" label="主题">
                <Select placeholder="请选择主题">
                  <Option value="light">浅色</Option>
                  <Option value="dark">深色</Option>
                  <Option value="auto">自动</Option>
                </Select>
              </Form.Item>
              <Form.Item name="language" label="语言">
                <Select placeholder="请选择语言">
                  <Option value="zh-CN">中文</Option>
                  <Option value="en-US">English</Option>
                </Select>
              </Form.Item>
              <Form.Item name="timezone" label="时区">
                <Select placeholder="请选择时区">
                  <Option value="Asia/Shanghai">亚洲/上海</Option>
                  <Option value="America/New_York">美洲/纽约</Option>
                  <Option value="Europe/London">欧洲/伦敦</Option>
                </Select>
              </Form.Item>
              <Form.Item name="pageSize" label="每页条数">
                <Select placeholder="请选择每页条数">
                  <Option value="10">10条</Option>
                  <Option value="20">20条</Option>
                  <Option value="50">50条</Option>
                  <Option value="100">100条</Option>
                </Select>
              </Form.Item>
            </Form>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Settings;
