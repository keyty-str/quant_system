"""
技术指标模块测试
"""
import pytest
import pandas as pd
import numpy as np
from src.strategies.indicators.technical_indicators import TechnicalIndicators


class TestTechnicalIndicators:
    """技术指标测试类"""

    @pytest.fixture
    def sample_data(self):
        """创建示例数据"""
        dates = pd.date_range('2024-01-01', periods=50, freq='D')
        df = pd.DataFrame({
            'trade_date': dates.strftime('%Y%m%d'),
            'open': np.random.uniform(10, 20, 50),
            'high': np.random.uniform(20, 25, 50),
            'low': np.random.uniform(8, 15, 50),
            'close': np.random.uniform(15, 22, 50),
            'vol': np.random.uniform(1000000, 5000000, 50),
            'amount': np.random.uniform(10000000, 50000000, 50)
        })
        return df

    def test_add_ma(self, sample_data):
        """测试移动平均线"""
        result = TechnicalIndicators.calculate_ma(sample_data, periods=[5, 10, 20])
        
        assert 'ma5' in result.columns
        assert 'ma10' in result.columns
        assert 'ma20' in result.columns
        
        # 检查MA值是否正确计算（应该是正数）
        assert result['ma5'].dropna().min() > 0
        assert result['ma10'].dropna().min() > 0
        assert result['ma20'].dropna().min() > 0

    def test_add_ema(self, sample_data):
        """测试指数移动平均线"""
        result = TechnicalIndicators.calculate_ema(sample_data, periods=[12, 26])
        
        assert 'ema12' in result.columns
        assert 'ema26' in result.columns

    def test_add_macd(self, sample_data):
        """测试MACD指标"""
        result = TechnicalIndicators.calculate_macd(sample_data)
        
        assert 'macd' in result.columns
        assert 'macd_signal' in result.columns
        assert 'macd_hist' in result.columns

    def test_add_rsi(self, sample_data):
        """测试RSI指标"""
        # 测试单个周期
        result = TechnicalIndicators.calculate_rsi(sample_data, period=14)
        
        assert 'rsi' in result.columns
        
        # RSI值应该在0-100之间
        rsi_values = result['rsi'].dropna()
        if len(rsi_values) > 0:
            assert (rsi_values >= 0).all()
            assert (rsi_values <= 100).all()

    def test_add_kdj(self, sample_data):
        """测试KDJ指标"""
        result = TechnicalIndicators.calculate_kdj(sample_data)
        
        assert 'kdj_k' in result.columns
        assert 'kdj_d' in result.columns
        assert 'kdj_j' in result.columns

    def test_add_bollinger_bands(self, sample_data):
        """测试布林带"""
        result = TechnicalIndicators.calculate_bollinger_bands(sample_data, period=20)
        
        assert 'boll_middle' in result.columns
        assert 'boll_upper' in result.columns
        assert 'boll_lower' in result.columns
        
        # 布林带上轨应该大于中轨，中轨应该大于下轨
        valid_data = result.dropna()
        if len(valid_data) > 0:
            assert (valid_data['boll_upper'] >= valid_data['boll_middle']).all()
            assert (valid_data['boll_middle'] >= valid_data['boll_lower']).all()

    def test_add_atr(self, sample_data):
        """测试ATR指标"""
        result = TechnicalIndicators.calculate_atr(sample_data, period=14)
        
        assert 'atr' in result.columns
        # ATR应该是正数
        assert result['atr'].dropna().min() > 0

    def test_add_volume_indicators(self, sample_data):
        """测试成交量指标"""
        # 需要先重命名列以匹配volume
        df = sample_data.copy()
        df = df.rename(columns={'vol': 'volume'})
        result = TechnicalIndicators.calculate_volume_indicators(df)
        
        assert 'obv' in result.columns
        assert 'volume_ma5' in result.columns

    def test_add_all_indicators(self, sample_data):
        """测试添加所有指标"""
        # 需要先重命名列以匹配volume
        df = sample_data.copy()
        df = df.rename(columns={'vol': 'volume'})
        result = TechnicalIndicators.calculate_all_indicators(df)
        
        # 检查所有主要指标列是否存在
        expected_columns = [
            'ma5', 'ma10', 'ma20', 'ma60',
            'ema12', 'ema26',
            'macd', 'macd_signal', 'macd_hist',
            'rsi',
            'kdj_k', 'kdj_d', 'kdj_j',
            'boll_middle', 'boll_upper', 'boll_lower',
            'atr',
            'obv', 'volume_ma5'
        ]
        
        for col in expected_columns:
            assert col in result.columns, f"缺少列: {col}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])