#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示新的同比环比和轨迹分析功能
"""

from src.data_pipeline import DataPipeline
from src.monthly_analysis import MonthlySellerAnalyzer

def test_comparison_analysis():
    """测试同比环比分析"""
    print("🚀 测试同比环比分析功能...")
    
    # 初始化
    data_pipeline = DataPipeline()
    analyzer = MonthlySellerAnalyzer(data_pipeline)
    
    # 获取可用月份
    available_months = analyzer.get_available_months()
    print(f"📅 可用月份: {available_months}")
    
    if len(available_months) >= 2:
        # 测试最新月份的同比环比
        target_month = available_months[-1]  # 2018-10
        print(f"\n🎯 分析目标月份: {target_month}")
        
        # 执行同比环比分析
        comparison_result = analyzer.analyze_period_comparison(target_month)
        
        if comparison_result:
            print("\n📊 分析结果摘要:")
            
            # 环比结果
            if comparison_result.get('mom_comparison'):
                mom = comparison_result['mom_comparison']['summary_stats']
                print(f"📈 环比分析 ({comparison_result['mom_comparison']['month1']} vs {comparison_result['mom_comparison']['month2']}):")
                print(f"   - 共同卖家: {mom['total_sellers']:,}")
                print(f"   - 升级卖家: {mom['upgraded_count']:,} ({mom['upgrade_rate']:.1f}%)")
                print(f"   - 降级卖家: {mom['downgraded_count']:,} ({mom['downgrade_rate']:.1f}%)")
                print(f"   - 稳定卖家: {mom['stable_count']:,} ({mom['stability_rate']:.1f}%)")
            
            # 同比结果
            if comparison_result.get('yoy_comparison'):
                yoy = comparison_result['yoy_comparison']['summary_stats']
                print(f"📅 同比分析 ({comparison_result['yoy_comparison']['month1']} vs {comparison_result['yoy_comparison']['month2']}):")
                print(f"   - 共同卖家: {yoy['total_sellers']:,}")
                print(f"   - 升级卖家: {yoy['upgraded_count']:,} ({yoy['upgrade_rate']:.1f}%)")
                print(f"   - 降级卖家: {yoy['downgraded_count']:,} ({yoy['downgrade_rate']:.1f}%)")
                print(f"   - 稳定卖家: {yoy['stable_count']:,} ({yoy['stability_rate']:.1f}%)")


def test_trajectory_analysis():
    """测试轨迹分析"""
    print("\n🛤️ 测试卖家轨迹分析功能...")
    
    # 初始化
    data_pipeline = DataPipeline()
    analyzer = MonthlySellerAnalyzer(data_pipeline)
    
    # 获取可用月份
    available_months = analyzer.get_available_months()
    
    if len(available_months) >= 3:
        # 分析最近3个月的轨迹
        analysis_months = available_months[-3:]
        print(f"📊 分析月份: {analysis_months}")
        
        # 执行轨迹分析
        trajectory_result = analyzer.analyze_seller_trajectory(analysis_months, min_months=3)
        
        if 'error' not in trajectory_result:
            print(f"\n📈 轨迹分析结果:")
            print(f"   - 分析卖家总数: {trajectory_result['total_sellers']:,}")
            
            summary = trajectory_result['trajectory_summary']
            for trajectory_type, count in summary.items():
                print(f"   - {trajectory_type}: {count:,}")
            
            # 显示具体轨迹示例
            if len(trajectory_result['trajectory_data']) > 0:
                print(f"\n🔍 轨迹示例 (前5名):")
                top_trajectories = trajectory_result['trajectory_data'].head(5)
                for _, row in top_trajectories.iterrows():
                    print(f"   - 卖家 {row['seller_id']}: {row['tier_path']} ({row['trajectory_type']})")
        else:
            print(f"❌ 轨迹分析失败: {trajectory_result['error']}")


def main():
    """主函数"""
    print("🔧 Olist月度分析新功能演示")
    print("=" * 50)
    
    try:
        # 测试同比环比分析
        test_comparison_analysis()
        
        # 测试轨迹分析
        test_trajectory_analysis()
        
        print("\n✅ 所有测试完成!")
        print("\n📱 请访问 http://localhost:8503 查看Dashboard界面")
        print("   在第6个tab '📅 月度分析' 中体验新功能")
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 