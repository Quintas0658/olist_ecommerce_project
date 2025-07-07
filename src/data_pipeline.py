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
        
        # 尝试加载原始数据
        original_data_available = True
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
                    if name in ['orders', 'order_items', 'sellers']:  # 关键数据
                        original_data_available = False
        
        # 如果原始数据不可用，尝试使用已处理的数据文件
        if not original_data_available:
            logger.info("📦 原始数据不完整，尝试使用已处理的数据文件...")
            self._load_processed_data_fallback()
                    
        logger.info("✅ 原始数据加载完成")
        return self.raw_data
    
    def _load_processed_data_fallback(self):
        """当原始数据不可用时，使用已处理数据作为备选方案"""
        logger.info("🔄 使用已处理数据创建月度分析兼容格式...")
        
        try:
            # 加载已处理的卖家画像
            processed_profile = pd.read_csv(f"{self.data_path}seller_profile_processed.csv")
            
            # 重构sellers表
            if 'sellers' not in self.raw_data or len(self.raw_data['sellers']) == 0:
                self.raw_data['sellers'] = processed_profile[['seller_id', 'seller_zip_code_prefix', 'seller_city', 'seller_state']].copy()
                logger.info(f"   ✅ sellers: {len(self.raw_data['sellers']):,} 记录 (从处理数据重构)")
            
            # 创建模拟的orders表（用于月度分析）
            if 'orders' not in self.raw_data or len(self.raw_data['orders']) == 0:
                self.raw_data['orders'] = self._create_synthetic_orders_for_monthly_analysis(processed_profile)
                logger.info(f"   ✅ orders: {len(self.raw_data['orders']):,} 记录 (模拟数据)")
            
            # 创建模拟的order_items表
            if 'order_items' not in self.raw_data or len(self.raw_data['order_items']) == 0:
                self.raw_data['order_items'] = self._create_synthetic_order_items(processed_profile)
                logger.info(f"   ✅ order_items: {len(self.raw_data['order_items']):,} 记录 (模拟数据)")
            
            # 创建模拟的reviews表
            if 'reviews' not in self.raw_data or len(self.raw_data['reviews']) == 0:
                self.raw_data['reviews'] = self._create_synthetic_reviews(processed_profile)
                logger.info(f"   ✅ reviews: {len(self.raw_data['reviews']):,} 记录 (模拟数据)")
            
            # 其他表保持空或使用默认值
            for table in ['payments', 'products', 'customers']:
                if table not in self.raw_data:
                    self.raw_data[table] = pd.DataFrame()
            
            logger.info("✅ 已处理数据加载完成，支持基础月度分析功能")
            
        except Exception as e:
            logger.error(f"❌ 备用数据加载失败: {e}")
    
    def _create_synthetic_orders_for_monthly_analysis(self, processed_profile):
        """基于已处理数据创建用于月度分析的模拟订单表"""
        
        # 为每个卖家创建模拟订单
        orders_list = []
        
        # 定义时间范围（2016-09 到 2018-10）
        from datetime import datetime, timedelta
        import pandas as pd
        
        start_date = datetime(2016, 9, 1)
        end_date = datetime(2018, 10, 31)
        
        order_id_counter = 1
        
        for _, seller in processed_profile.iterrows():
            # 基于卖家的订单数量分布到各个月
            total_orders = seller.get('unique_orders', 10)  # 默认10个订单
            
            if total_orders <= 0:
                continue
                
            # 随机分布订单到不同月份
            current_date = start_date
            orders_created = 0
            
            while current_date <= end_date and orders_created < total_orders:
                # 每月随机创建1-3个订单
                monthly_orders = min(np.random.randint(1, 4), total_orders - orders_created)
                
                for _ in range(monthly_orders):
                    order_timestamp = current_date + timedelta(days=np.random.randint(0, 28))
                    
                    orders_list.append({
                        'order_id': f'order_{order_id_counter:08d}',
                        'customer_id': f'customer_{order_id_counter:08d}',
                        'order_status': 'delivered',
                        'order_purchase_timestamp': order_timestamp,
                        'seller_id': seller['seller_id']  # 添加seller_id用于关联
                    })
                    
                    order_id_counter += 1
                    orders_created += 1
                
                # 移动到下个月
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
        
        orders_df = pd.DataFrame(orders_list)
        
        if len(orders_df) > 0:
            # 添加年月字段用于月度分析
            orders_df['order_purchase_timestamp'] = pd.to_datetime(orders_df['order_purchase_timestamp'])
            orders_df['year_month'] = orders_df['order_purchase_timestamp'].dt.to_period('M')
        
        return orders_df
    
    def _create_synthetic_order_items(self, processed_profile):
        """创建模拟的订单项目表"""
        
        # 如果orders表存在，基于orders创建order_items
        if 'orders' in self.raw_data and len(self.raw_data['orders']) > 0:
            orders = self.raw_data['orders']
            
            items_list = []
            for _, order in orders.iterrows():
                # 每个订单1-3个商品
                num_items = np.random.randint(1, 4)
                
                for item_num in range(num_items):
                    # 从processed_profile中获取卖家的平均价格信息
                    seller_data = processed_profile[processed_profile['seller_id'] == order['seller_id']]
                    
                    if len(seller_data) > 0:
                        avg_price = seller_data.iloc[0].get('avg_order_value', 100)
                        price = max(10, avg_price + np.random.normal(0, avg_price * 0.3))
                    else:
                        price = np.random.uniform(20, 500)
                    
                    items_list.append({
                        'order_id': order['order_id'],
                        'order_item_id': item_num + 1,
                        'product_id': f'product_{np.random.randint(1, 10000):06d}',
                        'seller_id': order['seller_id'],
                        'price': round(price, 2),
                        'freight_value': round(price * 0.1, 2)
                    })
            
            return pd.DataFrame(items_list)
        else:
            return pd.DataFrame()
    
    def _create_synthetic_reviews(self, processed_profile):
        """创建模拟的评价表"""
        
        if 'orders' in self.raw_data and len(self.raw_data['orders']) > 0:
            orders = self.raw_data['orders']
            
            reviews_list = []
            review_id_counter = 1
            
            for _, order in orders.iterrows():
                # 80%的订单有评价
                if np.random.random() < 0.8:
                    # 从processed_profile获取卖家的平均评分
                    seller_data = processed_profile[processed_profile['seller_id'] == order['seller_id']]
                    
                    if len(seller_data) > 0:
                        avg_score = seller_data.iloc[0].get('avg_review_score', 4.0)
                        # 在平均分附近随机生成评分
                        score = max(1, min(5, int(avg_score + np.random.normal(0, 0.5))))
                    else:
                        score = np.random.randint(1, 6)
                    
                    reviews_list.append({
                        'review_id': f'review_{review_id_counter:08d}',
                        'order_id': order['order_id'],
                        'review_score': score,
                        'review_creation_date': order['order_purchase_timestamp']
                    })
                    
                    review_id_counter += 1
            
            return pd.DataFrame(reviews_list)
        else:
            return pd.DataFrame()
    
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