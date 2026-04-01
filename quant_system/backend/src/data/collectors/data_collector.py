"""
数据采集模块
负责从AkShare和Tushare获取A股历史行情数据
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import pandas as pd
import akshare as ak
import tushare as ts
from loguru import logger

from src.utils.config import get_settings
from src.data.storage.mongodb import MongoDB
from src.data.storage.redis_cache import RedisCache


class DataCollector:
    """数据采集器"""
    
    def __init__(self):
        self.settings = get_settings()
        self.mongodb = MongoDB()
        self.redis = RedisCache()
        
        # 初始化Tushare
        if self.settings.TUSHARE_TOKEN:
            ts.set_token(self.settings.TUSHARE_TOKEN)
            self.pro = ts.pro_api()
        else:
            self.pro = None
            logger.warning("Tushare token未配置，Tushare数据源不可用")
    
    async def collect_stock_list(self) -> List[Dict]:
        """采集股票列表"""
        try:
            logger.info("开始采集股票列表...")
            
            # 使用AkShare获取股票列表
            stock_list = ak.stock_info_a_code_name()
            
            # 转换为字典列表
            stocks = []
            for _, row in stock_list.iterrows():
                stock = {
                    'code': row['code'],
                    'name': row['name'],
                    'market': 'SH' if row['code'].startswith('6') else 'SZ',
                    'list_date': datetime.now().isoformat(),
                    'status': 'active',
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                stocks.append(stock)
            
            # 保存到MongoDB
            for stock in stocks:
                await self.mongodb.upsert_one(
                    'stocks',
                    {'code': stock['code']},
                    stock
                )
            
            # 缓存到Redis
            await self.redis.set(
                'stock_list',
                stocks,
                expire=3600  # 1小时过期
            )
            
            logger.info(f"成功采集 {len(stocks)} 只股票信息")
            return stocks
            
        except Exception as e:
            logger.error(f"采集股票列表失败: {e}")
            return []
    
    async def collect_stock_history(
        self,
        stock_code: str,
        start_date: str = None,
        end_date: str = None,
        period: str = 'daily'
    ) -> List[Dict]:
        """采集股票历史数据"""
        try:
            logger.info(f"开始采集股票 {stock_code} 的历史数据...")
            
            # 设置默认日期范围
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            
            # 使用AkShare获取历史数据
            df = ak.stock_zh_a_hist(
                symbol=stock_code,
                period=period,
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"  # 前复权
            )
            
            if df.empty:
                logger.warning(f"未获取到股票 {stock_code} 的历史数据")
                return []
            
            # 转换为字典列表
            records = []
            for _, row in df.iterrows():
                record = {
                    'code': stock_code,
                    'date': row['日期'].isoformat() if hasattr(row['日期'], 'isoformat') else str(row['日期']),
                    'open': float(row['开盘']),
                    'high': float(row['最高']),
                    'low': float(row['最低']),
                    'close': float(row['收盘']),
                    'volume': int(row['成交量']),
                    'amount': float(row['成交额']),
                    'amplitude': float(row['振幅']),
                    'change_pct': float(row['涨跌幅']),
                    'change_amount': float(row['涨跌额']),
                    'turnover_rate': float(row['换手率']),
                    'created_at': datetime.now().isoformat()
                }
                records.append(record)
            
            # 批量保存到MongoDB
            if records:
                await self.mongodb.insert_many('stock_history', records)
            
            # 缓存最新数据到Redis
            if records:
                latest = records[-1]
                await self.redis.set(
                    f'stock_latest:{stock_code}',
                    latest,
                    expire=300  # 5分钟过期
                )
            
            logger.info(f"成功采集股票 {stock_code} 的 {len(records)} 条历史数据")
            return records
            
        except Exception as e:
            logger.error(f"采集股票 {stock_code} 历史数据失败: {e}")
            return []
    
    async def collect_sector_list(self) -> List[Dict]:
        """采集板块列表"""
        try:
            logger.info("开始采集板块列表...")
            
            # 使用AkShare获取行业板块
            sector_list = ak.stock_board_industry_name_em()
            
            # 转换为字典列表
            sectors = []
            for _, row in sector_list.iterrows():
                sector = {
                    'name': row['板块名称'],
                    'code': row['板块代码'],
                    'stock_count': int(row['总家数']),
                    'avg_price': float(row['平均价格']),
                    'change_pct': float(row['涨跌幅']),
                    'total_market_value': float(row['总市值']),
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                sectors.append(sector)
            
            # 保存到MongoDB
            for sector in sectors:
                await self.mongodb.upsert_one(
                    'sectors',
                    {'name': sector['name']},
                    sector
                )
            
            # 缓存到Redis
            await self.redis.set(
                'sector_list',
                sectors,
                expire=3600  # 1小时过期
            )
            
            logger.info(f"成功采集 {len(sectors)} 个板块信息")
            return sectors
            
        except Exception as e:
            logger.error(f"采集板块列表失败: {e}")
            return []
    
    async def collect_realtime_data(self, stock_codes: List[str] = None) -> List[Dict]:
        """采集实时行情数据"""
        try:
            logger.info("开始采集实时行情数据...")
            
            if not stock_codes:
                # 获取所有股票代码
                stocks = await self.mongodb.find_many('stocks', {})
                stock_codes = [s['code'] for s in stocks[:100]]  # 限制前100只
            
            # 使用AkShare获取实时行情
            realtime_data = []
            for code in stock_codes:
                try:
                    df = ak.stock_zh_a_spot_em()
                    if not df.empty:
                        stock_data = df[df['代码'] == code]
                        if not stock_data.empty:
                            row = stock_data.iloc[0]
                            data = {
                                'code': code,
                                'name': row['名称'],
                                'price': float(row['最新价']),
                                'change_pct': float(row['涨跌幅']),
                                'change_amount': float(row['涨跌额']),
                                'volume': int(row['成交量']),
                                'amount': float(row['成交额']),
                                'high': float(row['最高']),
                                'low': float(row['最低']),
                                'open': float(row['今开']),
                                'close': float(row['昨收']),
                                'amplitude': float(row['振幅']),
                                'turnover_rate': float(row['换手率']),
                                'pe_ratio': float(row['市盈率-动态']) if pd.notna(row['市盈率-动态']) else 0,
                                'pb_ratio': float(row['市净率']) if pd.notna(row['市净率']) else 0,
                                'total_market_value': float(row['总市值']) if pd.notna(row['总市值']) else 0,
                                'circulation_market_value': float(row['流通市值']) if pd.notna(row['流通市值']) else 0,
                                'timestamp': datetime.now().isoformat(),
                                'created_at': datetime.now().isoformat()
                            }
                            realtime_data.append(data)
                    
                    # 避免请求过于频繁
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.warning(f"获取股票 {code} 实时数据失败: {e}")
                    continue
            
            # 批量保存到MongoDB
            if realtime_data:
                await self.mongodb.insert_many('realtime_data', realtime_data)
            
            # 缓存到Redis
            if realtime_data:
                await self.redis.set(
                    'realtime_data',
                    realtime_data,
                    expire=60  # 1分钟过期
                )
            
            logger.info(f"成功采集 {len(realtime_data)} 只股票的实时数据")
            return realtime_data
            
        except Exception as e:
            logger.error(f"采集实时行情数据失败: {e}")
            return []
    
    async def collect_market_index(self) -> List[Dict]:
        """采集市场指数数据"""
        try:
            logger.info("开始采集市场指数数据...")
            
            # 使用AkShare获取主要指数
            index_list = ['sh000001', 'sz399001', 'sz399006']  # 上证指数、深证成指、创业板指
            
            indices = []
            for index_code in index_list:
                try:
                    df = ak.stock_zh_index_daily(symbol=index_code)
                    if not df.empty:
                        latest = df.iloc[-1]
                        index_data = {
                            'code': index_code,
                            'name': '上证指数' if index_code == 'sh000001' else 
                                   '深证成指' if index_code == 'sz399001' else '创业板指',
                            'close': float(latest['close']),
                            'open': float(latest['open']),
                            'high': float(latest['high']),
                            'low': float(latest['low']),
                            'volume': int(latest['volume']),
                            'amount': float(latest['amount']),
                            'change_pct': float((latest['close'] - latest['pre_close']) / latest['pre_close'] * 100),
                            'date': latest['date'].isoformat() if hasattr(latest['date'], 'isoformat') else str(latest['date']),
                            'created_at': datetime.now().isoformat()
                        }
                        indices.append(index_data)
                        
                except Exception as e:
                    logger.warning(f"获取指数 {index_code} 数据失败: {e}")
                    continue
            
            # 保存到MongoDB
            for index_data in indices:
                await self.mongodb.upsert_one(
                    'market_indices',
                    {'code': index_data['code']},
                    index_data
                )
            
            # 缓存到Redis
            if indices:
                await self.redis.set(
                    'market_indices',
                    indices,
                    expire=300  # 5分钟过期
                )
            
            logger.info(f"成功采集 {len(indices)} 个市场指数数据")
            return indices
            
        except Exception as e:
            logger.error(f"采集市场指数数据失败: {e}")
            return []
    
    async def collect_all_stocks_history(self, start_date: str = None, end_date: str = None):
        """采集所有股票的历史数据"""
        try:
            logger.info("开始采集所有股票历史数据...")
            
            # 获取股票列表
            stocks = await self.mongodb.find_many('stocks', {})
            
            total = len(stocks)
            success_count = 0
            
            for i, stock in enumerate(stocks):
                try:
                    logger.info(f"进度: {i+1}/{total} - 采集 {stock['code']} {stock['name']}")
                    
                    await self.collect_stock_history(
                        stock['code'],
                        start_date,
                        end_date
                    )
                    
                    success_count += 1
                    
                    # 避免请求过于频繁
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"采集股票 {stock['code']} 失败: {e}")
                    continue
            
            logger.info(f"完成所有股票历史数据采集，成功: {success_count}/{total}")
            
        except Exception as e:
            logger.error(f"采集所有股票历史数据失败: {e}")
    
    async def get_stock_data(self, stock_code: str, days: int = 365) -> pd.DataFrame:
        """获取股票数据"""
        try:
            # 先尝试从Redis缓存获取
            cached = await self.redis.get(f'stock_data:{stock_code}')
            if cached:
                return pd.DataFrame(cached)
            
            # 从MongoDB获取
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            data = await self.mongodb.find_many(
                'stock_history',
                {
                    'code': stock_code,
                    'date': {
                        '$gte': start_date.isoformat(),
                        '$lte': end_date.isoformat()
                    }
                },
                sort=[('date', 1)]
            )
            
            if data:
                df = pd.DataFrame(data)
                # 缓存到Redis
                await self.redis.set(
                    f'stock_data:{stock_code}',
                    data,
                    expire=1800  # 30分钟过期
                )
                return df
            
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"获取股票 {stock_code} 数据失败: {e}")
            return pd.DataFrame()
    
    async def get_sector_data(self, sector_name: str) -> Dict:
        """获取板块数据"""
        try:
            # 先尝试从Redis缓存获取
            cached = await self.redis.get(f'sector_data:{sector_name}')
            if cached:
                return cached
            
            # 从MongoDB获取
            data = await self.mongodb.find_one('sectors', {'name': sector_name})
            
            if data:
                # 缓存到Redis
                await self.redis.set(
                    f'sector_data:{sector_name}',
                    data,
                    expire=1800  # 30分钟过期
                )
                return data
            
            return {}
            
        except Exception as e:
            logger.error(f"获取板块 {sector_name} 数据失败: {e}")
            return {}
    
    async def run_daily_collection(self):
        """运行每日数据采集"""
        try:
            logger.info("开始执行每日数据采集任务...")
            
            # 1. 采集股票列表
            await self.collect_stock_list()
            
            # 2. 采集板块列表
            await self.collect_sector_list()
            
            # 3. 采集市场指数
            await self.collect_market_index()
            
            # 4. 采集实时行情
            await self.collect_realtime_data()
            
            # 5. 采集所有股票历史数据（最近1年）
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            await self.collect_all_stocks_history(start_date, end_date)
            
            logger.info("每日数据采集任务完成")
            
        except Exception as e:
            logger.error(f"每日数据采集任务失败: {e}")


# 创建全局数据采集器实例
data_collector = DataCollector()