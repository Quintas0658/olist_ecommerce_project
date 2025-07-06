#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Olist商业智能交互式仪表板
企业级BI Dashboard - 媲美Tableau的交互体验
🌐 Olist Business Intelligence Interactive Dashboard
Enterprise BI Dashboard - Tableau-level Interactive Experience
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

# 语言配置
LANGUAGES = {
    'zh': {
        'page_title': 'Olist BI Analytics Dashboard',
        'page_header': '🚀 Olist商业智能分析平台',
        'language_selector': '🌐 语言 / Language',
        'loading_data': '🔄 正在加载数据...',
        'data_load_error': '❌ 数据加载失败，请检查数据文件',
        'no_data_warning': '⚠️ 当前筛选条件下没有数据，请调整筛选器设置',
        'current_display': '📊 当前显示 {count:,} 个卖家 (占总数的 {percentage:.1f}%)',
        
        # 侧边栏
        'sidebar_header': '🔍 数据筛选器',
        'seller_tier': '🏆 卖家层级',
        'gmv_range': '💰 GMV范围 (R$)',
        'rating_range': '⭐ 评分范围',
        'select_states': '📍 选择州',
        'category_range': '🎁 品类数范围',
        
        # KPI指标
        'total_sellers': '🏪 卖家总数',
        'total_gmv': '💰 总GMV',
        'avg_gmv': '📊 平均GMV',
        'avg_rating': '⭐ 平均评分',
        'avg_orders': '📦 平均订单数',
        'of_total': 'of total',
        
        # 标签页
        'tab_overview': '📊 总览分析',
        'tab_tier': '🏆 层级分析',
        'tab_geo': '🗺️ 地理分析',
        'tab_performance': '📈 性能分析',
        'tab_insights': '🧠 智能洞察',
        
        # 分析标题
        'overview_title': '## 📊 平台总览分析',
        'tier_title': '## 🏆 卖家层级深度分析',
        'geo_title': '## 🗺️ 地理分布分析',
        'performance_title': '## 📈 性能相关性分析',
        'insights_title': '## 🧠 智能商业洞察',
        
        # 图表标题
        'tier_distribution': '卖家层级分布',
        'gmv_vs_orders': 'GMV vs 订单数关系',
        'geographic_distribution': '地理分布四象限分析',
        'performance_radar': '层级性能雷达图',
        'correlation_heatmap': '业务指标相关性热图',
        'gmv_distribution': '💰 GMV分布',
        'rating_distribution': '⭐ 评分分布',
        'gmv_hist_title': 'GMV分布直方图',
        'rating_hist_title': '评分分布直方图',
        
        # 表格标题
        'tier_stats_table': '### 📋 层级统计表',
        'state_detail_table': '### 📊 州级数据详情',
        'filtered_data_table': '### 📋 筛选结果数据',
        
        # 表格列名
        'count': '数量',
        'gmv_sum': 'GMV总和',
        'gmv_mean': 'GMV均值',
        'orders_sum': '订单总数',
        'orders_mean': '订单均值',
        'avg_score': '平均评分',
        'avg_categories': '平均品类数',
        'seller_count': '卖家数量',
        
        # 洞察分析
        'opportunity_identification': '### 🎯 机会识别',
        'key_metrics': '### 📊 关键指标',
        'high_potential_sellers': '**高潜力卖家**',
        'average_rating': '**平均评分**',
        'average_gmv': '**平均GMV**',
        'growth_potential': '**增长潜力**',
        'pareto_ratio': '**帕累托比例**',
        'category_effect': '**品类效应**',
        'rating_effect': '**评分效应**',
        'pareto_text': 'Top 20%贡献{ratio:.1f}%GMV',
        'category_text': '多品类GMV是单品类的{effect:.1f}倍',
        'rating_text': '高评分GMV是低评分的{effect:.1f}倍',
        
        # 按钮和操作
        'export_data': '📥 导出筛选数据为CSV',
        'download_csv': '下载CSV文件',
        
        # 层级
        'Platinum': 'Platinum',
        'Gold': 'Gold', 
        'Silver': 'Silver',
        'Bronze': 'Bronze',
        'Basic': 'Basic',
        'All': '全部',
        
        # 页脚
        'footer': """
        <div style='text-align: center; color: #666; font-size: 0.9rem;'>
            📊 Olist商业智能分析平台 | 基于155万+真实电商数据 | 
            <a href='https://github.com/Quintas0658/olist_ecommerce_project' style='color: #1f77b4;'>项目GitHub</a> | 
            <a href='#' style='color: #1f77b4;'>技术文档</a>
        </div>
        """
    },
    'en': {
        'page_title': 'Olist BI Analytics Dashboard',
        'page_header': '🚀 Olist Business Intelligence Analytics Platform',
        'language_selector': '🌐 Language / 语言',
        'loading_data': '🔄 Loading data...',
        'data_load_error': '❌ Data loading failed, please check data files',
        'no_data_warning': '⚠️ No data under current filter conditions, please adjust filter settings',
        'current_display': '📊 Currently displaying {count:,} sellers ({percentage:.1f}% of total)',
        
        # Sidebar
        'sidebar_header': '🔍 Data Filters',
        'seller_tier': '🏆 Seller Tier',
        'gmv_range': '💰 GMV Range (R$)',
        'rating_range': '⭐ Rating Range',
        'select_states': '📍 Select States',
        'category_range': '🎁 Category Count Range',
        
        # KPI Metrics
        'total_sellers': '🏪 Total Sellers',
        'total_gmv': '💰 Total GMV',
        'avg_gmv': '📊 Average GMV',
        'avg_rating': '⭐ Average Rating',
        'avg_orders': '📦 Average Orders',
        'of_total': 'of total',
        
        # Tabs
        'tab_overview': '📊 Overview',
        'tab_tier': '🏆 Tier Analysis',
        'tab_geo': '🗺️ Geographic',
        'tab_performance': '📈 Performance',
        'tab_insights': '🧠 Smart Insights',
        
        # Analysis Titles
        'overview_title': '## 📊 Platform Overview Analysis',
        'tier_title': '## 🏆 In-depth Seller Tier Analysis',
        'geo_title': '## 🗺️ Geographic Distribution Analysis',
        'performance_title': '## 📈 Performance Correlation Analysis',
        'insights_title': '## 🧠 Smart Business Insights',
        
        # Chart Titles
        'tier_distribution': 'Seller Tier Distribution',
        'gmv_vs_orders': 'GMV vs Orders Relationship',
        'geographic_distribution': 'Geographic Distribution Quadrant Analysis',
        'performance_radar': 'Tier Performance Radar Chart',
        'correlation_heatmap': 'Business Metrics Correlation Heatmap',
        'gmv_distribution': '💰 GMV Distribution',
        'rating_distribution': '⭐ Rating Distribution',
        'gmv_hist_title': 'GMV Distribution Histogram',
        'rating_hist_title': 'Rating Distribution Histogram',
        
        # Table Titles
        'tier_stats_table': '### 📋 Tier Statistics Table',
        'state_detail_table': '### 📊 State-level Data Details',
        'filtered_data_table': '### 📋 Filtered Results Data',
        
        # Table Columns
        'count': 'Count',
        'gmv_sum': 'GMV Sum',
        'gmv_mean': 'GMV Mean',
        'orders_sum': 'Orders Sum',
        'orders_mean': 'Orders Mean',
        'avg_score': 'Avg Rating',
        'avg_categories': 'Avg Categories',
        'seller_count': 'Seller Count',
        
        # Insights
        'opportunity_identification': '### 🎯 Opportunity Identification',
        'key_metrics': '### 📊 Key Metrics',
        'high_potential_sellers': '**High Potential Sellers**',
        'average_rating': '**Average Rating**',
        'average_gmv': '**Average GMV**',
        'growth_potential': '**Growth Potential**',
        'pareto_ratio': '**Pareto Ratio**',
        'category_effect': '**Category Effect**',
        'rating_effect': '**Rating Effect**',
        'pareto_text': 'Top 20% contribute {ratio:.1f}% GMV',
        'category_text': 'Multi-category GMV is {effect:.1f}x single-category',
        'rating_text': 'High-rating GMV is {effect:.1f}x low-rating',
        
        # Buttons and Actions
        'export_data': '📥 Export Filtered Data as CSV',
        'download_csv': 'Download CSV File',
        
        # Tiers
        'Platinum': 'Platinum',
        'Gold': 'Gold',
        'Silver': 'Silver', 
        'Bronze': 'Bronze',
        'Basic': 'Basic',
        'All': 'All',
        
        # Footer
        'footer': """
        <div style='text-align: center; color: #666; font-size: 0.9rem;'>
            📊 Olist Business Intelligence Analytics Platform | Based on 1.55M+ Real E-commerce Data | 
            <a href='https://github.com/Quintas0658/olist_ecommerce_project' style='color: #1f77b4;'>Project GitHub</a> | 
            <a href='#' style='color: #1f77b4;'>Technical Docs</a>
        </div>
        """
    }
}

