#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Olist业务分析模块
卖家分级、商业洞察与策略建议
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings('ignore')

class BusinessAnalyzer:
    """业务分析器类"""
    
    def __init__(self, seller_data=None):
        self.seller_data = seller_data
        self.business_tiers = None
        self.cluster_analysis = None
        self.opportunities = None
        
    def load_seller_data(self, filepath='data/seller_profile_processed.csv'):
        """加载卖家数据"""
        print("📊 正在加载卖家画像数据...")
        self.seller_data = pd.read_csv(filepath)
        print(f"✅ 加载完成: {len(self.seller_data):,} 个卖家，{self.seller_data.shape[1]} 个指标")
        return self.seller_data
    
    def create_business_tiers(self):
        """创建业务分级体系"""
        if self.seller_data is None:
            raise ValueError("请先加载卖家数据")
            
        print("\n🎯 构建卖家分级体系...")
        df = self.seller_data.copy()
        
        # 1. 基于业务规则的分级
        print("   📊 业务规则分级...")
        df['business_tier'] = df.apply(self._classify_seller_by_rules, axis=1)
        
        # 2. 基于数据驱动的聚类分级
        print("   🤖 数据驱动聚类分级...")
        cluster_tiers = self._create_cluster_tiers(df)
        df['cluster_tier'] = cluster_tiers
        
        self.business_tiers = df
        print("✅ 卖家分级完成")
        return df
    
    def _classify_seller_by_rules(self, row):
        """基于业务规则的卖家分级"""
        gmv = row.get('total_gmv', 0)
        orders = row.get('unique_orders', 0)
        rating = row.get('avg_review_score', 0)
        
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
    
    def _create_cluster_tiers(self, df):
        """基于聚类的卖家分级"""
        # 选择关键指标进行聚类
        clustering_features = [
            'total_gmv', 'unique_orders', 'avg_review_score',
            'category_count', 'avg_shipping_days', 'delivery_success_rate'
        ]
        
        # 确保所有特征都存在
        available_features = [f for f in clustering_features if f in df.columns]
        
        # 数据标准化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(df[available_features].fillna(0))
        
        # K-means聚类
        kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(X_scaled)
        
        # 根据聚类中心排序，映射到等级
        cluster_centers = pd.DataFrame(kmeans.cluster_centers_, columns=available_features)
        cluster_centers['gmv_score'] = cluster_centers.get('total_gmv', 0)
        cluster_order = cluster_centers.sort_values('gmv_score', ascending=False).index
        
        tier_mapping = {
            cluster_order[0]: 'Platinum',
            cluster_order[1]: 'Gold',
            cluster_order[2]: 'Silver',
            cluster_order[3]: 'Bronze',
            cluster_order[4]: 'Basic'
        }
        
        return pd.Series(cluster_labels).map(tier_mapping)
    
    def analyze_business_segments(self):
        """分析业务分层结果"""
        if self.business_tiers is None:
            self.create_business_tiers()
            
        print("\n📈 卖家分层分析:")
        df = self.business_tiers
        
        # 业务规则分级分析
        print("\n🏆 业务规则分级分布:")
        summary = self._create_tier_summary(df, 'business_tier')
        print(summary.to_string())
        
        # 关键洞察
        self._generate_business_insights(df)
        
        return summary
    
    def _create_tier_summary(self, df, tier_column):
        """创建分级汇总表"""
        summary = df.groupby(tier_column).agg({
            'seller_id': 'count',
            'total_gmv': ['sum', 'mean', 'median'],
            'unique_orders': ['sum', 'mean'],
            'avg_review_score': 'mean',
            'category_count': 'mean'
        }).round(2)
        
        summary.columns = ['卖家数量', 'GMV总和', 'GMV均值', 'GMV中位数',
                          '订单总数', '订单均值', '平均评分', '平均品类数']
        
        # 计算占比
        total_sellers = len(df)
        total_gmv = df['total_gmv'].sum()
        
        summary['卖家占比%'] = (summary['卖家数量'] / total_sellers * 100).round(1)
        summary['GMV占比%'] = (summary['GMV总和'] / total_gmv * 100).round(1)
        
        return summary
    
    def _generate_business_insights(self, df):
        """生成关键业务洞察"""
        print(f"\n💡 关键洞察:")
        
        total_sellers = len(df)
        total_gmv = df['total_gmv'].sum()
        
        # 帕累托分析
        df_sorted = df.sort_values('total_gmv', ascending=False)
        top_20_pct = int(len(df) * 0.2)
        top_20_gmv = df_sorted.head(top_20_pct)['total_gmv'].sum()
        pareto_ratio = top_20_gmv / total_gmv * 100
        
        print(f"   📊 帕累托法则: Top 20%卖家贡献 {pareto_ratio:.1f}% 的GMV")
        
        # 各等级表现
        for tier in ['Platinum', 'Gold']:
            tier_sellers = df[df['business_tier'] == tier]
            if len(tier_sellers) > 0:
                print(f"   🏅 {tier}卖家: {len(tier_sellers)} 个 ({len(tier_sellers)/total_sellers*100:.1f}%)")
                print(f"      - 平均GMV: R$ {tier_sellers['total_gmv'].mean():,.0f}")
                print(f"      - 平均评分: {tier_sellers['avg_review_score'].mean():.2f}")
    
    def identify_business_opportunities(self):
        """识别商业机会"""
        if self.business_tiers is None:
            self.create_business_tiers()
            
        print("\n🚀 商业机会识别:")
        df = self.business_tiers
        
        # 1. 高潜力低表现卖家
        high_potential = self._find_high_potential_sellers(df)
        
        # 2. 地域扩张机会
        geo_analysis = self._analyze_geographic_opportunities(df)
        
        # 3. 品类扩张机会
        category_analysis = self._analyze_category_opportunities(df)
        
        self.opportunities = {
            'high_potential_sellers': high_potential,
            'geographic_opportunities': geo_analysis,
            'category_opportunities': category_analysis
        }
        
        return self.opportunities
    
    def _find_high_potential_sellers(self, df):
        """寻找高潜力卖家"""
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
        
        if len(high_potential) > 0:
            potential_gmv = (df['total_gmv'].median() - high_potential['total_gmv'].mean()) * len(high_potential)
            print(f"   - 提升潜力: 如果达到中位数GMV，可增加 R$ {potential_gmv:,.0f}")
        
        return high_potential
    
    def _analyze_geographic_opportunities(self, df):
        """分析地域机会"""
        print("\n🗺️ 机会2: 地域扩张机会")
        
        if 'seller_state' not in df.columns:
            print("   缺少地域数据")
            return pd.DataFrame()
            
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
        
        return geo_analysis
    
    def _analyze_category_opportunities(self, df):
        """分析品类机会"""
        print("\n📦 机会3: 品类扩张机会")
        
        if 'category_count' not in df.columns:
            print("   缺少品类数据")
            return {}
            
        # 多品类vs单品类卖家对比
        single_category = df[df['category_count'] == 1]
        multi_category = df[df['category_count'] > 1]
        
        print(f"   单品类卖家 ({len(single_category)}个):")
        print(f"   - 平均GMV: R$ {single_category['total_gmv'].mean():,.0f}")
        print(f"   - 平均订单: {single_category['unique_orders'].mean():.1f}")
        
        print(f"   多品类卖家 ({len(multi_category)}个):")
        print(f"   - 平均GMV: R$ {multi_category['total_gmv'].mean():,.0f}")
        print(f"   - 平均订单: {multi_category['unique_orders'].mean():.1f}")
        
        if len(multi_category) > 0 and len(single_category) > 0:
            gmv_uplift = multi_category['total_gmv'].mean() / single_category['total_gmv'].mean()
            print(f"   💰 多品类GMV提升倍数: {gmv_uplift:.1f}x")
        
        return {
            'single_category_performance': single_category[['total_gmv', 'unique_orders']].mean(),
            'multi_category_performance': multi_category[['total_gmv', 'unique_orders']].mean()
        }
    
    def create_action_plan(self):
        """创建行动计划"""
        if self.opportunities is None:
            self.identify_business_opportunities()
            
        print("\n📋 战略行动计划:")
        
        # 针对高潜力卖家的策略
        high_potential = self.opportunities.get('high_potential_sellers', pd.DataFrame())
        if len(high_potential) > 0:
            print(f"\n🎯 策略1: 高潜力卖家扶持计划")
            print(f"   目标群体: {len(high_potential)} 个高评分低GMV卖家")
            print(f"   建议措施:")
            print(f"   - 提供营销支持，提升曝光度")
            print(f"   - 开展品类扩张培训")
            print(f"   - 优化运营效率指导")
        
        # 地域发展策略
        geo_opportunities = self.opportunities.get('geographic_opportunities', pd.DataFrame())
        if len(geo_opportunities) > 0:
            print(f"\n🗺️ 策略2: 地域发展计划")
            print(f"   重点发展区域: {geo_opportunities.head(3).index.tolist()}")
            print(f"   建议措施:")
            print(f"   - 加强重点州份的卖家招募")
            print(f"   - 提供本地化运营支持")
        
        # 品类扩张策略
        print(f"\n📦 策略3: 品类扩张计划")
        print(f"   建议措施:")
        print(f"   - 鼓励单品类卖家扩展产品线")
        print(f"   - 提供跨品类运营培训")
        print(f"   - 数据驱动的品类推荐")
    
    def get_performance_metrics(self):
        """获取关键绩效指标"""
        if self.business_tiers is None:
            return {}
            
        df = self.business_tiers
        active_sellers = df[df.get('is_active', 1) == 1]
        
        metrics = {
            'total_sellers': len(df),
            'active_sellers': len(active_sellers),
            'total_gmv': active_sellers['total_gmv'].sum(),
            'avg_gmv_per_seller': active_sellers['total_gmv'].mean(),
            'total_orders': active_sellers['unique_orders'].sum(),
            'avg_rating': active_sellers['avg_review_score'].mean(),
            'tier_distribution': df['business_tier'].value_counts().to_dict()
        }
        
        return metrics

def main():
    """主函数 - 演示业务分析使用"""
    # 初始化分析器
    analyzer = BusinessAnalyzer()
    
    # 加载数据
    analyzer.load_seller_data()
    
    # 创建业务分级
    analyzer.create_business_tiers()
    
    # 分析业务分层
    analyzer.analyze_business_segments()
    
    # 识别商业机会
    analyzer.identify_business_opportunities()
    
    # 创建行动计划
    analyzer.create_action_plan()
    
    # 获取关键指标
    metrics = analyzer.get_performance_metrics()
    print(f"\n📊 关键绩效指标:")
    print(f"   总卖家数: {metrics['total_sellers']:,}")
    print(f"   活跃卖家数: {metrics['active_sellers']:,}")
    print(f"   平台总GMV: R$ {metrics['total_gmv']:,.2f}")
    print(f"   平均评分: {metrics['avg_rating']:.2f}")

if __name__ == "__main__":
    main() 