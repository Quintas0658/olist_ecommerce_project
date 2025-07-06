#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
月度卖家分析模块
支持按月构建卖家画像和动态分类
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class MonthlySellerAnalyzer:
    """月度卖家分析器"""
    
    def __init__(self, data_pipeline):
        self.data_pipeline = data_pipeline
        self.raw_data = {}
        self.monthly_profiles = {}
        self.tier_definitions = self._get_tier_definitions()
        
    def _get_tier_definitions(self):
        """定义固定的分层标准"""
        return {
            'Platinum': {'min_gmv': 50000, 'min_orders': 200, 'min_rating': 4.0},
            'Gold': {'min_gmv': 10000, 'min_orders': 50, 'min_rating': 3.5},
            'Silver': {'min_gmv': 2000, 'min_orders': 10, 'min_rating': 3.0},
            'Bronze': {'min_gmv': 500, 'min_orders': 3, 'min_rating': 2.5},
            'Basic': {'min_gmv': 0, 'min_orders': 1, 'min_rating': 0}
        }
    
    def load_raw_data(self):
        """从DataPipeline加载原始数据"""
        logger.info("📊 正在加载原始数据...")
        
        try:
            # 使用DataPipeline加载数据
            self.raw_data = self.data_pipeline.load_raw_data()
            
            # 记录数据量
            for name, data in self.raw_data.items():
                if data is not None and len(data) > 0:
                    logger.info(f"   ✅ {name}: {len(data):,} 记录")
            
            # 预处理时间字段
            if 'orders' in self.raw_data and self.raw_data['orders'] is not None:
                if 'order_purchase_timestamp' in self.raw_data['orders'].columns:
                    self.raw_data['orders']['order_purchase_timestamp'] = pd.to_datetime(
                        self.raw_data['orders']['order_purchase_timestamp'], errors='coerce'
                    )
                    self.raw_data['orders']['year_month'] = self.raw_data['orders']['order_purchase_timestamp'].dt.to_period('M')
            
            logger.info("✅ 原始数据加载完成")
            return self.raw_data
            
        except Exception as e:
            logger.error(f"❌ 数据加载失败: {e}")
            return {}
    
    def get_available_months(self):
        """获取可用的月份列表"""
        if 'orders' not in self.raw_data:
            self.load_raw_data()
        
        if 'orders' in self.raw_data and 'year_month' in self.raw_data['orders'].columns:
            months = sorted(self.raw_data['orders']['year_month'].dropna().unique())
            return [str(m) for m in months]
        return []
    
    def build_monthly_seller_profile(self, target_month: str, lookback_months: int = 3):
        """
        构建指定月份的卖家画像
        
        Args:
            target_month: 目标月份，格式 '2017-01'
            lookback_months: 回望月数，用于计算累积指标
        """
        logger.info(f"🗓️ 构建 {target_month} 月份卖家画像 (回望{lookback_months}个月)")
        
        if not self.raw_data:
            self.load_raw_data()
        
        # 计算时间窗口
        target_period = pd.Period(target_month)
        start_period = target_period - lookback_months
        
        # 筛选时间窗口内的数据
        orders_filtered = self.raw_data['orders'][
            (self.raw_data['orders']['year_month'] >= start_period) &
            (self.raw_data['orders']['year_month'] <= target_period)
        ].copy()
        
        if len(orders_filtered) == 0:
            logger.warning(f"⚠️ {target_month} 月份无数据")
            return pd.DataFrame()
        
        # 构建各项指标
        logger.info(f"   📈 计算 {len(orders_filtered):,} 个订单的指标...")
        
        # 1. 基础卖家信息
        seller_profile = self.raw_data['sellers'].copy()
        seller_profile['analysis_month'] = target_month
        seller_profile['lookback_months'] = lookback_months
        
        # 2. 销售指标
        sales_metrics = self._calculate_monthly_sales_metrics(orders_filtered)
        seller_profile = seller_profile.merge(sales_metrics, on='seller_id', how='left')
        
        # 3. 满意度指标
        satisfaction_metrics = self._calculate_monthly_satisfaction_metrics(orders_filtered)
        seller_profile = seller_profile.merge(satisfaction_metrics, on='seller_id', how='left')
        
        # 4. 运营效率指标
        efficiency_metrics = self._calculate_monthly_efficiency_metrics(orders_filtered)
        seller_profile = seller_profile.merge(efficiency_metrics, on='seller_id', how='left')
        
        # 5. 品类指标
        category_metrics = self._calculate_monthly_category_metrics(orders_filtered)
        seller_profile = seller_profile.merge(category_metrics, on='seller_id', how='left')
        
        # 6. 时间趋势指标
        temporal_metrics = self._calculate_monthly_temporal_metrics(orders_filtered)
        seller_profile = seller_profile.merge(temporal_metrics, on='seller_id', how='left')
        
        # 7. 清洗和衍生指标
        seller_profile = self._clean_monthly_features(seller_profile)
        
        # 8. 应用分层标准
        seller_profile['business_tier'] = seller_profile.apply(self._classify_seller, axis=1)
        
        # 存储月度画像
        self.monthly_profiles[target_month] = seller_profile
        
        logger.info(f"✅ {target_month} 月份卖家画像构建完成: {len(seller_profile):,} 个卖家")
        return seller_profile
    
    def _calculate_monthly_sales_metrics(self, orders_filtered):
        """计算月度销售指标"""
        order_items = self.raw_data['order_items']
        
        # 合并订单和订单项目
        order_details = orders_filtered.merge(order_items, on='order_id', how='inner')
        
        if len(order_details) == 0:
            return pd.DataFrame(columns=['seller_id'])
        
        # 按卖家聚合
        metrics = order_details.groupby('seller_id').agg({
            'price': ['sum', 'mean', 'count'],
            'freight_value': ['sum', 'mean'],
            'order_id': 'nunique',
            'product_id': 'nunique'
        }).round(2)
        
        metrics.columns = [
            'total_gmv', 'avg_order_value', 'total_items',
            'total_freight', 'avg_freight',
            'unique_orders', 'unique_products'
        ]
        
        return metrics.reset_index()
    
    def _calculate_monthly_satisfaction_metrics(self, orders_filtered):
        """计算月度满意度指标"""
        order_items = self.raw_data['order_items']
        reviews = self.raw_data['reviews']
        
        # 合并数据
        order_details = orders_filtered.merge(order_items, on='order_id', how='inner')
        order_reviews = order_details.merge(reviews, on='order_id', how='left')
        
        if len(order_reviews) == 0:
            return pd.DataFrame(columns=['seller_id'])
        
        # 计算评价指标
        review_metrics = order_reviews.groupby('seller_id').agg({
            'review_score': ['mean', 'count', 'std'],
            'review_id': 'count'
        }).round(2)
        
        review_metrics.columns = ['avg_review_score', 'review_count', 'review_score_std', 'total_reviews']
        
        # 差评率
        bad_reviews = order_reviews[order_reviews['review_score'] <= 2].groupby('seller_id').size()
        total_reviews = order_reviews.groupby('seller_id')['review_score'].count()
        bad_review_rate = (bad_reviews / total_reviews * 100).fillna(0).round(2)
        
        review_metrics['bad_review_rate'] = bad_review_rate
        
        return review_metrics.reset_index()
    
    def _calculate_monthly_efficiency_metrics(self, orders_filtered):
        """计算月度运营效率指标"""
        order_items = self.raw_data['order_items']
        
        # 合并数据
        order_details = orders_filtered.merge(order_items, on='order_id', how='inner')
        
        # 转换时间字段
        time_cols = ['order_delivered_carrier_date', 'order_delivered_customer_date']
        for col in time_cols:
            if col in order_details.columns:
                order_details[col] = pd.to_datetime(order_details[col], errors='coerce')
        
        # 计算效率指标
        if 'order_delivered_carrier_date' in order_details.columns:
            order_details['shipping_days'] = (
                order_details['order_delivered_carrier_date'] - 
                order_details['order_purchase_timestamp']
            ).dt.days
        
        if 'order_delivered_customer_date' in order_details.columns:
            order_details['delivery_days'] = (
                order_details['order_delivered_customer_date'] - 
                order_details['order_delivered_carrier_date']
            ).dt.days
        
        # 聚合指标
        ops_metrics = order_details.groupby('seller_id').agg({
            'shipping_days': ['mean', 'median'],
            'delivery_days': ['mean', 'median'],
            'order_status': lambda x: (x == 'delivered').sum() / len(x) * 100
        }).round(2)
        
        ops_metrics.columns = [
            'avg_shipping_days', 'median_shipping_days',
            'avg_delivery_days', 'median_delivery_days',
            'delivery_success_rate'
        ]
        
        return ops_metrics.reset_index()
    
    def _calculate_monthly_category_metrics(self, orders_filtered):
        """计算月度品类指标"""
        order_items = self.raw_data['order_items']
        products = self.raw_data['products']
        
        # 合并数据
        order_details = orders_filtered.merge(order_items, on='order_id', how='inner')
        product_details = order_details.merge(products, on='product_id', how='left')
        
        # 品类指标
        category_metrics = product_details.groupby('seller_id').agg({
            'product_category_name': 'nunique',
            'product_id': 'nunique'
        })
        
        category_metrics.columns = ['category_count', 'sku_count']
        
        return category_metrics.reset_index()
    
    def _calculate_monthly_temporal_metrics(self, orders_filtered):
        """计算月度时间指标"""
        order_items = self.raw_data['order_items']
        
        # 合并数据
        order_details = orders_filtered.merge(order_items, on='order_id', how='inner')
        
        # 时间指标
        time_metrics = order_details.groupby('seller_id')['order_purchase_timestamp'].agg([
            'min', 'max', 'count'
        ])
        time_metrics.columns = ['first_order_date', 'last_order_date', 'total_orders']
        
        # 活跃天数
        time_metrics['active_days'] = (
            time_metrics['last_order_date'] - time_metrics['first_order_date']
        ).dt.days + 1
        
        time_metrics['order_frequency'] = (
            time_metrics['total_orders'] / time_metrics['active_days']
        ).round(4)
        
        return time_metrics.reset_index()
    
    def _clean_monthly_features(self, df):
        """清洗月度特征"""
        # 填充缺失值
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].fillna(0)
        
        # 衍生指标
        df['revenue_per_order'] = df['total_gmv'] / df['unique_orders'].replace(0, 1)
        df['items_per_order'] = df['total_items'] / df['unique_orders'].replace(0, 1)
        df['is_active'] = (df['total_gmv'] > 0).astype(int)
        
        return df
    
    def _classify_seller(self, row):
        """应用固定的分层标准"""
        gmv = row.get('total_gmv', 0)
        orders = row.get('unique_orders', 0)
        rating = row.get('avg_review_score', 0)
        
        # 按层级从高到低检查
        for tier, criteria in self.tier_definitions.items():
            if (gmv >= criteria['min_gmv'] and 
                orders >= criteria['min_orders'] and 
                rating >= criteria['min_rating']):
                return tier
        
        return 'Basic'
    
    def analyze_tier_changes(self, months_list: List[str]):
        """分析多个月份的层级变化"""
        logger.info(f"📊 分析 {len(months_list)} 个月的层级变化...")
        
        # 构建所有月份的画像
        for month in months_list:
            if month not in self.monthly_profiles:
                self.build_monthly_seller_profile(month)
        
        # 合并多月数据
        tier_changes = []
        for month in months_list:
            if month in self.monthly_profiles:
                df = self.monthly_profiles[month][['seller_id', 'business_tier', 'total_gmv', 'unique_orders']].copy()
                df['month'] = month
                tier_changes.append(df)
        
        if not tier_changes:
            return pd.DataFrame()
        
        combined_df = pd.concat(tier_changes, ignore_index=True)
        
        # 生成层级流转矩阵
        flow_matrix = self._create_tier_flow_matrix(combined_df, months_list)
        
        return {
            'monthly_data': combined_df,
            'tier_flow_matrix': flow_matrix,
            'tier_stability': self._calculate_tier_stability(combined_df)
        }
    
    def analyze_period_comparison(self, target_month: str):
        """
        分析指定月份的同比环比变化
        
        Args:
            target_month: 目标月份，格式 '2018-10'
        
        Returns:
            dict: 包含环比、同比分析结果
        """
        logger.info(f"📈 分析 {target_month} 的同比环比变化...")
        
        try:
            target_period = pd.Period(target_month)
            
            # 计算环比和同比月份
            mom_month = str(target_period - 1)  # 环比：上个月
            yoy_month = str(target_period - 12)  # 同比：去年同月
            
            logger.info(f"   环比对比: {target_month} vs {mom_month}")
            logger.info(f"   同比对比: {target_month} vs {yoy_month}")
            
            # 构建必要的月度画像
            months_to_build = [target_month, mom_month, yoy_month]
            available_months = self.get_available_months()
            
            for month in months_to_build:
                if month in available_months and month not in self.monthly_profiles:
                    self.build_monthly_seller_profile(month)
            
            result = {
                'target_month': target_month,
                'mom_comparison': None,
                'yoy_comparison': None
            }
            
            # 环比分析
            if mom_month in available_months and mom_month in self.monthly_profiles:
                result['mom_comparison'] = self._compare_two_months(
                    target_month, mom_month, "环比"
                )
            else:
                logger.warning(f"   ⚠️ 环比月份 {mom_month} 数据不可用")
            
            # 同比分析
            if yoy_month in available_months and yoy_month in self.monthly_profiles:
                result['yoy_comparison'] = self._compare_two_months(
                    target_month, yoy_month, "同比"
                )
            else:
                logger.warning(f"   ⚠️ 同比月份 {yoy_month} 数据不可用")
            
            return result
            
        except Exception as e:
            logger.error(f"   ❌ 同比环比分析失败: {e}")
            return {}
    
    def _compare_two_months(self, month1: str, month2: str, comparison_type: str):
        """
        对比两个月份的层级变化
        
        Args:
            month1: 新月份 (目标月份)
            month2: 基准月份 (对比月份)
            comparison_type: 对比类型 ("环比" or "同比")
        """
        logger.info(f"   🔍 {comparison_type}分析: {month1} vs {month2}")
        
        # 获取两个月份的数据
        df1 = self.monthly_profiles[month1][['seller_id', 'business_tier', 'total_gmv', 'unique_orders']].copy()
        df2 = self.monthly_profiles[month2][['seller_id', 'business_tier', 'total_gmv', 'unique_orders']].copy()
        
        # 合并数据找到共同卖家
        merged = df1.merge(
            df2, 
            on='seller_id', 
            suffixes=(f'_{month1}', f'_{month2}'),
            how='inner'
        )
        
        if len(merged) == 0:
            return {'error': f'没有共同卖家数据'}
        
        # 分析层级变化
        tier_order = {'Basic': 0, 'Bronze': 1, 'Silver': 2, 'Gold': 3, 'Platinum': 4}
        
        merged[f'tier_num_{month1}'] = merged[f'business_tier_{month1}'].map(tier_order)
        merged[f'tier_num_{month2}'] = merged[f'business_tier_{month2}'].map(tier_order)
        
        # 计算层级变化
        merged['tier_change'] = merged[f'tier_num_{month1}'] - merged[f'tier_num_{month2}']
        
        # 分类卖家
        upgraded_sellers = merged[merged['tier_change'] > 0].copy()
        downgraded_sellers = merged[merged['tier_change'] < 0].copy()
        stable_sellers = merged[merged['tier_change'] == 0].copy()
        
        # 创建流转矩阵
        flow_matrix = pd.crosstab(
            merged[f'business_tier_{month2}'], 
            merged[f'business_tier_{month1}'], 
            margins=True
        )
        
        # 计算汇总指标
        summary_stats = {
            'total_sellers': len(merged),
            'upgraded_count': len(upgraded_sellers),
            'downgraded_count': len(downgraded_sellers),
            'stable_count': len(stable_sellers),
            'upgrade_rate': len(upgraded_sellers) / len(merged) * 100,
            'downgrade_rate': len(downgraded_sellers) / len(merged) * 100,
            'stability_rate': len(stable_sellers) / len(merged) * 100
        }
        
        return {
            'comparison_type': comparison_type,
            'month1': month1,
            'month2': month2,
            'summary_stats': summary_stats,
            'flow_matrix': flow_matrix,
            'upgraded_sellers': upgraded_sellers,
            'downgraded_sellers': downgraded_sellers,
            'stable_sellers': stable_sellers,
            'merged_data': merged
        }
    
    def analyze_seller_trajectory(self, months_list: List[str], min_months: int = 3):
        """
        分析卖家多月轨迹变化
        
        Args:
            months_list: 要分析的月份列表
            min_months: 最少需要的月份数据
        """
        logger.info(f"🛤️ 分析卖家轨迹变化 ({len(months_list)} 个月)")
        
        # 构建所有月份的画像
        for month in months_list:
            if month not in self.monthly_profiles:
                self.build_monthly_seller_profile(month)
        
        # 合并多月数据
        trajectory_data = []
        for month in months_list:
            if month in self.monthly_profiles:
                df = self.monthly_profiles[month][['seller_id', 'business_tier']].copy()
                df['month'] = month
                trajectory_data.append(df)
        
        if len(trajectory_data) < min_months:
            return {'error': f'需要至少{min_months}个月数据'}
        
        combined_df = pd.concat(trajectory_data, ignore_index=True)
        
        # 创建透视表：seller_id x month
        pivot_df = combined_df.pivot(index='seller_id', columns='month', values='business_tier')
        
        # 只保留有足够数据的卖家
        valid_sellers = pivot_df.dropna(thresh=min_months)
        
        if len(valid_sellers) == 0:
            return {'error': '没有卖家有足够的月份数据'}
        
        # 分析轨迹模式
        tier_order = {'Basic': 0, 'Bronze': 1, 'Silver': 2, 'Gold': 3, 'Platinum': 4}
        
        trajectory_analysis = []
        for seller_id, row in valid_sellers.iterrows():
            # 转换为数值轨迹
            numeric_tiers = [tier_order.get(tier, 0) for tier in row.dropna()]
            tier_path = ' → '.join(row.dropna().astype(str))
            
            # 计算轨迹特征
            tier_changes = np.diff(numeric_tiers)
            total_changes = len(tier_changes[tier_changes != 0])
            volatility = np.std(numeric_tiers) if len(numeric_tiers) > 1 else 0
            trend = np.polyfit(range(len(numeric_tiers)), numeric_tiers, 1)[0] if len(numeric_tiers) > 1 else 0
            
            # 分类轨迹类型
            if trend > 0.1:
                trajectory_type = "持续上升"
            elif trend < -0.1:
                trajectory_type = "持续下降"
            elif volatility > 0.5:
                trajectory_type = "频繁波动"
            else:
                trajectory_type = "相对稳定"
            
            trajectory_analysis.append({
                'seller_id': seller_id,
                'tier_path': tier_path,
                'total_changes': total_changes,
                'volatility': round(volatility, 3),
                'trend': round(trend, 3),
                'trajectory_type': trajectory_type,
                'start_tier': row.dropna().iloc[0],
                'end_tier': row.dropna().iloc[-1],
                'data_months': len(row.dropna())
            })
        
        trajectory_df = pd.DataFrame(trajectory_analysis)
        
        # 统计各类轨迹
        trajectory_summary = trajectory_df['trajectory_type'].value_counts().to_dict()
        
        return {
            'trajectory_data': trajectory_df,
            'trajectory_summary': trajectory_summary,
            'months_analyzed': months_list,
            'total_sellers': len(trajectory_df)
        }

    def _create_tier_flow_matrix(self, combined_df, months_list):
        """创建层级流转矩阵 - 改为支持最后两个月对比"""
        if len(months_list) < 2:
            return pd.DataFrame()
        
        # 取最后两个月进行对比 (更符合时序逻辑)
        month1, month2 = months_list[-2], months_list[-1]
        
        df1 = combined_df[combined_df['month'] == month1][['seller_id', 'business_tier']].rename(
            columns={'business_tier': 'tier_from'}
        )
        df2 = combined_df[combined_df['month'] == month2][['seller_id', 'business_tier']].rename(
            columns={'business_tier': 'tier_to'}
        )
        
        # 合并找到流转
        flow_df = df1.merge(df2, on='seller_id', how='inner')
        
        # 创建流转矩阵
        flow_matrix = pd.crosstab(flow_df['tier_from'], flow_df['tier_to'], margins=True)
        
        return flow_matrix
    
    def _calculate_tier_stability(self, combined_df):
        """计算层级稳定性"""
        stability_metrics = {}
        
        # 按卖家统计层级变化频次
        seller_tiers = combined_df.pivot(index='seller_id', columns='month', values='business_tier')
        
        for tier in self.tier_definitions.keys():
            tier_sellers = seller_tiers[seller_tiers.iloc[:, 0] == tier]
            if len(tier_sellers) > 0:
                # 计算该层级卖家的稳定性（不变的比例）
                stable_count = 0
                for idx, row in tier_sellers.iterrows():
                    if row.nunique() == 1:  # 所有月份都是同一层级
                        stable_count += 1
                
                stability_metrics[tier] = {
                    'total_sellers': len(tier_sellers),
                    'stable_sellers': stable_count,
                    'stability_rate': stable_count / len(tier_sellers) if len(tier_sellers) > 0 else 0
                }
        
        return stability_metrics
    
    def save_monthly_analysis(self, target_month: str, filepath: str = None):
        """保存月度分析结果"""
        if target_month not in self.monthly_profiles:
            logger.warning(f"⚠️ {target_month} 月份数据不存在")
            return
        
        if filepath is None:
            filepath = f'data/monthly_seller_profile_{target_month}.csv'
        
        self.monthly_profiles[target_month].to_csv(filepath, index=False)
        logger.info(f"✅ 已保存 {target_month} 月份分析到: {filepath}")
    
    def get_monthly_summary(self, target_month: str):
        """获取月度摘要"""
        if target_month not in self.monthly_profiles:
            return {}
        
        df = self.monthly_profiles[target_month]
        active_sellers = df[df['is_active'] == 1]
        
        summary = {
            'analysis_month': target_month,
            'total_sellers': len(df),
            'active_sellers': len(active_sellers),
            'total_gmv': active_sellers['total_gmv'].sum(),
            'avg_gmv_per_seller': active_sellers['total_gmv'].mean(),
            'total_orders': active_sellers['unique_orders'].sum(),
            'avg_rating': active_sellers['avg_review_score'].mean(),
            'tier_distribution': df['business_tier'].value_counts().to_dict()
        }
        
        return summary

def main():
    """演示月度分析功能"""
    # 初始化分析器
    analyzer = MonthlySellerAnalyzer()
    
    # 获取可用月份
    available_months = analyzer.get_available_months()
    print(f"📅 可用月份: {available_months[:5]}...")  # 显示前5个月
    
    if len(available_months) >= 2:
        # 分析最近两个月
        recent_months = available_months[-2:]
        print(f"\n🔍 分析月份: {recent_months}")
        
        # 构建月度画像
        for month in recent_months:
            profile = analyzer.build_monthly_seller_profile(month)
            summary = analyzer.get_monthly_summary(month)
            print(f"\n📊 {month} 月份摘要:")
            print(f"   活跃卖家: {summary['active_sellers']:,}")
            print(f"   总GMV: R$ {summary['total_gmv']:,.2f}")
            print(f"   层级分布: {summary['tier_distribution']}")
        
        # 分析层级变化
        tier_analysis = analyzer.analyze_tier_changes(recent_months)
        print(f"\n📈 层级流转分析:")
        print(tier_analysis['tier_flow_matrix'])

if __name__ == "__main__":
    main() 