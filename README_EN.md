# 🚀 Olist E-commerce Analysis Platform

🌐 **Language / 语言**: [🇨🇳 中文](README.md) | [🇺🇸 English](README_EN.md)

## 📊 Project Overview

An **enterprise-level e-commerce data analysis platform** based on real data from Olist, Brazil's largest e-commerce platform, providing comprehensive seller lifecycle management and business intelligence analysis.

### 🎯 Core Features

- **📈 Data Processing Pipeline** - From raw data to analysis-ready feature engineering
- **🏆 Seller Tiering System** - Multi-dimensional classification based on business rules and machine learning
- **📊 Interactive BI Dashboard** - Streamlit-powered enterprise-grade visualization platform
- **🔍 Business Intelligence Engine** - Automated opportunity identification and strategic recommendations
- **📱 Responsive Design** - Support for desktop and mobile access

## 🏗️ Project Architecture

```
olist_ecommerce_project/
├── 📁 src/                    # Core analysis modules
│   ├── data_pipeline.py       # Data processing pipeline
│   ├── analysis.py            # Business analysis engine
│   ├── visualization.py       # Visualization tools
│   └── __init__.py
├── 📁 dashboard/              # Web application
│   └── app.py                 # Main Streamlit app
├── 📁 data/                   # Data files
│   ├── raw/                   # Raw data
│   └── processed/             # Processed data
├── 📁 reports/                # Analysis reports
│   └── charts/                # Chart outputs
├── 📁 notebooks/              # Jupyter analysis
├── 📁 docs/                   # Project documentation
└── 🔧 run_dashboard.py        # One-click launcher script
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone the project
git clone https://github.com/Quintas0658/olist_ecommerce_project.git
cd olist_ecommerce_project

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Data Preparation

Place Olist dataset CSV files in the `archive/` directory:
- `olist_sellers_dataset.csv`
- `olist_orders_dataset.csv`
- `olist_order_items_dataset.csv`
- `olist_order_reviews_dataset.csv`
- `olist_products_dataset.csv`
- `olist_customers_dataset.csv`
- `olist_order_payments_dataset.csv`
- `product_category_name_translation.csv`

### 3. Launch Options

#### 🚀 Method 1: One-click Launch (Recommended)
```bash
python run_dashboard.py
```

#### 🔧 Method 2: Manual Launch
```bash
streamlit run dashboard/app.py --server.port=8502
```

#### 📊 Method 3: Jupyter Analysis
```bash
jupyter notebook notebooks/
```

**Access URL**: http://localhost:8502

## 📊 Dashboard Features

### 🎯 Five Analysis Modules

#### 1️⃣ Data Overview
- 🏆 **Tier Distribution**: Dual pie charts showing quantity vs GMV contribution
- 📈 **Scatter Analysis**: GMV vs order count correlation analysis
- 💡 **Real-time KPIs**: 5 key metrics with dynamic updates

#### 2️⃣ Seller Tiering
- 📋 **Statistical Tables**: Detailed comparison data across tiers
- 🎯 **Radar Charts**: 5-dimensional performance indicator visualization
- 🔄 **Interactive Drill-down**: Click to view specific data

#### 3️⃣ Geographic Analysis
- 🗺️ **Quadrant Analysis**: Quantity/GMV/Average/Rating distribution
- 📊 **State Rankings**: Top 15 states detailed data
- 🎨 **Heatmap Style**: Intuitive geographic difference visualization

#### 4️⃣ Performance Analysis
- 🔥 **Correlation Heatmap**: 8 key metrics correlation analysis
- 📊 **Distribution Histograms**: GMV and rating distribution characteristics
- 📈 **Trend Identification**: Business pattern discovery

#### 5️⃣ Smart Insights
- 🧠 **AI High-potential Seller Identification**: Algorithm-driven growth opportunity screening
- 📊 **Pareto Analysis**: 80/20 rule verification
- 💰 **Quantified Impact**: Category/rating effects on GMV
- 📥 **One-click Export**: CSV format filtered data download

### 🔍 Interactive Features

#### Sidebar Filters
- **Seller Tiers**: Platinum/Gold/Silver/Bronze/Basic
- **GMV Range**: Drag slider to adjust revenue range
- **Rating Range**: 4.0-5.0 star rating filtering
- **Geographic Filter**: Multi-select state/region filtering
- **Category Count**: Single vs multi-category sellers

#### Professional Features
- **Enterprise UI**: Blue theme, clean and modern
- **Responsive Layout**: Adaptive desktop/tablet/mobile
- **Interactive Feedback**: Dynamic loading hints, smooth user experience
- **Data Caching**: Enhanced loading performance

## 🌐 Cloud Deployment

### Streamlit Cloud (Free Recommended)
```bash
# 1. Push code to GitHub
git add .
git commit -m "Deploy BI Dashboard"
git push origin main

