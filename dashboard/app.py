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
import os
import sys
import warnings
warnings.filterwarnings('ignore')

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# 导入月度分析模块
MonthlySellerAnalyzer = None
try:
    from src.monthly_analysis import MonthlySellerAnalyzer
    MONTHLY_ANALYSIS_AVAILABLE = True
except ImportError as e:
    MONTHLY_ANALYSIS_AVAILABLE = False
    st.sidebar.warning("⚠️ 月度分析模块不可用")

# ======================== 语言管理系统 ========================

# 初始化session state
if 'language' not in st.session_state:
    st.session_state.language = 'zh'

# 中英文文本字典
TEXTS = {
    'zh': {
        # 页面标题和基本文本
        'page_title': '🚀 Olist商业智能分析平台',
        'loading': '🔄 正在加载数据...',
        'data_load_error': '❌ 数据加载失败，请检查数据文件',
        'no_data_warning': '⚠️ 当前筛选条件下没有数据，请调整筛选器设置',
        'current_display': '📊 当前显示',
        'sellers': '个卖家',
        'of_total': '占总数的',
        
        # 侧边栏
        'sidebar_title': '🔍 数据筛选器',
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
        
        # 标签页
        'tab_overview': '📊 总览分析',
        'tab_tier': '🏆 层级分析',
        'tab_geo': '🗺️ 地理分析',
        'tab_performance': '📈 性能分析',
        'tab_insights': '🧠 智能洞察',
        'tab_monthly': '📅 月度分析',
        
        # 图表标题
        'platform_overview': '📊 平台总览分析',
        'tier_distribution': '🏆 卖家层级分布',
        'quantity_distribution': '数量分布',
        'gmv_distribution': 'GMV分布',
        'gmv_vs_orders': '💰 GMV vs 订单数关联分析',
        'tier_analysis': '🏆 卖家层级深度分析',
        'tier_stats': '📋 层级统计表',
        'performance_radar': '🎯 层级性能雷达图',
        'geo_analysis': '🗺️ 地理分布分析',
        'geo_distribution': '📊 地理四象限分析',
        'state_details': '📊 州级数据详情',
        'performance_corr': '📈 性能相关性分析',
        'correlation_heatmap': '🔥 业务指标相关性热力图',
        'gmv_dist': '💰 GMV分布',
        'rating_dist': '⭐ 评分分布',
        'gmv_histogram': 'GMV分布直方图',
        'rating_histogram': '评分分布直方图',
        
        # 洞察分析
        'smart_insights': '🧠 智能商业洞察',
        'opportunity_id': '🎯 机会识别',
        'high_potential_sellers': '高潜力卖家',
        'avg_rating_text': '平均评分',
        'avg_gmv_text': '平均GMV',
        'growth_potential': '增长潜力',
        'key_metrics': '📊 关键指标',
        'pareto_ratio': '帕累托比例',
        'top_20_contrib': 'Top 20%贡献',
        'gmv_text': 'GMV',
        'category_effect': '品类效应',
        'multi_cat_gmv': '多品类GMV是单品类的',
        'times': '倍',
        'rating_effect': '评分效应',
        'high_rating_gmv': '高评分GMV是低评分的',
        
        # 表格列名
        'seller_count': '数量',
        'gmv_sum': 'GMV总和',
        'gmv_mean': 'GMV均值',
        'orders_sum': '订单总数',
        'orders_mean': '订单均值',
        'avg_score': '平均评分',
        'avg_categories': '平均品类数',
        'seller_quantity': '卖家数量',
        
        # 数据导出
        'filtered_data': '📋 筛选结果数据',
        'export_csv': '📥 导出筛选数据为CSV',
        'download_csv': '下载CSV文件',
        
        # 页脚
        'footer': '📊 Olist商业智能分析平台 | 基于155万+真实电商数据',
        'github_link': '项目GitHub',
        'tech_docs': '技术文档',
        
        # 其他
        'all': 'All',
        'individual': '个',
        'pieces': '个',
        'percent': '%',
        
        # 雷达图相关
        'radar_categories': ['GMV', '评分', '品类数', '发货效率', '交付成功率'],
        'overall_average': '全体平均',
        'radar_title_single': '🎯 {}层级 vs 全体平均性能对比',
        'radar_title_multi': '🎯 各层级卖家性能雷达图',
        
        # 月度分析相关
        'monthly_analysis': '📅 月度卖家动态分析',
        'month_selection': '📆 选择分析月份',
        'lookback_months': '⏳ 回望月数',
        'tier_flow_matrix': '🔄 层级流转矩阵',
        'tier_stability': '⚖️ 层级稳定性',
        'monthly_trends': '📈 月度趋势',
        'upgrade_sellers': '⬆️ 升级卖家',
        'downgrade_sellers': '⬇️ 降级卖家',
        'stable_sellers': '🔒 稳定卖家',
        'volatile_sellers': '🌊 波动卖家',
        'data_timespan': '数据时间跨度',
        'analyzing_months': '正在分析月份',
        'monthly_kpi': '📊 月度关键指标',
        'active_sellers_month': '活跃卖家数',
        'monthly_gmv': '月度GMV',
        'avg_rating_month': '平均评分',
        'tier_changes': '层级变化情况',
        'stability_rate': '稳定率',
        'no_monthly_data': '⚠️ 暂无月度数据，请检查数据源',
    },
    'en': {
        # 页面标题和基本文本
        'page_title': '🚀 Olist Business Intelligence Platform',
        'loading': '🔄 Loading data...',
        'data_load_error': '❌ Data loading failed, please check data files',
        'no_data_warning': '⚠️ No data under current filters, please adjust filter settings',
        'current_display': '📊 Currently displaying',
        'sellers': 'sellers',
        'of_total': 'of total',
        
        # 侧边栏
        'sidebar_title': '🔍 Data Filters',
        'seller_tier': '🏆 Seller Tier',
        'gmv_range': '💰 GMV Range (R$)',
        'rating_range': '⭐ Rating Range',
        'select_states': '📍 Select States',
        'category_range': '🎁 Category Count Range',
        
        # KPI指标
        'total_sellers': '🏪 Total Sellers',
        'total_gmv': '💰 Total GMV',
        'avg_gmv': '📊 Average GMV',
        'avg_rating': '⭐ Average Rating',
        'avg_orders': '📦 Average Orders',
        
        # 标签页
        'tab_overview': '📊 Overview',
        'tab_tier': '🏆 Tier Analysis',
        'tab_geo': '🗺️ Geographic',
        'tab_performance': '📈 Performance',
        'tab_insights': '🧠 Smart Insights',
        'tab_monthly': '📅 Monthly Analysis',
        
        # 图表标题
        'platform_overview': '📊 Platform Overview Analysis',
        'tier_distribution': '🏆 Seller Tier Distribution',
        'quantity_distribution': 'Quantity Distribution',
        'gmv_distribution': 'GMV Distribution',
        'gmv_vs_orders': '💰 GMV vs Orders Correlation',
        'tier_analysis': '🏆 Seller Tier Deep Analysis',
        'tier_stats': '📋 Tier Statistics',
        'performance_radar': '🎯 Tier Performance Radar',
        'geo_analysis': '🗺️ Geographic Distribution Analysis',
        'geo_distribution': '📊 Geographic Quadrant Analysis',
        'state_details': '📊 State-level Details',
        'performance_corr': '📈 Performance Correlation Analysis',
        'correlation_heatmap': '🔥 Business Metrics Correlation Heatmap',
        'gmv_dist': '💰 GMV Distribution',
        'rating_dist': '⭐ Rating Distribution',
        'gmv_histogram': 'GMV Distribution Histogram',
        'rating_histogram': 'Rating Distribution Histogram',
        
        # 洞察分析
        'smart_insights': '🧠 Smart Business Insights',
        'opportunity_id': '🎯 Opportunity Identification',
        'high_potential_sellers': 'High-potential Sellers',
        'avg_rating_text': 'Average Rating',
        'avg_gmv_text': 'Average GMV',
        'growth_potential': 'Growth Potential',
        'key_metrics': '📊 Key Metrics',
        'pareto_ratio': 'Pareto Ratio',
        'top_20_contrib': 'Top 20% contribute',
        'gmv_text': 'GMV',
        'category_effect': 'Category Effect',
        'multi_cat_gmv': 'Multi-category GMV is',
        'times': 'times of single-category',
        'rating_effect': 'Rating Effect',
        'high_rating_gmv': 'High-rating GMV is',
        
        # 表格列名
        'seller_count': 'Count',
        'gmv_sum': 'GMV Sum',
        'gmv_mean': 'GMV Mean',
        'orders_sum': 'Orders Sum',
        'orders_mean': 'Orders Mean',
        'avg_score': 'Avg Rating',
        'avg_categories': 'Avg Categories',
        'seller_quantity': 'Seller Count',
        
        # 数据导出
        'filtered_data': '📋 Filtered Results',
        'export_csv': '📥 Export Filtered Data as CSV',
        'download_csv': 'Download CSV File',
        
        # 页脚
        'footer': '📊 Olist Business Intelligence Platform | Based on 1.55M+ real e-commerce data',
        'github_link': 'Project GitHub',
        'tech_docs': 'Technical Documentation',
        
        # 其他
        'all': 'All',
        'individual': '',
        'pieces': '',
        'percent': '%',
        
        # 雷达图相关
        'radar_categories': ['GMV', 'Rating', 'Categories', 'Shipping Efficiency', 'Delivery Success Rate'],
        'overall_average': 'Overall Average',
        'radar_title_single': '🎯 {} Tier vs Overall Average Performance',
        'radar_title_multi': '🎯 Seller Performance Radar by Tier',
        
        # 月度分析相关
        'monthly_analysis': '📅 Monthly Seller Dynamic Analysis',
        'month_selection': '📆 Select Analysis Month',
        'lookback_months': '⏳ Lookback Months',
        'tier_flow_matrix': '🔄 Tier Flow Matrix',
        'tier_stability': '⚖️ Tier Stability',
        'monthly_trends': '📈 Monthly Trends',
        'upgrade_sellers': '⬆️ Upgrading Sellers',
        'downgrade_sellers': '⬇️ Downgrading Sellers',
        'stable_sellers': '🔒 Stable Sellers',
        'volatile_sellers': '🌊 Volatile Sellers',
        'data_timespan': 'Data Timespan',
        'analyzing_months': 'Analyzing Months',
        'monthly_kpi': '📊 Monthly Key Indicators',
        'active_sellers_month': 'Active Sellers',
        'monthly_gmv': 'Monthly GMV',
        'avg_rating_month': 'Average Rating',
        'tier_changes': 'Tier Changes',
        'stability_rate': 'Stability Rate',
        'no_monthly_data': '⚠️ No monthly data available, please check data source',
    }
}

