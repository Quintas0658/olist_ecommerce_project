"""
Olist卖家分级管理仪表板

基于Streamlit构建的交互式卖家管理仪表板，展示分级分析结果和业务洞察。
适用于Amazon Global Selling ESM团队的日常业务管理。
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

# 添加src路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from business_metrics import SellerMetricsFramework, TIER_STRATEGIES
from data_pipeline import OlistDataPipeline
from seller_segmentation import SellerSegmentationModel

# 页面配置
st.set_page_config(
    page_title="Olist卖家分级管理仪表板",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .tier-platinum { background: linear-gradient(135deg, #FFD700, #FFA500); }
    .tier-gold { background: linear-gradient(135deg, #FFA500, #FF8C00); }
    .tier-silver { background: linear-gradient(135deg, #C0C0C0, #A9A9A9); }
    .tier-bronze { background: linear-gradient(135deg, #CD7F32, #B8860B); }
    .tier-basic { background: linear-gradient(135deg, #808080, #696969); }
    .tier-risk { background: linear-gradient(135deg, #FF0000, #DC143C); }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """加载和处理数据"""
    try:
        # 尝试加载已处理的数据
        seller_features = pd.read_csv('data/seller_features_processed.csv')
        return seller_features
    except FileNotFoundError:
        # 如果没有处理过的数据，运行数据管道
        st.info("首次运行，正在处理数据...")
        pipeline = OlistDataPipeline()
        results = pipeline.run_full_pipeline(save_output=True)
        return results['seller_features']

@st.cache_data
def run_segmentation_analysis(seller_data):
    """运行分级分析"""
    # 初始化业务指标框架
    metrics_framework = SellerMetricsFramework()
    
    # 计算卖家得分
    seller_scores = metrics_framework.calculate_overall_seller_score(seller_data)
    
    # 运行分级模型
    segmentation_model = SellerSegmentationModel()
    segmentation_results = segmentation_model.fit_segmentation_model(seller_scores)
    
    # 生成业务洞察
    insights = metrics_framework.generate_seller_insights(seller_scores)
    
    return seller_scores, segmentation_results, insights, segmentation_model

def main():
    """主应用函数"""
    
    # 页面标题
    st.markdown("""
    <div class="main-header">
        <h1>🏆 Olist卖家分级管理仪表板</h1>
        <p>数据驱动的卖家生命周期管理 | Amazon Global Selling ESM 最佳实践</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 侧边栏
    with st.sidebar:
        st.header("📋 分析选项")
        
        # 页面选择
        page = st.selectbox(
            "选择分析模块",
            ["📊 总览仪表板", "🎯 卖家分级分析", "📈 业务洞察", "🔍 个体卖家分析", "📋 策略建议"]
        )
        
        st.markdown("---")
        
        # 数据刷新
        if st.button("🔄 刷新数据"):
            st.cache_data.clear()
            st.experimental_rerun()
    
    # 加载数据
    with st.spinner("加载数据中..."):
        seller_data = load_data()
        seller_scores, segmentation_results, insights, segmentation_model = run_segmentation_analysis(seller_data)
    
    # 根据选择的页面显示内容
    if page == "📊 总览仪表板":
        show_overview_dashboard(seller_scores, insights)
    elif page == "🎯 卖家分级分析":
        show_segmentation_analysis(seller_scores, segmentation_results, segmentation_model)
    elif page == "📈 业务洞察":
        show_business_insights(seller_scores, insights)
    elif page == "🔍 个体卖家分析":
        show_individual_seller_analysis(seller_scores, segmentation_model)
    elif page == "📋 策略建议":
        show_strategy_recommendations(seller_scores, insights)