# 2. Visit https://share.streamlit.io
# 3. Connect GitHub repository, select dashboard/app.py
# 4. Click Deploy
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8502
CMD ["streamlit", "run", "dashboard/app.py", "--server.port=8502"]
```

## 🔬 Technology Stack

### Backend Analysis
- **Python 3.8+** - Core development language
- **Pandas** - Data processing and analysis
- **Scikit-learn** - Machine learning algorithms
- **NumPy** - Numerical computing

### Frontend Visualization
- **Streamlit** - Web application framework
- **Plotly** - Interactive charts
- **Seaborn/Matplotlib** - Static charts
- **CSS3** - Responsive styling

### Data Processing
- **Feature Engineering** - 30+ business metrics construction
- **Cluster Analysis** - K-means seller grouping
- **Time Series** - Trend analysis and forecasting

## 📈 Core Module Details

### 🔧 DataPipeline
```python
from src.data_pipeline import DataPipeline

# Initialize data pipeline
pipeline = DataPipeline()
seller_profile = pipeline.build_seller_features()
```

### 📊 BusinessAnalyzer
```python
from src.analysis import BusinessAnalyzer

# Business analysis
analyzer = BusinessAnalyzer()
analyzer.create_business_tiers()
opportunities = analyzer.identify_business_opportunities()
```

### 🎨 ChartGenerator
```python
from src.visualization import ChartGenerator

# Visualization
chart_gen = ChartGenerator()
chart_gen.generate_all_charts(data_dict, seller_data)
```

## 📋 Seller Tiering System

### 🏆 Five-tier Classification
- **💎 Platinum** - Top sellers (GMV>50K, Orders>200, Rating>4.0)
- **🥇 Gold** - Premium sellers (GMV>10K, Orders>50)
- **🥈 Silver** - Growing sellers (GMV>2K, Orders>10)
- **🥉 Bronze** - Basic sellers (GMV>500, Orders>3)
- **📋 Basic** - New sellers

### 🤖 Smart Algorithms
- **Business Rules** - Tier classification based on GMV, order volume, ratings
- **K-means Clustering** - Data-driven natural grouping
- **Multi-dimensional Assessment** - Comprehensive evaluation across 6 key business dimensions

## 💡 Business Value

### 🎯 Seller Operations
- **Precise Tiering** - Personalized operational strategies
- **Potential Mining** - Identify high-potential low-performance sellers
- **Risk Control** - Early warning for problematic sellers

### 📊 Platform Management
- **Resource Allocation** - Data-driven decision support
- **Growth Opportunities** - Geographic and category expansion recommendations
- **KPI Monitoring** - Real-time business health tracking

### 🚀 Strategic Decision Making
- **Pareto Analysis** - 20/80 rule verification
- **Market Segmentation** - Refined operational strategies
- **ROI Optimization** - Maximize input-output efficiency

## 🔧 Troubleshooting

### Common Issues Solutions

#### Dependency Installation Failed
```bash
# Upgrade pip
pip install --upgrade pip

# Use domestic mirror
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

#### Memory Insufficient
```bash
# Reduce data processing volume
# Adjust sampling parameters in data_pipeline.py
SAMPLE_SIZE = 50000
```

#### Dashboard Access Issues
```bash
# Check port usage
lsof -i :8502

# Try different port
streamlit run dashboard/app.py --server.port=8503
```

#### Data File Errors
```bash
# Check file integrity
ls -la archive/
# Ensure all CSV files exist and are non-empty
```

### Performance Optimization Tips
- **Data Caching**: Use `@st.cache_data` decorator
- **Paginated Loading**: Process large datasets in batches
- **Chart Optimization**: Set reasonable data point counts
- **Memory Management**: Clean up temporary variables promptly

## 📊 Dataset Information

Based on Olist public dataset (100K+ orders, 2016-2018):
- **9 Data Tables** - Orders, products, reviews, payments, etc.
- **30+ Features** - Sales, satisfaction, efficiency, category dimensions
- **Geographic Coverage** - Complete coverage of Brazil's 27 states

## 💼 Project Presentation Tips

### 🎯 Technical Highlights
1. **Data Processing Capability**: Real-time filtering of 1.55M+ records
2. **Visualization Skills**: Plotly interactive charts
3. **Product Thinking**: User experience optimization
4. **Technical Architecture**: Modular code design

### 📊 Demo Flow
1. **Overall Introduction** (30s): Project background and value
2. **Interactive Demo** (2min): Live operation of filtering features
3. **Insights Showcase** (1min): Smart analysis results
4. **Technical Overview** (1min): Architecture and implementation

## 🔗 Related Links

- **Live Demo**: [Streamlit Cloud Demo](https://share.streamlit.io) (Update after deployment)
- **Data Source**: [Kaggle Olist Dataset](https://www.kaggle.com/olistbr/brazilian-ecommerce)
- **Project Repository**: [GitHub Repository](https://github.com/Quintas0658/olist_ecommerce_project)

## 📄 License

MIT License

## 👥 Contributing

Welcome to submit Issues and Pull Requests!

---

⭐ **If this project helps you, please give it a Star!** ⭐ 