def get_text(key):
    """获取当前语言的文本"""
    return TEXTS[st.session_state.language].get(key, key)

def create_language_selector():
    """创建语言选择器"""
    col1, col2, col3 = st.columns([1, 1, 8])
    
    with col1:
        if st.button("🇨🇳 中文", key="btn_zh"):
            st.session_state.language = 'zh'
            st.rerun()
    
    with col2:
        if st.button("🇺🇸 English", key="btn_en"):
            st.session_state.language = 'en'
            st.rerun()
    
    return st.session_state.language

def classify_seller_tier(row):
    """卖家分级函数"""
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
        # 尝试加载处理后的数据
        if os.path.exists('data/seller_profile_processed.csv'):
            seller_profile = pd.read_csv('data/seller_profile_processed.csv')
        else:
            # 如果处理后的数据不存在，创建示例数据
            seller_profile = create_sample_data()
        
        # 尝试加载原始数据用于深度分析
        orders = None
        order_items = None
        reviews = None
        products = None
        
        try:
            if os.path.exists('data/olist_orders_dataset.csv'):
                orders = pd.read_csv('data/olist_orders_dataset.csv')
                orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
                orders['year_month'] = orders['order_purchase_timestamp'].dt.to_period('M').astype(str)
        except:
            pass
            
        try:
            if os.path.exists('data/olist_order_items_dataset.csv'):
                order_items = pd.read_csv('data/olist_order_items_dataset.csv')
        except:
            pass
            
        try:
            if os.path.exists('data/olist_order_reviews_dataset.csv'):
                reviews = pd.read_csv('data/olist_order_reviews_dataset.csv')
        except:
            pass
            
        try:
            if os.path.exists('data/olist_products_dataset.csv'):
                products = pd.read_csv('data/olist_products_dataset.csv')
        except:
            pass
        
        # 加载分析结果
        try:
            if os.path.exists('data/seller_analysis_results.csv'):
                seller_analysis = pd.read_csv('data/seller_analysis_results.csv')
            else:
                # 如果没有分析结果，创建简单分级
                seller_profile['business_tier'] = seller_profile.apply(classify_seller_tier, axis=1)
                seller_analysis = seller_profile
        except:
            seller_profile['business_tier'] = seller_profile.apply(classify_seller_tier, axis=1)
            seller_analysis = seller_profile
        
        return seller_profile, seller_analysis, orders, order_items, reviews, products
    except Exception as e:
        st.error(f"{get_text('data_load_error')}: {e}")
        return None, None, None, None, None, None

