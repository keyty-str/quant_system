"""
核心数据模型
定义Task、AgentMessage、ReviewResult等核心数据结构
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"           # 待处理
    PLANNING = "planning"         # 规划中
    REVIEWING = "reviewing"       # 审查中
    APPROVED = "approved"         # 已批准
    REJECTED = "rejected"         # 已驳回
    EXECUTING = "executing"       # 执行中
    COMPLETED = "completed"       # 已完成
    FAILED = "failed"             # 失败
    CANCELLED = "cancelled"       # 已取消


class TaskPriority(str, Enum):
    """任务优先级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Task(BaseModel):
    """任务数据模型"""
    task_id: str = Field(description="任务唯一标识")
    title: str = Field(description="任务标题")
    description: str = Field(description="任务描述")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="任务状态")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="优先级")
    
    # 任务分解相关
    subtasks: List["Task"] = Field(default_factory=list, description="子任务列表")
    parent_task_id: Optional[str] = Field(default=None, description="父任务ID")
    
    # 执行相关
    assigned_agents: List[str] = Field(default_factory=list, description="分配的Agent列表")
    required_capabilities: List[str] = Field(default_factory=list, description="所需能力")
    
    # 时间相关
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    deadline: Optional[datetime] = Field(default=None, description="截止时间")
    
    # 结果相关
    result: Optional[Dict[str, Any]] = Field(default=None, description="执行结果")
    error: Optional[str] = Field(default=None, description="错误信息")
    
    # 元数据
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class AgentMessage(BaseModel):
    """Agent间通信消息"""
    message_id: str = Field(description="消息唯一标识")
    sender: str = Field(description="发送者Agent名称")
    receiver: str = Field(description="接收者Agent名称")
    message_type: str = Field(description="消息类型: request/response/notification")
    content: Dict[str, Any] = Field(description="消息内容")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    correlation_id: Optional[str] = Field(default=None, description="关联ID")


class ReviewResult(BaseModel):
    """审查结果"""
    approved: bool = Field(description="是否通过")
    reviewer: str = Field(description="审查者")
    review_time: datetime = Field(default_factory=datetime.now, description="审查时间")
    
    # 审查详情
    criteria_results: Dict[str, bool] = Field(
        default_factory=dict, 
        description="各审查标准结果"
    )
    comments: List[str] = Field(default_factory=list, description="审查意见")
    suggestions: List[str] = Field(default_factory=list, description="改进建议")
    
    # 否决原因（如果被否决）
    veto_reason: Optional[str] = Field(default=None, description="否决原因")
    required_changes: List[str] = Field(default_factory=list, description="需要的修改")


class ExecutionResult(BaseModel):
    """执行结果"""
    task_id: str = Field(description="任务ID")
    success: bool = Field(description="是否成功")
    executor: str = Field(description="执行者")
    
    # 执行详情
    start_time: datetime = Field(description="开始时间")
    end_time: datetime = Field(default_factory=datetime.now, description="结束时间")
    duration_ms: Optional[int] = Field(default=None, description="执行时长(毫秒)")
    
    # 结果数据
    output: Dict[str, Any] = Field(default_factory=dict, description="输出数据")
    artifacts: List[str] = Field(default_factory=list, description="产物文件列表")
    
    # 错误信息
    error_message: Optional[str] = Field(default=None, description="错误信息")
    error_traceback: Optional[str] = Field(default=None, description="错误堆栈")
    
    # 执行日志
    execution_log: List[str] = Field(default_factory=list, description="执行日志")


class AgentCapability(BaseModel):
    """Agent能力定义"""
    name: str = Field(description="能力名称")
    description: str = Field(description="能力描述")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="参数定义")


class AgentConfig(BaseModel):
    """Agent配置"""
    name: str = Field(description="Agent名称")
    role: str = Field(description="Agent角色")
    description: str = Field(description="Agent描述")
    capabilities: List[str] = Field(default_factory=list, description="能力列表")
    max_retries: int = Field(default=3, description="最大重试次数")
    timeout: int = Field(default=60, description="超时时间(秒)")


class WorkflowState(BaseModel):
    """工作流状态"""
    workflow_id: str = Field(description="工作流ID")
    current_phase: str = Field(description="当前阶段")
    tasks: Dict[str, Task] = Field(default_factory=dict, description="任务字典")
    context: Dict[str, Any] = Field(default_factory=dict, description="上下文")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")