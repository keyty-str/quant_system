"""
中书Agent - 需求规划者
负责需求分析、任务分解、方案生成
"""

from typing import Any, Dict, List
from datetime import datetime
import uuid

from core.models import Task, TaskStatus


class ZhongShuAgent:
    """中书省Agent - 需求分析与规划"""
    
    def __init__(self, context_memory=None):
        self.name = "zhongshu"
        self.role = "需求规划者"
        self.context_memory = context_memory
    
    async def create_plan(self, task: Task) -> Dict[str, Any]:
        """创建执行计划"""
        analysis = self._analyze_requirement(task)
        subtasks = self._decompose_task(task, analysis)
        risks = self._assess_risks(subtasks)
        
        return {
            "plan_id": str(uuid.uuid4()),
            "task_id": task.task_id,
            "created_at": datetime.now().isoformat(),
            "creator": self.name,
            "requirement_analysis": analysis,
            "subtasks": subtasks,
            "risks": risks,
            "execution_strategy": {"type": "sequential"},
            "estimated_duration": len(subtasks) * 60,
            "required_resources": self._identify_resources(subtasks),
        }
    
    def _analyze_requirement(self, task: Task) -> Dict[str, Any]:
        """分析需求"""
        desc = task.description.lower()
        task_type = "general"
        
        if any(kw in desc for kw in ["创建", "构建", "开发", "build", "create"]):
            task_type = "creation"
        elif any(kw in desc for kw in ["修复", "修改", "fix"]):
            task_type = "modification"
        elif any(kw in desc for kw in ["分析", "查询", "analyze"]):
            task_type = "analysis"
        
        return {
            "task_type": task_type,
            "complexity": "medium" if len(task.description) < 500 else "high",
            "original_request": task.description,
        }
    
    def _decompose_task(self, task: Task, analysis: Dict) -> List[Dict]:
        """分解任务"""
        task_type = analysis.get("task_type", "general")
        
        if task_type == "creation":
            return [
                {"id": str(uuid.uuid4()), "name": "需求确认", "order": 1, "required_capabilities": ["analysis"]},
                {"id": str(uuid.uuid4()), "name": "方案设计", "order": 2, "required_capabilities": ["design"]},
                {"id": str(uuid.uuid4()), "name": "实现开发", "order": 3, "required_capabilities": ["engineering"]},
                {"id": str(uuid.uuid4()), "name": "测试验证", "order": 4, "required_capabilities": ["testing"]},
            ]
        
        return [
            {"id": str(uuid.uuid4()), "name": "任务分析", "order": 1, "required_capabilities": ["analysis"]},
            {"id": str(uuid.uuid4()), "name": "任务执行", "order": 2, "required_capabilities": ["execution"]},
            {"id": str(uuid.uuid4()), "name": "结果验证", "order": 3, "required_capabilities": ["verification"]},
        ]
    
    def _assess_risks(self, subtasks: List[Dict]) -> List[Dict]:
        """风险评估"""
        risks = []
        if len(subtasks) > 5:
            risks.append({
                "type": "complexity",
                "level": "medium",
                "description": "任务分解较多，协调复杂度较高"
            })
        return risks
    
    def _identify_resources(self, subtasks: List[Dict]) -> List[str]:
        """识别所需资源"""
        resources = set()
        for t in subtasks:
            resources.update(t.get("required_capabilities", []))
        return list(resources)