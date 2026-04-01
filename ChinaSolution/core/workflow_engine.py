"""
工作流引擎
驱动三审流程的执行
"""

from typing import Any, Callable, Dict, List, Optional
from datetime import datetime
from enum import Enum
import asyncio
import uuid

from .models import Task, TaskStatus, WorkflowState


class WorkflowPhase(str, Enum):
    """工作流阶段"""
    INTAKE = "intake"           # 需求受理
    PLANNING = "planning"       # 中书省：规划
    REVIEWING = "reviewing"     # 门下省：审查
    EXECUTING = "executing"     # 尚书省：执行
    MONITORING = "monitoring"   # 监控
    COMPLETED = "completed"     # 完成


class WorkflowEngine:
    """
    工作流引擎
    - 管理任务生命周期
    - 驱动三审流程
    - 支持状态持久化
    """
    
    def __init__(self, context_memory=None):
        self.context_memory = context_memory
        self._workflows: Dict[str, WorkflowState] = {}
        self._phase_handlers: Dict[WorkflowPhase, List[Callable]] = {
            phase: [] for phase in WorkflowPhase
        }
        self._transition_rules = self._init_transition_rules()
    
    def _init_transition_rules(self):
        """初始化状态转换规则"""
        return {
            (WorkflowPhase.INTAKE, WorkflowPhase.PLANNING): True,
            (WorkflowPhase.PLANNING, WorkflowPhase.REVIEWING): True,
            (WorkflowPhase.REVIEWING, WorkflowPhase.EXECUTING): True,
            (WorkflowPhase.REVIEWING, WorkflowPhase.PLANNING): True,
            (WorkflowPhase.EXECUTING, WorkflowPhase.MONITORING): True,
            (WorkflowPhase.MONITORING, WorkflowPhase.COMPLETED): True,
            (WorkflowPhase.MONITORING, WorkflowPhase.EXECUTING): True,
        }
    
    def create_workflow(self, workflow_id=None, initial_context=None):
        """创建新工作流"""
        wf_id = workflow_id or str(uuid.uuid4())
        workflow = WorkflowState(
            workflow_id=wf_id,
            current_phase=WorkflowPhase.INTAKE.value,
            tasks={},
            context=initial_context or {},
        )
        self._workflows[wf_id] = workflow
        return workflow
    
    def get_workflow(self, workflow_id):
        """获取工作流"""
        return self._workflows.get(workflow_id)
    
    def get_current_phase(self, workflow_id):
        """获取当前阶段"""
        workflow = self.get_workflow(workflow_id)
        if workflow:
            return WorkflowPhase(workflow.current_phase)
        return None
    
    def can_transition(self, workflow_id, target_phase):
        """检查是否可以转换到目标阶段"""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return False
        current = WorkflowPhase(workflow.current_phase)
        return self._transition_rules.get((current, target_phase), False)
    
    async def transition(self, workflow_id, target_phase, context_updates=None):
        """转换到目标阶段"""
        if not self.can_transition(workflow_id, target_phase):
            return False
        
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return False
        
        current_phase = WorkflowPhase(workflow.current_phase)
        workflow.current_phase = target_phase.value
        workflow.updated_at = datetime.now()
        
        if context_updates:
            workflow.context.update(context_updates)
        
        if self.context_memory:
            self.context_memory.set_task_context(workflow_id, "phase", target_phase.value)
        
        return True
    
    def add_task(self, workflow_id, task):
        """添加任务到工作流"""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return False
        workflow.tasks[task.task_id] = task
        workflow.updated_at = datetime.now()
        return True
    
    def update_task_status(self, workflow_id, task_id, status):
        """更新任务状态"""
        workflow = self.get_workflow(workflow_id)
        if not workflow or task_id not in workflow.tasks:
            return False
        workflow.tasks[task_id].status = status
        workflow.tasks[task_id].updated_at = datetime.now()
        workflow.updated_at = datetime.now()
        return True
    
    def get_tasks_by_status(self, workflow_id, status):
        """按状态获取任务"""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return []
        return [task for task in workflow.tasks.values() if task.status == status]
    
    def get_workflow_summary(self, workflow_id):
        """获取工作流摘要"""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return {}
        
        task_status_counts = {}
        for task in workflow.tasks.values():
            s = task.status.value
            task_status_counts[s] = task_status_counts.get(s, 0) + 1
        
        return {
            "workflow_id": workflow_id,
            "current_phase": workflow.current_phase,
            "total_tasks": len(workflow.tasks),
            "task_status_counts": task_status_counts,
            "created_at": workflow.created_at.isoformat(),
            "updated_at": workflow.updated_at.isoformat(),
        }
    
    def list_workflows(self):
        """列出所有工作流ID"""
        return list(self._workflows.keys())