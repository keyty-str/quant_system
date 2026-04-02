"""
风险控制模块
负责投资组合的风险管理和资金控制
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from loguru import logger


class RiskManager:
    """风险管理器"""
    
    # 默认参数
    DEFAULT_MAX_POSITION = 0.3  # 单只股票最大仓位30%
    DEFAULT_MAX_LOSS = 0.10     # 最大亏损10%
    DEFAULT_STOP_LOSS = 0.08    # 止损8%
    DEFAULT_STOP_PROFIT = 0.20  # 止盈20%
    DEFAULT_MAX_DRAWDOWN = 0.15 # 最大回撤15%
    
    def __init__(
        self,
        max_position: float = None,
        max_loss: float = None,
        stop_loss: float = None,
        stop_profit: float = None,
        max_drawdown: float = None
    ):
        """初始化风险管理器
        
        Args:
            max_position: 单只股票最大仓位比例
            max_loss: 最大总亏损比例
            stop_loss: 止损比例
            stop_profit: 止盈比例
            max_drawdown: 最大回撤比例
        """
        self.max_position = max_position or self.DEFAULT_MAX_POSITION
        self.max_loss = max_loss or self.DEFAULT_MAX_LOSS
        self.stop_loss = stop_loss or self.DEFAULT_STOP_LOSS
        self.stop_profit = stop_profit or self.DEFAULT_STOP_PROFIT
        self.max_drawdown = max_drawdown or self.DEFAULT_MAX_DRAWDOWN
        
        # 持仓记录
        self.positions = {}
        self.portfolio_value = 0
        self.peak_value = 0
    
    def check_position_limit(
        self, 
        stock_code: str, 
        current_position: float, 
        total_value: float,
        target_amount: float
    ) -> bool:
        """检查仓位限制
        
        Args:
            stock_code: 股票代码
            current_position: 当前持仓金额
            total_value: 总资产
            target_amount: 目标买入金额
            
        Returns:
            是否可以买入
        """
        try:
            # 计算买入后的仓位比例
            new_position = current_position + target_amount
            position_ratio = new_position / total_value
            
            if position_ratio > self.max_position:
                logger.warning(
                    f"股票 {stock_code} 仓位将达到 {position_ratio:.2%}，"
                    f"超过限制 {self.max_position:.2%}"
                )
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"仓位限制检查失败: {e}")
            return False
    
    def check_stop_loss(
        self, 
        stock_code: str, 
        buy_price: float, 
        current_price: float
    ) -> bool:
        """检查止损
        
        Args:
            stock_code: 股票代码
            buy_price: 买入价格
            current_price: 当前价格
            
        Returns:
            是否触发止损
        """
        try:
            if buy_price <= 0:
                return False
            
            # 计算亏损比例
            loss_ratio = (current_price - buy_price) / buy_price
            
            if loss_ratio < -self.stop_loss:
                logger.warning(
                    f"股票 {stock_code} 触发止损，"
                    f"亏损 {loss_ratio:.2%}，止损线 {self.stop_loss:.2%}"
                )
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"止损检查失败: {e}")
            return False
    
    def check_stop_profit(
        self, 
        stock_code: str, 
        buy_price: float, 
        current_price: float
    ) -> bool:
        """检查止盈
        
        Args:
            stock_code: 股票代码
            buy_price: 买入价格
            current_price: 当前价格
            
        Returns:
            是否触发止盈
        """
        try:
            if buy_price <= 0:
                return False
            
            # 计算盈利比例
            profit_ratio = (current_price - buy_price) / buy_price
            
            if profit_ratio > self.stop_profit:
                logger.info(
                    f"股票 {stock_code} 触发止盈，"
                    f"盈利 {profit_ratio:.2%}，止盈线 {self.stop_profit:.2%}"
                )
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"止盈检查失败: {e}")
            return False
    
    def check_max_loss(
        self, 
        current_value: float, 
        initial_value: float
    ) -> bool:
        """检查最大亏损
        
        Args:
            current_value: 当前资产
            initial_value: 初始资产
            
        Returns:
            是否触发最大亏损
        """
        try:
            if initial_value <= 0:
                return False
            
            # 计算亏损比例
            loss_ratio = (current_value - initial_value) / initial_value
            
            if loss_ratio < -self.max_loss:
                logger.warning(
                    f"触发最大亏损限制，"
                    f"亏损 {loss_ratio:.2%}，限制 {self.max_loss:.2%}"
                )
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"最大亏损检查失败: {e}")
            return False
    
    def check_max_drawdown(
        self, 
        current_value: float, 
        peak_value: float
    ) -> bool:
        """检查最大回撤
        
        Args:
            current_value: 当前资产
            peak_value: 历史最高资产
            
        Returns:
            是否触发最大回撤
        """
        try:
            if peak_value <= 0:
                return False
            
            # 计算回撤比例
            drawdown_ratio = (peak_value - current_value) / peak_value
            
            if drawdown_ratio > self.max_drawdown:
                logger.warning(
                    f"触发最大回撤限制，"
                    f"回撤 {drawdown_ratio:.2%}，限制 {self.max_drawdown:.2%}"
                )
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"最大回撤检查失败: {e}")
            return False
    
    def calculate_position_size(
        self,
        total_capital: float,
        stock_price: float,
        risk_per_trade: float = 0.02,
        stop_loss_distance: float = None
    ) -> int:
        """计算仓位大小（基于风险）
        
        Args:
            total_capital: 总资金
            stock_price: 当前股价
            risk_per_trade: 每笔交易风险比例
            stop_loss_distance: 止损距离比例
            
        Returns:
            建议买入股数
        """
        try:
            if stop_loss_distance is None:
                stop_loss_distance = self.stop_loss
            
            # 计算风险金额
            risk_amount = total_capital * risk_per_trade
            
            # 计算每股风险
            risk_per_share = stock_price * stop_loss_distance
            
            if risk_per_share <= 0:
                return 0
            
            # 计算股数
            shares = risk_amount / risk_per_share
            
            # 调整为100的整数倍（A股一手=100股）
            shares = int(shares / 100) * 100
            
            # 检查是否超过最大仓位
            max_shares_by_position = int(total_capital * self.max_position / stock_price / 100) * 100
            shares = min(shares, max_shares_by_position)
            
            return max(0, shares)
            
        except Exception as e:
            logger.error(f"计算仓位大小失败: {e}")
            return 0
    
    def calculate_portfolio_metrics(
        self, 
        positions: Dict[str, Dict],
        current_prices: Dict[str, float]
    ) -> Dict:
        """计算投资组合指标
        
        Args:
            positions: 持仓字典 {stock_code: {shares, buy_price}}
            current_prices: 当前价格字典
            
        Returns:
            投资组合指标
        """
        try:
            total_value = 0
            total_cost = 0
            total_profit = 0
            
            position_details = []
            
            for stock_code, position in positions.items():
                shares = position.get('shares', 0)
                buy_price = position.get('buy_price', 0)
                current_price = current_prices.get(stock_code, 0)
                
                market_value = shares * current_price
                cost = shares * buy_price
                profit = market_value - cost
                profit_ratio = profit / cost if cost > 0 else 0
                
                total_value += market_value
                total_cost += cost
                total_profit += profit
                
                position_details.append({
                    'stock_code': stock_code,
                    'shares': shares,
                    'buy_price': buy_price,
                    'current_price': current_price,
                    'market_value': market_value,
                    'profit': profit,
                    'profit_ratio': profit_ratio,
                    'weight': market_value / total_value if total_value > 0 else 0
                })
            
            # 计算整体盈亏比例
            total_profit_ratio = total_profit / total_cost if total_cost > 0 else 0
            
            # 计算仓位集中度（最大持仓占比）
            if position_details:
                max_weight = max(p['weight'] for p in position_details)
            else:
                max_weight = 0
            
            return {
                'total_value': total_value,
                'total_cost': total_cost,
                'total_profit': total_profit,
                'total_profit_ratio': total_profit_ratio,
                'position_count': len(positions),
                'max_position_weight': max_weight,
                'position_details': position_details,
                'calc_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"计算投资组合指标失败: {e}")
            return {}
    
    def get_risk_metrics(
        self, 
        returns: pd.Series,
        benchmark_returns: pd.Series = None
    ) -> Dict:
        """计算风险指标
        
        Args:
            returns: 收益率序列
            benchmark_returns: 基准收益率序列
            
        Returns:
            风险指标字典
        """
        try:
            if returns.empty or len(returns) < 2:
                return {}
            
            metrics = {}
            
            # 年化收益率
            total_return = (1 + returns).prod() - 1
            years = len(returns) / 252
            metrics['annual_return'] = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
            
            # 年化波动率
            metrics['volatility'] = returns.std() * np.sqrt(252)
            
            # 夏普比率（假设无风险利率3%）
            risk_free_rate = 0.03
            if metrics['volatility'] > 0:
                metrics['sharpe_ratio'] = (metrics['annual_return'] - risk_free_rate) / metrics['volatility']
            else:
                metrics['sharpe_ratio'] = 0
            
            # 最大回撤
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdowns = (running_max - cumulative) / running_max
            metrics['max_drawdown'] = drawdowns.max()
            
            # 胜率
            winning_days = (returns > 0).sum()
            metrics['win_rate'] = winning_days / len(returns)
            
            # 盈亏比
            avg_win = returns[returns > 0].mean() if winning_days > 0 else 0
            avg_loss = returns[returns < 0].mean() if (len(returns) - winning_days) > 0 else 0
            metrics['profit_loss_ratio'] = abs(avg_win / avg_loss) if avg_loss != 0 else 0
            
            # Beta（相对于基准）
            if benchmark_returns is not None and not benchmark_returns.empty:
                if len(returns) == len(benchmark_returns):
                    covariance = returns.cov(benchmark_returns)
                    benchmark_variance = benchmark_returns.var()
                    metrics['beta'] = covariance / benchmark_variance if benchmark_variance > 0 else 0
                    
                    # Alpha
                    metrics['alpha'] = metrics['annual_return'] - (risk_free_rate + metrics['beta'] * (benchmark_returns.mean() * 252 - risk_free_rate))
            
            # VaR (Value at Risk)
            metrics['var_95'] = returns.quantile(0.05)
            metrics['var_99'] = returns.quantile(0.01)
            
            # CVaR (Conditional VaR)
            metrics['cvar_95'] = returns[returns <= metrics['var_95']].mean()
            metrics['cvar_99'] = returns[returns <= metrics['var_99']].mean()
            
            return metrics
            
        except Exception as e:
            logger.error(f"计算风险指标失败: {e}")
            return {}
    
    def generate_risk_report(
        self,
        portfolio_metrics: Dict,
        risk_metrics: Dict,
        positions: List[Dict]
    ) -> Dict:
        """生成风险报告
        
        Args:
            portfolio_metrics: 投资组合指标
            risk_metrics: 风险指标
            positions: 持仓详情
            
        Returns:
            风险报告
        """
        try:
            # 风险评级
            risk_score = 0
            
            # 基于波动率评分
            volatility = risk_metrics.get('volatility', 0)
            if volatility < 0.15:
                risk_score += 30
            elif volatility < 0.25:
                risk_score += 20
            elif volatility < 0.35:
                risk_score += 10
            
            # 基于最大回撤评分
            max_drawdown = risk_metrics.get('max_drawdown', 0)
            if max_drawdown < 0.10:
                risk_score += 30
            elif max_drawdown < 0.20:
                risk_score += 20
            elif max_drawdown < 0.30:
                risk_score += 10
            
            # 基于夏普比率评分
            sharpe_ratio = risk_metrics.get('sharpe_ratio', 0)
            if sharpe_ratio > 1.5:
                risk_score += 40
            elif sharpe_ratio > 1.0:
                risk_score += 30
            elif sharpe_ratio > 0.5:
                risk_score += 20
            elif sharpe_ratio > 0:
                risk_score += 10
            
            # 确定风险等级
            if risk_score >= 80:
                risk_level = '低风险'
            elif risk_score >= 60:
                risk_level = '中低风险'
            elif risk_score >= 40:
                risk_level = '中等风险'
            elif risk_score >= 20:
                risk_level = '中高风险'
            else:
                risk_level = '高风险'
            
            # 生成建议
            suggestions = []
            
            if max_drawdown > 0.20:
                suggestions.append("建议降低仓位，控制回撤")
            
            if sharpe_ratio < 0.5:
                suggestions.append("建议优化策略，提高风险调整后收益")
            
            if len(positions) > 10:
                suggestions.append("持仓过于分散，建议适当集中")
            elif len(positions) < 3:
                suggestions.append("持仓过于集中，建议适当分散")
            
            return {
                'risk_score': risk_score,
                'risk_level': risk_level,
                'suggestions': suggestions,
                'portfolio_metrics': portfolio_metrics,
                'risk_metrics': risk_metrics,
                'report_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"生成风险报告失败: {e}")
            return {}
    
    def update_parameters(
        self,
        max_position: float = None,
        max_loss: float = None,
        stop_loss: float = None,
        stop_profit: float = None,
        max_drawdown: float = None
    ):
        """更新风险参数
        
        Args:
            max_position: 单只股票最大仓位比例
            max_loss: 最大总亏损比例
            stop_loss: 止损比例
            stop_profit: 止盈比例
            max_drawdown: 最大回撤比例
        """
        try:
            if max_position is not None:
                self.max_position = max_position
            if max_loss is not None:
                self.max_loss = max_loss
            if stop_loss is not None:
                self.stop_loss = stop_loss
            if stop_profit is not None:
                self.stop_profit = stop_profit
            if max_drawdown is not None:
                self.max_drawdown = max_drawdown
            
            logger.info("风险参数更新完成")
            
        except Exception as e:
            logger.error(f"更新风险参数失败: {e}")


# 创建全局风险管理器实例
risk_manager = RiskManager()