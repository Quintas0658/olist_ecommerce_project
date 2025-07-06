#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Olist商业智能交互式仪表板
企业级BI Dashboard - 媲美Tableau的交互体验
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 页面配置
st.set_page_config(
    page_title="Olist BI Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}
.metric-card {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 0.25rem solid #1f77b4;
}
.sidebar-header {
    font-size: 1.2rem;
    font-weight: bold;
    color: #1f77b4;
    margin-bottom: 1rem;
}
.insight-box {
    background-color: #e8f4fd;
    padding: 1rem;
    border-radius: 0.5rem;
    border: 1px solid #1f77b4;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """加载和缓存数据"""
    try:
        # 加载处理后的数据
        seller_profile = pd.read_csv('data/seller_profile_processed.csv')
        
        # 加载原始数据用于深度分析
        orders = pd.read_csv('data/olist_orders_dataset.csv')
        order_items = pd.read_csv('data/olist_order_items_dataset.csv')
        reviews = pd.read_csv('data/olist_order_reviews_dataset.csv')
        products = pd.read_csv('data/olist_products_dataset.csv')
        
        # 时间处理
        orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
        orders['year_month'] = orders['order_purchase_timestamp'].dt.to_period('M').astype(str)
        
        # 加载分析结果
        try:
            seller_analysis = pd.read_csv('data/seller_analysis_results.csv')
        except:
            # 如果没有分析结果，创建简单分级
            def classify_seller(row):
                gmv = row['total_gmv']
                orders_count = row['unique_orders']
                rating = row['avg_review_score']
                
                if gmv >= 50000 and orders_count >= 200 and rating >= 4.0:
                    return 'Platinum'
                elif gmv >= 10000 and orders_count >= 50:
                    return 'Gold'
                elif gmv >= 2000 and orders_count >= 10:
                    return 'Silver'
                elif gmv >= 500 and orders_count >= 3:
                    return 'Bronze'
                else:
                    return 'Basic'
            
            seller_profile['business_tier'] = seller_profile.apply(classify_seller, axis=1)
            seller_analysis = seller_profile
        
        return seller_profile, seller_analysis, orders, order_items, reviews, products
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        return None, None, None, None, None, None

def create_sidebar_filters(seller_analysis):
    """创建侧边栏筛选器"""
    st.sidebar.markdown('<p class="sidebar-header">🔍 数据筛选器</p>', unsafe_allow_html=True)
    
    # 卖家层级筛选
    tiers = ['All'] + list(seller_analysis['business_tier'].unique())
    selected_tier = st.sidebar.selectbox('🏆 卖家层级', tiers)
    
    # GMV范围筛选
    gmv_min, gmv_max = st.sidebar.slider(
        '💰 GMV范围 (R$)',
        min_value=float(seller_analysis['total_gmv'].min()),
        max_value=float(seller_analysis['total_gmv'].max()),
        value=(float(seller_analysis['total_gmv'].min()), float(seller_analysis['total_gmv'].max())),
        format="%.0f"
    )
    
    # 评分范围筛选
    rating_min, rating_max = st.sidebar.slider(
        '⭐ 评分范围',
        min_value=float(seller_analysis['avg_review_score'].min()),
        max_value=5.0,
        value=(float(seller_analysis['avg_review_score'].min()), 5.0),
        step=0.1
    )
    
    # 州筛选
    states = ['All'] + list(seller_analysis['seller_state'].unique())
    selected_states = st.sidebar.multiselect('📍 选择州', states, default=['All'])
    
    # 品类数筛选
    category_min, category_max = st.sidebar.slider(
        '🎁 品类数范围',
        min_value=int(seller_analysis['category_count'].min()),
        max_value=int(seller_analysis['category_count'].max()),
        value=(int(seller_analysis['category_count'].min()), int(seller_analysis['category_count'].max()))
    )
    
    return {
        'tier': selected_tier,
        'gmv_range': (gmv_min, gmv_max),
        'rating_range': (rating_min, rating_max),
        'states': selected_states,
        'category_range': (category_min, category_max)
    }

def apply_filters(data, filters):
    """应用筛选器"""
    filtered_data = data.copy()
    
    # 层级筛选
    if filters['tier'] != 'All':
        filtered_data = filtered_data[filtered_data['business_tier'] == filters['tier']]
    
    # GMV筛选
    filtered_data = filtered_data[
        (filtered_data['total_gmv'] >= filters['gmv_range'][0]) &
        (filtered_data['total_gmv'] <= filters['gmv_range'][1])
    ]
    
    # 评分筛选
    filtered_data = filtered_data[
        (filtered_data['avg_review_score'] >= filters['rating_range'][0]) &
        (filtered_data['avg_review_score'] <= filters['rating_range'][1])
    ]
    
    # 州筛选
    if 'All' not in filters['states'] and filters['states']:
        filtered_data = filtered_data[filtered_data['seller_state'].isin(filters['states'])]
    
    # 品类数筛选
    filtered_data = filtered_data[
        (filtered_data['category_count'] >= filters['category_range'][0]) &
        (filtered_data['category_count'] <= filters['category_range'][1])
    ]
    
    return filtered_data

def display_kpi_metrics(data):
    """显示KPI指标卡片"""
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="🏪 卖家总数",
            value=f"{len(data):,}",
            delta=f"{len(data)/3095*100:.1f}% of total"
        )
    
    with col2:
        total_gmv = data['total_gmv'].sum()
        st.metric(
            label="💰 总GMV",
            value=f"R$ {total_gmv:,.0f}",
            delta=f"{total_gmv/13591644*100:.1f}% of total"
        )
    
    with col3:
        avg_rating = data['avg_review_score'].mean()
        st.metric(
            label="⭐ 平均评分",
            value=f"{avg_rating:.2f}",
            delta=f"vs 3.97 overall"
        )
    
    with col4:
        total_orders = data['unique_orders'].sum()
        st.metric(
            label="📦 总订单数",
            value=f"{total_orders:,}",
            delta=f"{total_orders/100010*100:.1f}% of total"
        )
    
    with col5:
        avg_categories = data['category_count'].mean()
        st.metric(
            label="🎁 平均品类数",
            value=f"{avg_categories:.1f}",
            delta=f"vs 2.1 overall"
        )

def create_tier_distribution_chart(data):
    """创建卖家层级分布图"""
    tier_stats = data.groupby('business_tier').agg({
        'seller_id': 'count',
        'total_gmv': 'sum'
    }).reset_index()
    
    tier_stats.columns = ['Tier', 'Count', 'GMV']
    tier_stats['GMV_Pct'] = tier_stats['GMV'] / tier_stats['GMV'].sum() * 100
    tier_stats['Count_Pct'] = tier_stats['Count'] / tier_stats['Count'].sum() * 100
    
    # 创建双轴图
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('卖家数量分布', 'GMV贡献分布'),
        specs=[[{"type": "pie"}, {"type": "pie"}]]
    )
    
    # 颜色映射
    colors = {'Platinum': '#FFD700', 'Gold': '#FFA500', 'Silver': '#C0C0C0', 
              'Bronze': '#CD7F32', 'Basic': '#808080'}
    
    # 卖家数量饼图
    fig.add_trace(
        go.Pie(
            labels=tier_stats['Tier'],
            values=tier_stats['Count'],
            name="卖家数量",
            marker_colors=[colors.get(tier, '#1f77b4') for tier in tier_stats['Tier']],
            textinfo='label+percent',
            textposition='inside'
        ),
        row=1, col=1
    )
    
    # GMV贡献饼图
    fig.add_trace(
        go.Pie(
            labels=tier_stats['Tier'],
            values=tier_stats['GMV'],
            name="GMV贡献",
            marker_colors=[colors.get(tier, '#1f77b4') for tier in tier_stats['Tier']],
            textinfo='label+percent',
            textposition='inside'
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        title_text="🏆 卖家层级分布分析",
        height=400,
        showlegend=False
    )
    
    return fig

def create_gmv_vs_orders_scatter(data):
    """创建GMV vs 订单数散点图"""
    fig = px.scatter(
        data, 
        x='unique_orders', 
        y='total_gmv',
        color='business_tier',
        size='avg_review_score',
        hover_data=['seller_state', 'category_count', 'avg_shipping_days'],
        title='📈 GMV vs 订单数关系分析',
        labels={
            'unique_orders': '订单数',
            'total_gmv': 'GMV (R$)',
            'business_tier': '卖家层级',
            'avg_review_score': '平均评分'
        },
        color_discrete_map={
            'Platinum': '#FFD700',
            'Gold': '#FFA500', 
            'Silver': '#C0C0C0',
            'Bronze': '#CD7F32',
            'Basic': '#808080'
        }
    )
    
    fig.update_layout(height=500)
    return fig

def create_geographic_analysis(data):
    """创建地理分布分析"""
    state_stats = data.groupby('seller_state').agg({
        'seller_id': 'count',
        'total_gmv': ['sum', 'mean'],
        'avg_review_score': 'mean',
        'category_count': 'mean'
    }).round(2)
    
    state_stats.columns = ['卖家数量', 'GMV总和', 'GMV均值', '平均评分', '平均品类数']
    state_stats = state_stats.reset_index().sort_values('GMV总和', ascending=False).head(15)
    
    # 创建地理分布图
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('卖家数量分布', 'GMV总和分布', 'GMV均值分布', '平均评分分布'),
        specs=[[{"type": "bar"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "bar"}]]
    )
    
    # 卖家数量
    fig.add_trace(
        go.Bar(x=state_stats['seller_state'], y=state_stats['卖家数量'], 
               name='卖家数量', marker_color='lightblue'),
        row=1, col=1
    )
    
    # GMV总和
    fig.add_trace(
        go.Bar(x=state_stats['seller_state'], y=state_stats['GMV总和'], 
               name='GMV总和', marker_color='orange'),
        row=1, col=2
    )
    
    # GMV均值
    fig.add_trace(
        go.Bar(x=state_stats['seller_state'], y=state_stats['GMV均值'], 
               name='GMV均值', marker_color='green'),
        row=2, col=1
    )
    
    # 平均评分
    fig.add_trace(
        go.Bar(x=state_stats['seller_state'], y=state_stats['平均评分'], 
               name='平均评分', marker_color='purple'),
        row=2, col=2
    )
    
    fig.update_layout(
        title_text="🗺️ 地理分布深度分析",
        height=600,
        showlegend=False
    )
    
    return fig

