"""
协调调度系统模块
负责任务调度、资源分配和工作流管理
借鉴三审六司框架的协调机制
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass
from loguru import logger

from src.utils.config import get_settings
from src.data.storage.mongodb import MongoDB
from src.data.storage.redis_cache import RedisCache


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """任务优先级枚举"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


@dataclass
class Task:
    """任务数据类"""
    task_id: str
    name: str
    task_type: str
    priority: TaskPriority
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    parameters: Dict[str, Any] = None
    result: Dict[str, Any] = None
    error_message: str = None
    retry_count: int = 0
    max_retries: int = 3
    timeout: int = 3600  # 秒
    dependencies: List[str] = None
    assigned_worker: str = None


class CoordinationEngine:
    """协调调度引擎"""
    
    def __init__(self):
        self.settings = get_settings()
        self.mongodb = MongoDB()
        self.redis = RedisCache()
        self.workers: Dict[str, Dict] = {}
        self.task_queue: List[Task] = []
        self.running_tasks: Dict[str, Task] = {}
        self.completed_tasks: Dict[str, Task] = {}
        self.failed_tasks: Dict[str, Task] = {}
        
        # 注册默认worker
        self._register_default_workers()
    
    def _register_default_workers(self):
        """注册默认worker"""
        self.workers = {
            "data_collector": {
                "name": "数据采集Worker",
                "status": "active",
                "capacity": 5,
                "current_load": 0,
                "last_heartbeat": datetime.now().isoformat()
            },
            "strategy_engine": {
                "name": "策略引擎Worker",
                "status": "active",
                "capacity": 3,
                "current_load": 0,
                "last_heartbeat": datetime.now().isoformat()
            },
            "backtest_engine": {
                "name": "回测引擎Worker",
                "status": "active",
                "capacity": 2,
                "current_load": 0,
                "last_heartbeat": datetime.now().isoformat()
            },
            "prediction_engine": {
                "name": "预测引擎Worker",
                "status": "active",
                "capacity": 2,
                "current_load": 0,
                "last_heartbeat": datetime.now().isoformat()
            }
        }
    
    async def submit_task(self, task_data: Dict) -> str:
        """提交任务"""
        try:
            # 创建任务对象
            task = Task(
                task_id=task_data.get('task_id', f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                name=task_data['name'],
                task_type=task_data['type'],
                priority=TaskPriority(task_data.get('priority', 2)),
                status=TaskStatus.PENDING,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                scheduled_at=task_data.get('scheduled_at'),
                parameters=task_data.get('parameters', {}),
                max_retries=task_data.get('max_retries', 3),
                timeout=task_data.get('timeout', 3600),
                dependencies=task_data.get('dependencies', [])
            )
            
            # 保存到数据库
            await self.mongodb.insert_one('tasks', {
                'task_id': task.task_id,
                'name': task.name,
                'type': task.task_type,
                'priority': task.priority.value,
                'status': task.status.value,
                'created_at': task.created_at.isoformat(),
                'updated_at': task.updated_at.isoformat(),
                'scheduled_at': task.scheduled_at.isoformat() if task.scheduled_at else None,
                'parameters': task.parameters,
                'max_retries': task.max_retries,
                'timeout': task.timeout,
                'dependencies': task.dependencies
            })
            
            # 添加到任务队列
            self.task_queue.append(task)
            
            logger.info(f"任务已提交: {task.task_id}")
            return task.task_id
            
        except Exception as e:
            logger.error(f"提交任务失败: {e}")
            return ""
    
    async def schedule_tasks(self):
        """调度任务"""
        try:
            # 按优先级排序任务队列
            self.task_queue.sort(key=lambda x: x.priority.value, reverse=True)
            
            for task in self.task_queue[:]:
                # 检查依赖
                if not await self._check_dependencies(task):
                    continue
                
                # 检查是否到了调度时间
                if task.scheduled_at and task.scheduled_at > datetime.now():
                    continue
                
                # 寻找合适的worker
                worker_id = await self._find_available_worker(task)
                
                if worker_id:
                    # 分配任务给worker
                    await self._assign_task_to_worker(task, worker_id)
                    
                    # 从队列中移除
                    self.task_queue.remove(task)
                    
                    logger.info(f"任务已调度: {task.task_id} -> {worker_id}")
            
        except Exception as e:
            logger.error(f"调度任务失败: {e}")
    
    async def _check_dependencies(self, task: Task) -> bool:
        """检查任务依赖"""
        try:
            if not task.dependencies:
                return True
            
            for dep_task_id in task.dependencies:
                # 检查依赖任务是否完成
                dep_task = await self.mongodb.find_one('tasks', {'task_id': dep_task_id})
                
                if not dep_task:
                    logger.warning(f"依赖任务不存在: {dep_task_id}")
                    return False
                
                if dep_task['status'] != 'completed':
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"检查任务依赖失败: {e}")
            return False
    
    async def _find_available_worker(self, task: Task) -> Optional[str]:
        """寻找可用的worker"""
        try:
            # 根据任务类型选择worker
            worker_mapping = {
                'data_collection': 'data_collector',
                'strategy_execution': 'strategy_engine',
                'backtest': 'backtest_engine',
                'prediction': 'prediction_engine'
            }
            
            preferred_worker = worker_mapping.get(task.task_type)
            
            # 如果指定了preferred worker，优先使用
            if preferred_worker and preferred_worker in self.workers:
                worker = self.workers[preferred_worker]
                if worker['status'] == 'active' and worker['current_load'] < worker['capacity']:
                    return preferred_worker
            
            # 否则寻找任何可用的worker
            for worker_id, worker in self.workers.items():
                if worker['status'] == 'active' and worker['current_load'] < worker['capacity']:
                    return worker_id
            
            return None
            
        except Exception as e:
            logger.error(f"寻找可用worker失败: {e}")
            return None
    
    async def _assign_task_to_worker(self, task: Task, worker_id: str):
        """分配任务给worker"""
        try:
            # 更新任务状态
            task.status = TaskStatus.RUNNING
            task.assigned_worker = worker_id
            task.started_at = datetime.now()
            task.updated_at = datetime.now()
            
            # 更新worker负载
            self.workers[worker_id]['current_load'] += 1
            self.workers[worker_id]['last_heartbeat'] = datetime.now().isoformat()
            
            # 更新数据库
            await self.mongodb.update_one(
                'tasks',
                {'task_id': task.task_id},
                {
                    'status': task.status.value,
                    'assigned_worker': worker_id,
                    'started_at': task.started_at.isoformat(),
                    'updated_at': task.updated_at.isoformat()
                }
            )
            
            # 添加到运行中的任务
            self.running_tasks[task.task_id] = task
            
            # 启动任务执行
            asyncio.create_task(self._execute_task(task))
            
        except Exception as e:
            logger.error(f"分配任务给worker失败: {e}")
    
    async def _execute_task(self, task: Task):
        """执行任务"""
        try:
            logger.info(f"开始执行任务: {task.task_id}")
            
            # 根据任务类型执行不同的逻辑
            if task.task_type == 'data_collection':
                await self._execute_data_collection_task(task)
            elif task.task_type == 'strategy_execution':
                await self._execute_strategy_task(task)
            elif task.task_type == 'backtest':
                await self._execute_backtest_task(task)
            elif task.task_type == 'prediction':
                await self._execute_prediction_task(task)
            else:
                raise Exception(f"未知任务类型: {task.task_type}")
            
            # 任务完成
            await self._complete_task(task)
            
        except Exception as e:
            logger.error(f"执行任务失败: {e}")
            await self._fail_task(task, str(e))
    
    async def _execute_data_collection_task(self, task: Task):
        """执行数据采集任务"""
        try:
            from src.data.collectors.data_collector import DataCollector
            
            collector = DataCollector()
            params = task.parameters
            
            # 根据参数执行不同的数据采集
            if params.get('type') == 'stock_list':
                await collector.collect_stock_list()
            elif params.get('type') == 'sector_list':
                await collector.collect_sector_list()
            elif params.get('type') == 'market_index':
                await collector.collect_market_index()
            elif params.get('type') == 'realtime_data':
                await collector.collect_realtime_data(params.get('stock_codes'))
            elif params.get('type') == 'stock_history':
                await collector.collect_stock_history(
                    params['stock_code'],
                    params.get('start_date'),
                    params.get('end_date')
                )
            else:
                # 执行完整的每日数据采集
                await collector.run_daily_collection()
            
            task.result = {'message': '数据采集完成'}
            
        except Exception as e:
            logger.error(f"执行数据采集任务失败: {e}")
            raise
    
    async def _execute_strategy_task(self, task: Task):
        """执行策略任务"""
        try:
            from src.strategies.strategy_engine import StrategyEngine
            
            engine = StrategyEngine()
            params = task.parameters
            
            strategy_name = params['strategy_name']
            
            # 执行策略生成信号
            signals = await engine.generate_signals(
                strategy_name,
                params.get('stock_codes')
            )
            
            task.result = {
                'strategy_name': strategy_name,
                'signals_count': len(signals),
                'signals': signals[:10]  # 只返回前10个信号
            }
            
        except Exception as e:
            logger.error(f"执行策略任务失败: {e}")
            raise
    
    async def _execute_backtest_task(self, task: Task):
        """执行回测任务"""
        try:
            from src.backtest.backtest_engine import BacktestEngine
            
            engine = BacktestEngine()
            params = task.parameters
            
            # 执行回测
            result = await engine.run_backtest(
                strategy_name=params['strategy_name'],
                stock_codes=params['stock_codes'],
                start_date=params['start_date'],
                end_date=params['end_date'],
                initial_capital=params.get('initial_capital', 1000000.0),
                commission=params.get('commission', 0.001)
            )
            
            task.result = {
                'backtest_id': result.get('task_id'),
                'total_return': result.get('total_return'),
                'sharpe_ratio': result.get('sharpe_ratio'),
                'max_drawdown': result.get('max_drawdown')
            }
            
        except Exception as e:
            logger.error(f"执行回测任务失败: {e}")
            raise
    
    async def _execute_prediction_task(self, task: Task):
        """执行预测任务"""
        try:
            from src.prediction.prediction_engine import PredictionEngine
            
            engine = PredictionEngine()
            params = task.parameters
            
            # 执行预测
            result = await engine.run_prediction_task(
                period=params.get('period', '1m')
            )
            
            task.result = {
                'prediction_id': result.get('task_id'),
                'predictions_count': result.get('predictions_count'),
                'accuracy': result.get('accuracy')
            }
            
        except Exception as e:
            logger.error(f"执行预测任务失败: {e}")
            raise
    
    async def _complete_task(self, task: Task):
        """完成任务"""
        try:
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.updated_at = datetime.now()
            
            # 更新worker负载
            if task.assigned_worker:
                self.workers[task.assigned_worker]['current_load'] -= 1
            
            # 更新数据库
            await self.mongodb.update_one(
                'tasks',
                {'task_id': task.task_id},
                {
                    'status': task.status.value,
                    'completed_at': task.completed_at.isoformat(),
                    'updated_at': task.updated_at.isoformat(),
                    'result': task.result
                }
            )
            
            # 从运行中的任务移除
            if task.task_id in self.running_tasks:
                del self.running_tasks[task.task_id]
            
            # 添加到已完成的任务
            self.completed_tasks[task.task_id] = task
            
            logger.info(f"任务完成: {task.task_id}")
            
        except Exception as e:
            logger.error(f"完成任务失败: {e}")
    
    async def _fail_task(self, task: Task, error_message: str):
        """任务失败"""
        try:
            task.status = TaskStatus.FAILED
            task.error_message = error_message
            task.updated_at = datetime.now()
            
            # 更新worker负载
            if task.assigned_worker:
                self.workers[task.assigned_worker]['current_load'] -= 1
            
            # 检查是否需要重试
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                task.assigned_worker = None
                task.started_at = None
                
                # 重新加入队列
                self.task_queue.append(task)
                
                logger.info(f"任务重试: {task.task_id} (第{task.retry_count}次)")
            else:
                # 更新数据库
                await self.mongodb.update_one(
                    'tasks',
                    {'task_id': task.task_id},
                    {
                        'status': task.status.value,
                        'error_message': error_message,
                        'updated_at': task.updated_at.isoformat(),
                        'retry_count': task.retry_count
                    }
                )
                
                # 从运行中的任务移除
                if task.task_id in self.running_tasks:
                    del self.running_tasks[task.task_id]
                
                # 添加到失败的任务
                self.failed_tasks[task.task_id] = task
                
                logger.error(f"任务最终失败: {task.task_id}")
            
        except Exception as e:
            logger.error(f"处理任务失败失败: {e}")
    
    async def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        try:
            # 从队列中移除
            for task in self.task_queue[:]:
                if task.task_id == task_id:
                    task.status = TaskStatus.CANCELLED
                    task.updated_at = datetime.now()
                    
                    # 更新数据库
                    await self.mongodb.update_one(
                        'tasks',
                        {'task_id': task_id},
                        {
                            'status': 'cancelled',
                            'updated_at': task.updated_at.isoformat()
                        }
                    )
                    
                    self.task_queue.remove(task)
                    logger.info(f"任务已取消: {task_id}")
                    return True
            
            # 如果任务正在运行，标记为取消
            if task_id in self.running_tasks:
                task = self.running_tasks[task_id]
                task.status = TaskStatus.CANCELLED
                task.updated_at = datetime.now()
                
                # 更新worker负载
                if task.assigned_worker:
                    self.workers[task.assigned_worker]['current_load'] -= 1
                
                # 更新数据库
                await self.mongodb.update_one(
                    'tasks',
                    {'task_id': task_id},
                    {
                        'status': 'cancelled',
                        'updated_at': task.updated_at.isoformat()
                    }
                )
                
                del self.running_tasks[task_id]
                logger.info(f"运行中的任务已取消: {task_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"取消任务失败: {e}")
            return False
    
    async def get_task_status(self, task_id: str) -> Dict:
        """获取任务状态"""
        try:
            # 先从内存中查找
            if task_id in self.running_tasks:
                task = self.running_tasks[task_id]
                return {
                    'task_id': task.task_id,
                    'name': task.name,
                    'status': task.status.value,
                    'priority': task.priority.value,
                    'assigned_worker': task.assigned_worker,
                    'created_at': task.created_at.isoformat(),
                    'started_at': task.started_at.isoformat() if task.started_at else None,
                    'progress': self._calculate_task_progress(task)
                }
            
            # 从数据库获取
            task = await self.mongodb.find_one('tasks', {'task_id': task_id})
            return task if task else {}
            
        except Exception as e:
            logger.error(f"获取任务状态失败: {e}")
            return {}
    
    def _calculate_task_progress(self, task: Task) -> float:
        """计算任务进度"""
        try:
            # 简单进度估算
            if task.status == TaskStatus.PENDING:
                return 0.0
            elif task.status == TaskStatus.RUNNING:
                # 基于运行时间估算进度
                if task.started_at:
                    elapsed = (datetime.now() - task.started_at).total_seconds()
                    progress = min(elapsed / task.timeout, 0.95)  # 最多95%
                    return progress
                return 0.1
            elif task.status == TaskStatus.COMPLETED:
                return 1.0
            elif task.status == TaskStatus.FAILED:
                return 0.0
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"计算任务进度失败: {e}")
            return 0.0
    
    async def get_system_status(self) -> Dict:
        """获取系统状态"""
        try:
            # 获取任务统计
            total_tasks = await self.mongodb.count_documents('tasks', {})
            pending_tasks = await self.mongodb.count_documents('tasks', {'status': 'pending'})
            running_tasks = await self.mongodb.count_documents('tasks', {'status': 'running'})
            completed_tasks = await self.mongodb.count_documents('tasks', {'status': 'completed'})
            failed_tasks = await self.mongodb.count_documents('tasks', {'status': 'failed'})
            
            # 获取worker状态
            worker_status = {}
            for worker_id, worker in self.workers.items():
                worker_status[worker_id] = {
                    'name': worker['name'],
                    'status': worker['status'],
                    'capacity': worker['capacity'],
                    'current_load': worker['current_load'],
                    'utilization': worker['current_load'] / worker['capacity'] if worker['capacity'] > 0 else 0,
                    'last_heartbeat': worker['last_heartbeat']
                }
            
            return {
                'system_status': 'running',
                'timestamp': datetime.now().isoformat(),
                'task_statistics': {
                    'total': total_tasks,
                    'pending': pending_tasks,
                    'running': running_tasks,
                    'completed': completed_tasks,
                    'failed': failed_tasks
                },
                'worker_status': worker_status,
                'queue_length': len(self.task_queue),
                'running_tasks_count': len(self.running_tasks)
            }
            
        except Exception as e:
            logger.error(f"获取系统状态失败: {e}")
            return {}
    
    async def run_scheduler(self):
        """运行调度器"""
        try:
            logger.info("启动任务调度器...")
            
            while True:
                # 调度任务
                await self.schedule_tasks()
                
                # 检查超时任务
                await self._check_timeout_tasks()
                
                # 更新worker心跳
                await self._update_worker_heartbeat()
                
                # 等待一段时间
                await asyncio.sleep(5)  # 每5秒检查一次
                
        except Exception as e:
            logger.error(f"运行调度器失败: {e}")
    
    async def _check_timeout_tasks(self):
        """检查超时任务"""
        try:
            current_time = datetime.now()
            
            for task_id, task in list(self.running_tasks.items()):
                if task.started_at:
                    elapsed = (current_time - task.started_at).total_seconds()
                    
                    if elapsed > task.timeout:
                        logger.warning(f"任务超时: {task_id}")
                        await self._fail_task(task, "任务执行超时")
            
        except Exception as e:
            logger.error(f"检查超时任务失败: {e}")
    
    async def _update_worker_heartbeat(self):
        """更新worker心跳"""
        try:
            current_time = datetime.now().isoformat()
            
            for worker_id in self.workers:
                self.workers[worker_id]['last_heartbeat'] = current_time
            
        except Exception as e:
            logger.error(f"更新worker心跳失败: {e}")
    
    async def create_workflow(self, workflow_data: Dict) -> str:
        """创建工作流"""
        try:
            workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            workflow = {
                'workflow_id': workflow_id,
                'name': workflow_data['name'],
                'description': workflow_data.get('description', ''),
                'tasks': workflow_data['tasks'],
                'status': 'created',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # 保存工作流
            await self.mongodb.insert_one('workflows', workflow)
            
            # 提交工作流中的任务
            task_ids = []
            for task_data in workflow_data['tasks']:
                task_data['workflow_id'] = workflow_id
                task_id = await self.submit_task(task_data)
                task_ids.append(task_id)
            
            # 更新工作流中的任务ID
            await self.mongodb.update_one(
                'workflows',
                {'workflow_id': workflow_id},
                {'task_ids': task_ids, 'updated_at': datetime.now().isoformat()}
            )
            
            logger.info(f"工作流已创建: {workflow_id}")
            return workflow_id
            
        except Exception as e:
            logger.error(f"创建工作流失败: {e}")
            return ""
    
    async def get_workflow_status(self, workflow_id: str) -> Dict:
        """获取工作流状态"""
        try:
            workflow = await self.mongodb.find_one('workflows', {'workflow_id': workflow_id})
            
            if not workflow:
                return {}
            
            # 获取工作流中所有任务的状态
            task_statuses = []
            for task_id in workflow.get('task_ids', []):
                task_status = await self.get_task_status(task_id)
                if task_status:
                    task_statuses.append(task_status)
            
            # 计算工作流进度
            total_tasks = len(task_statuses)
            completed_tasks = len([t for t in task_statuses if t.get('status') == 'completed'])
            progress = completed_tasks / total_tasks if total_tasks > 0 else 0
            
            workflow['task_statuses'] = task_statuses
            workflow['progress'] = progress
            
            return workflow
            
        except Exception as e:
            logger.error(f"获取工作流状态失败: {e}")
            return {}


# 创建全局协调调度引擎实例
coordination_engine = CoordinationEngine()