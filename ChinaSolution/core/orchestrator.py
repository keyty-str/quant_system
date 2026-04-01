"""
战略决策中枢 - Orchestrator
协调三审六司，驱动整个流程
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import asyncio
import uuid

from .models import Task, TaskStatus, TaskPriority, ReviewResult, ExecutionResult
from .workflow_engine import WorkflowEngine, WorkflowPhase
from .context_memory import ContextMemory


class OrchestratorAgent:
    """
    战略决策中枢
    - 接收用户需求
    - 协调三审流程
    - 调度六司执行
    - 质量闭环管理
    """
    
    def __init__(self):
        self.context_memory = ContextMemory()
        self.workflow_engine = WorkflowEngine(self.context_memory)
        self.agents: Dict[str, Any] = {}
        self._setup_default_agents()
    
    def _setup_default_agents(self):
        """初始化默认Agent（延迟加载）"""
        self._agent_factories = {
            "zhongshu": self._create_zhongshu_agent,
            "menxia": self._create_menxia_agent,
            "shangshu": self._create_shangshu_agent,
        }
    
    def register_agent(self, name: str, agent: Any):
        """注册Agent"""
        self.agents[name] = agent
    
    async def _get_or_create_agent(self, name: str):
        """获取或创建Agent"""
        if name not in self.agents and name in self._agent_factories:
            self.agents[name] = await self._agent_factories[name]()
        return self.agents.get(name)
    
    async def _create_zhongshu_agent(self):
        """创建中书Agent"""
        from agents.zhongshu import ZhongShuAgent
        return ZhongShuAgent(self.context_memory)
    
    async def _create_menxia_agent(self):
        """创建门下Agent"""
        from agents.menxia import MenXiaAgent
        return MenXiaAgent(self.context_memory)
    
    async def _create_shangshu_agent(self):
        """创建尚书Agent"""
        from agents.shangshu import ShangShuAgent
        return ShangShuAgent(self.context_memory)
    
    # ==================== 核心流程 ====================
    
    async def process_request(
        self,
        user_request: str,
        priority: TaskPriority = TaskPriority.MEDIUM,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ExecutionResult:
        """
        处理用户请求的主入口
        完整流程：受理 -> 规划 -> 审查 -> 执行 -> 完成
        """
        # 1. 创建主任务
        task_id = str(uuid.uuid4())
        main_task = Task(
            task_id=task_id,
            title=user_request[:100],
            description=user_request,
            priority=priority,
            metadata=metadata or {}
        )
        
        # 2. 创建工作流
        workflow = self.workflow_engine.create_workflow(
            workflow_id=task_id,
            initial_context={"user_request": user_request}
        )
        self.workflow_engine.add_task(task_id, main_task)
        
        # 3. 记录到上下文
        self.context_memory.set_task_context(task_id, "main_task", main_task.dict())
        
        try:
            # 阶段1: 中书省 - 规划
            plan_result = await self._planning_phase(task_id, main_task)
            
            # 阶段2: 门下省 - 审查
            review_result = await self._reviewing_phase(task_id, plan_result)
            
            if not review_result.approved:
                # 审查不通过，返回驳回结果
                return ExecutionResult(
                    task_id=task_id,
                    success=False,
                    executor="orchestrator",
                    start_time=workflow.created_at,
                    error_message=f"审查未通过: {review_result.veto_reason}"
                )
            
            # 阶段3: 尚书省 - 执行
            execution_result = await self._executing_phase(task_id, review_result)
            
            return execution_result
            
        except Exception as e:
            return ExecutionResult(
                task_id=task_id,
                success=False,
                executor="orchestrator",
                start_time=workflow.created_at,
                error_message=str(e)
            )
    
    async def _planning_phase(self, task_id: str, task: Task) -> Dict[str, Any]:
        """规划阶段 - 中书省"""
        await self.workflow_engine.transition(task_id, WorkflowPhase.PLANNING)
        
        zhongshu = await self._get_or_create_agent("zhongshu")
        if not zhongshu:
            raise Exception("中书Agent未初始化")
        
        plan = await zhongshu.create_plan(task)
        
        self.context_memory.set_task_context(task_id, "plan", plan)
        return plan
    
    async def _reviewing_phase(
        self, 
        task_id: str, 
        plan: Dict[str, Any]
    ) -> ReviewResult:
        """审查阶段 - 门下省"""
        await self.workflow_engine.transition(task_id, WorkflowPhase.REVIEWING)
        
        menxia = await self._get_or_create_agent("menxia")
        if not menxia:
            raise Exception("门下Agent未初始化")
        
        review_result = await menxia.review(plan)
        
        self.context_memory.set_task_context(task_id, "review", review_result.dict())
        return review_result
    
    async def _executing_phase(
        self,
        task_id: str,
        review_result: ReviewResult
    ) -> ExecutionResult:
        """执行阶段 - 尚书省"""
        await self.workflow_engine.transition(task_id, WorkflowPhase.EXECUTING)
        
        shangshu = await self._get_or_create_agent("shangshu")
        if not shangshu:
            raise Exception("尚书Agent未初始化")
        
        plan = self.context_memory.get_task_context(task_id, "plan")
        execution_result = await shangshu.execute(plan)
        
        await self.workflow_engine.transition(task_id, WorkflowPhase.COMPLETED)
        
        self.context_memory.set_task_context(task_id, "result", execution_result.dict())
        return execution_result
    
    # ==================== 状态查询 ====================
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        workflow = self.workflow_engine.get_workflow(task_id)
        if not workflow:
            return {"error": "任务不存在"}
        
        summary = self.workflow_engine.get_workflow_summary(task_id)
        context = self.context_memory.get_all_task_context(task_id)
        
        return {
            "summary": summary,
            "context": context
        }
    
    def list_active_tasks(self) -> List[str]:
        """列出所有活跃任务"""
        return self.workflow_engine.list_workflows()