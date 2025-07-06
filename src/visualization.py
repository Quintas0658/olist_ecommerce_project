#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Olist可视化工具模块
生成业务分析图表和可视化报告
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
import os
warnings.filterwarnings('ignore')

# 设置中文字体和样式
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
try:
    plt.style.use('seaborn-v0_8')
except:
    plt.style.use('seaborn')
sns.set_palette("husl")

class ChartGenerator:
    """图表生成器类"""
    
    def __init__(self, output_dir='reports/charts'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def create_data_overview_chart(self, data_dict):
        """创建数据概览图表"""
        print("📈 生成数据概览图表...")
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('🗄️ Olist平台数据概览', fontsize=16, fontweight='bold')
        
        # 数据表规模
        if isinstance(data_dict, dict):
            table_sizes = {name: len(df) for name, df in data_dict.items() if isinstance(df, pd.DataFrame)}
        else:
            table_sizes = {'数据': len(data_dict) if hasattr(data_dict, '__len__') else 0}
        
        if table_sizes:
            axes[0,0].bar(table_sizes.keys(), table_sizes.values(), color='skyblue', alpha=0.8)
            axes[0,0].set_title('📊 数据表记录数量')
            axes[0,0].set_ylabel('记录数')
            axes[0,0].tick_params(axis='x', rotation=45)
        
        # 如果有订单数据，显示状态分布
        if 'orders' in data_dict and 'order_status' in data_dict['orders'].columns:
            order_status = data_dict['orders']['order_status'].value_counts()
            axes[0,1].pie(order_status.values, labels=order_status.index, autopct='%1.1f%%', startangle=90)
            axes[0,1].set_title('🛒 订单状态分布')
        else:
            axes[0,1].text(0.5, 0.5, '暂无订单状态数据', ha='center', va='center', transform=axes[0,1].transAxes)
            axes[0,1].set_title('🛒 订单状态分布')
        
        # 如果有评价数据，显示评分分布
        if 'reviews' in data_dict and 'review_score' in data_dict['reviews'].columns:
            review_scores = data_dict['reviews']['review_score'].value_counts().sort_index()
            axes[1,0].bar(review_scores.index, review_scores.values, color='orange', alpha=0.8)
            axes[1,0].set_title('⭐ 客户评分分布')
            axes[1,0].set_xlabel('评分')
            axes[1,0].set_ylabel('数量')
        else:
            axes[1,0].text(0.5, 0.5, '暂无评分数据', ha='center', va='center', transform=axes[1,0].transAxes)
            axes[1,0].set_title('⭐ 客户评分分布')
        
        # 如果有支付数据，显示支付方式分布
        if 'payments' in data_dict and 'payment_type' in data_dict['payments'].columns:
            payment_types = data_dict['payments']['payment_type'].value_counts()
            axes[1,1].bar(payment_types.index, payment_types.values, color='green', alpha=0.8)
            axes[1,1].set_title('💳 支付方式分布')
            axes[1,1].set_xlabel('支付方式')
            axes[1,1].set_ylabel('数量')
            axes[1,1].tick_params(axis='x', rotation=45)
        else:
            axes[1,1].text(0.5, 0.5, '暂无支付数据', ha='center', va='center', transform=axes[1,1].transAxes)
            axes[1,1].set_title('💳 支付方式分布')
        
        plt.tight_layout()
        output_path = f'{self.output_dir}/01_data_overview.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.show()
        print(f"✅ 保存: {output_path}")
        
    def create_seller_distribution_chart(self, seller_data):
        """创建卖家分布分析图表"""
        print("🏪 生成卖家分布分析...")
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('🏪 卖家分布特征分析', fontsize=16, fontweight='bold')
        
        # 1. 卖家地域分布
        if 'seller_state' in seller_data.columns:
            state_dist = seller_data['seller_state'].value_counts().head(10)
            axes[0,0].bar(state_dist.index, state_dist.values, color='lightcoral')
            axes[0,0].set_title('📍 卖家地域分布 (Top 10)')
            axes[0,0].set_xlabel('州')
            axes[0,0].set_ylabel('卖家数量')
        else:
            axes[0,0].text(0.5, 0.5, '无地域数据', ha='center', va='center', transform=axes[0,0].transAxes)
            axes[0,0].set_title('📍 卖家地域分布')
        
        # 2. GMV分布
        if 'total_gmv' in seller_data.columns:
            gmv_data = seller_data[seller_data['total_gmv'] > 0]['total_gmv']
            if len(gmv_data) > 0:
                axes[0,1].hist(np.log10(gmv_data), bins=50, color='gold', alpha=0.7, edgecolor='black')
                axes[0,1].set_title('💰 GMV分布 (log10)')
                axes[0,1].set_xlabel('log10(GMV)')
                axes[0,1].set_ylabel('卖家数量')
        else:
            axes[0,1].text(0.5, 0.5, '无GMV数据', ha='center', va='center', transform=axes[0,1].transAxes)
            axes[0,1].set_title('💰 GMV分布')
        
        # 3. 订单数分布
        if 'unique_orders' in seller_data.columns:
            order_data = seller_data[seller_data['unique_orders'] > 0]['unique_orders']
            if len(order_data) > 0:
                axes[0,2].hist(order_data, bins=50, color='lightblue', alpha=0.7, edgecolor='black')
                axes[0,2].set_title('📦 订单数分布')
                axes[0,2].set_xlabel('订单数')
                axes[0,2].set_ylabel('卖家数量')
                axes[0,2].set_xlim(0, min(200, order_data.max()))
        else:
            axes[0,2].text(0.5, 0.5, '无订单数据', ha='center', va='center', transform=axes[0,2].transAxes)
            axes[0,2].set_title('📦 订单数分布')
        
        # 4. 评分分布
        if 'avg_review_score' in seller_data.columns:
            rating_data = seller_data[seller_data['avg_review_score'] > 0]['avg_review_score']
            if len(rating_data) > 0:
                axes[1,0].hist(rating_data, bins=30, color='lightgreen', alpha=0.7, edgecolor='black')
                axes[1,0].set_title('⭐ 卖家平均评分分布')
                axes[1,0].set_xlabel('平均评分')
                axes[1,0].set_ylabel('卖家数量')
        else:
            axes[1,0].text(0.5, 0.5, '无评分数据', ha='center', va='center', transform=axes[1,0].transAxes)
            axes[1,0].set_title('⭐ 卖家平均评分分布')
        
        # 5. 品类数分布
        if 'category_count' in seller_data.columns:
            category_data = seller_data['category_count']
            axes[1,1].hist(category_data, bins=range(0, min(15, int(category_data.max()) + 2)), 
                          color='purple', alpha=0.7, edgecolor='black')
            axes[1,1].set_title('🎁 卖家品类数分布')
            axes[1,1].set_xlabel('品类数')
            axes[1,1].set_ylabel('卖家数量')
        else:
            axes[1,1].text(0.5, 0.5, '无品类数据', ha='center', va='center', transform=axes[1,1].transAxes)
            axes[1,1].set_title('🎁 卖家品类数分布')
        
        # 6. 发货天数分布
        if 'avg_shipping_days' in seller_data.columns:
            shipping_data = seller_data[seller_data['avg_shipping_days'] > 0]['avg_shipping_days']
            if len(shipping_data) > 0:
                axes[1,2].hist(shipping_data, bins=30, color='orange', alpha=0.7, edgecolor='black')
                axes[1,2].set_title('🚚 平均发货天数分布')
                axes[1,2].set_xlabel('发货天数')
                axes[1,2].set_ylabel('卖家数量')
                axes[1,2].set_xlim(0, min(20, shipping_data.quantile(0.95)))
        else:
            axes[1,2].text(0.5, 0.5, '无发货数据', ha='center', va='center', transform=axes[1,2].transAxes)
            axes[1,2].set_title('🚚 平均发货天数分布')
        
        plt.tight_layout()
        output_path = f'{self.output_dir}/02_seller_distribution.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.show()
        print(f"✅ 保存: {output_path}")
    
    def create_correlation_heatmap(self, seller_data):
        """创建业务指标相关性热力图"""
        print("📊 生成业务指标相关性分析...")
        
        # 选择关键业务指标
        key_metrics = [
            'total_gmv', 'unique_orders', 'avg_review_score',
            'category_count', 'avg_shipping_days', 'bad_review_rate',
            'revenue_per_order', 'items_per_order'
        ]
        
        # 筛选存在的指标
        available_metrics = [m for m in key_metrics if m in seller_data.columns]
        
        if len(available_metrics) < 2:
            print("⚠️ 可用指标不足，无法生成相关性分析")
            return
        
        correlation_data = seller_data[available_metrics].corr()
        
        plt.figure(figsize=(12, 10))
        mask = np.triu(np.ones_like(correlation_data, dtype=bool))
        sns.heatmap(correlation_data, mask=mask, annot=True, cmap='RdYlBu_r', center=0,
                    square=True, linewidths=0.5, fmt='.2f')
        plt.title('🔥 业务指标相关性热力图', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        output_path = f'{self.output_dir}/03_correlation_heatmap.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.show()
        print(f"✅ 保存: {output_path}")
    
    def create_tier_analysis_chart(self, seller_data_with_tiers):
        """创建卖家分级分析图表"""
        if 'business_tier' not in seller_data_with_tiers.columns:
            print("⚠️ 缺少business_tier字段，无法生成分级分析图表")
            return
            
        print("🏆 生成卖家分级分析图表...")
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('🏆 卖家分级分析', fontsize=16, fontweight='bold')
        
        # 1. 分级分布
        tier_counts = seller_data_with_tiers['business_tier'].value_counts()
        axes[0,0].pie(tier_counts.values, labels=tier_counts.index, autopct='%1.1f%%', startangle=90)
        axes[0,0].set_title('📊 卖家分级分布')
        
        # 2. 各级别GMV分布
        if 'total_gmv' in seller_data_with_tiers.columns:
            tier_gmv = seller_data_with_tiers.groupby('business_tier')['total_gmv'].sum().sort_values(ascending=False)
            axes[0,1].bar(tier_gmv.index, tier_gmv.values, color='gold', alpha=0.8)
            axes[0,1].set_title('💰 各级别GMV贡献')
            axes[0,1].set_ylabel('GMV总和')
            axes[0,1].tick_params(axis='x', rotation=45)
        
        # 3. 各级别平均评分
        if 'avg_review_score' in seller_data_with_tiers.columns:
            tier_rating = seller_data_with_tiers.groupby('business_tier')['avg_review_score'].mean().sort_values(ascending=False)
            axes[1,0].bar(tier_rating.index, tier_rating.values, color='lightgreen', alpha=0.8)
            axes[1,0].set_title('⭐ 各级别平均评分')
            axes[1,0].set_ylabel('平均评分')
            axes[1,0].tick_params(axis='x', rotation=45)
        
        # 4. 各级别平均订单数
        if 'unique_orders' in seller_data_with_tiers.columns:
            tier_orders = seller_data_with_tiers.groupby('business_tier')['unique_orders'].mean().sort_values(ascending=False)
            axes[1,1].bar(tier_orders.index, tier_orders.values, color='lightblue', alpha=0.8)
            axes[1,1].set_title('📦 各级别平均订单数')
            axes[1,1].set_ylabel('平均订单数')
            axes[1,1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        output_path = f'{self.output_dir}/08_seller_segments.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.show()
        print(f"✅ 保存: {output_path}")
    
    def create_interactive_dashboard_chart(self, seller_data):
        """创建交互式Plotly图表"""
        print("📱 生成交互式图表...")
        
        if 'total_gmv' not in seller_data.columns or 'unique_orders' not in seller_data.columns:
            print("⚠️ 缺少必要字段，无法生成交互式图表")
            return None
        
        # 创建散点图：GMV vs 订单数
        fig = px.scatter(
            seller_data,
            x='unique_orders',
            y='total_gmv',
            color='avg_review_score' if 'avg_review_score' in seller_data.columns else None,
            size='category_count' if 'category_count' in seller_data.columns else None,
            hover_data=['seller_id'] if 'seller_id' in seller_data.columns else None,
            title='🎯 卖家业绩分析：GMV vs 订单数',
            labels={
                'unique_orders': '订单数',
                'total_gmv': 'GMV (R$)',
                'avg_review_score': '平均评分',
                'category_count': '品类数'
            }
        )
        
        fig.update_layout(
            width=800,
            height=600,
            showlegend=True
        )
        
        # 保存为HTML
        output_path = f'{self.output_dir}/interactive_analysis.html'
        fig.write_html(output_path)
        print(f"✅ 保存交互式图表: {output_path}")
        
        return fig
    
    def generate_all_charts(self, data_dict, seller_data):
        """生成所有图表"""
        print("🎨 开始生成完整图表集...")
        
        # 1. 数据概览
        self.create_data_overview_chart(data_dict)
        
        # 2. 卖家分布分析
        self.create_seller_distribution_chart(seller_data)
        
        # 3. 相关性分析
        self.create_correlation_heatmap(seller_data)
        
        # 4. 如果有分级数据，生成分级分析
        if 'business_tier' in seller_data.columns:
            self.create_tier_analysis_chart(seller_data)
        
        # 5. 交互式图表
        self.create_interactive_dashboard_chart(seller_data)
        
        print("🎉 所有图表生成完成！")

def main():
    """主函数 - 演示可视化工具使用"""
    # 创建图表生成器
    chart_gen = ChartGenerator()
    
    # 如果有数据，生成示例图表
    try:
        # 尝试加载数据
        seller_data = pd.read_csv('data/seller_profile_processed.csv')
        print("📊 加载卖家数据成功")
        
        # 生成基础图表
        chart_gen.create_seller_distribution_chart(seller_data)
        chart_gen.create_correlation_heatmap(seller_data)
        
    except FileNotFoundError:
        print("⚠️ 未找到数据文件，请先运行数据处理管道")

if __name__ == "__main__":
    main() 