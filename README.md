# 🚀 Olist E-commerce Analysis Platform

## 📊 项目概述

一个**企业级电商数据分析平台**，基于巴西最大的电商平台Olist的真实数据，提供全方位的卖家生命周期管理和商业智能分析。

### 🎯 核心功能

- **📈 数据处理管道** - 从原始数据到分析就绪的特征工程
- **🏆 卖家分级系统** - 基于业务规则和机器学习的多维度分级
- **📊 交互式BI Dashboard** - Streamlit驱动的企业级可视化平台
- **🔍 商业洞察引擎** - 自动化商机识别和策略建议
- **📱 响应式设计** - 支持桌面端和移动端访问

## 🏗️ 项目架构

```
olist_ecommerce_project/
├── 📁 src/                    # 核心分析模块
│   ├── data_pipeline.py       # 数据处理管道
│   ├── analysis.py            # 业务分析引擎
│   ├── visualization.py       # 可视化工具
│   └── __init__.py
├── 📁 dashboard/              # Web应用
│   └── app.py                 # Streamlit主应用
├── 📁 data/                   # 数据文件
│   ├── raw/                   # 原始数据
│   └── processed/             # 处理后数据
├── 📁 reports/                # 分析报告
│   └── charts/                # 图表输出
├── 📁 notebooks/              # Jupyter分析
├── 📁 docs/                   # 项目文档
└── 🔧 run_dashboard.py        # 一键启动脚本
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/Quintas0658/olist_ecommerce_project.git
cd olist_ecommerce_project

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 数据准备

将Olist数据集CSV文件放入 `data/` 或 `archive/` 目录：
- `olist_sellers_dataset.csv`
- `olist_orders_dataset.csv`
- `olist_order_items_dataset.csv`
- 其他相关数据文件

### 3. 启动Dashboard

```bash
# 一键启动（推荐）
python run_dashboard.py

# 或手动启动
streamlit run dashboard/app.py --server.port=8502
```

访问：http://localhost:8502

## 📊 Dashboard功能

### 🎯 五大分析模块

1. **📊 数据概览** - 平台整体KPI和趋势
2. **🏆 卖家分级** - 智能分级和层级分析
3. **🗺️ 地理分析** - 区域分布和机会识别
4. **⚡ 性能分析** - 运营效率和客户满意度
5. **💡 智能洞察** - AI驱动的商业建议

### 🔧 交互功能

- **实时筛选器** - 多维度动态筛选
- **KPI仪表盘** - 关键指标实时更新
- **雷达图分析** - 多维度业绩对比
- **数据导出** - 支持CSV下载

## 🔬 技术栈

### 后端分析
- **Python 3.8+** - 核心开发语言
- **Pandas** - 数据处理和分析
- **Scikit-learn** - 机器学习算法
- **NumPy** - 数值计算

### 前端可视化
- **Streamlit** - Web应用框架
- **Plotly** - 交互式图表
- **Seaborn/Matplotlib** - 静态图表
- **CSS3** - 响应式样式

### 数据处理
- **特征工程** - 30+业务指标构建
- **聚类分析** - K-means卖家分组
- **时间序列** - 趋势分析和预测

## 📈 核心模块详解

### 🔧 DataPipeline
```python
from src.data_pipeline import DataPipeline

# 初始化数据管道
pipeline = DataPipeline()
seller_profile = pipeline.build_seller_features()
```

### 📊 BusinessAnalyzer
```python
from src.analysis import BusinessAnalyzer

# 业务分析
analyzer = BusinessAnalyzer()
analyzer.create_business_tiers()
opportunities = analyzer.identify_business_opportunities()
```

### 🎨 ChartGenerator
```python
from src.visualization import ChartGenerator

# 可视化
chart_gen = ChartGenerator()
chart_gen.generate_all_charts(data_dict, seller_data)
```

## 📋 卖家分级体系

### 🏆 五级分类
- **💎 Platinum** - 顶级卖家 (GMV>50K, 订单>200, 评分>4.0)
- **🥇 Gold** - 优质卖家 (GMV>10K, 订单>50)
- **🥈 Silver** - 成长卖家 (GMV>2K, 订单>10)
- **🥉 Bronze** - 基础卖家 (GMV>500, 订单>3)
- **📋 Basic** - 新手卖家

### 🤖 智能算法
- **业务规则** - 基于GMV、订单量、评分的层级划分
- **K-means聚类** - 数据驱动的自然分组
- **多维评估** - 6个关键业务维度综合评估

## 💡 商业价值

### 🎯 卖家运营
- **精准分级** - 个性化运营策略
- **潜力挖掘** - 识别高潜力低表现卖家
- **风险控制** - 预警问题卖家

### 📊 平台管理
- **资源分配** - 基于数据的决策支持
- **增长机会** - 地域和品类扩张建议
- **KPI监控** - 实时业务健康度追踪

### 🚀 战略决策
- **帕累托分析** - 20/80法则验证
- **市场细分** - 精细化运营策略
- **ROI优化** - 投入产出最大化

## 📊 数据集说明

基于Olist公开数据集 (100K+ 订单, 2016-2018)：
- **9个数据表** - 订单、商品、评价、支付等
- **30+特征** - 销售、满意度、效率、品类等维度
- **地理覆盖** - 巴西27个州全覆盖

## 🔗 相关链接

- **数据源**: [Kaggle Olist Dataset](https://www.kaggle.com/olistbr/brazilian-ecommerce)
- **技术文档**: [docs/](docs/)
- **示例报告**: [reports/](reports/)

## 📄 许可证

MIT License

## 👥 贡献

欢迎提交Issue和Pull Request！

---

⭐ **如果这个项目对您有帮助，请给个Star支持！** ⭐ 