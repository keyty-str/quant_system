"""
技术指标模块
提供各类技术指标的计算功能
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from loguru import logger


class TechnicalIndicators:
    """技术指标计算器"""
    
    # ========== 趋势指标 ==========
    
    @staticmethod
    def calculate_ma(df: pd.DataFrame, periods: List[int] = None) -> pd.DataFrame:
        """计算移动平均线 (Moving Average)
        
        Args:
            df: 包含close列的DataFrame
            periods: 周期列表，默认[5, 10, 20, 60]
            
        Returns:
            包含MA指标的DataFrame
        """
        try:
            if df.empty or 'close' not in df.columns:
                return df
            
            if periods is None:
                periods = [5, 10, 20, 60]
            
            df_ma = df.copy()
            
            for period in periods:
                col_name = f'ma{period}'
                df_ma[col_name] = df_ma['close'].rolling(window=period).mean()
            
            logger.info(f"移动平均线计算完成: {periods}")
            return df_ma
            
        except Exception as e:
            logger.error(f"移动平均线计算失败: {e}")
            return df
    
    @staticmethod
    def calculate_ema(df: pd.DataFrame, periods: List[int] = None) -> pd.DataFrame:
        """计算指数移动平均线 (Exponential Moving Average)
        
        Args:
            df: 包含close列的DataFrame
            periods: 周期列表，默认[12, 26]
            
        Returns:
            包含EMA指标的DataFrame
        """
        try:
            if df.empty or 'close' not in df.columns:
                return df
            
            if periods is None:
                periods = [12, 26]
            
            df_ema = df.copy()
            
            for period in periods:
                col_name = f'ema{period}'
                df_ema[col_name] = df_ema['close'].ewm(span=period, adjust=False).mean()
            
            logger.info(f"指数移动平均线计算完成: {periods}")
            return df_ema
            
        except Exception as e:
            logger.error(f"指数移动平均线计算失败: {e}")
            return df
    
    @staticmethod
    def calculate_macd(
        df: pd.DataFrame, 
        fast_period: int = 12, 
        slow_period: int = 26, 
        signal_period: int = 9
    ) -> pd.DataFrame:
        """计算MACD指标
        
        Args:
            df: 包含close列的DataFrame
            fast_period: 快线周期
            slow_period: 慢线周期
            signal_period: 信号线周期
            
        Returns:
            包含MACD指标的DataFrame
        """
        try:
            if df.empty or 'close' not in df.columns:
                return df
            
            df_macd = df.copy()
            
            # 计算快慢EMA
            ema_fast = df_macd['close'].ewm(span=fast_period, adjust=False).mean()
            ema_slow = df_macd['close'].ewm(span=slow_period, adjust=False).mean()
            
            # MACD线
            df_macd['macd'] = ema_fast - ema_slow
            
            # 信号线
            df_macd['macd_signal'] = df_macd['macd'].ewm(span=signal_period, adjust=False).mean()
            
            # MACD柱状图
            df_macd['macd_hist'] = df_macd['macd'] - df_macd['macd_signal']
            
            logger.info("MACD指标计算完成")
            return df_macd
            
        except Exception as e:
            logger.error(f"MACD指标计算失败: {e}")
            return df
    
    # ========== 动量指标 ==========
    
    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """计算RSI指标 (Relative Strength Index)
        
        Args:
            df: 包含close列的DataFrame
            period: 周期，默认14
            
        Returns:
            包含RSI指标的DataFrame
        """
        try:
            if df.empty or 'close' not in df.columns:
                return df
            
            df_rsi = df.copy()
            
            # 计算价格变化
            delta = df_rsi['close'].diff()
            
            # 分离涨跌
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            
            # 计算平均涨跌
            avg_gain = gain.rolling(window=period).mean()
            avg_loss = loss.rolling(window=period).mean()
            
            # 计算RS
            rs = avg_gain / avg_loss
            
            # 计算RSI
            df_rsi['rsi'] = 100 - (100 / (1 + rs))
            
            logger.info(f"RSI指标计算完成 (周期: {period})")
            return df_rsi
            
        except Exception as e:
            logger.error(f"RSI指标计算失败: {e}")
            return df
    
    @staticmethod
    def calculate_kdj(
        df: pd.DataFrame, 
        n: int = 9, 
        m1: int = 3, 
        m2: int = 3
    ) -> pd.DataFrame:
        """计算KDJ指标
        
        Args:
            df: 包含high, low, close列的DataFrame
            n: RSV周期
            m1: K值周期
            m2: D值周期
            
        Returns:
            包含KDJ指标的DataFrame
        """
        try:
            if df.empty or not all(col in df.columns for col in ['high', 'low', 'close']):
                return df
            
            df_kdj = df.copy()
            
            # 计算最低值和最高值
            low_min = df_kdj['low'].rolling(window=n).min()
            high_max = df_kdj['high'].rolling(window=n).max()
            
            # 计算RSV
            rsv = (df_kdj['close'] - low_min) / (high_max - low_min) * 100
            
            # 计算K, D, J
            df_kdj['kdj_k'] = rsv.ewm(com=m1-1, adjust=False).mean()
            df_kdj['kdj_d'] = df_kdj['kdj_k'].ewm(com=m2-1, adjust=False).mean()
            df_kdj['kdj_j'] = 3 * df_kdj['kdj_k'] - 2 * df_kdj['kdj_d']
            
            logger.info(f"KDJ指标计算完成 (n={n}, m1={m1}, m2={m2})")
            return df_kdj
            
        except Exception as e:
            logger.error(f"KDJ指标计算失败: {e}")
            return df
    
    @staticmethod
    def calculate_momentum(df: pd.DataFrame, period: int = 10) -> pd.DataFrame:
        """计算动量指标
        
        Args:
            df: 包含close列的DataFrame
            period: 周期
            
        Returns:
            包含动量指标的DataFrame
        """
        try:
            if df.empty or 'close' not in df.columns:
                return df
            
            df_momentum = df.copy()
            
            # 动量 = 当前价格 / N天前价格
            df_momentum['momentum'] = df_momentum['close'] / df_momentum['close'].shift(period) - 1
            
            logger.info(f"动量指标计算完成 (周期: {period})")
            return df_momentum
            
        except Exception as e:
            logger.error(f"动量指标计算失败: {e}")
            return df
    
    # ========== 波动率指标 ==========
    
    @staticmethod
    def calculate_bollinger_bands(
        df: pd.DataFrame, 
        period: int = 20, 
        std_dev: float = 2.0
    ) -> pd.DataFrame:
        """计算布林带 (Bollinger Bands)
        
        Args:
            df: 包含close列的DataFrame
            period: 周期
            std_dev: 标准差倍数
            
        Returns:
            包含布林带指标的DataFrame
        """
        try:
            if df.empty or 'close' not in df.columns:
                return df
            
            df_bb = df.copy()
            
            # 中轨
            df_bb['boll_middle'] = df_bb['close'].rolling(window=period).mean()
            
            # 标准差
            boll_std = df_bb['close'].rolling(window=period).std()
            
            # 上轨和下轨
            df_bb['boll_upper'] = df_bb['boll_middle'] + (boll_std * std_dev)
            df_bb['boll_lower'] = df_bb['boll_middle'] - (boll_std * std_dev)
            
            # 布林带宽度和位置
            df_bb['boll_width'] = (df_bb['boll_upper'] - df_bb['boll_lower']) / df_bb['boll_middle']
            df_bb['boll_position'] = (df_bb['close'] - df_bb['boll_lower']) / (df_bb['boll_upper'] - df_bb['boll_lower'])
            
            logger.info(f"布林带计算完成 (周期: {period}, 标准差: {std_dev})")
            return df_bb
            
        except Exception as e:
            logger.error(f"布林带计算失败: {e}")
            return df
    
    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """计算ATR指标 (Average True Range)
        
        Args:
            df: 包含high, low, close列的DataFrame
            period: 周期
            
        Returns:
            包含ATR指标的DataFrame
        """
        try:
            if df.empty or not all(col in df.columns for col in ['high', 'low', 'close']):
                return df
            
            df_atr = df.copy()
            
            # 计算真实波幅
            high_low = df_atr['high'] - df_atr['low']
            high_close = np.abs(df_atr['high'] - df_atr['close'].shift())
            low_close = np.abs(df_atr['low'] - df_atr['close'].shift())
            
            # 取三者最大值
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            
            # 计算ATR
            df_atr['atr'] = true_range.rolling(window=period).mean()
            
            logger.info(f"ATR指标计算完成 (周期: {period})")
            return df_atr
            
        except Exception as e:
            logger.error(f"ATR指标计算失败: {e}")
            return df
    
    @staticmethod
    def calculate_volatility(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """计算历史波动率
        
        Args:
            df: 包含close列的DataFrame
            period: 周期
            
        Returns:
            包含波动率指标的DataFrame
        """
        try:
            if df.empty or 'close' not in df.columns:
                return df
            
            df_vol = df.copy()
            
            # 计算对数收益率
            log_returns = np.log(df_vol['close'] / df_vol['close'].shift(1))
            
            # 计算滚动标准差（年化）
            df_vol['volatility'] = log_returns.rolling(window=period).std() * np.sqrt(252)
            
            logger.info(f"历史波动率计算完成 (周期: {period})")
            return df_vol
            
        except Exception as e:
            logger.error(f"历史波动率计算失败: {e}")
            return df
    
    # ========== 成交量指标 ==========
    
    @staticmethod
    def calculate_volume_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """计算成交量相关指标
        
        Args:
            df: 包含close, volume列的DataFrame
            
        Returns:
            包含成交量指标的DataFrame
        """
        try:
            if df.empty or 'volume' not in df.columns:
                return df
            
            df_vol = df.copy()
            
            # 成交量移动平均
            df_vol['volume_ma5'] = df_vol['volume'].rolling(window=5).mean()
            df_vol['volume_ma10'] = df_vol['volume'].rolling(window=10).mean()
            df_vol['volume_ma20'] = df_vol['volume'].rolling(window=20).mean()
            
            # 成交量比率
            df_vol['volume_ratio'] = df_vol['volume'] / df_vol['volume_ma5']
            
            # OBV (On-Balance Volume)
            direction = np.sign(df_vol['close'] - df_vol['close'].shift(1))
            df_vol['obv'] = (direction * df_vol['volume']).cumsum()
            
            logger.info("成交量指标计算完成")
            return df_vol
            
        except Exception as e:
            logger.error(f"成交量指标计算失败: {e}")
            return df
    
    # ========== 综合指标计算 ==========
    
    @staticmethod
    def calculate_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """计算所有技术指标
        
        Args:
            df: 包含ohlcv数据的DataFrame
            
        Returns:
            包含所有技术指标的DataFrame
        """
        try:
            if df.empty:
                return df
            
            # 趋势指标
            df = TechnicalIndicators.calculate_ma(df)
            df = TechnicalIndicators.calculate_ema(df)
            df = TechnicalIndicators.calculate_macd(df)
            
            # 动量指标
            df = TechnicalIndicators.calculate_rsi(df)
            df = TechnicalIndicators.calculate_kdj(df)
            df = TechnicalIndicators.calculate_momentum(df)
            
            # 波动率指标
            df = TechnicalIndicators.calculate_bollinger_bands(df)
            df = TechnicalIndicators.calculate_atr(df)
            df = TechnicalIndicators.calculate_volatility(df)
            
            # 成交量指标
            df = TechnicalIndicators.calculate_volume_indicators(df)
            
            logger.info("所有技术指标计算完成")
            return df
            
        except Exception as e:
            logger.error(f"技术指标计算失败: {e}")
            return df
    
    # ========== 信号生成辅助方法 ==========
    
    @staticmethod
    def generate_ma_signal(df: pd.DataFrame, short_period: int = 5, long_period: int = 20) -> str:
        """基于MA生成信号
        
        Returns:
            'buy', 'sell', 或 'hold'
        """
        try:
            if len(df) < long_period:
                return 'hold'
            
            ma_short = df['close'].rolling(window=short_period).mean().iloc[-1]
            ma_long = df['close'].rolling(window=long_period).mean().iloc[-1]
            
            ma_short_prev = df['close'].rolling(window=short_period).mean().iloc[-2]
            ma_long_prev = df['close'].rolling(window=long_period).mean().iloc[-2]
            
            # 金叉买入
            if ma_short > ma_long and ma_short_prev <= ma_long_prev:
                return 'buy'
            
            # 死叉卖出
            if ma_short < ma_long and ma_short_prev >= ma_long_prev:
                return 'sell'
            
            return 'hold'
            
        except Exception:
            return 'hold'
    
    @staticmethod
    def generate_rsi_signal(df: pd.DataFrame, oversold: float = 30, overbought: float = 70) -> str:
        """基于RSI生成信号
        
        Returns:
            'buy', 'sell', 或 'hold'
        """
        try:
            if len(df) < 14:
                return 'hold'
            
            rsi = df['close'].diff()
            gain = (rsi.where(rsi > 0, 0)).rolling(window=14).mean().iloc[-1]
            loss = (-rsi.where(rsi < 0, 0)).rolling(window=14).mean().iloc[-1]
            
            if loss == 0:
                return 'hold'
            
            rs = gain / loss
            rsi_value = 100 - (100 / (1 + rs))
            
            # 超卖买入
            if rsi_value < oversold:
                return 'buy'
            
            # 超买卖出
            if rsi_value > overbought:
                return 'sell'
            
            return 'hold'
            
        except Exception:
            return 'hold'
    
    @staticmethod
    def generate_macd_signal(df: pd.DataFrame) -> str:
        """基于MACD生成信号
        
        Returns:
            'buy', 'sell', 或 'hold'
        """
        try:
            if len(df) < 26:
                return 'hold'
            
            # 计算MACD
            ema12 = df['close'].ewm(span=12, adjust=False).mean()
            ema26 = df['close'].ewm(span=26, adjust=False).mean()
            macd = ema12 - ema26
            signal_line = macd.ewm(span=9, adjust=False).mean()
            
            macd_current = macd.iloc[-1]
            signal_current = signal_line.iloc[-1]
            macd_prev = macd.iloc[-2]
            signal_prev = signal_line.iloc[-2]
            
            # 金叉买入
            if macd_current > signal_current and macd_prev <= signal_prev:
                return 'buy'
            
            # 死叉卖出
            if macd_current < signal_current and macd_prev >= signal_prev:
                return 'sell'
            
            return 'hold'
            
        except Exception:
            return 'hold'
    
    @staticmethod
    def generate_bollinger_signal(df: pd.DataFrame) -> str:
        """基于布林带生成信号
        
        Returns:
            'buy', 'sell', 或 'hold'
        """
        try:
            if len(df) < 20:
                return 'hold'
            
            # 计算布林带
            middle = df['close'].rolling(window=20).mean()
            std = df['close'].rolling(window=20).std()
            upper = middle + (std * 2)
            lower = middle - (std * 2)
            
            close_current = df['close'].iloc[-1]
            lower_current = lower.iloc[-1]
            upper_current = upper.iloc[-1]
            
            # 触及下轨买入
            if close_current < lower_current:
                return 'buy'
            
            # 触及上轨卖出
            if close_current > upper_current:
                return 'sell'
            
            return 'hold'
            
        except Exception:
            return 'hold'


# 创建全局技术指标实例
technical_indicators = TechnicalIndicators()