def create_sample_data():
    """创建示例数据用于演示"""
    np.random.seed(42)
    
    # 巴西州名列表
    states = ['SP', 'RJ', 'MG', 'RS', 'PR', 'SC', 'BA', 'GO', 'PE', 'CE', 
              'PA', 'DF', 'ES', 'PB', 'RN', 'MT', 'MS', 'PI', 'AL', 'RO']
    
    n_sellers = 1000
    
    # 生成示例数据
    data = {
        'seller_id': [f'seller_{i:04d}' for i in range(n_sellers)],
        'seller_state': np.random.choice(states, n_sellers),
        'total_gmv': np.random.lognormal(8, 1.5, n_sellers),
        'unique_orders': np.random.poisson(20, n_sellers) + 1,
        'avg_review_score': np.random.beta(8, 2, n_sellers) * 5,
        'category_count': np.random.poisson(2, n_sellers) + 1,
        'avg_shipping_days': np.random.gamma(2, 3, n_sellers) + 1,
        'delivery_success_rate': np.random.beta(9, 1, n_sellers),
        'bad_review_rate': np.random.beta(1, 9, n_sellers),
        'revenue_per_order': np.random.lognormal(4, 0.8, n_sellers),
        'items_per_order': np.random.gamma(2, 1, n_sellers) + 1
    }
    
    df = pd.DataFrame(data)
    
    # 确保数据的合理性
    df['total_gmv'] = np.clip(df['total_gmv'], 100, 1000000)
    df['unique_orders'] = np.clip(df['unique_orders'], 1, 1000)
    df['avg_review_score'] = np.clip(df['avg_review_score'], 1, 5)
    df['category_count'] = np.clip(df['category_count'], 1, 20)
    df['avg_shipping_days'] = np.clip(df['avg_shipping_days'], 1, 30)
    df['delivery_success_rate'] = np.clip(df['delivery_success_rate'], 0.5, 1.0)
    df['bad_review_rate'] = np.clip(df['bad_review_rate'], 0, 0.5)
    
    return df

