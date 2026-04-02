/**
 * 回测系统API服务
 */
import axiosInstance from "./api";

export interface BacktestRequest {
  strategyId: string;
  symbols: string[];
  start_date: string;
  end_date: string;
  initial_capital: number;
  commission?: number;
  slippage?: number;
}

export interface BacktestResult {
  id: string;
  strategyId: string;
  totalReturn: number;
  annualizedReturn: number;
  sharpeRatio: number;
  maxDrawdown: number;
  winRate: number;
  totalTrades: number;
  winningTrades: number;
  losingTrades: number;
  avgWin: number;
  avgLoss: number;
  profitFactor: number;
  trades: Trade[];
  equityCurve: EquityPoint[];
}

export interface Trade {
  id: string;
  symbol: string;
  type: "buy" | "sell";
  price: number;
  quantity: number;
  timestamp: string;
  profit?: number;
}

export interface EquityPoint {
  date: string;
  value: number;
}

/**
 * 运行回测
 */
export const runBacktest = async (data: BacktestRequest) => {
  return axiosInstance.post("/backtest/run", data);
};

/**
 * 获取回测结果
 */
export const getBacktestResult = async (backtestId: string) => {
  return axiosInstance.get(`/backtest/${backtestId}/result`);
};

/**
 * 获取回测历史列表
 */
export const getBacktestHistory = async (params?: {
  strategyId?: string;
  limit?: number;
}) => {
  return axiosInstance.get("/backtest/history", { params });
};

/**
 * 删除回测记录
 */
export const deleteBacktest = async (backtestId: string) => {
  return axiosInstance.delete(`/backtest/${backtestId}`);
};
