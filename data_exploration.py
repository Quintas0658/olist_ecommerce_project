#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Olist卖家数据探索与预处理
构建seller_profile_df，包含关键业务指标
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def load_data():
    """加载所有数据表"""
    print("📊 正在加载数据...")
    
    # 加载核心表
    sellers = pd.read_csv('data/olist_sellers_dataset.csv')
    orders = pd.read_csv('data/olist_orders_dataset.csv')
    order_items = pd.read_csv('data/olist_order_items_dataset.csv')
    reviews = pd.read_csv('data/olist_order_reviews_dataset.csv')
    payments = pd.read_csv('data/olist_order_payments_dataset.csv')
    products = pd.read_csv('data/olist_products_dataset.csv')
    category_translation = pd.read_csv('data/product_category_name_translation.csv')
    
    print(f"✅ 数据加载完成:")
    print(f"   卖家: {len(sellers):,}")
    print(f"   订单: {len(orders):,}")
    print(f"   订单项目: {len(order_items):,}")
    print(f"   评价: {len(reviews):,}")
    print(f"   支付: {len(payments):,}")
    print(f"   产品: {len(products):,}")
    
    return sellers, orders, order_items, reviews, payments, products, category_translation

def build_seller_profile(sellers, orders, order_items, reviews, payments, products, category_translation):
    """构建卖家画像数据"""
    print("\n🔧 正在构建卖家画像...")
    
    # 1. 基础卖家信息
    seller_profile = sellers.copy()
    
    # 2. 关联订单数据，计算业务指标
    print("   📈 计算销售指标...")
    
    # 合并订单项目和订单信息
    order_details = order_items.merge(orders, on='order_id', how='left')
    
    # 按卖家聚合销售指标
    sales_metrics = order_details.groupby('seller_id').agg({
        'price': ['sum', 'mean', 'count'],  # GMV, 客单价, 订单数
        'freight_value': ['sum', 'mean'],    # 运费总额, 平均运费
        'order_id': 'nunique',               # 独立订单数
        'product_id': 'nunique'              # SKU数量
    }).round(2)
    
    # 重命名列
    sales_metrics.columns = [
        'total_gmv', 'avg_order_value', 'total_items',
        'total_freight', 'avg_freight', 
        'unique_orders', 'unique_products'
    ]
    
    # 3. 计算评价指标
    print("   ⭐ 计算客户满意度指标...")
    
    # 合并评价数据
    order_reviews = order_details.merge(reviews, on='order_id', how='left')
    
    review_metrics = order_reviews.groupby('seller_id').agg({
        'review_score': ['mean', 'count', 'std'],
        'review_id': 'count'
    }).round(2)
    
    # 计算差评率（1-2分）
    bad_reviews = order_reviews[order_reviews['review_score'] <= 2].groupby('seller_id').size()
    total_reviews = order_reviews.groupby('seller_id')['review_score'].count()
    bad_review_rate = (bad_reviews / total_reviews * 100).fillna(0).round(2)
    
    review_metrics.columns = ['avg_review_score', 'review_count', 'review_score_std', 'total_reviews']
    review_metrics['bad_review_rate'] = bad_review_rate
    
    # 4. 计算运营效率指标
    print("   ⚡ 计算运营效率指标...")
    
    # 转换时间字段
    for col in ['order_purchase_timestamp', 'order_delivered_carrier_date', 'order_delivered_customer_date']:
        if col in order_details.columns:
            order_details[col] = pd.to_datetime(order_details[col], errors='coerce')
    
    # 计算发货时长（从购买到交付给承运商）
    order_details['shipping_days'] = (
        order_details['order_delivered_carrier_date'] - 
        order_details['order_purchase_timestamp']
    ).dt.days
    
    # 计算配送时长（从承运商到客户）
    order_details['delivery_days'] = (
        order_details['order_delivered_customer_date'] - 
        order_details['order_delivered_carrier_date']
    ).dt.days
    
    # 按卖家聚合运营指标
    ops_metrics = order_details.groupby('seller_id').agg({
        'shipping_days': ['mean', 'median'],
        'delivery_days': ['mean', 'median'],
        'order_status': lambda x: (x == 'delivered').sum() / len(x) * 100  # 成功交付率
    }).round(2)
    
    ops_metrics.columns = ['avg_shipping_days', 'median_shipping_days', 
                          'avg_delivery_days', 'median_delivery_days', 'delivery_success_rate']
    
    # 5. 计算品类覆盖指标
    print("   🎯 计算品类覆盖指标...")
    
    # 合并产品信息
    product_details = order_items.merge(products, on='product_id', how='left')
    
    category_metrics = product_details.groupby('seller_id').agg({
        'product_category_name': 'nunique',  # 品类数量
        'product_id': 'nunique'              # SKU数量（确认）
    })
    category_metrics.columns = ['category_count', 'sku_count']
    
    # 6. 计算时间趋势指标
    print("   📅 计算时间趋势指标...")
    
    # 最早和最晚订单时间
    time_metrics = order_details.groupby('seller_id')['order_purchase_timestamp'].agg([
        'min', 'max', 'count'
    ])
    time_metrics.columns = ['first_order_date', 'last_order_date', 'total_orders']
    
    # 计算活跃天数
    time_metrics['active_days'] = (
        time_metrics['last_order_date'] - time_metrics['first_order_date']
    ).dt.days + 1
    
    # 计算订单频率（订单/天）
    time_metrics['order_frequency'] = (
        time_metrics['total_orders'] / time_metrics['active_days']
    ).round(4)
    
    # 7. 合并所有指标
    print("   🔗 合并所有指标...")
    
    # 逐步合并所有指标
    seller_profile = seller_profile.merge(sales_metrics, left_on='seller_id', right_index=True, how='left')
    seller_profile = seller_profile.merge(review_metrics, left_on='seller_id', right_index=True, how='left')
    seller_profile = seller_profile.merge(ops_metrics, left_on='seller_id', right_index=True, how='left')
    seller_profile = seller_profile.merge(category_metrics, left_on='seller_id', right_index=True, how='left')
    seller_profile = seller_profile.merge(time_metrics, left_on='seller_id', right_index=True, how='left')
    
    # 8. 数据清洗和补充
    print("   🧹 数据清洗...")
    
    # 填充缺失值
    numeric_cols = seller_profile.select_dtypes(include=[np.number]).columns
    seller_profile[numeric_cols] = seller_profile[numeric_cols].fillna(0)
    
    # 计算衍生指标
    seller_profile['revenue_per_order'] = seller_profile['total_gmv'] / seller_profile['unique_orders'].replace(0, 1)
    seller_profile['items_per_order'] = seller_profile['total_items'] / seller_profile['unique_orders'].replace(0, 1)
    
    # 标记活跃卖家（有实际订单的）
    seller_profile['is_active'] = (seller_profile['total_gmv'] > 0).astype(int)
    
    print(f"✅ 卖家画像构建完成！")
    print(f"   总卖家数: {len(seller_profile):,}")
    print(f"   活跃卖家数: {seller_profile['is_active'].sum():,}")
    print(f"   指标维度: {len(seller_profile.columns)}")
    
    return seller_profile

