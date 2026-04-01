import React, { useState } from "react";
import { Layout as AntLayout, Menu, Button, Avatar, Dropdown } from "antd";
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  DashboardOutlined,
  DatabaseOutlined,
  ExperimentOutlined,
  LineChartOutlined,
  PieChartOutlined,
  BarChartOutlined,
  SettingOutlined,
  UserOutlined,
  LogoutOutlined,
} from "@ant-design/icons";
import { useNavigate, useLocation } from "react-router-dom";

const { Header, Sider, Content } = AntLayout;

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: "/dashboard",
      icon: <DashboardOutlined />,
      label: "仪表板",
    },
    {
      key: "/data",
      icon: <DatabaseOutlined />,
      label: "数据管理",
    },
    {
      key: "/strategy",
      icon: <ExperimentOutlined />,
      label: "策略管理",
    },
    {
      key: "/backtest",
      icon: <LineChartOutlined />,
      label: "回测系统",
    },
    {
      key: "/prediction",
      icon: <PieChartOutlined />,
      label: "预测系统",
    },
    {
      key: "/sector",
      icon: <BarChartOutlined />,
      label: "板块分析",
    },
    {
      key: "/settings",
      icon: <SettingOutlined />,
      label: "系统设置",
    },
  ];

  const userMenuItems = [
    {
      key: "profile",
      icon: <UserOutlined />,
      label: "个人资料",
    },
    {
      key: "logout",
      icon: <LogoutOutlined />,
      label: "退出登录",
    },
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  const handleUserMenuClick = ({ key }: { key: string }) => {
    if (key === "logout") {
      // 处理退出登录
      console.log("退出登录");
    }
  };

  return (
    <AntLayout style={{ minHeight: "100vh" }}>
      <Sider trigger={null} collapsible collapsed={collapsed}>
        <div
          style={{
            height: 32,
            margin: 16,
            background: "rgba(255, 255, 255, 0.2)",
            borderRadius: 6,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "white",
            fontWeight: "bold",
            fontSize: collapsed ? 12 : 16,
          }}
        >
          {collapsed ? "量化" : "量化交易系统"}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
        />
      </Sider>
      <AntLayout>
        <Header
          style={{
            padding: 0,
            background: "white",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
            style={{
              fontSize: "16px",
              width: 64,
              height: 64,
            }}
          />
          <div style={{ marginRight: 24 }}>
            <Dropdown
              menu={{
                items: userMenuItems,
                onClick: handleUserMenuClick,
              }}
              placement="bottomRight"
            >
              <Avatar
                style={{ backgroundColor: "#1890ff", cursor: "pointer" }}
                icon={<UserOutlined />}
              />
            </Dropdown>
          </div>
        </Header>
        <Content
          style={{
            margin: "24px 16px",
            padding: 24,
            background: "white",
            borderRadius: 8,
            minHeight: 280,
          }}
        >
          {children}
        </Content>
      </AntLayout>
    </AntLayout>
  );
};

export default Layout;
