"""
回测引擎模块
负责策略的历史回测和性能评估
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import pandas as pd
import numpy as np
from loguru import logger

from src.utils.config import get_settings
from src.data.storage.mongodb import MongoDB
from src.data.storage.redis_cache import RedisCache
from src.data.collectors.data_collector import DataCollector


class BacktestEngine:
    """回测引擎"""
    
    def __init__(self):
        self.settings = get_settings()
        self.mongodb = MongoDB()
        self.redis = RedisCache()
        self.data_collector = DataCollector()
    
    async def run_backtest(
        self, 
        strategy_name: str, 
        stock_codes: List[str],
        start_date: str,
        end_date: str,
        initial_capital: float = 100000.0,
        commission_rate: float = 0.001,
        slippage: float = 0.001
    ) -> Dict:
        """运行回测
        
        Args:
            strategy_name: 策略名称
            stock_codes: 股票代码列表
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            initial_capital: 初始资金
            commission_rate: 手续费率
            slippage: 滑点
            
        Returns:
            回测结果
        """
        try:
            logger.info(f"开始回测策略: {strategy_name}")
            logger.info(f"回测区间: {start_date} - {end_date}")
            logger.info(f"初始资金: {initial_capital}")
            
            # 获取策略配置
            strategy = await self.mongodb.find_one('strategies', {'name': strategy_name})
            if not strategy:
                logger.error(f"策略不存在: {strategy_name}")
                return {}
            
            # 初始化回测结果
            backtest_result = {
                'strategy_name': strategy_name,
                'start_date': start_date,
                'end_date': end_date,
                'initial_capital': initial_capital,
                'final_capital': initial_capital,
                'total_return': 0.0,
                'annual_return': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'trades': [],
                'daily_returns': [],
                'capital_curve': [],
                'created_at': datetime.now().isoformat()
            }
            
            # 获取股票历史数据
            all_trades = []
            capital = initial_capital
            position = {}  # 持仓记录
            
            for stock_code in stock_codes:
                try:
                    # 获取历史数据
                    df = await self._get_historical_data(stock_code, start_date, end_date)
                    if df.empty:
                        continue
                    
                    # 生成回测信号
                    signals = await self._generate_backtest_signals(df, strategy, stock_code)
                    
                    # 模拟交易
                    trades = await self._simulate_trades(
                        df, signals, stock_code, capital, position,
                        commission_rate, slippage
                    )
                    
                    all_trades.extend(trades)
                    
                except Exception as e:
                    logger.warning(f"回测股票 {stock_code} 失败: {e}")
                    continue
            
            # 计算回测指标
            if all_trades:
                # 按日期排序
                all_trades.sort(key=lambda x: x['date'])
                
                # 计算资金曲线
                capital_curve = await self._calculate_capital_curve(
                    all_trades, initial_capital
                )
                
                # 计算收益指标
                metrics = await self._calculate_metrics(
                    all_trades, capital_curve, initial_capital
                )
                
                backtest_result.update(metrics)
                backtest_result['trades'] = all_trades
                backtest_result['capital_curve'] = capital_curve
                backtest_result['final_capital'] = capital_curve[-1] if capital_curve else initial_capital
            
            # 保存回测结果
            await self.mongodb.insert_one('backtest_results', backtest_result)
            
            # 缓存回测结果
            cache_key = f"backtest:{strategy_name}:{start_date}:{end_date}"
            await self.redis.set(cache_key, backtest_result, expire=3600)
            
            logger.info(f"回测完成: {strategy_name}")
            logger.info(f"总收益: {backtest_result['total_return']:.2%}")
            logger.info(f"夏普比率: {backtest_result['sharpe_ratio']:.2f}")
            logger.info(f"最大回撤: {backtest_result['max_drawdown']:.2%}")
            
            return backtest_result
            
        except Exception as e:
            logger.error(f"回测失败: {e}")
            return {}
    
    async def _get_historical_data(
        self, 
        stock_code: str, 
        start_date: str, 
        end_date: str
    ) -> pd.DataFrame:
        """获取历史数据"""
        try:
            # 先从MongoDB获取
            data = await self.mongodb.find_many(
                'stock_data',
                {
                    'code': stock_code,
                    'date': {
                        '$gte': start_date,
                        '$lte': end_date
                    }
                },
                sort=[('date', 1)]
            )
            
            if data:
                df = pd.DataFrame(data)
                # 转换日期格式
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
                return df
            
            # 如果数据库没有，从数据源获取
            df = await self.data_collector.get_stock_history(
                stock_code, start_date, end_date
            )
            
            if not df.empty:
                # 保存到数据库
                records = df.reset_index().to_dict('records')
                for record in records:
                    record['code'] = stock_code
                    record['date'] = record['date'].strftime('%Y-%m-%d')
                await self.mongodb.insert_many('stock_data', records)
            
            return df
            
        except Exception as e:
            logger.error(f"获取历史数据失败 {stock_code}: {e}")
            return pd.DataFrame()
    
    async def _generate_backtest_signals(
        self, 
        df: pd.DataFrame, 
        strategy: Dict, 
        stock_code: str
    ) -> List[Dict]:
        """生成回测信号"""
        try:
            signals = []
            strategy_type = strategy.get('type', 'trend')
            
            # 计算技术指标
            df = self._calculate_technical_indicators(df)
            
            for i in range(20, len(df)):
                current = df.iloc[i]
                prev = df.iloc[i-1]
                
                signal = None
                
                if strategy_type == 'trend':
                    signal = self._generate_trend_signal(
                        current, prev, stock_code, df.index[i]
                    )
                elif strategy_type == 'mean_reversion':
                    signal = self._generate_mean_reversion_signal(
                        current, stock_code, df.index[i]
                    )
                elif strategy_type == 'momentum':
                    signal = self._generate_momentum_signal(
                        current, prev, stock_code, df.index[i]
                    )
                
                if signal:
                    signals.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"生成回测信号失败: {e}")
            return []
    
    def _generate_trend_signal(
        self, 
        current: pd.Series, 
        prev: pd.Series, 
        stock_code: str, 
        date
    ) -> Optional[Dict]:
        """生成趋势策略信号"""
        try:
            # 金叉买入
            if (current['ma5'] > current['ma20'] and 
                prev['ma5'] <= prev['ma20']):
                return {
                    'stock_code': stock_code,
                    'date': date.strftime('%Y-%m-%d'),
                    'signal_type': 'buy',
                    'price': current['close'],
                    'confidence': 0.8
                }
            
            # 死叉卖出
            if (current['ma5'] < current['ma20'] and 
                prev['ma5'] >= prev['ma20']):
                return {
                    'stock_code': stock_code,
                    'date': date.strftime('%Y-%m-%d'),
                    'signal_type': 'sell',
                    'price': current['close'],
                    'confidence': 0.8
                }
            
            return None
            
        except Exception:
            return None
    
    def _generate_mean_reversion_signal(
        self, 
        current: pd.Series, 
        stock_code: str, 
        date
    ) -> Optional[Dict]:
        """生成均值回归策略信号"""
        try:
            # 超卖买入
            if current['rsi'] < 30:
                return {
                    'stock_code': stock_code,
                    'date': date.strftime('%Y-%m-%d'),
                    'signal_type': 'buy',
                    'price': current['close'],
                    'confidence': 0.75
                }
            
            # 超买卖出
            if current['rsi'] > 70:
                return {
                    'stock_code': stock_code,
                    'date': date.strftime('%Y-%m-%d'),
                    'signal_type': 'sell',
                    'price': current['close'],
                    'confidence': 0.75
                }
            
            return None
            
        except Exception:
            return None
    
    def _generate_momentum_signal(
        self, 
        current: pd.Series, 
        prev: pd.Series, 
        stock_code: str, 
        date
    ) -> Optional[Dict]:
        """生成动量策略信号"""
        try:
            # 计算动量
            momentum = (current['close'] - df.iloc[-20]['close']) / df.iloc[-20]['close']
            
            # 正动量买入
            if momentum > 0.1:
                return {
                    'stock_code': stock_code,
                    'date': date.strftime('%Y-%m-%d'),
                    'signal_type': 'buy',
                    'price': current['close'],
                    'confidence': 0.7
                }
            
            # 负动量卖出
            if momentum < -0.1:
                return {
                    'stock_code': stock_code,
                    'date': date.strftime('%Y-%m-%d'),
                    'signal_type': 'sell',
                    'price': current['close'],
                    'confidence': 0.7
                }
            
            return None
            
        except Exception:
            return None
    
    async def _simulate_trades(
        self, 
        df: pd.DataFrame,
        signals: List[Dict],
        stock_code: str,
        capital: float,
        position: Dict,
        commission_rate: float,
        slippage: float
    ) -> List[Dict]:
        """模拟交易"""
        try:
            trades = []
            current_position = position.get(stock_code, 0)
            current_capital = capital
            
            for signal in signals:
                price = signal['price']
                
                if signal['signal_type'] == 'buy' and current_capital > 0:
                    # 买入
                    # 考虑滑点
                    buy_price = price * (1 + slippage)
                    # 计算可买入手数（100股为一手）
                    max_shares = int(current_capital / (buy_price * 100)) * 100
                    
                    if max_shares > 0:
                        cost = max_shares * buy_price
                        commission = cost * commission_rate
                        
                        trade = {
                            'stock_code': stock_code,
                            'date': signal['date'],
                            'type': 'buy',
                            'price': buy_price,
                            'shares': max_shares,
                            'cost': cost,
                            'commission': commission,
                            'capital_before': current_capital,
                            'capital_after': current_capital - cost - commission
                        }
                        
                        current_capital -= (cost + commission)
                        current_position += max_shares
                        
                        trades.append(trade)
                
                elif signal['signal_type'] == 'sell' and current_position > 0:
                    # 卖出
                    # 考虑滑点
                    sell_price = price * (1 - slippage)
                    revenue = current_position * sell_price
                    commission = revenue * commission_rate
                    
                    trade = {
                        'stock_code': stock_code,
                        'date': signal['date'],
                        'type': 'sell',
                        'price': sell_price,
                        'shares': current_position,
                        'revenue': revenue,
                        'commission': commission,
                        'capital_before': current_capital,
                        'capital_after': current_capital + revenue - commission
                    }
                    
                    current_capital += (revenue - commission)
                    current_position = 0
                    
                    trades.append(trade)
            
            # 更新持仓记录
            position[stock_code] = current_position
            
            return trades
            
        except Exception as e:
            logger.error(f"模拟交易失败: {e}")
            return []
    
    async def _calculate_capital_curve(
        self, 
        trades: List[Dict], 
        initial_capital: float
    ) -> List[float]:
        """计算资金曲线"""
        try:
            capital_curve = [initial_capital]
            current_capital = initial_capital
            
            # 按日期排序
            trades_sorted = sorted(trades, key=lambda x: x['date'])
            
            for trade in trades_sorted:
                if trade['type'] == 'buy':
                    current_capital = trade['capital_after']
                elif trade['type'] == 'sell':
                    current_capital = trade['capital_after']
                
                capital_curve.append(current_capital)
            
            return capital_curve
            
        except Exception as e:
            logger.error(f"计算资金曲线失败: {e}")
            return [initial_capital]
    
    async def _calculate_metrics(
        self, 
        trades: List[Dict],
        capital_curve: List[float],
        initial_capital: float
    ) -> Dict:
        """计算回测指标"""
        try:
            if not capital_curve or len(capital_curve) < 2:
                return {
                    'total_return': 0.0,
                    'annual_return': 0.0,
                    'sharpe_ratio': 0.0,
                    'max_drawdown': 0.0,
                    'total_trades': 0,
                    'winning_trades': 0,
                    'losing_trades': 0,
                    'win_rate': 0.0
                }
            
            # 总收益
            final_capital = capital_curve[-1]
            total_return = (final_capital - initial_capital) / initial_capital
            
            # 年化收益
            days = len(capital_curve)
            annual_return = (1 + total_return) ** (365 / days) - 1 if days > 0 else 0
            
            # 计算日收益率
            daily_returns = [
                (capital_curve[i] - capital_curve[i-1]) / capital_curve[i-1]
                for i in range(1, len(capital_curve))
            ]
            
            # 夏普比率（假设无风险利率为3%）
            risk_free_rate = 0.03 / 252  # 日化
            if daily_returns and np.std(daily_returns) > 0:
                sharpe_ratio = (np.mean(daily_returns) - risk_free_rate) / np.std(daily_returns) * np.sqrt(252)
            else:
                sharpe_ratio = 0.0
            
            # 最大回撤
            max_drawdown = 0.0
            peak = capital_curve[0]
            for capital in capital_curve:
                if capital > peak:
                    peak = capital
                drawdown = (peak - capital) / peak
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
            
            # 交易统计
            total_trades = len([t for t in trades if t['type'] == 'sell'])
            
            # 计算盈亏交易
            winning_trades = 0
            losing_trades = 0
            
            # 配对买卖交易
            buy_trades = [t for t in trades if t['type'] == 'buy']
            sell_trades = [t for t in trades if t['type'] == 'sell']
            
            for i in range(min(len(buy_trades), len(sell_trades))):
                buy_trade = buy_trades[i]
                sell_trade = sell_trades[i]
                
                if sell_trade['revenue'] > buy_trade['cost']:
                    winning_trades += 1
                else:
                    losing_trades += 1
            
            win_rate = winning_trades / total_trades if total_trades > 0 else 0.0
            
            return {
                'total_return': round(total_return, 4),
                'annual_return': round(annual_return, 4),
                'sharpe_ratio': round(sharpe_ratio, 2),
                'max_drawdown': round(max_drawdown, 4),
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': round(win_rate, 4)
            }
            
        except Exception as e:
            logger.error(f"计算回测指标失败: {e}")
            return {}
    
    def _calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算技术指标"""
        try:
            # 移动平均线
            df['ma5'] = df['close'].rolling(window=5).mean()
            df['ma10'] = df['close'].rolling(window=10).mean()
            df['ma20'] = df['close'].rolling(window=20).mean()
            df['ma60'] = df['close'].rolling(window=60).mean()
            
            # MACD
            exp1 = df['close'].ewm(span=12, adjust=False).mean()
            exp2 = df['close'].ewm(span=26, adjust=False).mean()
            df['macd'] = exp1 - exp2
            df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
            
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # 布林带
            df['boll_middle'] = df['close'].rolling(window=20).mean()
            boll_std = df['close'].rolling(window=20).std()
            df['boll_upper'] = df['boll_middle'] + (boll_std * 2)
            df['boll_lower'] = df['boll_middle'] - (boll_std * 2)
            
            return df
            
        except Exception as e:
            logger.error(f"计算技术指标失败: {e}")
            return df
    
    async def get_backtest_result(
        self, 
        strategy_name: str, 
        start_date: str, 
        end_date: str
    ) -> Optional[Dict]:
        """获取回测结果"""
        try:
            # 先从缓存获取
            cache_key = f"backtest:{strategy_name}:{start_date}:{end_date}"
            cached = await self.redis.get(cache_key)
            if cached:
                return cached
            
            # 从数据库获取
            result = await self.mongodb.find_one(
                'backtest_results',
                {
                    'strategy_name': strategy_name,
                    'start_date': start_date,
                    'end_date': end_date
                }
            )
            
            if result:
                # 缓存结果
                await self.redis.set(cache_key, result, expire=3600)
            
            return result
            
        except Exception as e:
            logger.error(f"获取回测结果失败: {e}")
            return None
    
    async def get_all_backtest_results(self, strategy_name: str = None) -> List[Dict]:
        """获取所有回测结果"""
        try:
            filter_dict = {}
            if strategy_name:
                filter_dict['strategy_name'] = strategy_name
            
            results = await self.mongodb.find_many(
                'backtest_results',
                filter_dict,
                sort=[('created_at', -1)],
                limit=50
            )
            
            return results
            
        except Exception as e:
            logger.error(f"获取回测结果列表失败: {e}")
            return []
    
    async def delete_backtest_result(self, backtest_id: str) -> bool:
        """删除回测结果"""
        try:
            await self.mongodb.delete_one('backtest_results', {'_id': backtest_id})
            logger.info(f"回测结果已删除: {backtest_id}")
            return True
        except Exception as e:
            logger.error(f"删除回测结果失败: {e}")
            return False


# 创建全局回测引擎实例
backtest_engine = BacktestEngine()