def get_text(key, **kwargs):
    """获取当前语言的文本"""
    lang = st.session_state.get('language', 'zh')
    text = LANGUAGES[lang].get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text

# 页面配置
st.set_page_config(
    page_title=get_text('page_title'),
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
        st.error(f"{get_text('data_load_error')}: {e}")
        return None, None, None, None, None, None

def create_sidebar_filters(seller_analysis):
    """创建侧边栏筛选器"""
    # 语言选择器
    st.sidebar.markdown('<p class="sidebar-header">🌐 Language / 语言</p>', unsafe_allow_html=True)
    language_options = {'中文': 'zh', 'English': 'en'}
    selected_lang = st.sidebar.selectbox(
        '',
        options=list(language_options.keys()),
        index=0 if st.session_state.get('language', 'zh') == 'zh' else 1,
        key='lang_selector'
    )
    
    # 更新语言状态
    if 'language' not in st.session_state or st.session_state.language != language_options[selected_lang]:
        st.session_state.language = language_options[selected_lang]
        st.rerun()
    
    st.sidebar.markdown('<p class="sidebar-header">' + get_text('sidebar_header') + '</p>', unsafe_allow_html=True)
    
    # 卖家层级筛选
    tiers = [get_text('All')] + list(seller_analysis['business_tier'].unique())
    selected_tier = st.sidebar.selectbox(get_text('seller_tier'), tiers)
    
    # GMV范围筛选
    gmv_min, gmv_max = st.sidebar.slider(
        get_text('gmv_range'),
        min_value=float(seller_analysis['total_gmv'].min()),
        max_value=float(seller_analysis['total_gmv'].max()),
        value=(float(seller_analysis['total_gmv'].min()), float(seller_analysis['total_gmv'].max())),
        format="%.0f"
    )
    
    # 评分范围筛选
    rating_min, rating_max = st.sidebar.slider(
        get_text('rating_range'),
        min_value=float(seller_analysis['avg_review_score'].min()),
        max_value=5.0,
        value=(float(seller_analysis['avg_review_score'].min()), 5.0),
        step=0.1
    )
    
    # 州筛选
    states = [get_text('All')] + list(seller_analysis['seller_state'].unique())
    selected_states = st.sidebar.multiselect(get_text('select_states'), states, default=[get_text('All')])
    
    # 品类数筛选
    category_min, category_max = st.sidebar.slider(
        get_text('category_range'),
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
    if filters['tier'] != get_text('All'):
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
    if get_text('All') not in filters['states'] and filters['states']:
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
            label=get_text('total_sellers'),
            value=f"{len(data):,}",
            delta=f"{len(data)/3095*100:.1f}% {get_text('of_total')}"
        )
    
    with col2:
        total_gmv = data['total_gmv'].sum()
        st.metric(
            label=get_text('total_gmv'),
            value=f"R$ {total_gmv:,.0f}",
            delta=f"{total_gmv/13591644*100:.1f}% {get_text('of_total')}"
        )
    
    with col3:
        avg_gmv = data['total_gmv'].mean()
        st.metric(
            label=get_text('avg_gmv'),
            value=f"R$ {avg_gmv:,.0f}",
            delta=f"{(avg_gmv/4393)*100:.1f}% vs platform avg"
        )
    
    with col4:
        avg_rating = data['avg_review_score'].mean()
        st.metric(
            label=get_text('avg_rating'),
            value=f"{avg_rating:.2f}",
            delta=f"{((avg_rating-4.0)/4.0)*100:.1f}% vs 4.0"
        )
    
    with col5:
        avg_orders = data['unique_orders'].mean()
        st.metric(
            label=get_text('avg_orders'),
            value=f"{avg_orders:.1f}",
            delta=f"{(avg_orders/10.7)*100:.1f}% vs platform avg"
        )

def create_tier_distribution_chart(data):
    """创建层级分布图"""
    tier_counts = data['business_tier'].value_counts()
    tier_gmv = data.groupby('business_tier')['total_gmv'].sum()
    
    # 创建双饼图
    fig = make_subplots(
        rows=1, cols=2, 
        specs=[[{'type':'pie'}, {'type':'pie'}]],
        subplot_titles=[
            get_text('tier_distribution') + ' - ' + get_text('count'),
            get_text('tier_distribution') + ' - GMV'
        ]
    )
    
    # 数量分布
    fig.add_trace(go.Pie(
        labels=tier_counts.index,
        values=tier_counts.values,
        name=get_text('count'),
        hole=0.3
    ), row=1, col=1)
    
    # GMV分布
    fig.add_trace(go.Pie(
        labels=tier_gmv.index,
        values=tier_gmv.values,
        name="GMV",
        hole=0.3
    ), row=1, col=2)
    
    fig.update_layout(
        title_text=get_text('tier_distribution'),
        height=400
    )
    
    return fig

def create_gmv_vs_orders_scatter(data):
    """创建GMV与订单数散点图"""
    fig = px.scatter(
        data, 
        x='unique_orders', 
        y='total_gmv',
        color='business_tier',
        size='avg_review_score',
        hover_data=['seller_state', 'category_count'],
        title=get_text('gmv_vs_orders'),
        labels={
            'unique_orders': get_text('avg_orders'),
            'total_gmv': 'GMV (R$)',
            'business_tier': get_text('seller_tier'),
            'avg_review_score': get_text('avg_rating')
        }
    )
    
    fig.update_layout(height=400)
    return fig

def create_geographic_analysis(data):
    """创建地理分析图"""
    # 按州聚合数据
    state_data = data.groupby('seller_state').agg({
        'seller_id': 'count',
        'total_gmv': ['sum', 'mean'],
        'avg_review_score': 'mean'
    }).reset_index()
    
    state_data.columns = ['state', 'seller_count', 'gmv_sum', 'gmv_mean', 'avg_rating']
    
    # 创建四象限散点图
    fig = px.scatter(
        state_data.head(15),  # 只显示前15个州
        x='seller_count',
        y='gmv_sum', 
        size='gmv_mean',
        color='avg_rating',
        text='state',
        title=get_text('geographic_distribution'),
        labels={
            'seller_count': get_text('seller_count'),
            'gmv_sum': get_text('gmv_sum'),
            'gmv_mean': get_text('gmv_mean'),
            'avg_rating': get_text('avg_rating')
        }
    )
    
    fig.update_traces(textposition="top center")
    fig.update_layout(height=500)
    
    return fig

def create_performance_radar(data, all_data=None):
    """创建性能雷达图"""
    if all_data is None:
        all_data = data
    
    # 按层级聚合数据
    tier_performance = data.groupby('business_tier').agg({
        'total_gmv': 'mean',
        'unique_orders': 'mean', 
        'avg_review_score': 'mean',
        'category_count': 'mean',
        'avg_shipping_days': 'mean'
    }).reset_index()
    
    # 归一化处理 (相对于全部数据)
    for col in ['total_gmv', 'unique_orders', 'category_count']:
        tier_performance[f'{col}_norm'] = tier_performance[col] / all_data[col].max()
    
    tier_performance['rating_norm'] = tier_performance['avg_review_score'] / 5.0
    tier_performance['shipping_norm'] = 1 - (tier_performance['avg_shipping_days'] / all_data['avg_shipping_days'].max())
    
    # 创建雷达图
    fig = go.Figure()
    
    categories = [
        get_text('total_gmv'),
        get_text('avg_orders'), 
        get_text('avg_rating'),
        get_text('avg_categories'),
        'Shipping Speed'
    ]
    
    for tier in tier_performance['business_tier'].unique():
        tier_data = tier_performance[tier_performance['business_tier'] == tier].iloc[0]
        values = [
            tier_data['total_gmv_norm'],
            tier_data['unique_orders_norm'],
            tier_data['rating_norm'],
            tier_data['category_count_norm'],
            tier_data['shipping_norm']
        ]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=tier
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        title=get_text('performance_radar'),
        height=500
    )
    
    return fig

