"""
预测系统模块
负责基于技术分析和机器学习进行板块预测
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


class PredictionEngine:
    """预测引擎"""
    
    def __init__(self):
        self.settings = get_settings()
        self.mongodb = MongoDB()
        self.redis = RedisCache()
        self.data_collector = DataCollector()
    
    async def generate_sector_prediction(self, period: str = "1m") -> List[Dict]:
        """生成板块预测"""
        try:
            logger.info(f"开始生成板块预测，周期: {period}")
            
            # 获取板块列表
            sectors = await self.data_collector.collect_sector_list()
            
            if not sectors:
                logger.warning("未获取到板块数据")
                return []
            
            predictions = []
            
            for sector in sectors:
                try:
                    # 计算板块热度分数
                    score = await self._calculate_sector_score(sector)
                    
                    # 分析趋势
                    trend = await self._analyze_sector_trend(sector)
                    
                    # 计算置信度
                    confidence = await self._calculate_confidence(sector, score, trend)
                    
                    # 生成预测理由
                    reason = self._generate_prediction_reason(sector, score, trend)
                    
                    prediction = {
                        'sector_name': sector['name'],
                        'sector_code': sector.get('code', ''),
                        'score': round(score, 2),
                        'trend': trend,
                        'change': sector.get('change_pct', 0),
                        'confidence': confidence,
                        'reason': reason,
                        'period': period,
                        'timestamp': datetime.now().isoformat(),
                        'created_at': datetime.now().isoformat()
                    }
                    
                    predictions.append(prediction)
                    
                except Exception as e:
                    logger.warning(f"为板块 {sector.get('name')} 生成预测失败: {e}")
                    continue
            
            # 按分数排序
            predictions.sort(key=lambda x: x['score'], reverse=True)
            
            # 添加排名
            for i, pred in enumerate(predictions):
                pred['rank'] = i + 1
            
            # 保存到数据库
            if predictions:
                await self.mongodb.insert_many('sector_predictions', predictions)
                
                # 缓存到Redis
                await self.redis.set(
                    f"sector_predictions:{period}",
                    predictions,
                    expire=3600  # 1小时过期
                )
            
            logger.info(f"生成了 {len(predictions)} 个板块预测")
            return predictions
            
        except Exception as e:
            logger.error(f"生成板块预测失败: {e}")
            return []
    
    async def _calculate_sector_score(self, sector: Dict) -> float:
        """计算板块热度分数"""
        try:
            score = 0.0
            
            # 基于涨跌幅的分数
            change_pct = sector.get('change_pct', 0)
            if change_pct > 0:
                score += min(change_pct * 10, 30)  # 最多30分
            else:
                score += max(change_pct * 5, -20)  # 最多扣20分
            
            # 基于市值的分数
            total_market_value = sector.get('total_market_value', 0)
            if total_market_value > 0:
                # 市值越大，分数越高（最多20分）
                market_score = min(np.log10(total_market_value + 1) * 5, 20)
                score += market_score
            
            # 基于股票数量的分数
            stock_count = sector.get('stock_count', 0)
            if stock_count > 0:
                # 股票数量适中为好（最多15分）
                if 10 <= stock_count <= 100:
                    score += 15
                elif stock_count > 100:
                    score += 10
                else:
                    score += 5
            
            # 基于平均价格的分数
            avg_price = sector.get('avg_price', 0)
            if avg_price > 0:
                # 价格适中为好（最多10分）
                if 5 <= avg_price <= 50:
                    score += 10
                elif avg_price > 50:
                    score += 5
                else:
                    score += 3
            
            # 基于资金流向的分数（如果有数据）
            capital_flow = sector.get('capital_flow', 0)
            if capital_flow > 0:
                score += min(capital_flow / 100, 15)  # 最多15分
            
            # 基于成交量的分数
            volume = sector.get('volume', 0)
            if volume > 0:
                score += min(np.log10(volume + 1) * 2, 10)  # 最多10分
            
            return max(0, min(100, score))  # 限制在0-100之间
            
        except Exception as e:
            logger.error(f"计算板块分数失败: {e}")
            return 50.0  # 默认分数
    
    async def _analyze_sector_trend(self, sector: Dict) -> str:
        """分析板块趋势"""
        try:
            change_pct = sector.get('change_pct', 0)
            
            if change_pct > 2:
                return 'up'
            elif change_pct < -2:
                return 'down'
            else:
                return 'neutral'
                
        except Exception as e:
            logger.error(f"分析板块趋势失败: {e}")
            return 'neutral'
    
    async def _calculate_confidence(self, sector: Dict, score: float, trend: str) -> str:
        """计算预测置信度"""
        try:
            confidence_score = 0
            
            # 基于分数的置信度
            if score >= 80:
                confidence_score += 3
            elif score >= 60:
                confidence_score += 2
            else:
                confidence_score += 1
            
            # 基于趋势的置信度
            change_pct = sector.get('change_pct', 0)
            if abs(change_pct) > 3:
                confidence_score += 2
            elif abs(change_pct) > 1:
                confidence_score += 1
            
            # 基于市值的置信度
            total_market_value = sector.get('total_market_value', 0)
            if total_market_value > 1000000000000:  # 1万亿
                confidence_score += 2
            elif total_market_value > 100000000000:  # 1000亿
                confidence_score += 1
            
            # 基于股票数量的置信度
            stock_count = sector.get('stock_count', 0)
            if stock_count >= 20:
                confidence_score += 1
            
            if confidence_score >= 6:
                return '高'
            elif confidence_score >= 4:
                return '中'
            else:
                return '低'
                
        except Exception as e:
            logger.error(f"计算置信度失败: {e}")
            return '中'
    
    def _generate_prediction_reason(self, sector: Dict, score: float, trend: str) -> str:
        """生成预测理由"""
        try:
            reasons = []
            
            change_pct = sector.get('change_pct', 0)
            if change_pct > 0:
                reasons.append(f"涨幅{change_pct:.2f}%")
            elif change_pct < 0:
                reasons.append(f"跌幅{abs(change_pct):.2f}%")
            
            total_market_value = sector.get('total_market_value', 0)
            if total_market_value > 0:
                if total_market_value > 1000000000000:
                    reasons.append("万亿市值板块")
                elif total_market_value > 100000000000:
                    reasons.append("千亿市值板块")
            
            stock_count = sector.get('stock_count', 0)
            if stock_count > 0:
                reasons.append(f"包含{stock_count}只股票")
            
            avg_price = sector.get('avg_price', 0)
            if avg_price > 0:
                reasons.append(f"平均价格{avg_price:.2f}元")
            
            if score >= 80:
                reasons.append("热度极高")
            elif score >= 60:
                reasons.append("热度较高")
            
            if trend == 'up':
                reasons.append("趋势向上")
            elif trend == 'down':
                reasons.append("趋势向下")
            
            return "，".join(reasons) if reasons else "综合分析结果"
            
        except Exception as e:
            logger.error(f"生成预测理由失败: {e}")
            return "综合分析结果"
    
    async def get_sector_prediction(self, sector_name: str, period: str = "1m") -> Dict:
        """获取单个板块预测"""
        try:
            # 先从Redis缓存获取
            cached = await self.redis.get(f"sector_predictions:{period}")
            if cached:
                for pred in cached:
                    if pred['sector_name'] == sector_name:
                        return pred
            
            # 从MongoDB获取
            prediction = await self.mongodb.find_one(
                'sector_predictions',
                {'sector_name': sector_name, 'period': period}
            )
            
            return prediction if prediction else {}
            
        except Exception as e:
            logger.error(f"获取板块预测失败: {e}")
            return {}
    
    async def get_hot_sectors(self, period: str = "1m", limit: int = 10) -> List[Dict]:
        """获取热门板块"""
        try:
            # 先从Redis缓存获取
            cached = await self.redis.get(f"sector_predictions:{period}")
            if cached:
                return cached[:limit]
            
            # 从MongoDB获取
            predictions = await self.mongodb.find_many(
                'sector_predictions',
                {'period': period},
                limit=limit,
                sort=[('score', -1)]
            )
            
            return predictions
            
        except Exception as e:
            logger.error(f"获取热门板块失败: {e}")
            return []
    
    async def get_prediction_accuracy(self, period: str = "1m") -> Dict:
        """获取预测准确度统计"""
        try:
            # 获取历史预测
            predictions = await self.mongodb.find_many(
                'sector_predictions',
                {'period': period},
                limit=100,
                sort=[('created_at', -1)]
            )
            
            if not predictions:
                return {}
            
            # 计算准确度指标
            total_predictions = len(predictions)
            up_predictions = len([p for p in predictions if p['trend'] == 'up'])
            down_predictions = len([p for p in predictions if p['trend'] == 'down'])
            neutral_predictions = len([p for p in predictions if p['trend'] == 'neutral'])
            
            # 基于分数的准确度估算
            high_score_predictions = len([p for p in predictions if p['score'] >= 70])
            medium_score_predictions = len([p for p in predictions if 50 <= p['score'] < 70])
            low_score_predictions = len([p for p in predictions if p['score'] < 50])
            
            # 基于置信度的统计
            high_confidence = len([p for p in predictions if p['confidence'] == '高'])
            medium_confidence = len([p for p in predictions if p['confidence'] == '中'])
            low_confidence = len([p for p in predictions if p['confidence'] == '低'])
            
            return {
                'total_predictions': total_predictions,
                'trend_distribution': {
                    'up': up_predictions,
                    'down': down_predictions,
                    'neutral': neutral_predictions
                },
                'score_distribution': {
                    'high': high_score_predictions,
                    'medium': medium_score_predictions,
                    'low': low_score_predictions
                },
                'confidence_distribution': {
                    'high': high_confidence,
                    'medium': medium_confidence,
                    'low': low_confidence
                },
                'avg_score': np.mean([p['score'] for p in predictions]),
                'period': period,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取预测准确度失败: {e}")
            return {}
    
    async def get_sector_trend(self, sector_name: str, days: int = 30) -> Dict:
        """获取板块趋势分析"""
        try:
            # 获取板块历史数据
            sector_data = await self.data_collector.get_sector_data(sector_name)
            
            if not sector_data:
                return {}
            
            # 分析趋势
            change_pct = sector_data.get('change_pct', 0)
            
            if change_pct > 5:
                direction = 'strong_up'
                strength = 0.8
            elif change_pct > 2:
                direction = 'up'
                strength = 0.6
            elif change_pct > -2:
                direction = 'neutral'
                strength = 0.4
            elif change_pct > -5:
                direction = 'down'
                strength = 0.6
            else:
                direction = 'strong_down'
                strength = 0.8
            
            # 计算支撑和阻力位
            avg_price = sector_data.get('avg_price', 0)
            support_level = avg_price * 0.9 if avg_price > 0 else 0
            resistance_level = avg_price * 1.1 if avg_price > 0 else 0
            
            return {
                'sector_name': sector_name,
                'direction': direction,
                'strength': strength,
                'duration': days,
                'support_level': round(support_level, 2),
                'resistance_level': round(resistance_level, 2),
                'current_change': change_pct,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取板块趋势失败: {e}")
            return {}
    
    async def compare_predictions(self, period1: str, period2: str) -> Dict:
        """比较不同周期预测"""
        try:
            pred1 = await self.get_hot_sectors(period1, limit=10)
            pred2 = await self.get_hot_sectors(period2, limit=10)
            
            if not pred1 or not pred2:
                return {}
            
            # 提取板块名称
            sectors1 = set(p['sector_name'] for p in pred1)
            sectors2 = set(p['sector_name'] for p in pred2)
            
            common_sectors = sectors1.intersection(sectors2)
            different_sectors = sectors1.symmetric_difference(sectors2)
            
            return {
                'period1': period1,
                'period2': period2,
                'common_sectors': list(common_sectors),
                'different_sectors': list(different_sectors),
                'predictions1': pred1,
                'predictions2': pred2,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"比较预测失败: {e}")
            return {}
    
    async def run_prediction_task(self, period: str = "1m") -> Dict:
        """运行预测任务"""
        try:
            logger.info(f"开始运行预测任务，周期: {period}")
            
            # 生成板块预测
            predictions = await self.generate_sector_prediction(period)
            
            # 获取准确度统计
            accuracy = await self.get_prediction_accuracy(period)
            
            # 保存任务结果
            task_result = {
                'task_id': f"prediction_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'period': period,
                'predictions_count': len(predictions),
                'accuracy': accuracy,
                'status': 'completed',
                'created_at': datetime.now().isoformat()
            }
            
            await self.mongodb.insert_one('prediction_tasks', task_result)
            
            logger.info(f"预测任务完成，生成了 {len(predictions)} 个预测")
            return task_result
            
        except Exception as e:
            logger.error(f"运行预测任务失败: {e}")
            return {}


# 创建全局预测引擎实例
prediction_engine = PredictionEngine()