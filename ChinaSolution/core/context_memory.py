"""
上下文记忆系统
提供全局状态管理和Agent间信息共享
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from collections import defaultdict
import threading


class ContextMemory:
    """
    全局上下文记忆系统
    - 存储任务执行过程中的上下文信息
    - 支持Agent间信息共享
    - 提供历史记录和追溯能力
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        self._global_context: Dict[str, Any] = {}
        self._task_contexts: Dict[str, Dict[str, Any]] = {}
        self._agent_states: Dict[str, Dict[str, Any]] = {}
        self._history: List[Dict[str, Any]] = []
        self._max_history = 1000
    
    # ==================== 全局上下文操作 ====================
    
    def set_global(self, key: str, value: Any) -> None:
        """设置全局上下文"""
        with self._lock:
            self._global_context[key] = value
            self._record_history("set_global", key, value)
    
    def get_global(self, key: str, default: Any = None) -> Any:
        """获取全局上下文"""
        with self._lock:
            return self._global_context.get(key, default)
    
    def delete_global(self, key: str) -> None:
        """删除全局上下文"""
        with self._lock:
            if key in self._global_context:
                del self._global_context[key]
                self._record_history("delete_global", key, None)
    
    # ==================== 任务上下文操作 ====================
    
    def set_task_context(self, task_id: str, key: str, value: Any) -> None:
        """设置任务上下文"""
        with self._lock:
            if task_id not in self._task_contexts:
                self._task_contexts[task_id] = {}
            self._task_contexts[task_id][key] = value
            self._record_history("set_task_context", f"{task_id}.{key}", value)
    
    def get_task_context(self, task_id: str, key: str, default: Any = None) -> Any:
        """获取任务上下文"""
        with self._lock:
            if task_id not in self._task_contexts:
                return default
            return self._task_contexts[task_id].get(key, default)
    
    def get_all_task_context(self, task_id: str) -> Dict[str, Any]:
        """获取任务的所有上下文"""
        with self._lock:
            return self._task_contexts.get(task_id, {}).copy()
    
    def clear_task_context(self, task_id: str) -> None:
        """清除任务上下文"""
        with self._lock:
            if task_id in self._task_contexts:
                del self._task_contexts[task_id]
                self._record_history("clear_task_context", task_id, None)
    
    # ==================== Agent状态操作 ====================
    
    def set_agent_state(self, agent_name: str, state: Dict[str, Any]) -> None:
        """设置Agent状态"""
        with self._lock:
            self._agent_states[agent_name] = {
                **state,
                "updated_at": datetime.now().isoformat()
            }
            self._record_history("set_agent_state", agent_name, state)
    
    def get_agent_state(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """获取Agent状态"""
        with self._lock:
            return self._agent_states.get(agent_name)
    
    def update_agent_state(self, agent_name: str, updates: Dict[str, Any]) -> None:
        """更新Agent状态"""
        with self._lock:
            if agent_name not in self._agent_states:
                self._agent_states[agent_name] = {}
            self._agent_states[agent_name].update(updates)
            self._agent_states[agent_name]["updated_at"] = datetime.now().isoformat()
    
    # ==================== 历史记录操作 ====================
    
    def _record_history(self, action: str, key: str, value: Any) -> None:
        """记录历史"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "key": key,
            "value": str(value)[:200] if value else None  # 限制长度
        }
        self._history.append(entry)
        
        # 限制历史记录数量
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]
    
    def get_history(
        self, 
        action_filter: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取历史记录"""
        with self._lock:
            history = self._history.copy()
            
            if action_filter:
                history = [h for h in history if h["action"] == action_filter]
            
            return history[-limit:]
    
    def clear_history(self) -> None:
        """清除历史记录"""
        with self._lock:
            self._history.clear()
    
    # ==================== 批量操作 ====================
    
    def snapshot(self) -> Dict[str, Any]:
        """创建当前状态快照"""
        with self._lock:
            return {
                "timestamp": datetime.now().isoformat(),
                "global_context": self._global_context.copy(),
                "task_contexts": {k: v.copy() for k, v in self._task_contexts.items()},
                "agent_states": {k: v.copy() for k, v in self._agent_states.items()},
            }
    
    def restore(self, snapshot: Dict[str, Any]) -> None:
        """从快照恢复状态"""
        with self._lock:
            self._global_context = snapshot.get("global_context", {}).copy()
            self._task_contexts = {
                k: v.copy() for k, v in snapshot.get("task_contexts", {}).items()
            }
            self._agent_states = {
                k: v.copy() for k, v in snapshot.get("agent_states", {}).items()
            }
            self._record_history("restore", "snapshot", snapshot["timestamp"])
    
    # ==================== 查询操作 ====================
    
    def search(
        self, 
        query: str, 
        scope: str = "all"
    ) -> Dict[str, List[str]]:
        """搜索上下文中的关键字"""
        results = {
            "global": [],
            "task": [],
            "agent": []
        }
        
        with self._lock:
            query_lower = query.lower()
            
            if scope in ("all", "global"):
                for key, value in self._global_context.items():
                    if query_lower in key.lower() or query_lower in str(value).lower():
                        results["global"].append(key)
            
            if scope in ("all", "task"):
                for task_id, ctx in self._task_contexts.items():
                    for key, value in ctx.items():
                        if query_lower in key.lower() or query_lower in str(value).lower():
                            results["task"].append(f"{task_id}.{key}")
            
            if scope in ("all", "agent"):
                for agent_name, state in self._agent_states.items():
                    if query_lower in agent_name.lower() or query_lower in str(state).lower():
                        results["agent"].append(agent_name)
        
        return results