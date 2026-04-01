# 三审六司 - AI多Agent智能治理体系

基于中国古代三省六部制的治理智慧，设计的现代化AI多Agent管理框架。

## 核心理念

本框架将三省六部制的"程序正义"与"制衡思维"，转化为AI系统的"流程可控"与"质量保障"：

- **三审机制**：中书(规划) → 门下(审查) → 尚书(执行)
- **六司体系**：吏/户/礼/兵/刑/工 六个专业化执行Agent
- **双环联动**：稳态环(标准任务) + 敏态环(复杂攻坚)

## 架构概览

```
                    战略决策中枢 (Orchestrator)
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
      中书Agent        门下Agent        尚书Agent
     (需求规划)       (质量审查)       (执行交付)
                                       │
       ┌──────┬──────┬──────┬──────┬────┴────┐
       ▼      ▼      ▼      ▼      ▼         ▼
     吏部   户部   礼部   兵部   刑部      工部
    人员   资源   通信   安全   审计      工程
```

## 快速开始

```python
from core.orchestrator import OrchestratorAgent

# 创建主控Agent
orchestrator = OrchestratorAgent()

# 处理用户需求
result = await orchestrator.process_request("帮我创建一个Web应用")
```

## 目录结构

- `core/` - 核心框架（决策中枢、工作流引擎）
- `agents/` - Agent实现（三审+六司）
- `mechanisms/` - 核心机制（双环、数字孪生、反脆弱）
- `utils/` - 工具类
- `tests/` - 测试用例
