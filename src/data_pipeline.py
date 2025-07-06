#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Olist数据处理管道
整合原始数据，构建卖家画像特征
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataPipeline:
    """数据处理管道类"""
    
    def __init__(self, data_path='data/'):
        self.data_path = data_path
        self.raw_data = {}
        self.seller_profile = None
        
    def load_raw_data(self):
        """加载所有原始数据表"""
        logger.info("📊 正在加载原始数据...")
        
        datasets = {
            'sellers': 'olist_sellers_dataset.csv',
            'orders': 'olist_orders_dataset.csv',
            'order_items': 'olist_order_items_dataset.csv',
            'reviews': 'olist_order_reviews_dataset.csv',
            'payments': 'olist_order_payments_dataset.csv',
            'products': 'olist_products_dataset.csv',
            'customers': 'olist_customers_dataset.csv',
            'category_translation': 'product_category_name_translation.csv'
        }
        
        for name, filename in datasets.items():
            try:
                self.raw_data[name] = pd.read_csv(f"{self.data_path}{filename}")
                logger.info(f"   ✅ {name}: {len(self.raw_data[name]):,} 记录")
            except FileNotFoundError:
                # 尝试从archive目录加载
                try:
                    self.raw_data[name] = pd.read_csv(f"archive/{filename}")
                    logger.info(f"   ✅ {name}: {len(self.raw_data[name]):,} 记录 (从archive加载)")
                except FileNotFoundError:
                    logger.warning(f"   ❌ 未找到 {filename}")
                    
        logger.info("✅ 原始数据加载完成")
        return self.raw_data
    
    def build_seller_features(self):
        """构建卖家特征画像"""
        logger.info("\n🔧 正在构建卖家特征画像...")
        
        if not self.raw_data:
            self.load_raw_data()
            
        # 1. 基础卖家信息
        seller_profile = self.raw_data['sellers'].copy()
        
        # 2. 销售业绩指标
        sales_features = self._build_sales_features()
        seller_profile = seller_profile.merge(sales_features, on='seller_id', how='left')
        
        # 3. 客户满意度指标
        satisfaction_features = self._build_satisfaction_features()
        seller_profile = seller_profile.merge(satisfaction_features, on='seller_id', how='left')
        
        # 4. 运营效率指标
        efficiency_features = self._build_efficiency_features()
        seller_profile = seller_profile.merge(efficiency_features, on='seller_id', how='left')
        
        # 5. 产品品类指标
        category_features = self._build_category_features()
        seller_profile = seller_profile.merge(category_features, on='seller_id', how='left')
        
        # 6. 时间趋势指标
        temporal_features = self._build_temporal_features()
        seller_profile = seller_profile.merge(temporal_features, on='seller_id', how='left')
        
        # 7. 数据清洗和衍生指标
        seller_profile = self._clean_and_derive_features(seller_profile)
        
        self.seller_profile = seller_profile
        
        logger.info(f"✅ 卖家画像构建完成!")
        logger.info(f"   总卖家数: {len(seller_profile):,}")
        logger.info(f"   活跃卖家数: {seller_profile['is_active'].sum():,}")
        logger.info(f"   特征维度: {len(seller_profile.columns)}")
        
        return seller_profile
    
    def _build_sales_features(self):
        """构建销售业绩特征"""
        logger.info("   📈 构建销售业绩指标...")
        
        orders = self.raw_data['orders']
        order_items = self.raw_data['order_items']
        
        # 合并订单项目和订单信息
        order_details = order_items.merge(orders, on='order_id', how='left')
        
        # 按卖家聚合销售指标
        sales_metrics = order_details.groupby('seller_id').agg({
            'price': ['sum', 'mean', 'count'],
            'freight_value': ['sum', 'mean'],
            'order_id': 'nunique',
            'product_id': 'nunique'
        }).round(2)
        
        sales_metrics.columns = [
            'total_gmv', 'avg_order_value', 'total_items',
            'total_freight', 'avg_freight',
            'unique_orders', 'unique_products'
        ]
        
        return sales_metrics.reset_index()
    
    def _build_satisfaction_features(self):
        """构建客户满意度特征"""
        logger.info("   ⭐ 构建客户满意度指标...")
        
        orders = self.raw_data['orders']
        order_items = self.raw_data['order_items']
        reviews = self.raw_data['reviews']
        
        # 合并评价数据
        order_details = order_items.merge(orders, on='order_id', how='left')
        order_reviews = order_details.merge(reviews, on='order_id', how='left')
        
        # 基础评价指标
        review_metrics = order_reviews.groupby('seller_id').agg({
            'review_score': ['mean', 'count', 'std'],
            'review_id': 'count'
        }).round(2)
        
        review_metrics.columns = ['avg_review_score', 'review_count', 'review_score_std', 'total_reviews']
        
        # 差评率计算
        bad_reviews = order_reviews[order_reviews['review_score'] <= 2].groupby('seller_id').size()
        total_reviews = order_reviews.groupby('seller_id')['review_score'].count()
        bad_review_rate = (bad_reviews / total_reviews * 100).fillna(0).round(2)
        
        review_metrics['bad_review_rate'] = bad_review_rate
        
        return review_metrics.reset_index()
    
    def _build_efficiency_features(self):
        """构建运营效率特征"""
        logger.info("   ⚡ 构建运营效率指标...")
        
        orders = self.raw_data['orders']
        order_items = self.raw_data['order_items']
        
        order_details = order_items.merge(orders, on='order_id', how='left')
        
        # 转换时间字段
        time_cols = ['order_purchase_timestamp', 'order_delivered_carrier_date', 'order_delivered_customer_date']
        for col in time_cols:
            if col in order_details.columns:
                order_details[col] = pd.to_datetime(order_details[col], errors='coerce')
        
        # 计算时长指标
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
        
        # 按卖家聚合运营指标
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
    
    def _build_category_features(self):
        """构建产品品类特征"""
        logger.info("   🎯 构建品类覆盖指标...")
        
        order_items = self.raw_data['order_items']
        products = self.raw_data['products']
        
        # 合并产品信息
        product_details = order_items.merge(products, on='product_id', how='left')
        
        category_metrics = product_details.groupby('seller_id').agg({
            'product_category_name': 'nunique',
            'product_id': 'nunique'
        })
        
        category_metrics.columns = ['category_count', 'sku_count']
        
        return category_metrics.reset_index()
    
    def _build_temporal_features(self):
        """构建时间趋势特征"""
        logger.info("   📅 构建时间趋势指标...")
        
        orders = self.raw_data['orders']
        order_items = self.raw_data['order_items']
        
        order_details = order_items.merge(orders, on='order_id', how='left')
        order_details['order_purchase_timestamp'] = pd.to_datetime(
            order_details['order_purchase_timestamp'], errors='coerce'
        )
        
        # 时间指标
        time_metrics = order_details.groupby('seller_id')['order_purchase_timestamp'].agg([
            'min', 'max', 'count'
        ])
        time_metrics.columns = ['first_order_date', 'last_order_date', 'total_orders']
        
        # 活跃天数和订单频率
        time_metrics['active_days'] = (
            time_metrics['last_order_date'] - time_metrics['first_order_date']
        ).dt.days + 1
        
        time_metrics['order_frequency'] = (
            time_metrics['total_orders'] / time_metrics['active_days']
        ).round(4)
        
        return time_metrics.reset_index()
    
    def _clean_and_derive_features(self, df):
        """数据清洗和衍生特征计算"""
        logger.info("   🧹 数据清洗和特征衍生...")
        
        # 填充缺失值
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].fillna(0)
        
        # 衍生特征
        df['revenue_per_order'] = df['total_gmv'] / df['unique_orders'].replace(0, 1)
        df['items_per_order'] = df['total_items'] / df['unique_orders'].replace(0, 1)
        df['is_active'] = (df['total_gmv'] > 0).astype(int)
        
        return df
    
    def save_processed_data(self, filepath='data/seller_profile_processed.csv'):
        """保存处理后的数据"""
        if self.seller_profile is not None:
            self.seller_profile.to_csv(filepath, index=False)
            logger.info(f"✅ 已保存到: {filepath}")
        else:
            logger.warning("❌ 没有处理后的数据可保存")
    
    def get_data_summary(self):
        """获取数据摘要信息"""
        if self.seller_profile is None:
            return "尚未构建卖家画像数据"
            
        active_sellers = self.seller_profile[self.seller_profile['is_active'] == 1]
        
        summary = {
            'total_sellers': len(self.seller_profile),
            'active_sellers': len(active_sellers),
            'total_gmv': active_sellers['total_gmv'].sum(),
            'total_orders': active_sellers['unique_orders'].sum(),
            'avg_rating': active_sellers['avg_review_score'].mean(),
            'features_count': len(self.seller_profile.columns)
        }
        
        return summary

def main():
    """主函数 - 演示数据管道使用"""
    # 初始化数据管道
    pipeline = DataPipeline()
    
    # 构建卖家特征画像
    seller_profile = pipeline.build_seller_features()
    
    # 显示数据摘要
    print("\n🎯 数据管道执行结果:")
    print(f"  📊 处理后的卖家数量: {len(seller_profile):,}")
    print(f"  📋 特征数量: {len(seller_profile.columns)}")
    print(f"  🎯 活跃卖家: {(seller_profile['is_active'] == 1).sum():,}")
    print(f"  💰 平台总GMV: R$ {seller_profile['total_gmv'].sum():,.2f}")
    
    return seller_profile

if __name__ == "__main__":
    main() 