def create_performance_radar(data, all_data=None):
    """创建性能雷达图"""
    # 检查当前数据是否只有一个层级
    unique_tiers = data['business_tier'].nunique()
    
    # 按层级计算平均指标
    tier_performance = data.groupby('business_tier').agg({
        'total_gmv': 'mean',
        'avg_review_score': 'mean', 
        'category_count': 'mean',
        'avg_shipping_days': 'mean',
        'delivery_success_rate': 'mean'
    }).round(2)
    
    # 如果只有一个层级，添加全体平均水平作为对比
    if unique_tiers == 1 and all_data is not None:
        overall_performance = all_data.agg({
            'total_gmv': 'mean',
            'avg_review_score': 'mean', 
            'category_count': 'mean',
            'avg_shipping_days': 'mean',
            'delivery_success_rate': 'mean'
        }).round(2)
        
        # 添加全体平均到dataframe
        tier_performance.loc['全体平均'] = overall_performance
    
    # 获取全局数据范围用于标准化
    if all_data is not None:
        # 选择需要的列进行统计
        required_cols = ['total_gmv', 'avg_review_score', 'category_count', 'avg_shipping_days', 'delivery_success_rate']
        available_cols = [col for col in required_cols if col in all_data.columns]
        global_stats = all_data[available_cols].agg(['min', 'max'])
    else:
        global_stats = None
    
    # 标准化数据（0-1）
    normalized_performance = tier_performance.copy()
    for col in tier_performance.columns:
        if global_stats is not None and col in global_stats.columns:
            min_val = global_stats.loc['min', col]
            max_val = global_stats.loc['max', col]
        else:
            min_val = tier_performance[col].min()
            max_val = tier_performance[col].max()
        
        # 避免除零错误
        if max_val == min_val:
            normalized_performance[col] = 0.5  # 设置为中间值
        else:
            if col == 'avg_shipping_days':  # 发货天数越少越好
                normalized_performance[col] = 1 - (tier_performance[col] - min_val) / (max_val - min_val)
            else:
                normalized_performance[col] = (tier_performance[col] - min_val) / (max_val - min_val)
    
    # 创建雷达图
    fig = go.Figure()
    
    categories = ['GMV', '评分', '品类数', '发货效率', '交付成功率']
    colors = ['#FFD700', '#FFA500', '#C0C0C0', '#CD7F32', '#808080', '#FF6B6B']
    
    for i, tier in enumerate(normalized_performance.index):
        values = normalized_performance.loc[tier].values.tolist()
        values += values[:1]  # 闭合雷达图
        
        # 为全体平均设置特殊样式
        if tier == '全体平均':
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories + [categories[0]],
                fill='none',
                name=tier,
                line=dict(color='#666666', dash='dash', width=2),
                opacity=0.8
            ))
        else:
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories + [categories[0]],
                fill='toself',
                name=tier,
                line_color=colors[i % len(colors)],
                opacity=0.7
            ))
    
    # 动态设置标题
    if unique_tiers == 1:
        selected_tier = tier_performance.index[0] if '全体平均' not in tier_performance.index else [t for t in tier_performance.index if t != '全体平均'][0]
        title = f"🎯 {selected_tier}层级 vs 全体平均性能对比"
    else:
        title = "🎯 各层级卖家性能雷达图"
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                tickmode='array',
                tickvals=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
                ticktext=['0%', '20%', '40%', '60%', '80%', '100%']
            )
        ),
        title=title,
        height=500,
        showlegend=True
    )
    
    return fig