def create_sidebar_filters(seller_analysis):
    """创建侧边栏筛选器"""
    st.sidebar.markdown(f'<p class="sidebar-header">{get_text("sidebar_title")}</p>', unsafe_allow_html=True)
    
    # 卖家层级筛选
    tiers = [get_text('all')] + list(seller_analysis['business_tier'].unique())
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
    states = [get_text('all')] + list(seller_analysis['seller_state'].unique())
    selected_states = st.sidebar.multiselect(get_text('select_states'), states, default=[get_text('all')])
    
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
    if filters['tier'] != get_text('all'):
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
    if get_text('all') not in filters['states'] and filters['states']:
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
            label=get_text("total_sellers"),
            value=f"{len(data):,}",
            delta=f"{len(data)/3095*100:.1f}{get_text('percent')} {get_text('of_total')}"
        )
    
    with col2:
        total_gmv = data['total_gmv'].sum()
        st.metric(
            label=get_text("total_gmv"),
            value=f"R$ {total_gmv:,.0f}",
            delta=f"{total_gmv/13591644*100:.1f}{get_text('percent')} {get_text('of_total')}"
        )
    
    with col3:
        avg_rating = data['avg_review_score'].mean()
        st.metric(
            label=get_text("avg_rating"),
            value=f"{avg_rating:.2f}",
            delta=f"vs 3.97 overall"
        )
    
    with col4:
        total_orders = data['unique_orders'].sum()
        st.metric(
            label=get_text("avg_orders"),
            value=f"{total_orders:,}",
            delta=f"{total_orders/100010*100:.1f}{get_text('percent')} {get_text('of_total')}"
        )
    
    with col5:
        avg_categories = data['category_count'].mean()
        st.metric(
            label=get_text("avg_categories"),
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
        subplot_titles=(get_text('quantity_distribution'), get_text('gmv_distribution')),
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
            name=get_text('seller_quantity'),
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
            name=get_text('gmv_text'),
            marker_colors=[colors.get(tier, '#1f77b4') for tier in tier_stats['Tier']],
            textinfo='label+percent',
            textposition='inside'
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        title_text=get_text('tier_distribution'),
        height=400,
        showlegend=False
    )
    
    return fig

def create_gmv_vs_orders_scatter(data):
    """创建GMV vs 订单数散点图"""
    # 根据语言设置标签
    labels_dict = {
        'unique_orders': 'Orders' if st.session_state.language == 'en' else '订单数',
        'total_gmv': 'GMV (R$)',
        'business_tier': 'Seller Tier' if st.session_state.language == 'en' else '卖家层级',
        'avg_review_score': 'Avg Rating' if st.session_state.language == 'en' else '平均评分'
    }
    
    fig = px.scatter(
        data, 
        x='unique_orders', 
        y='total_gmv',
        color='business_tier',
        size='avg_review_score',
        hover_data=['seller_state', 'category_count', 'avg_shipping_days'],
        title=get_text('gmv_vs_orders'),
        labels=labels_dict,
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
    
    # 根据语言设置列名
    if st.session_state.language == 'en':
        state_stats.columns = ['Seller Count', 'GMV Sum', 'GMV Mean', 'Avg Rating', 'Avg Categories']
        chart_titles = ('Seller Count Distribution', 'GMV Sum Distribution', 'GMV Mean Distribution', 'Avg Rating Distribution')
        sort_col = 'GMV Sum'
    else:
        state_stats.columns = ['卖家数量', 'GMV总和', 'GMV均值', '平均评分', '平均品类数']
        chart_titles = ('卖家数量分布', 'GMV总和分布', 'GMV均值分布', '平均评分分布')
        sort_col = 'GMV总和'
    
    state_stats = state_stats.reset_index().sort_values(sort_col, ascending=False).head(15)
    
    # 创建地理分布图
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=chart_titles,
        specs=[[{"type": "bar"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "bar"}]]
    )
    
    # 获取列名（根据语言）
    seller_count_col = state_stats.columns[1]  # 卖家数量/Seller Count
    gmv_sum_col = state_stats.columns[2]       # GMV总和/GMV Sum  
    gmv_mean_col = state_stats.columns[3]      # GMV均值/GMV Mean
    avg_rating_col = state_stats.columns[4]    # 平均评分/Avg Rating
    
    # 卖家数量
    fig.add_trace(
        go.Bar(x=state_stats['seller_state'], y=state_stats[seller_count_col], 
               name=seller_count_col, marker_color='lightblue'),
        row=1, col=1
    )
    
    # GMV总和
    fig.add_trace(
        go.Bar(x=state_stats['seller_state'], y=state_stats[gmv_sum_col], 
               name=gmv_sum_col, marker_color='orange'),
        row=1, col=2
    )
    
    # GMV均值
    fig.add_trace(
        go.Bar(x=state_stats['seller_state'], y=state_stats[gmv_mean_col], 
               name=gmv_mean_col, marker_color='green'),
        row=2, col=1
    )
    
    # 平均评分
    fig.add_trace(
        go.Bar(x=state_stats['seller_state'], y=state_stats[avg_rating_col], 
               name=avg_rating_col, marker_color='purple'),
        row=2, col=2
    )
    
    fig.update_layout(
        title_text=get_text('geo_analysis'),
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
        tier_performance.loc[get_text('overall_average')] = overall_performance
    
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
    
    categories = get_text('radar_categories')
    colors = ['#FFD700', '#FFA500', '#C0C0C0', '#CD7F32', '#808080', '#FF6B6B']
    
    for i, tier in enumerate(normalized_performance.index):
        values = normalized_performance.loc[tier].values.tolist()
        values += values[:1]  # 闭合雷达图
        
        # 为全体平均设置特殊样式
        if tier == get_text('overall_average'):
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
        overall_avg_text = get_text('overall_average')
        selected_tier = tier_performance.index[0] if overall_avg_text not in tier_performance.index else [t for t in tier_performance.index if t != overall_avg_text][0]
        title = get_text('radar_title_single').format(selected_tier)
    else:
        title = get_text('radar_title_multi')
    
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
        title=get_text('correlation_heatmap'),
        color_continuous_scale='RdBu_r',
        aspect='auto'
    )
    
    fig.update_layout(height=500)
    return fig

