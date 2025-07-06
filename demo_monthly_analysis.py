#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
月度卖家分析演示
展示动态分层和层级流转分析
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from src.monthly_analysis import MonthlySellerAnalyzer
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

def demonstrate_monthly_analysis():
    """演示月度分析功能"""
    print("🎯 Olist月度卖家分析演示")
    print("=" * 50)
    
    # 1. 初始化分析器
    print("\n📊 1. 初始化月度分析器...")
    analyzer = MonthlySellerAnalyzer()
    
    # 2. 获取可用月份
    available_months = analyzer.get_available_months()
    print(f"   📅 数据时间跨度: {available_months[0]} ~ {available_months[-1]}")
    print(f"   📊 总月数: {len(available_months)} 个月")
    
    # 3. 选择分析月份 (取最后6个月)
    analysis_months = available_months[-6:]
    print(f"   🔍 分析时间段: {analysis_months[0]} ~ {analysis_months[-1]}")
    
    # 4. 构建多月份卖家画像
    print("\n📈 2. 构建月度卖家画像...")
    monthly_summaries = []
    
    for month in analysis_months:
        print(f"   正在处理: {month}")
        profile = analyzer.build_monthly_seller_profile(month, lookback_months=2)
        summary = analyzer.get_monthly_summary(month)
        monthly_summaries.append(summary)
        
        # 保存月度数据
        analyzer.save_monthly_analysis(month)
    
    # 5. 生成月度趋势报告
    print("\n📊 3. 月度趋势分析")
    trend_df = pd.DataFrame(monthly_summaries)
    
    print("\n📋 月度关键指标:")
    print(trend_df[['analysis_month', 'active_sellers', 'total_gmv', 'avg_rating']].to_string(index=False))
    
    # 6. 层级流转分析
    print("\n🏆 4. 卖家层级流转分析")
    tier_analysis = analyzer.analyze_tier_changes(analysis_months[-3:])  # 分析最后3个月
    
    print("\n📈 层级流转矩阵 (最近两月):")
    flow_matrix = tier_analysis['tier_flow_matrix']
    print(flow_matrix)
    
    # 7. 层级稳定性分析
    print("\n⚖️ 5. 层级稳定性分析")
    stability = tier_analysis['tier_stability']
    
    stability_df = pd.DataFrame(stability).T
    stability_df['stability_rate'] = stability_df['stability_rate'] * 100
    print("\n📊 各层级稳定性 (稳定率%):")
    print(stability_df[['total_sellers', 'stable_sellers', 'stability_rate']].round(1).to_string())
    
    # 8. 业务洞察
    print("\n💡 6. 关键业务洞察")
    generate_business_insights(trend_df, flow_matrix, stability_df)
    
    # 9. 可视化
    print("\n📊 7. 生成可视化报告...")
    create_monthly_visualizations(trend_df, flow_matrix, analysis_months)
    
    return analyzer, trend_df, tier_analysis

def generate_business_insights(trend_df, flow_matrix, stability_df):
    """生成业务洞察"""
    
    # GMV趋势
    if len(trend_df) >= 2:
        gmv_change = (trend_df.iloc[-1]['total_gmv'] - trend_df.iloc[0]['total_gmv']) / trend_df.iloc[0]['total_gmv'] * 100
        print(f"   📈 GMV变化: {gmv_change:+.1f}% (6个月)")
    
    # 活跃卖家趋势  
    if len(trend_df) >= 2:
        seller_change = (trend_df.iloc[-1]['active_sellers'] - trend_df.iloc[0]['active_sellers']) / trend_df.iloc[0]['active_sellers'] * 100
        print(f"   👥 活跃卖家变化: {seller_change:+.1f}% (6个月)")
    
    # 层级流转洞察
    if not flow_matrix.empty and 'All' in flow_matrix.index:
        total_sellers = flow_matrix.loc['All', 'All']
        print(f"   🔄 月度活跃卖家: {total_sellers:,} 个")
        
        # 升级和降级分析
        upgrade_count = 0
        downgrade_count = 0
        
        tier_order = ['Basic', 'Bronze', 'Silver', 'Gold', 'Platinum']
        for i, tier_from in enumerate(tier_order):
            if tier_from not in flow_matrix.index:
                continue
            for j, tier_to in enumerate(tier_order):
                if tier_to not in flow_matrix.columns:
                    continue
                count = flow_matrix.loc[tier_from, tier_to]
                if i < j:  # 升级
                    upgrade_count += count
                elif i > j:  # 降级
                    downgrade_count += count
        
        print(f"   ⬆️ 升级卖家: {upgrade_count:,} 个")
        print(f"   ⬇️ 降级卖家: {downgrade_count:,} 个")
        print(f"   ⚖️ 升降级比: {upgrade_count/max(downgrade_count, 1):.2f}")
    
    # 稳定性洞察
    if not stability_df.empty:
        avg_stability = stability_df['stability_rate'].mean()
        print(f"   🎯 平均层级稳定率: {avg_stability:.1f}%")
        
        most_stable = stability_df['stability_rate'].idxmax()
        least_stable = stability_df['stability_rate'].idxmin()
        print(f"   🔒 最稳定层级: {most_stable} ({stability_df.loc[most_stable, 'stability_rate']:.1f}%)")
        print(f"   🌊 最不稳定层级: {least_stable} ({stability_df.loc[least_stable, 'stability_rate']:.1f}%)")

