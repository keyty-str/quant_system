"""
数据处理模块
负责数据的清洗、转换和预处理
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from loguru import logger


class DataProcessor:
    """数据处理器"""
    
    @staticmethod
    def clean_stock_data(df: pd.DataFrame) -> pd.DataFrame:
        """清洗股票数据
        
        Args:
            df: 原始股票数据DataFrame
            
        Returns:
            清洗后的DataFrame
        """
        try:
            if df.empty:
                return df
            
            # 复制数据避免修改原数据
            df_clean = df.copy()
            
            # 1. 处理缺失值
            # 对于价格数据，使用前值填充
            price_cols = ['open', 'high', 'low', 'close', 'volume']
            for col in price_cols:
                if col in df_clean.columns:
                    df_clean[col] = df_clean[col].ffill()
            
            # 如果仍有缺失值，使用0填充（可能是停牌）
            df_clean = df_clean.fillna(0)
            
            # 2. 去除重复数据
            if 'date' in df_clean.columns:
                df_clean = df_clean.drop_duplicates(subset=['date'], keep='last')
            
            # 3. 数据类型转换
            numeric_cols = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_cols:
                if col in df_clean.columns:
                    df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            
            # 4. 日期格式转换
            if 'date' in df_clean.columns:
                df_clean['date'] = pd.to_datetime(df_clean['date'])
            
            # 5. 去除异常值
            df_clean = DataProcessor._remove_outliers(df_clean)
            
            logger.info(f"数据清洗完成，原始记录: {len(df)}, 清洗后: {len(df_clean)}")
            
            return df_clean
            
        except Exception as e:
            logger.error(f"数据清洗失败: {e}")
            return df
    
    @staticmethod
    def _remove_outliers(df: pd.DataFrame, threshold: float = 3.0) -> pd.DataFrame:
        """去除异常值"""
        try:
            df_outlier = df.copy()
            
            # 对价格列进行异常值检测
            price_cols = ['open', 'high', 'low', 'close']
            for col in price_cols:
                if col in df_outlier.columns:
                    # 计算收益率
                    returns = df_outlier[col].pct_change()
                    
                    # 使用Z-score方法检测异常值
                    z_scores = np.abs((returns - returns.mean()) / returns.std())
                    
                    # 标记异常值
                    outlier_mask = z_scores > threshold
                    
                    # 将异常值替换为NaN，然后前向填充
                    df_outlier.loc[outlier_mask.index[outlier_mask], col] = np.nan
                    df_outlier[col] = df_outlier[col].ffill()
            
            return df_outlier
            
        except Exception as e:
            logger.warning(f"去除异常值失败: {e}")
            return df
    
    @staticmethod
    def adjust_prices(df: pd.DataFrame, adjust_type: str = 'forward') -> pd.DataFrame:
        """价格复权
        
        Args:
            df: 股票数据DataFrame
            adjust_type: 复权类型 ('forward' 前复权, 'backward' 后复权)
            
        Returns:
            复权后的DataFrame
        """
        try:
            if df.empty:
                return df
            
            df_adjusted = df.copy()
            
            # 检查是否有复权因子
            if 'adjust_factor' not in df_adjusted.columns:
                logger.warning("数据中缺少复权因子，跳过复权处理")
                return df_adjusted
            
            # 前复权
            if adjust_type == 'forward':
                # 使用最新的复权因子
                latest_factor = df_adjusted['adjust_factor'].iloc[-1]
                for col in ['open', 'high', 'low', 'close']:
                    df_adjusted[col] = df_adjusted[col] * df_adjusted['adjust_factor'] / latest_factor
            
            # 后复权
            elif adjust_type == 'backward':
                for col in ['open', 'high', 'low', 'close']:
                    df_adjusted[col] = df_adjusted[col] * df_adjusted['adjust_factor']
            
            # 更新成交量（如果有复权因子）
            if 'volume' in df_adjusted.columns and 'adjust_factor' in df_adjusted.columns:
                if adjust_type == 'forward':
                    latest_factor = df_adjusted['adjust_factor'].iloc[-1]
                    df_adjusted['volume'] = df_adjusted['volume'] * latest_factor / df_adjusted['adjust_factor']
                elif adjust_type == 'backward':
                    df_adjusted['volume'] = df_adjusted['volume'] / df_adjusted['adjust_factor']
            
            # 删除复权因子列
            df_adjusted = df_adjusted.drop(columns=['adjust_factor'], errors='ignore')
            
            logger.info(f"价格{adjust_type}复权完成")
            
            return df_adjusted
            
        except Exception as e:
            logger.error(f"价格复权失败: {e}")
            return df
    
    @staticmethod
    def calculate_returns(df: pd.DataFrame, periods: List[int] = None) -> pd.DataFrame:
        """计算收益率
        
        Args:
            df: 股票数据DataFrame
            periods: 收益率计算周期列表，如[1, 5, 10, 20]
            
        Returns:
            包含收益率的DataFrame
        """
        try:
            if df.empty:
                return df
            
            if periods is None:
                periods = [1, 5, 10, 20]
            
            df_returns = df.copy()
            
            # 计算不同周期的收益率
            for period in periods:
                col_name = f'return_{period}d'
                df_returns[col_name] = df_returns['close'].pct_change(periods=period)
            
            # 计算对数收益率
            df_returns['log_return_1d'] = np.log(df_returns['close'] / df_returns['close'].shift(1))
            
            logger.info(f"收益率计算完成")
            
            return df_returns
            
        except Exception as e:
            logger.error(f"收益率计算失败: {e}")
            return df
    
    @staticmethod
    def normalize_data(df: pd.DataFrame, method: str = 'zscore') -> pd.DataFrame:
        """数据标准化
        
        Args:
            df: 股票数据DataFrame
            method: 标准化方法 ('zscore', 'minmax', 'robust')
            
        Returns:
            标准化后的DataFrame
        """
        try:
            if df.empty:
                return df
            
            df_normalized = df.copy()
            
            # 选择数值列
            numeric_cols = df_normalized.select_dtypes(include=[np.number]).columns.tolist()
            
            # 排除一些不需要标准化的列
            exclude_cols = ['volume', 'turnover']
            numeric_cols = [col for col in numeric_cols if col not in exclude_cols]
            
            for col in numeric_cols:
                if method == 'zscore':
                    # Z-score标准化
                    mean = df_normalized[col].mean()
                    std = df_normalized[col].std()
                    if std > 0:
                        df_normalized[col] = (df_normalized[col] - mean) / std
                    else:
                        df_normalized[col] = 0
                
                elif method == 'minmax':
                    # Min-Max标准化
                    min_val = df_normalized[col].min()
                    max_val = df_normalized[col].max()
                    if max_val > min_val:
                        df_normalized[col] = (df_normalized[col] - min_val) / (max_val - min_val)
                    else:
                        df_normalized[col] = 0
                
                elif method == 'robust':
                    # Robust标准化（对异常值更稳健）
                    median = df_normalized[col].median()
                    iqr = df_normalized[col].quantile(0.75) - df_normalized[col].quantile(0.25)
                    if iqr > 0:
                        df_normalized[col] = (df_normalized[col] - median) / iqr
                    else:
                        df_normalized[col] = 0
            
            logger.info(f"数据标准化完成 (方法: {method})")
            
            return df_normalized
            
        except Exception as e:
            logger.error(f"数据标准化失败: {e}")
            return df
    
    @staticmethod
    def resample_data(df: pd.DataFrame, freq: str = 'W') -> pd.DataFrame:
        """数据重采样
        
        Args:
            df: 股票数据DataFrame
            freq: 重采样频率 ('W' 周, 'M' 月, 'Q' 季)
            
        Returns:
            重采样后的DataFrame
        """
        try:
            if df.empty:
                return df
            
            # 确保日期是索引
            df_resampled = df.copy()
            if 'date' in df_resampled.columns:
                df_resampled['date'] = pd.to_datetime(df_resampled['date'])
                df_resampled.set_index('date', inplace=True)
            
            # 重采样
            agg_dict = {
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            }
            
            # 只聚合存在的列
            agg_dict = {k: v for k, v in agg_dict.items() if k in df_resampled.columns}
            
            if agg_dict:
                df_resampled = df_resampled.resample(freq).agg(agg_dict)
                df_resampled = df_resampled.dropna()
            
            logger.info(f"数据重采样完成 (频率: {freq})")
            
            return df_resampled
            
        except Exception as e:
            logger.error(f"数据重采样失败: {e}")
            return df
    
    @staticmethod
    def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """添加技术指标
        
        Args:
            df: 股票数据DataFrame
            
        Returns:
            包含技术指标的DataFrame
        """
        try:
            if df.empty:
                return df
            
            df_indicators = df.copy()
            
            # 移动平均线
            df_indicators['ma5'] = df_indicators['close'].rolling(window=5).mean()
            df_indicators['ma10'] = df_indicators['close'].rolling(window=10).mean()
            df_indicators['ma20'] = df_indicators['close'].rolling(window=20).mean()
            df_indicators['ma60'] = df_indicators['close'].rolling(window=60).mean()
            
            # MACD
            exp1 = df_indicators['close'].ewm(span=12, adjust=False).mean()
            exp2 = df_indicators['close'].ewm(span=26, adjust=False).mean()
            df_indicators['macd'] = exp1 - exp2
            df_indicators['macd_signal'] = df_indicators['macd'].ewm(span=9, adjust=False).mean()
            df_indicators['macd_hist'] = df_indicators['macd'] - df_indicators['macd_signal']
            
            # RSI
            delta = df_indicators['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df_indicators['rsi'] = 100 - (100 / (1 + rs))
            
            # 布林带
            df_indicators['boll_middle'] = df_indicators['close'].rolling(window=20).mean()
            boll_std = df_indicators['close'].rolling(window=20).std()
            df_indicators['boll_upper'] = df_indicators['boll_middle'] + (boll_std * 2)
            df_indicators['boll_lower'] = df_indicators['boll_middle'] - (boll_std * 2)
            
            # ATR (Average True Range)
            high_low = df_indicators['high'] - df_indicators['low']
            high_close = np.abs(df_indicators['high'] - df_indicators['close'].shift())
            low_close = np.abs(df_indicators['low'] - df_indicators['close'].shift())
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            df_indicators['atr'] = true_range.rolling(window=14).mean()
            
            # 成交量相关指标
            if 'volume' in df_indicators.columns:
                df_indicators['volume_ma5'] = df_indicators['volume'].rolling(window=5).mean()
                df_indicators['volume_ma20'] = df_indicators['volume'].rolling(window=20).mean()
                df_indicators['volume_ratio'] = df_indicators['volume'] / df_indicators['volume_ma5']
            
            logger.info("技术指标计算完成")
            
            return df_indicators
            
        except Exception as e:
            logger.error(f"技术指标计算失败: {e}")
            return df
    
    @staticmethod
    def prepare_features(df: pd.DataFrame, target_col: str = 'close') -> Tuple[pd.DataFrame, pd.Series]:
        """准备机器学习特征
        
        Args:
            df: 股票数据DataFrame
            target_col: 目标列名
            
        Returns:
            (特征DataFrame, 目标Series)
        """
        try:
            if df.empty:
                return pd.DataFrame(), pd.Series()
            
            # 先添加技术指标
            df_features = DataProcessor.add_technical_indicators(df)
            
            # 计算目标变量（未来N天的收益率）
            forecast_horizon = 5  # 预测未来5天
            df_features['target'] = df_features[target_col].shift(-forecast_horizon)
            df_features['target_return'] = (df_features['target'] - df_features[target_col]) / df_features[target_col]
            
            # 选择特征列
            feature_cols = [
                'open', 'high', 'low', 'close', 'volume',
                'ma5', 'ma10', 'ma20', 'ma60',
                'macd', 'macd_signal', 'macd_hist',
                'rsi', 'boll_upper', 'boll_lower', 'boll_middle',
                'atr', 'volume_ma5', 'volume_ma20', 'volume_ratio'
            ]
            
            # 只保留存在的列
            feature_cols = [col for col in feature_cols if col in df_features.columns]
            
            # 删除缺失值
            df_features = df_features.dropna()
            
            X = df_features[feature_cols]
            y = df_features['target_return']
            
            logger.info(f"特征准备完成，特征数量: {len(feature_cols)}, 样本数量: {len(X)}")
            
            return X, y
            
        except Exception as e:
            logger.error(f"特征准备失败: {e}")
            return pd.DataFrame(), pd.Series()
    
    @staticmethod
    def merge_sector_data(stock_data: pd.DataFrame, sector_data: pd.DataFrame) -> pd.DataFrame:
        """合并板块数据
        
        Args:
            stock_data: 个股数据
            sector_data: 板块数据
            
        Returns:
            合并后的DataFrame
        """
        try:
            if stock_data.empty:
                return stock_data
            
            if sector_data.empty:
                return stock_data
            
            # 确保日期格式一致
            if 'date' in stock_data.columns:
                stock_data['date'] = pd.to_datetime(stock_data['date'])
            if 'date' in sector_data.columns:
                sector_data['date'] = pd.to_datetime(sector_data['date'])
            
            # 合并数据
            if 'date' in sector_data.columns:
                merged = pd.merge(
                    stock_data, 
                    sector_data[['date', 'sector_index', 'sector_change']],
                    on='date',
                    how='left'
                )
            else:
                merged = stock_data.copy()
            
            logger.info("板块数据合并完成")
            
            return merged
            
        except Exception as e:
            logger.error(f"板块数据合并失败: {e}")
            return stock_data


# 创建全局数据处理器实例
data_processor = DataProcessor()