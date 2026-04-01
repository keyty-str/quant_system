"""
策略引擎模块
负责策略的管理、执行和信号生成
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import pandas as pd
import numpy as np
from loguru import logger

from src.utils.config import get_settings
from src.data.storage.mongodb import MongoDB
from src.data.storage.redis_cache import RedisCache
from src.data.collectors.data_collector import DataCollector


class StrategyEngine:
    """策略引擎"""
    
    def __init__(self):
        self.settings = get_settings()
        self.mongodb = MongoDB()
        self.redis = RedisCache()
        self.data_collector = DataCollector()
    
    async def create_strategy(self, strategy_data: Dict) -> Dict:
        """创建策略"""
        try:
            logger.info(f"创建策略: {strategy_data.get('name')}")
            
            # 添加创建时间
            strategy_data['created_at'] = datetime.now().isoformat()
            strategy_data['updated_at'] = datetime.now().isoformat()
            strategy_data['status'] = 'inactive'
            
            # 保存到MongoDB
            result = await self.mongodb.insert_one('strategies', strategy_data)
            
            # 缓存到Redis
            await self.redis.set(
                f"strategy:{strategy_data['name']}",
                strategy_data,
                expire=3600
            )
            
            logger.info(f"策略创建成功: {strategy_data.get('name')}")
            return strategy_data
            
        except Exception as e:
            logger.error(f"创建策略失败: {e}")
            return {}
    
    async def get_strategy(self, strategy_name: str) -> Dict:
        """获取策略"""
        try:
            # 先从Redis缓存获取
            cached = await self.redis.get(f"strategy:{strategy_name}")
            if cached:
                return cached
            
            # 从MongoDB获取
            strategy = await self.mongodb.find_one('strategies', {'name': strategy_name})
            
            if strategy:
                # 缓存到Redis
                await self.redis.set(
                    f"strategy:{strategy_name}",
                    strategy,
                    expire=3600
                )
                return strategy
            
            return {}
            
        except Exception as e:
            logger.error(f"获取策略失败: {e}")
            return {}
    
    async def get_all_strategies(self) -> List[Dict]:
        """获取所有策略"""
        try:
            strategies = await self.mongodb.find_many('strategies', {})
            return strategies
        except Exception as e:
            logger.error(f"获取策略列表失败: {e}")
            return []
    
    async def update_strategy(self, strategy_name: str, update_data: Dict) -> bool:
        """更新策略"""
        try:
            update_data['updated_at'] = datetime.now().isoformat()
            
            result = await self.mongodb.update_one(
                'strategies',
                {'name': strategy_name},
                update_data
            )
            
            # 清除缓存
            await self.redis.delete(f"strategy:{strategy_name}")
            
            logger.info(f"策略更新成功: {strategy_name}")
            return True
            
        except Exception as e:
            logger.error(f"更新策略失败: {e}")
            return False
    
    async def delete_strategy(self, strategy_name: str) -> bool:
        """删除策略"""
        try:
            await self.mongodb.delete_one('strategies', {'name': strategy_name})
            
            # 清除缓存
            await self.redis.delete(f"strategy:{strategy_name}")
            
            logger.info(f"策略删除成功: {strategy_name}")
            return True
            
        except Exception as e:
            logger.error(f"删除策略失败: {e}")
            return False
    
    async def activate_strategy(self, strategy_name: str) -> bool:
        """激活策略"""
        try:
            await self.update_strategy(strategy_name, {'status': 'active'})
            logger.info(f"策略激活成功: {strategy_name}")
            return True
        except Exception as e:
            logger.error(f"激活策略失败: {e}")
            return False
    
    async def deactivate_strategy(self, strategy_name: str) -> bool:
        """停用策略"""
        try:
            await self.update_strategy(strategy_name, {'status': 'inactive'})
            logger.info(f"策略停用成功: {strategy_name}")
            return True
        except Exception as e:
            logger.error(f"停用策略失败: {e}")
            return False
    
    async def generate_signals(self, strategy_name: str, stock_codes: List[str] = None) -> List[Dict]:
        """生成交易信号"""
        try:
            logger.info(f"开始为策略 {strategy_name} 生成信号...")
            
            # 获取策略配置
            strategy = await self.get_strategy(strategy_name)
            if not strategy:
                logger.error(f"策略不存在: {strategy_name}")
                return []
            
            if strategy.get('status') != 'active':
                logger.warning(f"策略未激活: {strategy_name}")
                return []
            
            # 获取股票列表
            if not stock_codes:
                stocks = await self.mongodb.find_many('stocks', {})
                stock_codes = [s['code'] for s in stocks[:50]]  # 限制50只
            
            signals = []
            
            for stock_code in stock_codes:
                try:
                    # 获取股票数据
                    df = await self.data_collector.get_stock_data(stock_code)
                    if df.empty:
                        continue
                    
                    # 根据策略类型生成信号
                    strategy_type = strategy.get('type', 'trend')
                    
                    if strategy_type == 'trend':
                        signal = await self._generate_trend_signal(df, strategy, stock_code)
                    elif strategy_type == 'mean_reversion':
                        signal = await self._generate_mean_reversion_signal(df, strategy, stock_code)
                    elif strategy_type == 'momentum':
                        signal = await self._generate_momentum_signal(df, strategy, stock_code)
                    else:
                        signal = await self._generate_trend_signal(df, strategy, stock_code)
                    
                    if signal:
                        signals.append(signal)
                        
                except Exception as e:
                    logger.warning(f"为股票 {stock_code} 生成信号失败: {e}")
                    continue
            
            # 保存信号到数据库
            if signals:
                await self.mongodb.insert_many('signals', signals)
                
                # 缓存最新信号
                await self.redis.set(
                    f"signals:{strategy_name}",
                    signals,
                    expire=1800  # 30分钟过期
                )
            
            logger.info(f"策略 {strategy_name} 生成了 {len(signals)} 个信号")
            return signals
            
        except Exception as e:
            logger.error(f"生成信号失败: {e}")
            return []
    
    async def _generate_trend_signal(self, df: pd.DataFrame, strategy: Dict, stock_code: str) -> Dict:
        """生成趋势策略信号"""
        try:
            if len(df) < 60:  # 需要至少60天数据
                return {}
            
            # 计算技术指标
            df = self._calculate_technical_indicators(df)
            
            # 获取最新数据
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            # 趋势策略逻辑
            signal_type = None
            confidence = 0.0
            
            # 金叉信号（短期均线上穿长期均线）
            if (latest['ma5'] > latest['ma20'] and 
                prev['ma5'] <= prev['ma20'] and
                latest['close'] > latest['ma5']):
                signal_type = 'buy'
                confidence = 0.8
            
            # 死叉信号（短期均线下穿长期均线）
            elif (latest['ma5'] < latest['ma20'] and 
                  prev['ma5'] >= prev['ma20'] and
                  latest['close'] < latest['ma5']):
                signal_type = 'sell'
                confidence = 0.8
            
            # MACD金叉
            elif (latest['macd'] > latest['signal'] and 
                  prev['macd'] <= prev['signal']):
                signal_type = 'buy'
                confidence = 0.7
            
            # MACD死叉
            elif (latest['macd'] < latest['signal'] and 
                  prev['macd'] >= prev['signal']):
                signal_type = 'sell'
                confidence = 0.7
            
            if signal_type:
                return {
                    'strategy': strategy['name'],
                    'stock_code': stock_code,
                    'signal_type': signal_type,
                    'confidence': confidence,
                    'price': latest['close'],
                    'timestamp': datetime.now().isoformat(),
                    'indicators': {
                        'ma5': latest['ma5'],
                        'ma20': latest['ma20'],
                        'macd': latest['macd'],
                        'signal': latest['signal'],
                        'rsi': latest['rsi']
                    },
                    'created_at': datetime.now().isoformat()
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"生成趋势信号失败: {e}")
            return {}
    
    async def _generate_mean_reversion_signal(self, df: pd.DataFrame, strategy: Dict, stock_code: str) -> Dict:
        """生成均值回归策略信号"""
        try:
            if len(df) < 20:
                return {}
            
            # 计算技术指标
            df = self._calculate_technical_indicators(df)
            
            latest = df.iloc[-1]
            
            signal_type = None
            confidence = 0.0
            
            # 超卖反弹信号
            if latest['rsi'] < 30 and latest['boll_lower'] < latest['close']:
                signal_type = 'buy'
                confidence = 0.75
            
            # 超买回落信号
            elif latest['rsi'] > 70 and latest['boll_upper'] > latest['close']:
                signal_type = 'sell'
                confidence = 0.75
            
            if signal_type:
                return {
                    'strategy': strategy['name'],
                    'stock_code': stock_code,
                    'signal_type': signal_type,
                    'confidence': confidence,
                    'price': latest['close'],
                    'timestamp': datetime.now().isoformat(),
                    'indicators': {
                        'rsi': latest['rsi'],
                        'boll_upper': latest['boll_upper'],
                        'boll_lower': latest['boll_lower'],
                        'close': latest['close']
                    },
                    'created_at': datetime.now().isoformat()
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"生成均值回归信号失败: {e}")
            return {}
    
    async def _generate_momentum_signal(self, df: pd.DataFrame, strategy: Dict, stock_code: str) -> Dict:
        """生成动量策略信号"""
        try:
            if len(df) < 30:
                return {}
            
            # 计算动量指标
            df['momentum'] = df['close'].pct_change(periods=10)
            df['volume_momentum'] = df['volume'].pct_change(periods=5)
            
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            signal_type = None
            confidence = 0.0
            
            # 动量突破信号
            if (latest['momentum'] > 0.05 and 
                latest['volume_momentum'] > 0.3 and
                latest['close'] > latest['ma20']):
                signal_type = 'buy'
                confidence = 0.7
            
            # 动量衰减信号
            elif (latest['momentum'] < -0.05 and 
                  latest['volume_momentum'] < -0.2 and
                  latest['close'] < latest['ma20']):
                signal_type = 'sell'
                confidence = 0.7
            
            if signal_type:
                return {
                    'strategy': strategy['name'],
                    'stock_code': stock_code,
                    'signal_type': signal_type,
                    'confidence': confidence,
                    'price': latest['close'],
                    'timestamp': datetime.now().isoformat(),
                    'indicators': {
                        'momentum': latest['momentum'],
                        'volume_momentum': latest['volume_momentum'],
                        'ma20': latest['ma20']
                    },
                    'created_at': datetime.now().isoformat()
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"生成动量信号失败: {e}")
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
            df['histogram'] = df['macd'] - df['signal']
            
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
            
            # KDJ
            low_min = df['low'].rolling(window=9).min()
            high_max = df['high'].rolling(window=9).max()
            rsv = (df['close'] - low_min) / (high_max - low_min) * 100
            df['kdj_k'] = rsv.ewm(com=2, adjust=False).mean()
            df['kdj_d'] = df['kdj_k'].ewm(com=2, adjust=False).mean()
            df['kdj_j'] = 3 * df['kdj_k'] - 2 * df['kdj_d']
            
            return df
            
        except Exception as e:
            logger.error(f"计算技术指标失败: {e}")
            return df
    
    async def get_strategy_signals(self, strategy_name: str, limit: int = 50) -> List[Dict]:
        """获取策略信号"""
        try:
            # 先从Redis缓存获取
            cached = await self.redis.get(f"signals:{strategy_name}")
            if cached:
                return cached[:limit]
            
            # 从MongoDB获取
            signals = await self.mongodb.find_many(
                'signals',
                {'strategy': strategy_name},
                limit=limit,
                sort=[('timestamp', -1)]
            )
            
            return signals
            
        except Exception as e:
            logger.error(f"获取策略信号失败: {e}")
            return []
    
    async def get_strategy_performance(self, strategy_name: str) -> Dict:
        """获取策略表现"""
        try:
            # 获取策略信号
            signals = await self.get_strategy_signals(strategy_name, limit=100)
            
            if not signals:
                return {}
            
            # 计算表现指标
            total_signals = len(signals)
            buy_signals = len([s for s in signals if s.get('signal_type') == 'buy'])
            sell_signals = len([s for s in signals if s.get('signal_type') == 'sell'])
            
            avg_confidence = np.mean([s.get('confidence', 0) for s in signals])
            
            return {
                'strategy_name': strategy_name,
                'total_signals': total_signals,
                'buy_signals': buy_signals,
                'sell_signals': sell_signals,
                'avg_confidence': round(avg_confidence, 3),
                'last_signal_time': signals[0].get('timestamp') if signals else None
            }
            
        except Exception as e:
            logger.error(f"获取策略表现失败: {e}")
            return {}


# 创建全局策略引擎实例
strategy_engine = StrategyEngine()