def create_monthly_visualizations(trend_df, flow_matrix, analysis_months):
    """创建月度分析可视化"""
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('📊 月度卖家分析报告', fontsize=16, fontweight='bold')
    
    # 1. GMV趋势
    axes[0,0].plot(trend_df['analysis_month'], trend_df['total_gmv'] / 1e6, marker='o', linewidth=2)
    axes[0,0].set_title('💰 月度GMV趋势 (百万雷亚尔)')
    axes[0,0].set_xlabel('月份')
    axes[0,0].set_ylabel('GMV (M R$)')
    axes[0,0].tick_params(axis='x', rotation=45)
    axes[0,0].grid(True, alpha=0.3)
    
    # 2. 活跃卖家趋势
    axes[0,1].plot(trend_df['analysis_month'], trend_df['active_sellers'], marker='s', linewidth=2, color='orange')
    axes[0,1].set_title('👥 活跃卖家数趋势')
    axes[0,1].set_xlabel('月份')
    axes[0,1].set_ylabel('活跃卖家数')
    axes[0,1].tick_params(axis='x', rotation=45)
    axes[0,1].grid(True, alpha=0.3)
    
    # 3. 平均评分趋势
    axes[1,0].plot(trend_df['analysis_month'], trend_df['avg_rating'], marker='^', linewidth=2, color='green')
    axes[1,0].set_title('⭐ 平均评分趋势')
    axes[1,0].set_xlabel('月份')
    axes[1,0].set_ylabel('平均评分')
    axes[1,0].tick_params(axis='x', rotation=45)
    axes[1,0].grid(True, alpha=0.3)
    axes[1,0].set_ylim(3.5, 5.0)
    
    # 4. 层级流转热力图
    if not flow_matrix.empty:
        # 移除总计行列
        flow_for_viz = flow_matrix.drop('All', axis=0).drop('All', axis=1)
        if not flow_for_viz.empty:
            sns.heatmap(flow_for_viz, annot=True, fmt='d', cmap='Blues', ax=axes[1,1])
            axes[1,1].set_title('🔄 层级流转热力图')
            axes[1,1].set_xlabel('目标层级')
            axes[1,1].set_ylabel('原始层级')
    
    plt.tight_layout()
    plt.savefig('monthly_analysis_report.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("✅ 可视化报告已保存为: monthly_analysis_report.png")

def demonstrate_seller_lifecycle():
    """演示卖家生命周期管理"""
    print("\n🔄 卖家生命周期管理演示")
    print("=" * 30)
    
    analyzer = MonthlySellerAnalyzer()
    
    # 分析最近3个月
    available_months = analyzer.get_available_months()
    recent_months = available_months[-3:]
    
    print(f"📅 分析时间段: {recent_months}")
    
    # 构建多月数据
    tier_analysis = analyzer.analyze_tier_changes(recent_months)
    monthly_data = tier_analysis['monthly_data']
    
    if monthly_data.empty:
        print("⚠️ 没有足够的数据进行生命周期分析")
        return
    
    # 找出有趣的卖家案例
    print("\n🎯 卖家生命周期案例:")
    
    # 1. 持续升级的卖家
    print("\n⬆️ 持续升级的卖家:")
    upgrade_sellers = find_upgrading_sellers(monthly_data, recent_months)
    if len(upgrade_sellers) > 0:
        print(upgrade_sellers.head().to_string(index=False))
    else:
        print("   未发现显著升级的卖家")
    
    # 2. 持续降级的卖家
    print("\n⬇️ 需要关注的降级卖家:")
    downgrade_sellers = find_downgrading_sellers(monthly_data, recent_months)
    if len(downgrade_sellers) > 0:
        print(downgrade_sellers.head().to_string(index=False))
    else:
        print("   未发现显著降级的卖家")
    
    # 3. 波动较大的卖家
    print("\n🌊 表现波动较大的卖家:")
    volatile_sellers = find_volatile_sellers(monthly_data, recent_months)
    if len(volatile_sellers) > 0:
        print(volatile_sellers.head().to_string(index=False))

def find_upgrading_sellers(monthly_data, months):
    """找出持续升级的卖家"""
    tier_order = {'Basic': 0, 'Bronze': 1, 'Silver': 2, 'Gold': 3, 'Platinum': 4}
    
    # 转换为透视表
    pivot_df = monthly_data.pivot(index='seller_id', columns='month', values='business_tier')
    
    # 计算数值化层级
    for col in pivot_df.columns:
        pivot_df[f'{col}_num'] = pivot_df[col].map(tier_order)
    
    # 找出升级的卖家
    upgrade_sellers = []
    for idx, row in pivot_df.iterrows():
        tier_values = [row[f'{month}_num'] for month in months if pd.notna(row[f'{month}_num'])]
        if len(tier_values) >= 2 and tier_values[-1] > tier_values[0]:
            upgrade_sellers.append({
                'seller_id': idx,
                'from_tier': row[months[0]], 
                'to_tier': row[months[-1]],
                'upgrade_level': tier_values[-1] - tier_values[0]
            })
    
    return pd.DataFrame(upgrade_sellers).sort_values('upgrade_level', ascending=False)

def find_downgrading_sellers(monthly_data, months):
    """找出持续降级的卖家"""
    tier_order = {'Basic': 0, 'Bronze': 1, 'Silver': 2, 'Gold': 3, 'Platinum': 4}
    
    pivot_df = monthly_data.pivot(index='seller_id', columns='month', values='business_tier')
    
    for col in pivot_df.columns:
        pivot_df[f'{col}_num'] = pivot_df[col].map(tier_order)
    
    downgrade_sellers = []
    for idx, row in pivot_df.iterrows():
        tier_values = [row[f'{month}_num'] for month in months if pd.notna(row[f'{month}_num'])]
        if len(tier_values) >= 2 and tier_values[-1] < tier_values[0]:
            downgrade_sellers.append({
                'seller_id': idx,
                'from_tier': row[months[0]],
                'to_tier': row[months[-1]], 
                'downgrade_level': tier_values[0] - tier_values[-1]
            })
    
    return pd.DataFrame(downgrade_sellers).sort_values('downgrade_level', ascending=False)

def find_volatile_sellers(monthly_data, months):
    """找出表现波动较大的卖家"""
    tier_order = {'Basic': 0, 'Bronze': 1, 'Silver': 2, 'Gold': 3, 'Platinum': 4}
    
    pivot_df = monthly_data.pivot(index='seller_id', columns='month', values='business_tier')
    
    for col in pivot_df.columns:
        pivot_df[f'{col}_num'] = pivot_df[col].map(tier_order)
    
    volatile_sellers = []
    for idx, row in pivot_df.iterrows():
        tier_values = [row[f'{month}_num'] for month in months if pd.notna(row[f'{month}_num'])]
        if len(tier_values) >= 3:
            volatility = np.std(tier_values)
            if volatility > 0.5:  # 标准差大于0.5表示波动较大
                volatile_sellers.append({
                    'seller_id': idx,
                    'tier_volatility': volatility,
                    'tier_range': f"{row[months[0]]} → {row[months[1]]} → {row[months[2]]}"
                })
    
    return pd.DataFrame(volatile_sellers).sort_values('tier_volatility', ascending=False)

if __name__ == "__main__":
    # 运行完整演示
    analyzer, trend_df, tier_analysis = demonstrate_monthly_analysis()
    
    # 运行生命周期管理演示
    demonstrate_seller_lifecycle()
    
    print("\n🎉 月度分析演示完成！")
    print("\n📋 生成的文件:")
    print("   - monthly_analysis_report.png (可视化报告)")
    print("   - data/monthly_seller_profile_*.csv (月度数据)")
    print("\n💡 下一步建议:")
    print("   1. 将月度分析集成到现有dashboard")
    print("   2. 设置自动化月度报告")
    print("   3. 建立卖家生命周期预警机制") 