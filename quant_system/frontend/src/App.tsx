import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  Outlet,
} from "react-router-dom";
import { ConfigProvider } from "antd";
import zhCN from "antd/locale/zh_CN";
import { HelmetProvider } from "react-helmet-async";
import { Toaster } from "react-hot-toast";

// 页面组件
import Layout from "./components/Layout";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import DataManagement from "./pages/DataManagement";
import StrategyManagement from "./pages/StrategyManagement";
import Backtest from "./pages/Backtest";
import Prediction from "./pages/Prediction";
import SectorAnalysis from "./pages/SectorAnalysis";
import Settings from "./pages/Settings";

// 认证状态
import useAuthStore from "./store/auth";

// 受保护的路由组件
const ProtectedRoute: React.FC = () => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  if (!isAuthenticated) {
    // 重定向到登录页，并保存当前路径
    return (
      <Navigate
        to="/login"
        replace
        state={{ from: window.location.pathname }}
      />
    );
  }

  return (
    <Layout>
      <Outlet />
    </Layout>
  );
};

const App: React.FC = () => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  return (
    <HelmetProvider>
      <ConfigProvider locale={zhCN}>
        <Router>
          <Routes>
            {/* 公开路由 */}
            <Route
              path="/login"
              element={
                isAuthenticated ? (
                  <Navigate to="/dashboard" replace />
                ) : (
                  <Login />
                )
              }
            />
            <Route
              path="/register"
              element={
                isAuthenticated ? (
                  <Navigate to="/dashboard" replace />
                ) : (
                  <Register />
                )
              }
            />

            {/* 受保护的路由 */}
            <Route path="/" element={<ProtectedRoute />}>
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="data" element={<DataManagement />} />
              <Route path="strategy" element={<StrategyManagement />} />
              <Route path="backtest" element={<Backtest />} />
              <Route path="prediction" element={<Prediction />} />
              <Route path="sector" element={<SectorAnalysis />} />
              <Route path="settings" element={<Settings />} />
            </Route>

            {/* 404重定向 */}
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </Router>
        <Toaster position="top-right" />
      </ConfigProvider>
    </HelmetProvider>
  );
};

export default App;
