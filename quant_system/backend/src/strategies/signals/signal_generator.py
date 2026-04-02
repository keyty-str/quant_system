"""
信号生成模块
负责生成交易信号和信号管理
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from loguru import logger


class SignalGenerator:
    """信号生成器"""
    
    # 信号类型
    SIGNAL_BUY = 'buy'
    SIGNAL_SELL = 'sell'
    SIGNAL_HOLD = 'hold'
    
    # 信号强度
    STRENGTH_WEAK = 1
    STRENGTH_MEDIUM = 2
    STRENGTH_STRONG = 3
    
    def __init__(self):
        """初始化信号生成器"""
        self.signal_history = []
        self.active_signals = {}
    
    def generate_signal(
        self,
        df: pd.DataFrame,
        strategy_type: str = 'trend',
        stock_code: str = None
    ) -> Dict:
        """生成交易信号
        
        Args:
            df: 包含技术指标的DataFrame
            strategy_type: 策略类型 ('trend', 'mean_reversion', 'momentum')
            stock_code: 股票代码
            
        Returns:
            信号字典
        """
        try:
            if df.empty:
                return self._create_empty_signal(stock_code)
            
            # 确保有足够的历史数据
            if len(df) < 30:
                logger.warning(f"数据不足，需要至少30条记录，当前: {len(df)}")
                return self._create_empty_signal(stock_code)
            
            # 根据策略类型生成信号
            if strategy_type == 'trend':
                signal = self._generate_trend_signal(df, stock_code)
            elif strategy_type == 'mean_reversion':
                signal = self._generate_mean_reversion_signal(df, stock_code)
            elif strategy_type == 'momentum':
                signal = self._generate_momentum_signal(df, stock_code)
            elif strategy_type == 'combined':
                signal = self._generate_combined_signal(df, stock_code)
            else:
                signal = self._generate_trend_signal(df, stock_code)
            
            # 记录信号
            if signal['signal_type'] != self.SIGNAL_HOLD:
                self.signal_history.append(signal)
                self.active_signals[stock_code] = signal
            
            return signal
            
        except Exception as e:
            logger.error(f"生成信号失败: {e}")
            return self._create_empty_signal(stock_code)
    
    def _generate_trend_signal(self, df: pd.DataFrame, stock_code: str) -> Dict:
        """生成趋势策略信号"""
        try:
            # 确保有足够的历史数据
            if len(df) < 20:
                return self._create_empty_signal(stock_code)
            
            # 计算技术指标
            df = self._add_trend_indicators(df)
            
            current = df.iloc[-1]
            prev = df.iloc[-2]
            
            signal_type = self.SIGNAL_HOLD
            strength = 0
            reasons = []
            confidence = 0.5
            
            # MA金叉/死叉
            if 'ma5' in df.columns and 'ma20' in df.columns:
                if current['ma5'] > current['ma20'] and prev['ma5'] <= prev['ma20']:
                    signal_type = self.SIGNAL_BUY
                    reasons.append('MA金叉')
                    confidence += 0.2
                elif current['ma5'] < current['ma20'] and prev['ma5'] >= prev['ma20']:
                    signal_type = self.SIGNAL_SELL
                    reasons.append('MA死叉')
                    confidence += 0.2
            
            # MACD金叉/死叉
            if 'macd' in df.columns and 'macd_signal' in df.columns:
                if current['macd'] > current['macd_signal'] and prev['macd'] <= prev['macd_signal']:
                    if signal_type == self.SIGNAL_BUY:
                        strength = self.STRENGTH_STRONG
                    else:
                        signal_type = self.SIGNAL_BUY
                        strength = self.STRENGTH_MEDIUM
                    reasons.append('MACD金叉')
                    confidence += 0.15
                elif current['macd'] < current['macd_signal'] and prev['macd'] >= prev['macd_signal']:
                    if signal_type == self.SIGNAL_SELL:
                        strength = self.STRENGTH_STRONG
                    else:
                        signal_type = self.SIGNAL_SELL
                        strength = self.STRENGTH_MEDIUM
                    reasons.append('MACD死叉')
                    confidence += 0.15
            
            # 价格突破
            if 'boll_upper' in df.columns and 'boll_lower' in df.columns:
                if current['close'] > current['boll_upper']:
                    if signal_type == self.SIGNAL_SELL:
                        signal_type = self.SIGNAL_HOLD
                    reasons.append('突破布林带上轨')
                elif current['close'] < current['boll_lower']:
                    if signal_type == self.SIGNAL_BUY:
                        signal_type = self.SIGNAL_HOLD
                    reasons.append('跌破布林带下轨')
            
            return self._create_signal(
                stock_code=stock_code,
                signal_type=signal_type,
                strength=strength if strength > 0 else self.STRENGTH_MEDIUM,
                price=current['close'],
                confidence=min(confidence, 1.0),
                reasons=reasons
            )
            
        except Exception as e:
            logger.error(f"生成趋势信号失败: {e}")
            return self._create_empty_signal(stock_code)
    
    def _generate_mean_reversion_signal(self, df: pd.DataFrame, stock_code: str) -> Dict:
        """生成均值回归策略信号"""
        try:
            if len(df) < 20:
                return self._create_empty_signal(stock_code)
            
            # 计算技术指标
            df = self._add_mean_reversion_indicators(df)
            
            current = df.iloc[-1]
            
            signal_type = self.SIGNAL_HOLD
            reasons = []
            confidence = 0.5
            
            # RSI超卖/超买
            if 'rsi' in df.columns:
                if current['rsi'] < 20:
                    signal_type = self.SIGNAL_BUY
                    reasons.append(f'RSI超卖 ({current["rsi"]:.1f})')
                    confidence = 0.7
                elif current['rsi'] > 80:
                    signal_type = self.SIGNAL_SELL
                    reasons.append(f'RSI超买 ({current["rsi"]:.1f})')
                    confidence = 0.7
                elif current['rsi'] < 30:
                    signal_type = self.SIGNAL_BUY
                    reasons.append(f'RSI偏低 ({current["rsi"]:.1f})')
                    confidence = 0.6
                elif current['rsi'] > 70:
                    signal_type = self.SIGNAL_SELL
                    reasons.append(f'RSI偏高 ({current["rsi"]:.1f})')
                    confidence = 0.6
            
            # 布林带回归
            if 'boll_upper' in df.columns and 'boll_lower' in df.columns:
                if current['close'] < current['boll_lower']:
                    if signal_type == self.SIGNAL_BUY:
                        confidence = 0.8
                        reasons.append('触及布林带下轨')
                elif current['close'] > current['boll_upper']:
                    if signal_type == self.SIGNAL_SELL:
                        confidence = 0.8
                        reasons.append('触及布林带上轨')
            
            return self._create_signal(
                stock_code=stock_code,
                signal_type=signal_type,
                strength=self.STRENGTH_MEDIUM,
                price=current['close'],
                confidence=confidence,
                reasons=reasons
            )
            
        except Exception as e:
            logger.error(f"生成均值回归信号失败: {e}")
            return self._create_empty_signal(stock_code)
    
    def _generate_momentum_signal(self, df: pd.DataFrame, stock_code: str) -> Dict:
        """生成动量策略信号"""
        try:
            if len(df) < 20:
                return self._create_empty_signal(stock_code)
            
            # 计算动量指标
            df = self._add_momentum_indicators(df)
            
            current = df.iloc[-1]
            
            signal_type = self.SIGNAL_HOLD
            reasons = []
            confidence = 0.5
            
            # 价格动量
            if 'momentum' in df.columns:
                if current['momentum'] > 0.1:
                    signal_type = self.SIGNAL_BUY
                    reasons.append(f'正向动量 ({current["momentum"]:.2%})')
                    confidence = 0.7
                elif current['momentum'] < -0.1:
                    signal_type = self.SIGNAL_SELL
                    reasons.append(f'负向动量 ({current["momentum"]:.2%})')
                    confidence = 0.7
            
            # 成交量动量
            if 'volume_momentum' in df.columns:
                if current.get('volume_momentum', 0) > 0.5:
                    if signal_type == self.SIGNAL_BUY:
                        confidence = 0.85
                    reasons.append(f'成交量放大 ({current["volume_momentum"]:.2%})')
                elif current.get('volume_momentum', 0) < -0.3:
                    if signal_type == self.SIGNAL_SELL:
                        confidence = 0.85
                    reasons.append(f'成交量萎缩 ({current["volume_momentum"]:.2%})')
            
            return self._create_signal(
                stock_code=stock_code,
                signal_type=signal_type,
                strength=self.STRENGTH_MEDIUM,
                price=current['close'],
                confidence=confidence,
                reasons=reasons
            )
            
        except Exception as e:
            logger.error(f"生成动量信号失败: {e}")
            return self._create_empty_signal(stock_code)
    
    def _generate_combined_signal(self, df: pd.DataFrame, stock_code: str) -> Dict:
        """生成组合策略信号"""
        try:
            # 分别生成三种策略信号
            trend_signal = self._generate_trend_signal(df, stock_code)
            mean_signal = self._generate_mean_reversion_signal(df, stock_code)
            momentum_signal = self._generate_momentum_signal(df, stock_code)
            
            # 投票决定最终信号
            signals = [trend_signal, mean_signal, momentum_signal]
            buy_count = sum(1 for s in signals if s['signal_type'] == self.SIGNAL_BUY)
            sell_count = sum(1 for s in signals if s['signal_type'] == self.SIGNAL_SELL)
            
            # 合并理由
            all_reasons = []
            for s in signals:
                all_reasons.extend(s.get('reasons', []))
            
            # 计算综合置信度
            avg_confidence = np.mean([s['confidence'] for s in signals])
            
            if buy_count >= 2:
                signal_type = self.SIGNAL_BUY
                strength = self.STRENGTH_STRONG if buy_count == 3 else self.STRENGTH_MEDIUM
            elif sell_count >= 2:
                signal_type = self.SIGNAL_SELL
                strength = self.STRENGTH_STRONG if sell_count == 3 else self.STRENGTH_MEDIUM
            else:
                signal_type = self.SIGNAL_HOLD
                strength = 0
            
            return self._create_signal(
                stock_code=stock_code,
                signal_type=signal_type,
                strength=strength,
                price=df.iloc[-1]['close'],
                confidence=avg_confidence,
                reasons=all_reasons
            )
            
        except Exception as e:
            logger.error(f"生成组合信号失败: {e}")
            return self._create_empty_signal(stock_code)
    
    def _create_signal(
        self,
        stock_code: str,
        signal_type: str,
        strength: int,
        price: float,
        confidence: float,
        reasons: List[str]
    ) -> Dict:
        """创建信号字典"""
        return {
            'stock_code': stock_code,
            'signal_type': signal_type,
            'strength': strength,
            'price': price,
            'confidence': round(confidence, 3),
            'reasons': reasons,
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'strategy': 'technical'
        }
    
    def _create_empty_signal(self, stock_code: str) -> Dict:
        """创建空信号"""
        return {
            'stock_code': stock_code,
            'signal_type': self.SIGNAL_HOLD,
            'strength': 0,
            'price': 0,
            'confidence': 0,
            'reasons': [],
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'strategy': 'none'
        }
    
    def _add_trend_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """添加趋势指标"""
        df = df.copy()
        
        # MA
        df['ma5'] = df['close'].rolling(window=5).mean()
        df['ma10'] = df['close'].rolling(window=10).mean()
        df['ma20'] = df['close'].rolling(window=20).mean()
        
        # MACD
        ema12 = df['close'].ewm(span=12, adjust=False).mean()
        ema26 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = ema12 - ema26
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        # 布林带
        df['boll_middle'] = df['close'].rolling(window=20).mean()
        boll_std = df['close'].rolling(window=20).std()
        df['boll_upper'] = df['boll_middle'] + (boll_std * 2)
        df['boll_lower'] = df['boll_middle'] - (boll_std * 2)
        
        return df
    
    def _add_mean_reversion_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """添加均值回归指标"""
        df = df.copy()
        
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
    
    def _add_momentum_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """添加动量指标"""
        df = df.copy()
        
        # 价格动量
        df['momentum'] = df['close'].pct_change(periods=10)
        
        # 成交量动量
        if 'volume' in df.columns:
            df['volume_momentum'] = df['volume'].pct_change(periods=5)
        
        return df
    
    def filter_signals(
        self,
        signals: List[Dict],
        min_confidence: float = 0.6,
        signal_types: List[str] = None
    ) -> List[Dict]:
        """过滤信号
        
        Args:
            signals: 信号列表
            min_confidence: 最小置信度
            signal_types: 信号类型列表
            
        Returns:
            过滤后的信号列表
        """
        try:
            filtered = []
            
            for signal in signals:
                # 置信度过滤
                if signal['confidence'] < min_confidence:
                    continue
                
                # 类型过滤
                if signal_types and signal['signal_type'] not in signal_types:
                    continue
                
                filtered.append(signal)
            
            # 按置信度排序
            filtered.sort(key=lambda x: x['confidence'], reverse=True)
            
            return filtered
            
        except Exception as e:
            logger.error(f"过滤信号失败: {e}")
            return []
    
    def get_signal_strength_label(self, strength: int) -> str:
        """获取信号强度标签"""
        if strength >= self.STRENGTH_STRONG:
            return '强'
        elif strength >= self.STRENGTH_MEDIUM:
            return '中'
        else:
            return '弱'
    
    def get_signal_type_label(self, signal_type: str) -> str:
        """获取信号类型标签"""
        labels = {
            self.SIGNAL_BUY: '买入',
            self.SIGNAL_SELL: '卖出',
            self.SIGNAL_HOLD: '持有'
        }
        return labels.get(signal_type, '未知')
    
    def get_recent_signals(self, limit: int = 10) -> List[Dict]:
        """获取最近的信号"""
        return self.signal_history[-limit:]
    
    def clear_history(self):
        """清除历史记录"""
        self.signal_history = []
        self.active_signals = {}


# 创建全局信号生成器实例
signal_generator = SignalGenerator()