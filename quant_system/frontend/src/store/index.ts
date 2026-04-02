/**
 * 全局状态管理
 */
import { create } from "zustand";
import type { Strategy } from "../services/strategy";
import type { BacktestResult } from "../services/backtest";

interface AppState {
  // 用户信息
  user: {
    name: string;
    email: string;
  } | null;

  // 系统状态
  systemStatus: {
    backendConnected: boolean;
    mongodbConnected: boolean;
    redisConnected: boolean;
    lastCheck: string | null;
  };

  // 当前活跃策略
  activeStrategies: Strategy[];

  // 回测结果缓存
  backtestResults: Map<string, BacktestResult>;

  // 设置
  settings: {
    theme: "light" | "dark";
    language: "zh-CN" | "en-US";
    refreshInterval: number;
  };

  // 操作
  setSystemStatus: (status: Partial<AppState["systemStatus"]>) => void;
  setActiveStrategies: (strategies: Strategy[]) => void;
  addBacktestResult: (id: string, result: BacktestResult) => void;
  updateSettings: (settings: Partial<AppState["settings"]>) => void;
  login: (user: { name: string; email: string }) => void;
  logout: () => void;
}

const useStore = create<AppState>((set) => ({
  // 初始状态
  user: null,

  systemStatus: {
    backendConnected: false,
    mongodbConnected: false,
    redisConnected: false,
    lastCheck: null,
  },

  activeStrategies: [],

  backtestResults: new Map(),

  settings: {
    theme: "light",
    language: "zh-CN",
    refreshInterval: 5000,
  },

  // 操作
  setSystemStatus: (status) =>
    set((state) => ({
      systemStatus: { ...state.systemStatus, ...status },
    })),

  setActiveStrategies: (strategies) => set({ activeStrategies: strategies }),

  addBacktestResult: (id, result) =>
    set((state) => {
      const newMap = new Map(state.backtestResults);
      newMap.set(id, result);
      return { backtestResults: newMap };
    }),

  updateSettings: (settings) =>
    set((state) => ({
      settings: { ...state.settings, ...settings },
    })),

  login: (user) => set({ user }),

  logout: () => set({ user: null }),
}));

export default useStore;
