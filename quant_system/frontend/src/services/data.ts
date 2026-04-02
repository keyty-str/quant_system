/**
 * 数据管理API服务
 */
import axiosInstance from "./api";

export interface StockData {
  code: string;
  name: string;
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  amount: number;
}

export interface Stock {
  code: string;
  name: string;
  exchange: string;
  listDate: string;
  industry?: string;
}

/**
 * 获取股票列表
 */
export const getStockList = async (params?: {
  symbol?: string;
  limit?: number;
}) => {
  return axiosInstance.get("/data/stocks", { params });
};

/**
 * 获取股票价格数据
 */
export const getStockPrices = async (params: {
  symbol: string;
  start_date: string;
  end_date: string;
}) => {
  return axiosInstance.get(`/data/stocks/${params.symbol}/prices`, {
    params: {
      start_date: params.start_date,
      end_date: params.end_date,
    },
  });
};

/**
 * 获取实时行情
 */
export const getRealTimeQuotes = async (symbols: string[]) => {
  return axiosInstance.get("/data/quotes", {
    params: { symbols: symbols.join(",") },
  });
};

/**
 * 更新股票数据
 */
export const updateStockData = async (symbol: string) => {
  return axiosInstance.post(`/data/stocks/${symbol}/update`);
};

/**
 * 获取数据更新状态
 */
export const getUpdateStatus = async () => {
  return axiosInstance.get("/data/update-status");
};
