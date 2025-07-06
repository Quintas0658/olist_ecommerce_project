#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Olist卖家商业分析与分级
基于真实数据进行商业洞察挖掘
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def load_seller_data():
    """加载卖家数据"""
    print("📊 正在加载卖家画像数据...")
    df = pd.read_csv('data/seller_profile_processed.csv')
    print(f"✅ 加载完成: {len(df):,} 个卖家，{df.shape[1]} 个指标")
    return df

def create_seller_segments(df):
    """创建卖家分级体系"""
    print("\n🎯 构建卖家分级体系...")
    
    # 1. 基于业务规则的分级
    print("   📊 业务规则分级...")
    
    def classify_seller(row):
        gmv = row['total_gmv']
        orders = row['unique_orders'] 
        rating = row['avg_review_score']
        
        # 白金卖家：GMV高 + 订单多 + 评分好
        if gmv >= 50000 and orders >= 200 and rating >= 4.0:
            return 'Platinum'
        # 黄金卖家：GMV较高 + 订单较多
        elif gmv >= 10000 and orders >= 50:
            return 'Gold'
        # 银卖家：中等表现
        elif gmv >= 2000 and orders >= 10:
            return 'Silver'
        # 铜卖家：基础表现
        elif gmv >= 500 and orders >= 3:
            return 'Bronze'
        # 基础卖家
        else:
            return 'Basic'
    
    df['business_tier'] = df.apply(classify_seller, axis=1)
    
    # 2. 基于数据驱动的聚类分级
    print("   🤖 数据驱动聚类分级...")
    
    # 选择关键指标进行聚类
    clustering_features = [
        'total_gmv', 'unique_orders', 'avg_review_score', 
        'category_count', 'avg_shipping_days', 'delivery_success_rate'
    ]
    
    # 数据标准化
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[clustering_features].fillna(0))
    
    # K-means聚类
    kmeans = KMeans(n_clusters=5, random_state=42)
    df['cluster_tier'] = kmeans.fit_predict(X_scaled)
    
    # 根据聚类中心排序，映射到等级
    cluster_centers = pd.DataFrame(kmeans.cluster_centers_, columns=clustering_features)
    cluster_centers['gmv_score'] = cluster_centers['total_gmv']
    cluster_order = cluster_centers.sort_values('gmv_score', ascending=False).index
    
    tier_mapping = {
        cluster_order[0]: 'Platinum',
        cluster_order[1]: 'Gold', 
        cluster_order[2]: 'Silver',
        cluster_order[3]: 'Bronze',
        cluster_order[4]: 'Basic'
    }
    
    df['cluster_tier_name'] = df['cluster_tier'].map(tier_mapping)
    
    print("✅ 卖家分级完成")
    return df

def analyze_seller_segments(df):
    """分析卖家分层结果"""
    print("\n📈 卖家分层分析:")
    
    # 1. 业务规则分级分析
    print("\n🏆 业务规则分级分布:")
    business_summary = df.groupby('business_tier').agg({
        'seller_id': 'count',
        'total_gmv': ['sum', 'mean', 'median'],
        'unique_orders': ['sum', 'mean'],
        'avg_review_score': 'mean',
        'category_count': 'mean'
    }).round(2)
    
    business_summary.columns = ['卖家数量', 'GMV总和', 'GMV均值', 'GMV中位数', 
                               '订单总数', '订单均值', '平均评分', '平均品类数']
    
    # 计算占比
    total_sellers = len(df)
    total_gmv = df['total_gmv'].sum()
    
    business_summary['卖家占比%'] = (business_summary['卖家数量'] / total_sellers * 100).round(1)
    business_summary['GMV占比%'] = (business_summary['GMV总和'] / total_gmv * 100).round(1)
    
    print(business_summary.to_string())
    
    # 2. 关键洞察
    print(f"\n💡 关键洞察:")
    
    # 帕累托分析
    df_sorted = df.sort_values('total_gmv', ascending=False)
    top_20_pct = int(len(df) * 0.2)
    top_20_gmv = df_sorted.head(top_20_pct)['total_gmv'].sum()
    pareto_ratio = top_20_gmv / total_gmv * 100
    
    print(f"   📊 帕累托法则: Top 20%卖家贡献 {pareto_ratio:.1f}% 的GMV")
    
    # 各等级表现
    platinum_sellers = df[df['business_tier'] == 'Platinum']
    gold_sellers = df[df['business_tier'] == 'Gold']
    
    print(f"   🥇 白金卖家: {len(platinum_sellers)} 个 ({len(platinum_sellers)/total_sellers*100:.1f}%)")
    print(f"      - 平均GMV: R$ {platinum_sellers['total_gmv'].mean():,.0f}")
    print(f"      - 平均评分: {platinum_sellers['avg_review_score'].mean():.2f}")
    
    print(f"   🥈 黄金卖家: {len(gold_sellers)} 个 ({len(gold_sellers)/total_sellers*100:.1f}%)")
    print(f"      - 平均GMV: R$ {gold_sellers['total_gmv'].mean():,.0f}")
    print(f"      - 平均评分: {gold_sellers['avg_review_score'].mean():.2f}")
    
    return business_summary

