"""
卖家生命周期管理业务指标框架

基于Amazon Global Selling ESM (Existing Seller Management) 最佳实践，
构建多维度卖家评估指标体系。
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

class SellerMetricsFramework:
    """卖家业务指标框架类"""
    
    def __init__(self):
        """初始化指标权重和阈值"""
        # 指标权重配置 (总和=1.0)
        self.metric_weights = {
            'business_performance': 0.4,    # 业务表现 40%
            'customer_satisfaction': 0.25,  # 客户满意度 25%
            'operational_efficiency': 0.25, # 运营效率 25%
            'growth_potential': 0.1         # 成长潜力 10%
        }
        
        # 分级阈值
        self.tier_thresholds = {
            'platinum': 0.85,   # 白金级 (Top 5%)
            'gold': 0.70,       # 金牌级 (Top 15%)
            'silver': 0.50,     # 银牌级 (Top 40%)
            'bronze': 0.30,     # 铜牌级 (Top 70%)
            'basic': 0.0        # 基础级 (Bottom 30%)
        }
    
    def calculate_business_performance_score(self, seller_data: pd.DataFrame) -> pd.Series:
        """
        计算业务表现得分
        
        包含指标:
        - 销售额(30%): 标准化总销售额
        - 订单量(25%): 标准化订单数量  
        - 商品丰富度(20%): SKU数量评分
        - 客单价(15%): 平均订单价值
        - 市场覆盖(10%): 地理覆盖范围
        """
        score_components = {}
        
        # 1. 销售额得分 (对数变换处理长尾分布)
        revenue = seller_data['total_revenue'].fillna(0)
        revenue_log = np.log1p(revenue)  # log(1+x) 避免log(0)
        score_components['revenue'] = self._normalize_score(revenue_log) * 0.30
        
        # 2. 订单量得分
        orders = seller_data['total_orders'].fillna(0)
        orders_log = np.log1p(orders)
        score_components['orders'] = self._normalize_score(orders_log) * 0.25
        
        # 3. 商品丰富度得分
        sku_count = seller_data['unique_products'].fillna(0)
        sku_score = np.minimum(sku_count / 50, 1.0)  # 50个SKU为满分
        score_components['sku_diversity'] = sku_score * 0.20
        
        # 4. 客单价得分
        aov = seller_data['avg_order_value'].fillna(0)
        aov_normalized = self._normalize_score(aov)
        score_components['aov'] = aov_normalized * 0.15
        
        # 5. 市场覆盖得分（简化版：暂时给固定分）
        score_components['market_coverage'] = 0.5 * 0.10
        
        # 综合得分
        total_score = sum(score_components.values())
        return total_score
    
    def calculate_customer_satisfaction_score(self, seller_data: pd.DataFrame) -> pd.Series:
        """
        计算客户满意度得分
        
        包含指标:
        - 平均评分(40%): 1-5分标准化
        - 好评率(30%): 4-5分评价占比
        - 评价数量(20%): 评价样本量充足度
        - 评分稳定性(10%): 评分标准差(逆向)
        """
        score_components = {}
        
        # 1. 平均评分得分
        avg_rating = seller_data['avg_review_score'].fillna(3.0)  # 缺失值用中位数填充
        rating_score = (avg_rating - 1) / 4  # 转换为0-1分数
        score_components['avg_rating'] = np.clip(rating_score, 0, 1) * 0.40
        
        # 2. 好评率得分
        positive_rate = seller_data['positive_rate'].fillna(0.6)  # 默认60%好评率
        score_components['positive_rate'] = positive_rate * 0.30
        
        # 3. 评价数量充足度
        review_count = seller_data['total_reviews'].fillna(0)
        review_sufficiency = np.minimum(review_count / 30, 1.0)  # 30个评价为满分
        score_components['review_volume'] = review_sufficiency * 0.20
        
        # 4. 评分稳定性 (标准差越小越好)
        rating_std = seller_data['review_score_std'].fillna(1.0)
        stability_score = np.maximum(1 - (rating_std / 2), 0)  # 标准差2为0分
        score_components['rating_stability'] = stability_score * 0.10
        
        # 综合得分
        total_score = sum(score_components.values())
        return total_score
    
    def calculate_operational_efficiency_score(self, seller_data: pd.DataFrame) -> pd.Series:
        """
        计算运营效率得分
        
        包含指标:
        - 订单履约率(30%): 成功完成订单比例
        - 平均件单价(25%): 商品定价合理性
        - 运费比例(20%): 物流成本控制
        - 商品转化率(15%): 商品-订单转化
        - 复购指标(10%): 客户粘性
        """
        score_components = {}
        
        # 1. 订单履约率 (简化：假设90%基础履约率)
        score_components['fulfillment_rate'] = 0.90 * 0.30
        
        # 2. 平均件单价合理性
        avg_item_price = seller_data['avg_price_per_item'].fillna(50)
        # 假设50-200 R$为合理价格区间
        price_reasonableness = np.where(
            (avg_item_price >= 50) & (avg_item_price <= 200), 1.0,
            np.where(avg_item_price < 50, avg_item_price/50, 200/avg_item_price)
        )
        score_components['pricing'] = np.clip(price_reasonableness, 0, 1) * 0.25
        
        # 3. 运费比例控制
        freight_ratio = seller_data['freight_ratio'].fillna(0.15)
        # 运费比例越低越好，15%以下为优秀
        freight_score = np.maximum(1 - (freight_ratio / 0.15), 0)
        score_components['freight_efficiency'] = np.clip(freight_score, 0, 1) * 0.20
        
        # 4. 商品转化率
        items_per_order = seller_data['avg_items_per_order'].fillna(1.2)
        conversion_score = np.minimum(items_per_order / 2.0, 1.0)  # 2件/订单为满分
        score_components['conversion'] = conversion_score * 0.15
        
        # 5. 复购指标 (简化版)
        score_components['retention'] = 0.6 * 0.10
        
        # 综合得分
        total_score = sum(score_components.values())
        return total_score
    
    def calculate_growth_potential_score(self, seller_data: pd.DataFrame) -> pd.Series:
        """
        计算成长潜力得分
        
        包含指标:
        - 商品扩展能力(40%): SKU增长潜力
        - 销售趋势(30%): 近期增长趋势
        - 市场定位(20%): 细分市场机会
        - 创新能力(10%): 新品推出频率
        """
        score_components = {}
        
        # 1. 商品扩展潜力
        current_sku = seller_data['unique_products'].fillna(1)
        expansion_potential = np.where(
            current_sku < 10, 0.8,    # 低SKU卖家有较高扩展潜力
            np.where(current_sku < 25, 0.6, 0.4)  # 高SKU卖家扩展潜力递减
        )
        score_components['expansion_potential'] = expansion_potential * 0.40
        
        # 2. 销售趋势 (简化：基于当前表现推断)
        revenue_tier = pd.qcut(seller_data['total_revenue'].fillna(0), 5, labels=['low', 'below_avg', 'avg', 'above_avg', 'high'])
        trend_score = {
            'low': 0.7,        # 低收入卖家增长潜力大
            'below_avg': 0.6,
            'avg': 0.5,
            'above_avg': 0.4,
            'high': 0.3        # 高收入卖家增长空间有限
        }
        growth_trend = revenue_tier.map(trend_score).fillna(0.5)
        score_components['growth_trend'] = growth_trend * 0.30
        
        # 3. 市场定位
        score_components['market_positioning'] = 0.5 * 0.20
        
        # 4. 创新能力
        score_components['innovation'] = 0.4 * 0.10
        
        # 综合得分
        total_score = sum(score_components.values())
        return total_score
    
    def calculate_overall_seller_score(self, seller_data: pd.DataFrame) -> pd.DataFrame:
        """
        计算卖家综合得分
        
        返回包含各维度得分和综合得分的DataFrame
        """
        result = seller_data.copy()
        
        # 计算各维度得分
        result['business_performance_score'] = self.calculate_business_performance_score(seller_data)
        result['customer_satisfaction_score'] = self.calculate_customer_satisfaction_score(seller_data)
        result['operational_efficiency_score'] = self.calculate_operational_efficiency_score(seller_data)
        result['growth_potential_score'] = self.calculate_growth_potential_score(seller_data)
        
        # 计算加权综合得分
        result['overall_score'] = (
            result['business_performance_score'] * self.metric_weights['business_performance'] +
            result['customer_satisfaction_score'] * self.metric_weights['customer_satisfaction'] +
            result['operational_efficiency_score'] * self.metric_weights['operational_efficiency'] +
            result['growth_potential_score'] * self.metric_weights['growth_potential']
        )
        
        # 分配等级
        result['seller_tier'] = self._assign_tier(result['overall_score'])
        
        return result
    
    def _normalize_score(self, values: pd.Series) -> pd.Series:
        """标准化分数到0-1区间"""
        min_val = values.min()
        max_val = values.max()
        if max_val == min_val:
            return pd.Series(0.5, index=values.index)
        return (values - min_val) / (max_val - min_val)
    
    def _assign_tier(self, scores: pd.Series) -> pd.Series:
        """根据得分分配等级"""
        conditions = [
            scores >= self.tier_thresholds['platinum'],
            scores >= self.tier_thresholds['gold'],
            scores >= self.tier_thresholds['silver'],
            scores >= self.tier_thresholds['bronze']
        ]
        choices = ['Platinum', 'Gold', 'Silver', 'Bronze']
        return pd.Series(np.select(conditions, choices, default='Basic'), index=scores.index)
    
    def generate_seller_insights(self, seller_scores: pd.DataFrame) -> Dict:
        """
        生成卖家洞察报告
        """
        insights = {
            'tier_distribution': seller_scores['seller_tier'].value_counts().to_dict(),
            'avg_scores_by_tier': seller_scores.groupby('seller_tier')[
                ['business_performance_score', 'customer_satisfaction_score', 
                 'operational_efficiency_score', 'growth_potential_score', 'overall_score']
            ].mean().round(3).to_dict(),
            'top_performers': seller_scores.nlargest(10, 'overall_score')[
                ['seller_id', 'seller_tier', 'overall_score', 'total_revenue']
            ].to_dict('records'),
            'improvement_opportunities': self._identify_improvement_opportunities(seller_scores)
        }
        
        return insights
    
    def _identify_improvement_opportunities(self, seller_scores: pd.DataFrame) -> Dict:
        """识别改进机会"""
        opportunities = {}
        
        # 识别低满意度但高销量的卖家
        high_revenue_low_satisfaction = seller_scores[
            (seller_scores['total_revenue'] > seller_scores['total_revenue'].quantile(0.75)) &
            (seller_scores['customer_satisfaction_score'] < 0.6)
        ]
        
        opportunities['satisfaction_improvement'] = {
            'count': len(high_revenue_low_satisfaction),
            'avg_revenue': high_revenue_low_satisfaction['total_revenue'].mean(),
            'potential_impact': 'High'
        }
        
        # 识别高潜力但低表现的卖家
        high_potential_low_performance = seller_scores[
            (seller_scores['growth_potential_score'] > 0.7) &
            (seller_scores['business_performance_score'] < 0.4)
        ]
        
        opportunities['growth_acceleration'] = {
            'count': len(high_potential_low_performance),
            'avg_potential_score': high_potential_low_performance['growth_potential_score'].mean(),
            'potential_impact': 'Medium'
        }
        
        return opportunities


# 业务策略建议映射
TIER_STRATEGIES = {
    'Platinum': {
        'priority': 'VIP服务',
        'actions': [
            '提供专属客户经理',
            '优先营销资源投放',
            '新产品试点合作',
            '平台政策优先级'
        ],
        'kpi_focus': ['市场份额扩大', '品牌影响力提升']
    },
    'Gold': {
        'priority': '重点扶持',
        'actions': [
            '营销工具培训',
            '运营数据分析支持',
            '类目拓展建议',
            '物流效率优化'
        ],
        'kpi_focus': ['销售额增长', '客户满意度']
    },
    'Silver': {
        'priority': '标准服务',
        'actions': [
            '基础运营培训',
            '产品优化建议',
            '客服质量提升',
            '定期业务回顾'
        ],
        'kpi_focus': ['运营效率', '稳定增长']
    },
    'Bronze': {
        'priority': '改进引导',
        'actions': [
            '基础平台使用培训',
            '产品质量改进',
            '客户服务标准化',
            '问题诊断与解决'
        ],
        'kpi_focus': ['基础指标达标', '服务质量']
    },
    'Basic': {
        'priority': '风险管控',
        'actions': [
            '合规性检查',
            '基础培训',
            '问题整改',
            '定期监控'
        ],
        'kpi_focus': ['合规性', '基础服务质量']
    }
} 