def show_overview_dashboard(seller_scores, insights):
    """显示总览仪表板"""
    st.header("📊 平台总览")
    
    # 关键指标
    col1, col2, col3, col4 = st.columns(4)
    
    total_sellers = len(seller_scores)
    active_sellers = (seller_scores['total_orders'] > 0).sum()
    total_gmv = seller_scores['total_revenue'].sum()
    avg_rating = seller_scores['avg_review_score'].mean()
    
    with col1:
        st.metric("📈 总卖家数", f"{total_sellers:,}")
    
    with col2:
        st.metric("🎯 活跃卖家", f"{active_sellers:,}", f"{active_sellers/total_sellers*100:.1f}%")
    
    with col3:
        st.metric("💰 平台GMV", f"R$ {total_gmv:,.0f}")
    
    with col4:
        st.metric("⭐ 平均评分", f"{avg_rating:.2f}")
    
    st.markdown("---")
    
    # 分级分布
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 卖家分级分布")
        tier_counts = seller_scores['seller_tier'].value_counts()
        
        # 创建饼图
        fig = px.pie(
            values=tier_counts.values,
            names=tier_counts.index,
            title="卖家分级分布",
            color_discrete_map={
                'Platinum': '#FFD700', 'Gold': '#FFA500', 'Silver': '#C0C0C0',
                'Bronze': '#CD7F32', 'Basic': '#808080'
            }
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💼 各分级业务贡献")
        
        # 计算各分级的GMV贡献
        tier_gmv = seller_scores.groupby('seller_tier')['total_revenue'].sum().sort_values(ascending=False)
        
        fig = px.bar(
            x=tier_gmv.index,
            y=tier_gmv.values,
            title="各分级GMV贡献",
            color=tier_gmv.index,
            color_discrete_map={
                'Platinum': '#FFD700', 'Gold': '#FFA500', 'Silver': '#C0C0C0',
                'Bronze': '#CD7F32', 'Basic': '#808080'
            }
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # 业务趋势
    st.subheader("📈 核心业务指标分布")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 销售额分布
        active_data = seller_scores[seller_scores['total_orders'] > 0]
        fig = px.histogram(
            active_data,
            x='total_revenue',
            nbins=50,
            title="卖家销售额分布",
            labels={'total_revenue': '销售额 (R$)', 'count': '卖家数量'}
        )
        fig.update_layout(bargap=0.1)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 评分vs销售额散点图
        fig = px.scatter(
            active_data.sample(min(1000, len(active_data))),  # 采样避免过多点
            x='avg_review_score',
            y='total_revenue',
            color='seller_tier',
            title="客户满意度 vs 销售表现",
            labels={'avg_review_score': '平均评分', 'total_revenue': '销售额 (R$)'},
            color_discrete_map={
                'Platinum': '#FFD700', 'Gold': '#FFA500', 'Silver': '#C0C0C0',
                'Bronze': '#CD7F32', 'Basic': '#808080'
            }
        )
        st.plotly_chart(fig, use_container_width=True)

def show_segmentation_analysis(seller_scores, segmentation_results, segmentation_model):
    """显示分级分析"""
    st.header("🎯 卖家分级分析")
    
    # 分级方法对比
    st.subheader("🔍 分级方法对比")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**💼 业务规则分级**")
        business_segments = segmentation_results['business_segments']
        business_counts = business_segments.value_counts()
        
        for tier, count in business_counts.items():
            percentage = count / len(business_segments) * 100
            st.write(f"• {tier}: {count} ({percentage:.1f}%)")
    
    with col2:
        st.markdown("**🤖 机器学习分级**")
        kmeans_segments = segmentation_results['kmeans_segments']
        kmeans_counts = kmeans_segments.value_counts()
        
        for tier, count in kmeans_counts.items():
            percentage = count / len(kmeans_segments) * 100
            st.write(f"• {tier}: {count} ({percentage:.1f}%)")
    
    with col3:
        st.markdown("**🎯 混合分级方法**")
        hybrid_segments = segmentation_results['hybrid_segments']
        hybrid_counts = hybrid_segments.value_counts()
        
        for tier, count in hybrid_counts.items():
            percentage = count / len(hybrid_segments) * 100
            st.write(f"• {tier}: {count} ({percentage:.1f}%)")
    
    st.markdown("---")
    
    # 分级详细分析
    st.subheader("📊 各分级详细特征分析")
    
    # 特征对比雷达图
    tier_profiles = seller_scores.groupby('seller_tier')[
        ['business_performance_score', 'customer_satisfaction_score', 
         'operational_efficiency_score', 'growth_potential_score']
    ].mean()
    
    fig = go.Figure()
    
    categories = ['业务表现', '客户满意度', '运营效率', '成长潜力']
    
    colors = {'Platinum': '#FFD700', 'Gold': '#FFA500', 'Silver': '#C0C0C0',
              'Bronze': '#CD7F32', 'Basic': '#808080'}
    
    for tier in tier_profiles.index:
        if tier in colors:
            values = tier_profiles.loc[tier].values.tolist()
            values += [values[0]]  # 闭合雷达图
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories + [categories[0]],
                fill='toself',
                name=tier,
                line_color=colors[tier]
            ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=True,
        title="各分级维度得分对比"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 分级模型性能
    if segmentation_model.classification_model:
        st.subheader("🎯 模型性能评估")
        
        col1, col2 = st.columns(2)
        
        with col1:
            accuracy = segmentation_model.classification_model['accuracy']
            st.metric("🎯 分类准确率", f"{accuracy:.1%}")
            
            separation_ratio = segmentation_results['evaluation']['separation_ratio']
            st.metric("📏 分离度指标", f"{separation_ratio:.3f}")
        
        with col2:
            # 特征重要性
            importance_df = segmentation_model.classification_model['feature_importance']
            fig = px.bar(
                importance_df.head(8),
                x='importance',
                y='feature',
                orientation='h',
                title="Top 8 重要特征"
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

def show_business_insights(seller_scores, insights):
    """显示业务洞察"""
    st.header("📈 业务洞察与机会识别")
    
    # 高价值卖家分析
    st.subheader("💎 高价值卖家群体")
    
    high_value_tiers = ['Platinum', 'Gold']
    high_value_sellers = seller_scores[seller_scores['seller_tier'].isin(high_value_tiers)]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        hv_count = len(high_value_sellers)
        hv_percentage = hv_count / len(seller_scores) * 100
        st.metric("👑 高价值卖家数量", f"{hv_count:,}", f"{hv_percentage:.1f}%")
    
    with col2:
        hv_gmv = high_value_sellers['total_revenue'].sum()
        total_gmv = seller_scores['total_revenue'].sum()
        hv_contribution = hv_gmv / total_gmv * 100
        st.metric("💰 GMV贡献", f"R$ {hv_gmv:,.0f}", f"{hv_contribution:.1f}%")
    
    with col3:
        hv_avg_rating = high_value_sellers['avg_review_score'].mean()
        st.metric("⭐ 平均满意度", f"{hv_avg_rating:.2f}")
    
    # 成长机会分析
    st.subheader("🚀 成长机会识别")
    
    # 高潜力但低表现的卖家
    growth_opportunity = seller_scores[
        (seller_scores['growth_potential_score'] > 0.6) &
        (seller_scores['business_performance_score'] < 0.4) &
        (seller_scores['total_orders'] > 0)
    ]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🎯 高潜力待发展卖家**")
        st.metric("潜力卖家数量", f"{len(growth_opportunity):,}")
        
        if len(growth_opportunity) > 0:
            avg_potential = growth_opportunity['growth_potential_score'].mean()
            current_gmv = growth_opportunity['total_revenue'].sum()
            st.write(f"• 平均潜力得分: {avg_potential:.2f}")
            st.write(f"• 当前GMV: R$ {current_gmv:,.0f}")
            st.write(f"• 平均订单数: {growth_opportunity['total_orders'].mean():.1f}")
    
    with col2:
        # 风险卖家分析
        risk_sellers = seller_scores[
            (seller_scores['customer_satisfaction_score'] < 0.4) |
            (seller_scores['risk_score'] > 0.7)
        ]
        
        st.markdown("**⚠️ 风险卖家监控**")
        st.metric("风险卖家数量", f"{len(risk_sellers):,}")
        
        if len(risk_sellers) > 0:
            risk_gmv = risk_sellers['total_revenue'].sum()
            avg_risk_score = risk_sellers['risk_score'].mean()
            st.write(f"• GMV影响: R$ {risk_gmv:,.0f}")
            st.write(f"• 平均风险得分: {avg_risk_score:.2f}")
    
    # 市场机会分析
    st.subheader("🎨 市场细分机会")
    
    # 按地区分析
    if 'seller_state' in seller_scores.columns:
        state_analysis = seller_scores.groupby('seller_state').agg({
            'total_revenue': ['count', 'sum', 'mean'],
            'avg_review_score': 'mean'
        }).round(2)
        
        state_analysis.columns = ['seller_count', 'total_gmv', 'avg_revenue', 'avg_rating']
        state_analysis = state_analysis.sort_values('total_gmv', ascending=False).head(10)
        
        fig = px.bar(
            x=state_analysis.index,
            y=state_analysis['total_gmv'],
            title="各州GMV分布 Top 10",
            labels={'x': '州', 'y': 'GMV (R$)'}
        )
        st.plotly_chart(fig, use_container_width=True)

def show_individual_seller_analysis(seller_scores, segmentation_model):
    """显示个体卖家分析"""
    st.header("🔍 个体卖家分析")
    
    # 卖家选择
    active_sellers = seller_scores[seller_scores['total_orders'] > 0]
    seller_ids = active_sellers['seller_id'].tolist()
    
    selected_seller = st.selectbox(
        "选择要分析的卖家ID",
        options=seller_ids,
        help="从活跃卖家中选择进行详细分析"
    )
    
    if selected_seller:
        seller_data = seller_scores[seller_scores['seller_id'] == selected_seller].iloc[0]
        
        # 基本信息
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🏆 当前等级", seller_data['seller_tier'])
        
        with col2:
            st.metric("💰 总销售额", f"R$ {seller_data['total_revenue']:,.2f}")
        
        with col3:
            st.metric("📦 订单数量", f"{int(seller_data['total_orders'])}")
        
        with col4:
            st.metric("⭐ 平均评分", f"{seller_data['avg_review_score']:.2f}")
        
        # 详细得分
        st.subheader("📊 详细得分分析")
        
        scores = {
            '业务表现': seller_data['business_performance_score'],
            '客户满意度': seller_data['customer_satisfaction_score'],
            '运营效率': seller_data['operational_efficiency_score'],
            '成长潜力': seller_data['growth_potential_score']
        }
        
        # 得分雷达图
        fig = go.Figure()
        
        categories = list(scores.keys())
        values = list(scores.values()) + [list(scores.values())[0]]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories + [categories[0]],
            fill='toself',
            name=selected_seller[:8] + '...'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            showlegend=True,
            title=f"卖家 {selected_seller[:8]}... 综合得分分析"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 改进建议
        st.subheader("💡 个性化改进建议")
        
        current_tier = seller_data['seller_tier']
        if current_tier in TIER_STRATEGIES:
            strategy = TIER_STRATEGIES[current_tier]
            
            st.markdown(f"**🎯 当前策略重点: {strategy['priority']}**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📋 建议行动:**")
                for action in strategy['actions']:
                    st.write(f"• {action}")
            
            with col2:
                st.markdown("**📈 关注指标:**")
                for kpi in strategy['kpi_focus']:
                    st.write(f"• {kpi}")

def show_strategy_recommendations(seller_scores, insights):
    """显示策略建议"""
    st.header("📋 管理策略建议")
    
    # 整体策略框架
    st.subheader("🎯 分级管理策略框架")
    
    for tier, strategy in TIER_STRATEGIES.items():
        with st.expander(f"{tier} 级卖家管理策略"):
            
            tier_sellers = seller_scores[seller_scores['seller_tier'] == tier]
            tier_count = len(tier_sellers)
            
            if tier_count > 0:
                tier_gmv = tier_sellers['total_revenue'].sum()
                tier_contribution = tier_gmv / seller_scores['total_revenue'].sum() * 100
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**📊 群体规模**: {tier_count:,} 个卖家")
                    st.markdown(f"**💰 GMV贡献**: R$ {tier_gmv:,.0f} ({tier_contribution:.1f}%)")
                    st.markdown(f"**🎯 管理重点**: {strategy['priority']}")
                
                with col2:
                    st.markdown("**📋 具体行动:**")
                    for action in strategy['actions']:
                        st.write(f"• {action}")
    
    # 资源配置建议
    st.subheader("💼 资源配置优化")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🎯 重点投入领域**")
        
        # 高价值卖家维护
        platinum_gold = seller_scores[seller_scores['seller_tier'].isin(['Platinum', 'Gold'])]
        st.write(f"1. **高价值卖家维护** ({len(platinum_gold)} 个)")
        st.write("   - 专属客户经理配置")
        st.write("   - 优先营销资源投放")
        
        # 成长潜力挖掘
        growth_potential = seller_scores[
            (seller_scores['growth_potential_score'] > 0.6) & 
            (seller_scores['seller_tier'].isin(['Silver', 'Bronze']))
        ]
        st.write(f"2. **成长潜力挖掘** ({len(growth_potential)} 个)")
        st.write("   - 定向培训和支持")
        st.write("   - 营销工具使用指导")
    
    with col2:
        st.markdown("**⚠️ 风险控制重点**")
        
        # 风险卖家管理
        risk_sellers = seller_scores[
            (seller_scores['customer_satisfaction_score'] < 0.4) |
            (seller_scores['avg_review_score'] < 3.0)
        ]
        st.write(f"1. **风险卖家管控** ({len(risk_sellers)} 个)")
        st.write("   - 加强合规性检查")
        st.write("   - 服务质量改进计划")
        
        # 流失预警
        inactive_risk = seller_scores[
            (seller_scores['total_orders'] < 5) & 
            (seller_scores['total_orders'] > 0)
        ]
        st.write(f"2. **流失预警监控** ({len(inactive_risk)} 个)")
        st.write("   - 定期沟通和关怀")
        st.write("   - 重新激活计划")
    
    # 执行优先级
    st.subheader("🚀 执行优先级排序")
    
    priorities = [
        {
            "优先级": "🔴 高",
            "项目": "Platinum/Gold卖家VIP服务",
            "影响": "保持高价值客户忠诚度",
            "预期ROI": "高"
        },
        {
            "优先级": "🟠 中高", 
            "项目": "Silver级卖家成长加速",
            "影响": "扩大中坚力量规模",
            "预期ROI": "中高"
        },
        {
            "优先级": "🟡 中",
            "项目": "风险卖家质量改进",
            "影响": "降低平台风险",
            "预期ROI": "中"
        },
        {
            "优先级": "🟢 中低",
            "项目": "Bronze级基础培训",
            "影响": "提升整体生态质量",
            "预期ROI": "中低"
        }
    ]
    
    priority_df = pd.DataFrame(priorities)
    st.dataframe(priority_df, use_container_width=True)

if __name__ == "__main__":
    main() 