def identify_business_opportunities(df):
    """识别商业机会"""
    print("\n🚀 商业机会识别:")
    
    # 1. 高潜力低表现卖家
    print("\n🎯 机会1: 高潜力低表现卖家")
    
    # 定义潜力指标：评分高但GMV低
    high_potential = df[
        (df['avg_review_score'] >= 4.2) & 
        (df['total_gmv'] < df['total_gmv'].quantile(0.5)) &
        (df['unique_orders'] >= 5)
    ].sort_values('avg_review_score', ascending=False)
    
    print(f"   发现 {len(high_potential)} 个高潜力卖家:")
    print(f"   - 平均评分: {high_potential['avg_review_score'].mean():.2f}")
    print(f"   - 平均GMV: R$ {high_potential['total_gmv'].mean():,.0f}")
    print(f"   - 提升潜力: 如果达到中位数GMV，可增加 R$ {(df['total_gmv'].median() - high_potential['total_gmv'].mean()) * len(high_potential):,.0f}")
    
    # 2. 地域扩张机会
    print("\n🗺️ 机会2: 地域扩张机会")
    
    geo_analysis = df.groupby('seller_state').agg({
        'seller_id': 'count',
        'total_gmv': ['sum', 'mean'],
        'avg_review_score': 'mean'
    }).round(2)
    
    geo_analysis.columns = ['卖家数量', 'GMV总和', 'GMV人均', '平均评分']
    geo_analysis['GMV密度'] = geo_analysis['GMV总和'] / geo_analysis['卖家数量']
    geo_analysis = geo_analysis.sort_values('GMV总和', ascending=False)
    
    print("   Top 5 州份GMV表现:")
    print(geo_analysis.head().to_string())
    
    # 3. 品类机会分析
    print("\n📦 机会3: 品类扩张机会")
    
    # 多品类vs单品类卖家对比
    single_category = df[df['category_count'] == 1]
    multi_category = df[df['category_count'] > 1]
    
    print(f"   单品类卖家 ({len(single_category)}个):")
    print(f"   - 平均GMV: R$ {single_category['total_gmv'].mean():,.0f}")
    print(f"   - 平均订单: {single_category['unique_orders'].mean():.1f}")
    
    print(f"   多品类卖家 ({len(multi_category)}个):")
    print(f"   - 平均GMV: R$ {multi_category['total_gmv'].mean():,.0f}")
    print(f"   - 平均订单: {multi_category['unique_orders'].mean():.1f}")
    
    gmv_uplift = multi_category['total_gmv'].mean() / single_category['total_gmv'].mean()
    print(f"   💰 多品类GMV提升倍数: {gmv_uplift:.1f}x")
    
    return high_potential, geo_analysis

def operational_insights(df):
    """运营洞察分析"""
    print("\n⚙️ 运营洞察分析:")
    
    # 1. 发货效率分析
    print("\n🚚 发货效率影响分析:")
    
    # 按发货速度分组
    df['shipping_speed'] = pd.cut(df['avg_shipping_days'], 
                                 bins=[0, 1, 3, 7, float('inf')], 
                                 labels=['极快(≤1天)', '快速(1-3天)', '一般(3-7天)', '慢速(>7天)'])
    
    shipping_analysis = df.groupby('shipping_speed').agg({
        'seller_id': 'count',
        'avg_review_score': 'mean',
        'total_gmv': 'mean',
        'bad_review_rate': 'mean'
    }).round(2)
    
    print(shipping_analysis.to_string())
    
    # 2. 评分与GMV关系
    print("\n⭐ 客户满意度影响分析:")
    
    df['rating_group'] = pd.cut(df['avg_review_score'], 
                               bins=[0, 3.5, 4.0, 4.5, 5.0], 
                               labels=['低评分(<3.5)', '中评分(3.5-4.0)', '高评分(4.0-4.5)', '优秀(4.5-5.0)'])
    
    rating_analysis = df.groupby('rating_group').agg({
        'seller_id': 'count',
        'total_gmv': 'mean',
        'unique_orders': 'mean',
        'bad_review_rate': 'mean'
    }).round(2)
    
    print(rating_analysis.to_string())
    
    # 3. 风险卖家识别
    print("\n⚠️ 风险卖家识别:")
    
    risk_sellers = df[
        (df['avg_review_score'] < 3.5) | 
        (df['bad_review_rate'] > 10) | 
        (df['avg_shipping_days'] > 7)
    ]
    
    print(f"   风险卖家数量: {len(risk_sellers)} ({len(risk_sellers)/len(df)*100:.1f}%)")
    print(f"   风险GMV占比: {risk_sellers['total_gmv'].sum()/df['total_gmv'].sum()*100:.1f}%")
    
    return shipping_analysis, rating_analysis, risk_sellers