def analyze_seller_profile(seller_profile):
    """分析卖家画像数据"""
    print("\n📊 卖家画像数据分析:")
    
    # 基础统计
    active_sellers = seller_profile[seller_profile['is_active'] == 1]
    
    print(f"\n💼 基础指标:")
    print(f"   总卖家数: {len(seller_profile):,}")
    print(f"   活跃卖家数: {len(active_sellers):,} ({len(active_sellers)/len(seller_profile)*100:.1f}%)")
    print(f"   平台总GMV: R$ {active_sellers['total_gmv'].sum():,.2f}")
    print(f"   平台总订单: {active_sellers['unique_orders'].sum():,}")
    
    print(f"\n🏆 Top指标 (活跃卖家):")
    print(f"   GMV中位数: R$ {active_sellers['total_gmv'].median():,.2f}")
    print(f"   平均评分: {active_sellers['avg_review_score'].mean():.2f}")
    print(f"   平均发货天数: {active_sellers['avg_shipping_days'].mean():.1f}")
    print(f"   平均品类数: {active_sellers['category_count'].mean():.1f}")
    
    # Top卖家
    print(f"\n🥇 Top 10 卖家 (按GMV):")
    top_sellers = active_sellers.nlargest(10, 'total_gmv')[
        ['seller_id', 'seller_state', 'total_gmv', 'unique_orders', 'avg_review_score', 'category_count']
    ]
    print(top_sellers.to_string(index=False))
    
    return active_sellers

def main():
    """主函数"""
    print("🚀 开始Olist卖家数据探索与预处理\n")
    
    # 1. 加载数据
    sellers, orders, order_items, reviews, payments, products, category_translation = load_data()
    
    # 2. 构建卖家画像
    seller_profile = build_seller_profile(sellers, orders, order_items, reviews, payments, products, category_translation)
    
    # 3. 分析结果
    active_sellers = analyze_seller_profile(seller_profile)
    
    # 4. 保存结果
    print(f"\n💾 保存结果...")
    seller_profile.to_csv('data/seller_profile_processed.csv', index=False)
    active_sellers.to_csv('data/active_sellers_profile.csv', index=False)
    
    print(f"✅ 文件已保存:")
    print(f"   完整卖家数据: data/seller_profile_processed.csv")
    print(f"   活跃卖家数据: data/active_sellers_profile.csv")
    
    return seller_profile

if __name__ == "__main__":
    seller_profile = main() 