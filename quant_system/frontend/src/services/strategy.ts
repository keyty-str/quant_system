/**
 * 策略管理API服务
 */
import axiosInstance from "./api";

export interface Strategy {
  id: string;
  name: string;
  description: string;
  type: string;
  parameters: Record<string, unknown>;
  status: "active" | "inactive";
  createdAt: string;
  updatedAt: string;
}

export interface StrategySignal {
  id: string;
  strategyId: string;
  symbol: string;
  type: "buy" | "sell";
  price: number;
  quantity: number;
  timestamp: string;
}

/**
 * 获取策略列表
 */
export const getStrategyList = async () => {
  return axiosInstance.get("/strategy/list");
};

/**
 * 获取策略详情
 */
export const getStrategyDetail = async (strategyId: string) => {
  return axiosInstance.get(`/strategy/${strategyId}`);
};

/**
 * 创建策略
 */
export const createStrategy = async (data: {
  name: string;
  description: string;
  strategy_type: string;
  parameters?: Record<string, unknown>;
}) => {
  return axiosInstance.post("/strategy/create", data);
};

/**
 * 更新策略
 */
export const updateStrategy = async (
  strategyId: string,
  data: {
    name?: string;
    description?: string;
    parameters?: Record<string, unknown>;
  },
) => {
  return axiosInstance.put(`/strategy/${strategyId}`, data);
};

/**
 * 删除策略
 */
export const deleteStrategy = async (strategyId: string) => {
  return axiosInstance.delete(`/strategy/${strategyId}`);
};

/**
 * 激活策略
 */
export const activateStrategy = async (strategyId: string) => {
  return axiosInstance.post(`/strategy/${strategyId}/activate`);
};

/**
 * 停用策略
 */
export const deactivateStrategy = async (strategyId: string) => {
  return axiosInstance.post(`/strategy/${strategyId}/deactivate`);
};

/**
 * 获取策略信号
 */
export const getStrategySignals = async (params: {
  strategyId: string;
  start_date?: string;
  end_date?: string;
}) => {
  return axiosInstance.get(`/strategy/${params.strategyId}/signals`, {
    params: {
      start_date: params.start_date,
      end_date: params.end_date,
    },
  });
};

/**
 * 获取策略类型列表
 */
export const getStrategyTypes = async () => {
  return axiosInstance.get("/strategy/types");
};

/**
 * 获取技术指标列表
 */
export const getTechnicalIndicators = async () => {
  return axiosInstance.get("/strategy/indicators");
};