def create_action_plan(df, high_potential, risk_sellers):
    """制定行动计划"""
    print("\n📋 战略行动计划:")
    
    total_gmv = df['total_gmv'].sum()
    
    # 1. 白金卖家VIP计划
    platinum = df[df['business_tier'] == 'Platinum']
    print(f"\n🥇 白金卖家VIP计划 ({len(platinum)}个卖家):")
    print(f"   - 当前贡献: R$ {platinum['total_gmv'].sum():,.0f} ({platinum['total_gmv'].sum()/total_gmv*100:.1f}%)")
    print(f"   - 专属客户经理、优先技术支持")
    print(f"   - 新品类扩展支持、营销资源倾斜")
    print(f"   - 预期GMV增长: 15-20%")
    
    # 2. 黄金卖家成长计划
    gold = df[df['business_tier'] == 'Gold']
    print(f"\n🥈 黄金卖家成长计划 ({len(gold)}个卖家):")
    print(f"   - 当前贡献: R$ {gold['total_gmv'].sum():,.0f} ({gold['total_gmv'].sum()/total_gmv*100:.1f}%)")
    print(f"   - 品类扩展建议、运营效率提升")
    print(f"   - 数据分析报告、培训资源")
    print(f"   - 预期GMV增长: 25-30%")
    
    # 3. 潜力卖家孵化计划
    print(f"\n🚀 潜力卖家孵化计划 ({len(high_potential)}个卖家):")
    print(f"   - 当前GMV: R$ {high_potential['total_gmv'].sum():,.0f}")
    print(f"   - 定向培训、流量扶持")
    print(f"   - 品类推荐、供应链优化")
    median_gmv = df['total_gmv'].median()
    potential_increase = (median_gmv - high_potential['total_gmv'].mean()) * len(high_potential)
    print(f"   - 预期GMV增长: R$ {potential_increase:,.0f}")
    
    # 4. 风险卖家改进计划
    print(f"\n⚠️ 风险卖家改进计划 ({len(risk_sellers)}个卖家):")
    print(f"   - 风险GMV: R$ {risk_sellers['total_gmv'].sum():,.0f}")
    print(f"   - 客服培训、物流优化")
    print(f"   - 6个月改进期，不达标考虑清退")
    
    # 5. 总体预期
    print(f"\n🎯 总体预期效果:")
    expected_growth = (
        platinum['total_gmv'].sum() * 0.175 +  # 白金增长17.5%
        gold['total_gmv'].sum() * 0.275 +      # 黄金增长27.5%
        potential_increase                      # 潜力卖家增长
    )
    print(f"   - 预期GMV增长: R$ {expected_growth:,.0f}")
    print(f"   - 增长率: {expected_growth/total_gmv*100:.1f}%")
    print(f"   - 投资回报率: 预计300-500%")

def main():
    """主函数"""
    print("🎯 开始Olist卖家商业分析\n")
    
    # 1. 加载数据
    df = load_seller_data()
    
    # 2. 创建分级体系
    df = create_seller_segments(df)
    
    # 3. 分层分析
    business_summary = analyze_seller_segments(df)
    
    # 4. 识别商业机会
    high_potential, geo_analysis = identify_business_opportunities(df)
    
    # 5. 运营洞察
    shipping_analysis, rating_analysis, risk_sellers = operational_insights(df)
    
    # 6. 制定行动计划
    create_action_plan(df, high_potential, risk_sellers)
    
    # 7. 保存分析结果
    print(f"\n💾 保存分析结果...")
    df.to_csv('data/seller_analysis_results.csv', index=False)
    business_summary.to_csv('data/business_tier_summary.csv')
    high_potential.to_csv('data/high_potential_sellers.csv', index=False)
    
    print(f"✅ 分析完成！文件已保存到data/目录")
    
    return df, business_summary, high_potential

if __name__ == "__main__":
    df, summary, potential = main() 