def create_correlation_heatmap(data):
    """创建相关性热力图"""
    # 选择数值型指标
    numeric_cols = [
        'total_gmv', 'unique_orders', 'avg_review_score', 
        'category_count', 'avg_shipping_days', 'bad_review_rate',
        'revenue_per_order', 'items_per_order'
    ]
    
    correlation_matrix = data[numeric_cols].corr()
    
    # 创建热力图
    fig = px.imshow(
        correlation_matrix,
        title="🔥 业务指标相关性热力图",
        color_continuous_scale='RdBu_r',
        aspect='auto'
    )
    
    fig.update_layout(height=500)
    return fig

def display_business_insights(data):
    """显示商业洞察"""
    st.markdown("## 🧠 智能商业洞察")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.markdown("### 🎯 机会识别")
        
        # 高潜力卖家识别
        high_potential = data[
            (data['avg_review_score'] >= 4.2) & 
            (data['total_gmv'] < data['total_gmv'].median()) &
            (data['unique_orders'] >= 5)
        ]
        
        st.write(f"**高潜力卖家**: {len(high_potential)}个")
        st.write(f"**平均评分**: {high_potential['avg_review_score'].mean():.2f}")
        st.write(f"**平均GMV**: R$ {high_potential['total_gmv'].mean():,.0f}")
        
        if len(high_potential) > 0:
            potential_growth = (data['total_gmv'].median() - high_potential['total_gmv'].mean()) * len(high_potential)
            st.write(f"**增长潜力**: R$ {potential_growth:,.0f}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.markdown("### 📊 关键指标")
        
        # 计算关键比率
        pareto_threshold = int(len(data) * 0.2)
        top_20_gmv = data.nlargest(pareto_threshold, 'total_gmv')['total_gmv'].sum()
        pareto_ratio = top_20_gmv / data['total_gmv'].sum() * 100
        
        st.write(f"**帕累托比例**: Top 20%贡献{pareto_ratio:.1f}%GMV")
        
        # 多品类效应
        single_cat = data[data['category_count'] == 1]['total_gmv'].mean()
        multi_cat = data[data['category_count'] > 1]['total_gmv'].mean()
        if single_cat > 0:
            category_effect = multi_cat / single_cat
            st.write(f"**品类效应**: 多品类GMV是单品类的{category_effect:.1f}倍")
        
        # 评分效应
        high_rating = data[data['avg_review_score'] >= 4.0]['total_gmv'].mean()
        low_rating = data[data['avg_review_score'] < 3.5]['total_gmv'].mean()
        if low_rating > 0:
            rating_effect = high_rating / low_rating
            st.write(f"**评分效应**: 高评分GMV是低评分的{rating_effect:.1f}倍")
        
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    """主函数"""
    # 页面标题
    st.markdown('<h1 class="main-header">🚀 Olist商业智能分析平台</h1>', unsafe_allow_html=True)
    
    # 加载数据
    with st.spinner('🔄 正在加载数据...'):
        seller_profile, seller_analysis, orders, order_items, reviews, products = load_data()
    
    if seller_analysis is None:
        st.error("❌ 数据加载失败，请检查数据文件")
        return
    
    # 侧边栏筛选器
    filters = create_sidebar_filters(seller_analysis)
    
    # 应用筛选器
    filtered_data = apply_filters(seller_analysis, filters)
    
    if len(filtered_data) == 0:
        st.warning("⚠️ 当前筛选条件下没有数据，请调整筛选器设置")
        return
    
    # 显示筛选结果
    st.info(f"📊 当前显示 {len(filtered_data):,} 个卖家 (占总数的 {len(filtered_data)/len(seller_analysis)*100:.1f}%)")
    
    # KPI指标卡片
    display_kpi_metrics(filtered_data)
    
    # 创建标签页
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 总览分析", "🏆 层级分析", "🗺️ 地理分析", "📈 性能分析", "🧠 智能洞察"
    ])
    
    with tab1:
        st.markdown("## 📊 平台总览分析")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 层级分布
            tier_fig = create_tier_distribution_chart(filtered_data)
            st.plotly_chart(tier_fig, use_container_width=True)
        
        with col2:
            # GMV vs 订单数散点图
            scatter_fig = create_gmv_vs_orders_scatter(filtered_data)
            st.plotly_chart(scatter_fig, use_container_width=True)
    
    with tab2:
        st.markdown("## 🏆 卖家层级深度分析")
        
        # 层级统计表
        tier_summary = filtered_data.groupby('business_tier').agg({
            'seller_id': 'count',
            'total_gmv': ['sum', 'mean'],
            'unique_orders': ['sum', 'mean'],
            'avg_review_score': 'mean',
            'category_count': 'mean'
        }).round(2)
        
        tier_summary.columns = ['数量', 'GMV总和', 'GMV均值', '订单总数', '订单均值', '平均评分', '平均品类数']
        
        st.markdown("### 📋 层级统计表")
        st.dataframe(tier_summary, use_container_width=True)
        
        # 性能雷达图
        radar_fig = create_performance_radar(filtered_data, seller_analysis)
        st.plotly_chart(radar_fig, use_container_width=True)
    
    with tab3:
        st.markdown("## 🗺️ 地理分布分析")
        
        geo_fig = create_geographic_analysis(filtered_data)
        st.plotly_chart(geo_fig, use_container_width=True)
        
        # 州级详细数据
        state_detail = filtered_data.groupby('seller_state').agg({
            'seller_id': 'count',
            'total_gmv': ['sum', 'mean'],
            'avg_review_score': 'mean'
        }).round(2)
        state_detail.columns = ['卖家数量', 'GMV总和', 'GMV均值', '平均评分']
        state_detail = state_detail.sort_values('GMV总和', ascending=False)
        
        st.markdown("### 📊 州级数据详情")
        st.dataframe(state_detail, use_container_width=True)
    
    with tab4:
        st.markdown("## 📈 性能相关性分析")
        
        corr_fig = create_correlation_heatmap(filtered_data)
        st.plotly_chart(corr_fig, use_container_width=True)
        
        # 性能分布
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 💰 GMV分布")
            gmv_hist = px.histogram(filtered_data, x='total_gmv', nbins=50, 
                                   title='GMV分布直方图')
            st.plotly_chart(gmv_hist, use_container_width=True)
        
        with col2:
            st.markdown("### ⭐ 评分分布")
            rating_hist = px.histogram(filtered_data, x='avg_review_score', nbins=30,
                                      title='评分分布直方图')
            st.plotly_chart(rating_hist, use_container_width=True)
    
    with tab5:
        display_business_insights(filtered_data)
        
        # 详细数据表
        st.markdown("### 📋 筛选结果数据")
        display_columns = [
            'seller_id', 'seller_state', 'business_tier', 'total_gmv', 
            'unique_orders', 'avg_review_score', 'category_count', 'avg_shipping_days'
        ]
        
        st.dataframe(
            filtered_data[display_columns].sort_values('total_gmv', ascending=False),
            use_container_width=True
        )
        
        # 数据导出
        if st.button("📥 导出筛选数据为CSV"):
            csv = filtered_data.to_csv(index=False)
            st.download_button(
                label="下载CSV文件",
                data=csv,
                file_name=f"olist_filtered_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

    # 页脚
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9rem;'>
        📊 Olist商业智能分析平台 | 基于155万+真实电商数据 | 
        <a href='#' style='color: #1f77b4;'>项目GitHub</a> | 
        <a href='#' style='color: #1f77b4;'>技术文档</a>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 