def display_business_insights(data):
    """显示商业洞察"""
    st.markdown(f"## {get_text('smart_insights')}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.markdown(f"### {get_text('opportunity_id')}")
        
        # 高潜力卖家识别
        high_potential = data[
            (data['avg_review_score'] >= 4.2) & 
            (data['total_gmv'] < data['total_gmv'].median()) &
            (data['unique_orders'] >= 5)
        ]
        
        st.write(f"**{get_text('high_potential_sellers')}**: {len(high_potential)}{get_text('individual')}")
        st.write(f"**{get_text('avg_rating_text')}**: {high_potential['avg_review_score'].mean():.2f}")
        st.write(f"**{get_text('avg_gmv_text')}**: R$ {high_potential['total_gmv'].mean():,.0f}")
        
        if len(high_potential) > 0:
            potential_growth = (data['total_gmv'].median() - high_potential['total_gmv'].mean()) * len(high_potential)
            st.write(f"**{get_text('growth_potential')}**: R$ {potential_growth:,.0f}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.markdown(f"### {get_text('key_metrics')}")
        
        # 计算关键比率
        pareto_threshold = int(len(data) * 0.2)
        top_20_gmv = data.nlargest(pareto_threshold, 'total_gmv')['total_gmv'].sum()
        pareto_ratio = top_20_gmv / data['total_gmv'].sum() * 100
        
        st.write(f"**{get_text('pareto_ratio')}**: {get_text('top_20_contrib')}{pareto_ratio:.1f}{get_text('percent')}{get_text('gmv_text')}")
        
        # 多品类效应
        single_cat = data[data['category_count'] == 1]['total_gmv'].mean()
        multi_cat = data[data['category_count'] > 1]['total_gmv'].mean()
        if single_cat > 0:
            category_effect = multi_cat / single_cat
            st.write(f"**{get_text('category_effect')}**: {get_text('multi_cat_gmv')}{category_effect:.1f}{get_text('times')}")
        
        # 评分效应
        high_rating = data[data['avg_review_score'] >= 4.0]['total_gmv'].mean()
        low_rating = data[data['avg_review_score'] < 3.5]['total_gmv'].mean()
        if low_rating > 0:
            rating_effect = high_rating / low_rating
            st.write(f"**{get_text('rating_effect')}**: {get_text('high_rating_gmv')}{rating_effect:.1f}{get_text('times')}")
        
        st.markdown('</div>', unsafe_allow_html=True)

def show_monthly_analysis():
    """显示月度分析"""
    
    # 检查模块可用性
    if not monthly_analyzer_available:
        if st.session_state.language == 'zh':
            st.error("❌ 月度分析模块不可用")
            st.info("📝 请确保 src/monthly_analysis.py 文件存在且正确配置")
        else:
            st.error("❌ Monthly Analysis module not available")
            st.info("📝 Please ensure src/monthly_analysis.py exists and is properly configured")
        return
    
    if st.session_state.language == 'zh':
        st.title("📅 月度卖家层级分析")
        st.markdown("---")
        
        # 创建分析器
        analyzer = MonthlySellerAnalyzer(data_pipeline)
        available_months = analyzer.get_available_months()
        
        if not available_months:
            st.error("❌ 没有可用的月度数据")
            return
        
        # 侧边栏控制
        st.sidebar.markdown("### 📊 分析配置")
        
        # 分析类型选择
        analysis_type = st.sidebar.selectbox(
            "🔍 选择分析类型",
            ["同比环比分析", "多月轨迹分析", "层级流转分析"],
            help="选择不同的分析维度"
        )
        
        if analysis_type == "同比环比分析":
            # 同比环比分析
            st.subheader("📈 同比环比分析")
            
            # 月份选择
            selected_month = st.selectbox(
                "📅 选择目标月份",
                available_months,
                index=len(available_months)-1,  # 默认最新月份
                help="将分析此月份与环比（上月）、同比（去年同月）的对比"
            )
            
            # 回望期设置
            lookback_months = st.slider("📆 数据回望月数", 1, 12, 3, 
                                      help="计算卖家指标时回望的历史月份数")
            
            if st.button("🔍 开始同比环比分析", type="primary"):
                with st.spinner("🔄 正在进行同比环比分析..."):
                    # 先构建目标月份画像
                    analyzer.build_monthly_seller_profile(selected_month, lookback_months)
                    
                    # 执行同比环比分析
                    comparison_result = analyzer.analyze_period_comparison(selected_month)
                    
                    if comparison_result and ('mom_comparison' in comparison_result or 'yoy_comparison' in comparison_result):
                        # 显示分析结果
                        display_comparison_results(comparison_result, selected_month)
                    else:
                        st.warning("⚠️ 无法获取对比数据，请检查历史月份数据")
        
        elif analysis_type == "多月轨迹分析":
            # 多月轨迹分析
            st.subheader("🛤️ 卖家轨迹分析")
            
            # 月份范围选择
            col1, col2 = st.columns(2)
            with col1:
                start_month = st.selectbox("📅 起始月份", available_months, 
                                         index=max(0, len(available_months)-6))
            with col2:
                end_month = st.selectbox("📅 结束月份", available_months,
                                       index=len(available_months)-1)
            
            # 参数设置
            min_months = st.slider("📊 最少数据月数", 2, 6, 3,
                                 help="卖家至少需要的有效月份数据")
            
            # 生成月份列表
            start_idx = available_months.index(start_month)
            end_idx = available_months.index(end_month)
            if start_idx <= end_idx:
                analysis_months = available_months[start_idx:end_idx+1]
                st.info(f"📊 将分析 {len(analysis_months)} 个月份: {', '.join(analysis_months)}")
                
                if st.button("🔍 开始轨迹分析", type="primary"):
                    with st.spinner("🔄 正在分析卖家轨迹..."):
                        trajectory_result = analyzer.analyze_seller_trajectory(analysis_months, min_months)
                        
                        if 'error' not in trajectory_result:
                            display_trajectory_results(trajectory_result)
                        else:
                            st.error(f"❌ {trajectory_result['error']}")
            else:
                st.error("❌ 起始月份不能晚于结束月份")
        
        else:  # 层级流转分析
            # 原有的层级流转分析
            st.subheader("🔄 层级流转分析")
            
            # 月份选择
            start_month = st.selectbox("📅 起始月份", available_months, 
                                     index=max(0, len(available_months)-3))
            end_month = st.selectbox("📅 结束月份", available_months,
                                   index=len(available_months)-1)
            
            lookback_months = st.slider("📆 数据回望月数", 1, 12, 3)
            
            # 生成月份列表
            start_idx = available_months.index(start_month)
            end_idx = available_months.index(end_month)
            if start_idx <= end_idx:
                analysis_months = available_months[start_idx:end_idx+1]
                
                if st.button("🔍 开始层级流转分析", type="primary"):
                    with st.spinner("🔄 正在分析层级流转..."):
                        # 构建选定月份的画像
                        for month in analysis_months:
                            analyzer.build_monthly_seller_profile(month, lookback_months)
                        
                        # 分析层级变化
                        flow_result = analyzer.analyze_tier_changes(analysis_months)
                        
                        if not flow_result.empty and isinstance(flow_result, dict):
                            display_flow_results(flow_result, analysis_months)
                        else:
                            st.warning("⚠️ 暂无层级流转数据")
            else:
                st.error("❌ 起始月份不能晚于结束月份")
    
    else:
        # English version
        st.title("📅 Monthly Seller Tier Analysis")
        st.markdown("---")
        
        # 创建分析器
        analyzer = MonthlySellerAnalyzer(data_pipeline)
        available_months = analyzer.get_available_months()
        
        if not available_months:
            st.error("❌ No monthly data available")
            return
        
        # Sidebar controls
        st.sidebar.markdown("### 📊 Analysis Configuration")
        
        # Analysis type selection
        analysis_type = st.sidebar.selectbox(
            "🔍 Select Analysis Type",
            ["Period Comparison", "Trajectory Analysis", "Tier Flow Analysis"],
            help="Choose different analysis dimensions"
        )
        
        # 英文版本的实现类似...
        st.info("🚧 English interface for new features coming soon...")


def display_comparison_results(comparison_result, target_month):
    """显示同比环比分析结果"""
    st.markdown("### 📊 分析结果")
    
    # 环比分析
    if comparison_result.get('mom_comparison'):
        mom_data = comparison_result['mom_comparison']
        st.markdown("#### 📈 环比分析 (Month-over-Month)")
        
        col1, col2, col3, col4 = st.columns(4)
        stats = mom_data['summary_stats']
        
        with col1:
            st.metric("共同卖家", f"{stats['total_sellers']:,}")
        with col2:
            st.metric("升级卖家", f"{stats['upgraded_count']:,}", 
                     f"{stats['upgrade_rate']:.1f}%")
        with col3:
            st.metric("降级卖家", f"{stats['downgraded_count']:,}", 
                     f"-{stats['downgrade_rate']:.1f}%")
        with col4:
            st.metric("稳定卖家", f"{stats['stable_count']:,}", 
                     f"{stats['stability_rate']:.1f}%")
        
        # 显示流转矩阵
        st.markdown("##### 📊 环比流转矩阵")
        st.dataframe(mom_data['flow_matrix'], use_container_width=True)
        
        # 升级降级明细
        col1, col2 = st.columns(2)
        
        with col1:
            if len(mom_data['upgraded_sellers']) > 0:
                st.markdown("##### 📈 升级卖家明细 (前10名)")
                upgraded_display = mom_data['upgraded_sellers'].head(10)[
                    ['seller_id', f'business_tier_{mom_data["month2"]}', 
                     f'business_tier_{mom_data["month1"]}', 'tier_change']
                ].rename(columns={
                    f'business_tier_{mom_data["month2"]}': '原层级',
                    f'business_tier_{mom_data["month1"]}': '新层级',
                    'tier_change': '升级幅度'
                })
                st.dataframe(upgraded_display, use_container_width=True)
            else:
                st.info("📈 本月无升级卖家")
        
        with col2:
            if len(mom_data['downgraded_sellers']) > 0:
                st.markdown("##### 📉 降级卖家明细 (前10名)")
                downgraded_display = mom_data['downgraded_sellers'].head(10)[
                    ['seller_id', f'business_tier_{mom_data["month2"]}', 
                     f'business_tier_{mom_data["month1"]}', 'tier_change']
                ].rename(columns={
                    f'business_tier_{mom_data["month2"]}': '原层级',
                    f'business_tier_{mom_data["month1"]}': '新层级', 
                    'tier_change': '降级幅度'
                })
                st.dataframe(downgraded_display, use_container_width=True)
            else:
                st.info("📉 本月无降级卖家")
    
    # 同比分析
    if comparison_result.get('yoy_comparison'):
        st.markdown("---")
        yoy_data = comparison_result['yoy_comparison']
        st.markdown("#### 📅 同比分析 (Year-over-Year)")
        
        col1, col2, col3, col4 = st.columns(4)
        stats = yoy_data['summary_stats']
        
        with col1:
            st.metric("共同卖家", f"{stats['total_sellers']:,}")
        with col2:
            st.metric("升级卖家", f"{stats['upgraded_count']:,}", 
                     f"{stats['upgrade_rate']:.1f}%")
        with col3:
            st.metric("降级卖家", f"{stats['downgraded_count']:,}", 
                     f"-{stats['downgrade_rate']:.1f}%") 
        with col4:
            st.metric("稳定卖家", f"{stats['stable_count']:,}", 
                     f"{stats['stability_rate']:.1f}%")
        
        # 显示流转矩阵
        st.markdown("##### 📊 同比流转矩阵")
        st.dataframe(yoy_data['flow_matrix'], use_container_width=True)


def display_trajectory_results(trajectory_result):
    """显示轨迹分析结果"""
    st.markdown("### 🛤️ 轨迹分析结果")
    
    # 总体统计
    col1, col2, col3, col4 = st.columns(4)
    
    summary = trajectory_result['trajectory_summary']
    with col1:
        st.metric("分析卖家总数", f"{trajectory_result['total_sellers']:,}")
    with col2:
        st.metric("持续上升", f"{summary.get('持续上升', 0):,}")
    with col3:
        st.metric("持续下降", f"{summary.get('持续下降', 0):,}")
    with col4:
        st.metric("频繁波动", f"{summary.get('频繁波动', 0):,}")
    
    # 轨迹类型分布
    st.markdown("#### 📊 轨迹类型分布")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 饼图
        fig_pie = px.pie(
            values=list(summary.values()),
            names=list(summary.keys()),
            title="轨迹类型分布"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # 柱状图
        fig_bar = px.bar(
            x=list(summary.keys()),
            y=list(summary.values()),
            title="轨迹类型数量"
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # 详细轨迹数据
    st.markdown("#### 📋 详细轨迹数据")
    
    # 筛选选项
    col1, col2 = st.columns(2)
    with col1:
        selected_type = st.selectbox(
            "筛选轨迹类型",
            ["全部"] + list(summary.keys())
        )
    with col2:
        sort_by = st.selectbox(
            "排序方式",
            ["波动率", "趋势值", "变化次数"]
        )
    
    # 数据筛选和排序
    display_df = trajectory_result['trajectory_data'].copy()
    
    if selected_type != "全部":
        display_df = display_df[display_df['trajectory_type'] == selected_type]
    
    sort_columns = {
        "波动率": "volatility", 
        "趋势值": "trend",
        "变化次数": "total_changes"
    }
    
    display_df = display_df.sort_values(sort_columns[sort_by], ascending=False)
    
    # 显示数据表
    st.dataframe(
        display_df[['seller_id', 'tier_path', 'trajectory_type', 
                   'total_changes', 'volatility', 'trend']].rename(columns={
            'seller_id': '卖家ID',
            'tier_path': '层级轨迹',
            'trajectory_type': '轨迹类型',
            'total_changes': '变化次数',
            'volatility': '波动率',
            'trend': '趋势值'
        }),
        use_container_width=True
    )


def display_flow_results(flow_result, analysis_months):
    """显示层级流转分析结果 - 保持原有功能"""
    st.markdown("### 🔄 层级流转分析结果")
    
    if 'monthly_data' in flow_result:
        monthly_data = flow_result['monthly_data']
        
        # 显示月度KPI
        st.markdown("#### 📊 月度关键指标")
        
        # 按月汇总
        monthly_summary = monthly_data.groupby('month').agg({
            'seller_id': 'count',
            'total_gmv': 'sum',
            'unique_orders': 'sum'
        }).round(2)
        monthly_summary.columns = ['活跃卖家数', '总GMV', '总订单数']
        
        st.dataframe(monthly_summary, use_container_width=True)
        
        # 显示层级流转矩阵 
        if 'tier_flow_matrix' in flow_result and not flow_result['tier_flow_matrix'].empty:
            st.markdown("#### 🔄 层级流转矩阵")
            st.info(f"📅 对比最后两个月: {analysis_months[-2]} → {analysis_months[-1]}")
            st.dataframe(flow_result['tier_flow_matrix'], use_container_width=True)
        
        # 显示层级稳定性
        if 'tier_stability' in flow_result:
            st.markdown("#### 📈 层级稳定性")
            stability_df = pd.DataFrame(list(flow_result['tier_stability'].items()),
                                      columns=['层级', '稳定性(%)'])
            stability_df['稳定性(%)'] = stability_df['稳定性(%)'].round(1)
            
            fig = px.bar(stability_df, x='层级', y='稳定性(%)', 
                        title='各层级稳定性对比')
            st.plotly_chart(fig, use_container_width=True)

def main():
    """主函数"""
    # 语言选择器
    create_language_selector()
    
    # 页面标题
    st.markdown(f'<h1 class="main-header">{get_text("page_title")}</h1>', unsafe_allow_html=True)
    
    # 加载数据
    with st.spinner(get_text('loading')):
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
    st.info(f"{get_text('current_display')} {len(filtered_data):,} {get_text('sellers')} ({get_text('of_total')} {len(filtered_data)/len(seller_analysis)*100:.1f}{get_text('percent')})")
    
    # KPI指标卡片
    display_kpi_metrics(filtered_data)
    
    # 创建标签页
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        get_text('tab_overview'), get_text('tab_tier'), get_text('tab_geo'), 
        get_text('tab_performance'), get_text('tab_insights'), get_text('tab_monthly')
    ])
    
    with tab1:
        st.markdown(f"## {get_text('platform_overview')}")
        
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
        st.markdown(f"## {get_text('tier_analysis')}")
        
        # 层级统计表
        tier_summary = filtered_data.groupby('business_tier').agg({
            'seller_id': 'count',
            'total_gmv': ['sum', 'mean'],
            'unique_orders': ['sum', 'mean'],
            'avg_review_score': 'mean',
            'category_count': 'mean'
        }).round(2)
        
        # 根据语言设置列名
        if st.session_state.language == 'en':
            tier_summary.columns = ['Count', 'GMV Sum', 'GMV Mean', 'Orders Sum', 'Orders Mean', 'Avg Rating', 'Avg Categories']
        else:
            tier_summary.columns = ['数量', 'GMV总和', 'GMV均值', '订单总数', '订单均值', '平均评分', '平均品类数']
        
        st.markdown(f"### {get_text('tier_stats')}")
        st.dataframe(tier_summary, use_container_width=True)
        
        # 性能雷达图
        radar_fig = create_performance_radar(filtered_data, seller_analysis)
        st.plotly_chart(radar_fig, use_container_width=True)
    
    with tab3:
        st.markdown(f"## {get_text('geo_analysis')}")
        
        geo_fig = create_geographic_analysis(filtered_data)
        st.plotly_chart(geo_fig, use_container_width=True)
        
        # 州级详细数据
        state_detail = filtered_data.groupby('seller_state').agg({
            'seller_id': 'count',
            'total_gmv': ['sum', 'mean'],
            'avg_review_score': 'mean'
        }).round(2)
        
        # 根据语言设置列名
        if st.session_state.language == 'en':
            state_detail.columns = ['Seller Count', 'GMV Sum', 'GMV Mean', 'Avg Rating']
            sort_col = 'GMV Sum'
        else:
            state_detail.columns = ['卖家数量', 'GMV总和', 'GMV均值', '平均评分']
            sort_col = 'GMV总和'
            
        state_detail = state_detail.sort_values(sort_col, ascending=False)
        
        st.markdown(f"### {get_text('state_details')}")
        st.dataframe(state_detail, use_container_width=True)
    
    with tab4:
        st.markdown(f"## {get_text('performance_corr')}")
        
        corr_fig = create_correlation_heatmap(filtered_data)
        st.plotly_chart(corr_fig, use_container_width=True)
        
        # 性能分布
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"### {get_text('gmv_dist')}")
            gmv_hist = px.histogram(filtered_data, x='total_gmv', nbins=50, 
                                   title=get_text('gmv_histogram'))
            st.plotly_chart(gmv_hist, use_container_width=True)
        
        with col2:
            st.markdown(f"### {get_text('rating_dist')}")
            rating_hist = px.histogram(filtered_data, x='avg_review_score', nbins=30,
                                      title=get_text('rating_histogram'))
            st.plotly_chart(rating_hist, use_container_width=True)
    
    with tab5:
        display_business_insights(filtered_data)
        
        # 详细数据表
        st.markdown(f"### {get_text('filtered_data')}")
        display_columns = [
            'seller_id', 'seller_state', 'business_tier', 'total_gmv', 
            'unique_orders', 'avg_review_score', 'category_count', 'avg_shipping_days'
        ]
        
        st.dataframe(
            filtered_data[display_columns].sort_values('total_gmv', ascending=False),
            use_container_width=True
        )
        
        # 数据导出
        if st.button(get_text('export_csv')):
            csv = filtered_data.to_csv(index=False)
            st.download_button(
                label=get_text('download_csv'),
                data=csv,
                file_name=f"olist_filtered_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with tab6:
        show_monthly_analysis()

    # 页脚
    st.markdown("---")
    st.markdown(f"""
    <div style='text-align: center; color: #666; font-size: 0.9rem;'>
        {get_text('footer')} | 
        <a href='https://github.com/Quintas0658/olist_ecommerce_project' style='color: #1f77b4;'>{get_text('github_link')}</a> | 
        <a href='#' style='color: #1f77b4;'>{get_text('tech_docs')}</a>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 