def create_correlation_heatmap(data):
    """创建相关性热图"""
    # 选择数值列
    numeric_cols = ['total_gmv', 'unique_orders', 'avg_review_score', 
                   'category_count', 'avg_shipping_days', 'unique_customers']
    
    # 计算相关性矩阵
    corr_matrix = data[numeric_cols].corr()
    
    # 创建热图
    fig = px.imshow(
        corr_matrix,
        title=get_text('correlation_heatmap'),
        color_continuous_scale='RdBu_r',
        aspect="auto"
    )
    
    fig.update_layout(height=500)
    return fig

def display_business_insights(data):
    """显示商业洞察"""
    st.markdown(get_text('insights_title'))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.markdown(get_text('opportunity_identification'))
        
        # 高潜力卖家识别
        high_potential = data[
            (data['avg_review_score'] >= 4.2) & 
            (data['total_gmv'] < data['total_gmv'].median()) &
            (data['unique_orders'] >= 5)
        ]
        
        st.write(f"{get_text('high_potential_sellers')}: {len(high_potential)}")
        st.write(f"{get_text('average_rating')}: {high_potential['avg_review_score'].mean():.2f}")
        st.write(f"{get_text('average_gmv')}: R$ {high_potential['total_gmv'].mean():,.0f}")
        
        if len(high_potential) > 0:
            potential_growth = (data['total_gmv'].median() - high_potential['total_gmv'].mean()) * len(high_potential)
            st.write(f"{get_text('growth_potential')}: R$ {potential_growth:,.0f}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.markdown(get_text('key_metrics'))
        
        # 计算关键比率
        pareto_threshold = int(len(data) * 0.2)
        top_20_gmv = data.nlargest(pareto_threshold, 'total_gmv')['total_gmv'].sum()
        pareto_ratio = top_20_gmv / data['total_gmv'].sum() * 100
        
        st.write(f"{get_text('pareto_ratio')}: {get_text('pareto_text', ratio=pareto_ratio)}")
        
        # 多品类效应
        single_cat = data[data['category_count'] == 1]['total_gmv'].mean()
        multi_cat = data[data['category_count'] > 1]['total_gmv'].mean()
        if single_cat > 0:
            category_effect = multi_cat / single_cat
            st.write(f"{get_text('category_effect')}: {get_text('category_text', effect=category_effect)}")
        
        # 评分效应
        high_rating = data[data['avg_review_score'] >= 4.0]['total_gmv'].mean()
        low_rating = data[data['avg_review_score'] < 3.5]['total_gmv'].mean()
        if low_rating > 0:
            rating_effect = high_rating / low_rating
            st.write(f"{get_text('rating_effect')}: {get_text('rating_text', effect=rating_effect)}")
        
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    """主函数"""
    # 初始化语言状态
    if 'language' not in st.session_state:
        st.session_state.language = 'zh'
    
    # 页面标题
    st.markdown(f'<h1 class="main-header">{get_text("page_header")}</h1>', unsafe_allow_html=True)
    
    # 加载数据
    with st.spinner(get_text('loading_data')):
        seller_profile, seller_analysis, orders, order_items, reviews, products = load_data()
    
    if seller_analysis is None:
        st.error(get_text('data_load_error'))
        return
    
    # 侧边栏筛选器
    filters = create_sidebar_filters(seller_analysis)
    
    # 应用筛选器
    filtered_data = apply_filters(seller_analysis, filters)
    
    if len(filtered_data) == 0:
        st.warning(get_text('no_data_warning'))
        return
    
    # 显示筛选结果
    st.info(get_text('current_display', 
                    count=len(filtered_data), 
                    percentage=len(filtered_data)/len(seller_analysis)*100))
    
    # KPI指标卡片
    display_kpi_metrics(filtered_data)
    
    # 创建标签页
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        get_text('tab_overview'), 
        get_text('tab_tier'), 
        get_text('tab_geo'), 
        get_text('tab_performance'), 
        get_text('tab_insights')
    ])
    
    with tab1:
        st.markdown(get_text('overview_title'))
        
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
        st.markdown(get_text('tier_title'))
        
        # 层级统计表
        tier_summary = filtered_data.groupby('business_tier').agg({
            'seller_id': 'count',
            'total_gmv': ['sum', 'mean'],
            'unique_orders': ['sum', 'mean'],
            'avg_review_score': 'mean',
            'category_count': 'mean'
        }).round(2)
        
        tier_summary.columns = [
            get_text('count'), 
            get_text('gmv_sum'), 
            get_text('gmv_mean'), 
            get_text('orders_sum'), 
            get_text('orders_mean'), 
            get_text('avg_score'), 
            get_text('avg_categories')
        ]
        
        st.markdown(get_text('tier_stats_table'))
        st.dataframe(tier_summary, use_container_width=True)
        
        # 性能雷达图
        radar_fig = create_performance_radar(filtered_data, seller_analysis)
        st.plotly_chart(radar_fig, use_container_width=True)
    
    with tab3:
        st.markdown(get_text('geo_title'))
        
        geo_fig = create_geographic_analysis(filtered_data)
        st.plotly_chart(geo_fig, use_container_width=True)
        
        # 州级详细数据
        state_detail = filtered_data.groupby('seller_state').agg({
            'seller_id': 'count',
            'total_gmv': ['sum', 'mean'],
            'avg_review_score': 'mean'
        }).round(2)
        state_detail.columns = [
            get_text('seller_count'), 
            get_text('gmv_sum'), 
            get_text('gmv_mean'), 
            get_text('avg_score')
        ]
        state_detail = state_detail.sort_values(get_text('gmv_sum'), ascending=False)
        
        st.markdown(get_text('state_detail_table'))
        st.dataframe(state_detail, use_container_width=True)
    
    with tab4:
        st.markdown(get_text('performance_title'))
        
        corr_fig = create_correlation_heatmap(filtered_data)
        st.plotly_chart(corr_fig, use_container_width=True)
        
        # 性能分布
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(get_text('gmv_distribution'))
            gmv_hist = px.histogram(filtered_data, x='total_gmv', nbins=50, 
                                   title=get_text('gmv_hist_title'))
            st.plotly_chart(gmv_hist, use_container_width=True)
        
        with col2:
            st.markdown(get_text('rating_distribution'))
            rating_hist = px.histogram(filtered_data, x='avg_review_score', nbins=30,
                                      title=get_text('rating_hist_title'))
            st.plotly_chart(rating_hist, use_container_width=True)
    
    with tab5:
        display_business_insights(filtered_data)
        
        # 详细数据表
        st.markdown(get_text('filtered_data_table'))
        display_columns = [
            'seller_id', 'seller_state', 'business_tier', 'total_gmv', 
            'unique_orders', 'avg_review_score', 'category_count', 'avg_shipping_days'
        ]
        
        st.dataframe(
            filtered_data[display_columns].sort_values('total_gmv', ascending=False),
            use_container_width=True
        )
        
        # 数据导出
        if st.button(get_text('export_data')):
            csv = filtered_data.to_csv(index=False)
            st.download_button(
                label=get_text('download_csv'),
                data=csv,
                file_name=f"olist_filtered_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

    # 页脚
    st.markdown("---")
    st.markdown(get_text('footer'), unsafe_allow_html=True)

if __name__ == "__main__":
    main() 