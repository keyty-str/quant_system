"""
数据验证模块
负责数据质量检查和验证
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from loguru import logger


class DataValidator:
    """数据验证器"""
    
    # A股市场交易时间规则
    MARKET_OPEN_TIME = "09:30:00"
    MARKET_CLOSE_TIME = "15:00:00"
    
    # 股票价格有效范围
    MIN_PRICE = 0.01
    MAX_PRICE = 100000.0
    
    # 成交量有效范围
    MIN_VOLUME = 0
    MAX_VOLUME = 10000000000
    
    @staticmethod
    def validate_stock_data(df: pd.DataFrame, stock_code: str = None) -> Dict:
        """验证股票数据质量
        
        Args:
            df: 股票数据DataFrame
            stock_code: 股票代码
            
        Returns:
            验证结果字典
        """
        try:
            if df.empty:
                return {
                    'valid': False,
                    'errors': ['数据为空'],
                    'warnings': [],
                    'stock_code': stock_code
                }
            
            errors = []
            warnings = []
            
            # 1. 检查必需列
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                errors.append(f"缺少必需列: {missing_columns}")
            
            # 2. 检查价格有效性
            price_errors = DataValidator._validate_prices(df)
            errors.extend(price_errors['errors'])
            warnings.extend(price_errors['warnings'])
            
            # 3. 检查成交量有效性
            volume_errors = DataValidator._validate_volume(df)
            errors.extend(volume_errors['errors'])
            warnings.extend(volume_errors['warnings'])
            
            # 4. 检查OHLC关系
            ohlc_errors = DataValidator._validate_ohlc_relationship(df)
            errors.extend(ohlc_errors['errors'])
            warnings.extend(ohlc_errors['warnings'])
            
            # 5. 检查数据连续性
            continuity_errors = DataValidator._validate_continuity(df)
            errors.extend(continuity_errors['errors'])
            warnings.extend(continuity_errors['warnings'])
            
            # 6. 检查数据时效性
            timeliness_errors = DataValidator._validate_timeliness(df)
            errors.extend(timeliness_errors['errors'])
            warnings.extend(timeliness_errors['warnings'])
            
            is_valid = len(errors) == 0
            
            if is_valid:
                logger.info(f"数据验证通过: {stock_code}, 记录数: {len(df)}")
            else:
                logger.warning(f"数据验证失败: {stock_code}, 错误: {errors}")
            
            return {
                'valid': is_valid,
                'errors': errors,
                'warnings': warnings,
                'stock_code': stock_code,
                'total_records': len(df),
                'validation_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"数据验证失败: {e}")
            return {
                'valid': False,
                'errors': [f"验证过程出错: {str(e)}"],
                'warnings': [],
                'stock_code': stock_code
            }
    
    @staticmethod
    def _validate_prices(df: pd.DataFrame) -> Dict:
        """验证价格数据"""
        errors = []
        warnings = []
        
        price_cols = ['open', 'high', 'low', 'close']
        for col in price_cols:
            if col not in df.columns:
                continue
            
            # 检查价格是否为负
            negative_count = (df[col] < 0).sum()
            if negative_count > 0:
                errors.append(f"列 {col} 存在 {negative_count} 个负值")
            
            # 检查价格是否超出合理范围
            out_of_range = ((df[col] < DataValidator.MIN_PRICE) | 
                           (df[col] > DataValidator.MAX_PRICE)).sum()
            if out_of_range > 0:
                warnings.append(f"列 {col} 存在 {out_of_range} 个超出合理范围的值")
            
            # 检查是否存在异常波动（单日涨跌超过20%）
            if len(df) > 1:
                returns = df[col].pct_change().abs()
                abnormal_count = (returns > 0.2).sum()
                if abnormal_count > 0:
                    warnings.append(f"列 {col} 存在 {abnormal_count} 次异常波动（>20%）")
        
        return {'errors': errors, 'warnings': warnings}
    
    @staticmethod
    def _validate_volume(df: pd.DataFrame) -> Dict:
        """验证成交量数据"""
        errors = []
        warnings = []
        
        if 'volume' not in df.columns:
            return {'errors': errors, 'warnings': warnings}
        
        # 检查成交量是否为负
        negative_count = (df['volume'] < 0).sum()
        if negative_count > 0:
            errors.append(f"成交量存在 {negative_count} 个负值")
        
        # 检查成交量是否超出合理范围
        out_of_range = ((df['volume'] < DataValidator.MIN_VOLUME) | 
                       (df['volume'] > DataValidator.MAX_VOLUME)).sum()
        if out_of_range > 0:
            warnings.append(f"成交量存在 {out_of_range} 个超出合理范围的值")
        
        # 检查成交量是否突然异常放大（超过5日均量的10倍）
        if len(df) > 5:
            volume_ma5 = df['volume'].rolling(window=5).mean()
            abnormal_volume = (df['volume'] > volume_ma5 * 10).sum()
            if abnormal_volume > 0:
                warnings.append(f"成交量存在 {abnormal_volume} 次异常放大")
        
        return {'errors': errors, 'warnings': warnings}
    
    @staticmethod
    def _validate_ohlc_relationship(df: pd.DataFrame) -> Dict:
        """验证OHLC关系"""
        errors = []
        warnings = []
        
        required_cols = ['open', 'high', 'low', 'close']
        if not all(col in df.columns for col in required_cols):
            return {'errors': errors, 'warnings': warnings}
        
        # 检查 high >= low
        invalid_hl = (df['high'] < df['low']).sum()
        if invalid_hl > 0:
            errors.append(f"存在 {invalid_hl} 条记录 high < low")
        
        # 检查 open, close 在 high, low 范围内
        invalid_open = ((df['open'] > df['high']) | (df['open'] < df['low'])).sum()
        if invalid_open > 0:
            errors.append(f"存在 {invalid_open} 条记录 open 超出 [low, high] 范围")
        
        invalid_close = ((df['close'] > df['high']) | (df['close'] < df['low'])).sum()
        if invalid_close > 0:
            errors.append(f"存在 {invalid_close} 条记录 close 超出 [low, high] 范围")
        
        return {'errors': errors, 'warnings': warnings}
    
    @staticmethod
    def _validate_continuity(df: pd.DataFrame) -> Dict:
        """验证数据连续性"""
        errors = []
        warnings = []
        
        if 'date' not in df.columns:
            return {'errors': errors, 'warnings': warnings}
        
        # 检查日期是否排序
        dates = pd.to_datetime(df['date'])
        if not dates.is_monotonic_increasing:
            warnings.append("日期未按时序排序")
        
        # 检查日期是否有重复
        duplicate_dates = dates.duplicated().sum()
        if duplicate_dates > 0:
            warnings.append(f"存在 {duplicate_dates} 个重复日期")
        
        # 检查是否有缺失交易日（排除周末和节假日）
        if len(dates) > 1:
            date_diffs = dates.diff().dropna()
            # 工作日应该是1天，周末是2-3天
            business_day_gaps = (date_diffs.dt.days > 3).sum()
            if business_day_gaps > 0:
                warnings.append(f"存在 {business_day_gaps} 个超过3天的交易间隔")
        
        return {'errors': errors, 'warnings': warnings}
    
    @staticmethod
    def _validate_timeliness(df: pd.DataFrame) -> Dict:
        """验证数据时效性"""
        errors = []
        warnings = []
        
        if 'date' not in df.columns:
            return {'errors': errors, 'warnings': warnings}
        
        # 检查最新数据是否在合理时间内
        latest_date = pd.to_datetime(df['date']).max()
        days_since_latest = (datetime.now() - latest_date).days
        
        if days_since_latest > 30:
            warnings.append(f"数据可能过时，最新数据距今 {days_since_latest} 天")
        elif days_since_latest > 7:
            warnings.append(f"数据较旧，最新数据距今 {days_since_latest} 天")
        
        return {'errors': errors, 'warnings': warnings}
    
    @staticmethod
    def validate_realtime_data(data: Dict, expected_fields: List[str] = None) -> Dict:
        """验证实时数据
        
        Args:
            data: 实时数据字典
            expected_fields: 期望的字段列表
            
        Returns:
            验证结果字典
        """
        try:
            errors = []
            warnings = []
            
            if not data:
                return {
                    'valid': False,
                    'errors': ['数据为空'],
                    'warnings': warnings
                }
            
            # 检查必需字段
            if expected_fields:
                missing_fields = [f for f in expected_fields if f not in data]
                if missing_fields:
                    errors.append(f"缺少必需字段: {missing_fields}")
            
            # 检查价格字段
            price_fields = ['price', 'open', 'high', 'low', 'close', 'last_price']
            for field in price_fields:
                if field in data:
                    value = data[field]
                    if not isinstance(value, (int, float)):
                        errors.append(f"字段 {field} 类型错误，应为数值")
                    elif value < 0:
                        errors.append(f"字段 {field} 为负值")
                    elif value > DataValidator.MAX_PRICE:
                        warnings.append(f"字段 {field} 超出合理范围")
            
            # 检查成交量字段
            volume_fields = ['volume', 'vol', 'amount']
            for field in volume_fields:
                if field in data:
                    value = data[field]
                    if not isinstance(value, (int, float)):
                        errors.append(f"字段 {field} 类型错误，应为数值")
                    elif value < 0:
                        errors.append(f"字段 {field} 为负值")
            
            # 检查时间戳
            if 'timestamp' in data:
                try:
                    ts = datetime.fromisoformat(data['timestamp'])
                    # 检查时间是否合理（不能是未来时间）
                    if ts > datetime.now() + timedelta(hours=1):
                        warnings.append("时间戳可能是未来时间")
                except (ValueError, TypeError):
                    errors.append("时间戳格式错误")
            
            is_valid = len(errors) == 0
            
            return {
                'valid': is_valid,
                'errors': errors,
                'warnings': warnings,
                'validation_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"实时数据验证失败: {e}")
            return {
                'valid': False,
                'errors': [f"验证过程出错: {str(e)}"],
                'warnings': []
            }
    
    @staticmethod
    def validate_sector_data(sector_data: Dict) -> Dict:
        """验证板块数据
        
        Args:
            sector_data: 板块数据字典
            
        Returns:
            验证结果字典
        """
        try:
            errors = []
            warnings = []
            
            if not sector_data:
                return {
                    'valid': False,
                    'errors': ['板块数据为空'],
                    'warnings': warnings
                }
            
            # 检查必需字段
            required_fields = ['name', 'change_percent']
            missing_fields = [f for f in required_fields if f not in sector_data]
            if missing_fields:
                errors.append(f"缺少必需字段: {missing_fields}")
            
            # 检查涨跌幅
            if 'change_percent' in sector_data:
                change = sector_data['change_percent']
                if not isinstance(change, (int, float)):
                    errors.append("涨跌幅类型错误")
                elif abs(change) > 20:
                    warnings.append(f"涨跌幅异常: {change}%")
            
            # 检查成分股列表
            if 'stocks' in sector_data:
                stocks = sector_data['stocks']
                if not isinstance(stocks, list):
                    errors.append("成分股列表类型错误")
                elif len(stocks) == 0:
                    warnings.append("板块成分股列表为空")
            
            is_valid = len(errors) == 0
            
            return {
                'valid': is_valid,
                'errors': errors,
                'warnings': warnings,
                'validation_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"板块数据验证失败: {e}")
            return {
                'valid': False,
                'errors': [f"验证过程出错: {str(e)}"],
                'warnings': []
            }
    
    @staticmethod
    def check_data_quality(df: pd.DataFrame) -> Dict:
        """检查数据质量评分
        
        Args:
            df: 股票数据DataFrame
            
        Returns:
            数据质量评分和详细信息
        """
        try:
            if df.empty:
                return {
                    'score': 0,
                    'level': 'F',
                    'details': '数据为空'
                }
            
            score = 100
            issues = []
            
            # 1. 缺失值检查（每项扣5分）
            missing_ratio = df.isnull().sum().sum() / (len(df) * len(df.columns))
            if missing_ratio > 0:
                deduction = min(int(missing_ratio * 100), 25)
                score -= deduction
                issues.append(f"缺失值比例: {missing_ratio:.2%}")
            
            # 2. 异常值检查（每项扣10分）
            if len(df) > 10:
                for col in ['open', 'high', 'low', 'close']:
                    if col in df.columns:
                        z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                        outlier_ratio = (z_scores > 3).sum() / len(df)
                        if outlier_ratio > 0.05:
                            score -= 10
                            issues.append(f"列 {col} 异常值比例: {outlier_ratio:.2%}")
            
            # 3. 数据连续性检查（扣10分）
            if 'date' in df.columns:
                dates = pd.to_datetime(df['date'])
                duplicate_dates = dates.duplicated().sum()
                if duplicate_dates > 0:
                    score -= 10
                    issues.append(f"重复日期数量: {duplicate_dates}")
            
            # 4. 数据时效性检查（扣10分）
            if 'date' in df.columns:
                latest_date = pd.to_datetime(df['date']).max()
                days_old = (datetime.now() - latest_date).days
                if days_old > 30:
                    score -= 10
                    issues.append(f"数据陈旧: {days_old}天")
            
            # 确保分数在0-100之间
            score = max(0, min(100, score))
            
            # 确定质量等级
            if score >= 90:
                level = 'A'
            elif score >= 80:
                level = 'B'
            elif score >= 70:
                level = 'C'
            elif score >= 60:
                level = 'D'
            else:
                level = 'F'
            
            return {
                'score': score,
                'level': level,
                'total_records': len(df),
                'issues': issues,
                'check_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"数据质量检查失败: {e}")
            return {
                'score': 0,
                'level': 'F',
                'details': f'检查过程出错: {str(e)}'
            }


# 创建全局数据验证器实例
data_validator = DataValidator()