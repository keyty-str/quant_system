import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { ConfigProvider } from "antd";
import zhCN from "antd/locale/zh_CN";
import { HelmetProvider } from "react-helmet-async";
import { Toaster } from "react-hot-toast";

// 页面组件
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import DataManagement from "./pages/DataManagement";
import StrategyManagement from "./pages/StrategyManagement";
import Backtest from "./pages/Backtest";
import Prediction from "./pages/Prediction";
import SectorAnalysis from "./pages/SectorAnalysis";
import Settings from "./pages/Settings";

// 样式
import "./styles/global.css";

const App: React.FC = () => {
  return (
    <HelmetProvider>
      <ConfigProvider locale={zhCN}>
        <Router>
          <Layout>
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/data" element={<DataManagement />} />
              <Route path="/strategy" element={<StrategyManagement />} />
              <Route path="/backtest" element={<Backtest />} />
              <Route path="/prediction" element={<Prediction />} />
              <Route path="/sector" element={<SectorAnalysis />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </Layout>
        </Router>
        <Toaster position="top-right" />
      </ConfigProvider>
    </HelmetProvider>
  );
};

export default App;
