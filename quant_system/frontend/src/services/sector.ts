/**
 * 板块分析API服务
 */
import axiosInstance from "./api";

export interface Sector {
  id: string;
  name: string;
  changePercent: number;
  volume: number;
  amount: number;
  leadingStocks: string[];
}

export interface SectorRank {
  name: string;
  changePercent: number;
  volume: number;
  turnoverRate: number;
}

/**
 * 获取板块列表
 */
export const getSectors = async () => {
  return axiosInstance.get("/sector/sectors");
};

/**
 * 获取板块排行
 */
export const getSectorRanking = async (params?: {
  sort_by?: "change" | "volume" | "turnover";
  limit?: number;
}) => {
  return axiosInstance.get("/sector/ranking", { params });
};

/**
 * 获取板块详情
 */
export const getSectorDetail = async (sectorId: string) => {
  return axiosInstance.get(`/sector/${sectorId}`);
};

/**
 * 获取板块成分股
 */
export const getSectorStocks = async (sectorId: string) => {
  return axiosInstance.get(`/sector/${sectorId}/stocks`);
};

/**
 * 获取板块资金流向
 */
export const getSectorFundFlow = async (params?: {
  date?: string;
  limit?: number;
}) => {
  return axiosInstance.get("/sector/fund-flow", { params });
};
