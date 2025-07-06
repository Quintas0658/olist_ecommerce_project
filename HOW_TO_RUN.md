# 🚀 Olist卖家分级管理项目 - 运行指南

## 📋 项目概述

这是一个基于Olist电商平台数据构建的**卖家分级管理系统**，展示了Amazon Global Selling Senior Business Analyst岗位所需的核心技能：
- 数据处理与ETL管道
- 业务指标框架设计
- 机器学习模型开发
- 交互式可视化仪表板
- 业务洞察与策略建议

## 🛠️ 环境准备

### 1. 系统要求
- Python 3.8+
- 4GB+ RAM
- 2GB+ 磁盘空间

### 2. 依赖安装
```bash
# 克隆项目到本地
git clone <repository-url>
cd Olist_ecommerce_project

# 安装依赖
pip install -r requirements.txt
```

### 3. 数据文件检查
确保 `archive/` 目录包含以下数据文件：
```
archive/
├── olist_sellers_dataset.csv
├── olist_orders_dataset.csv
├── olist_order_items_dataset.csv
├── olist_order_reviews_dataset.csv
├── olist_products_dataset.csv
├── olist_customers_dataset.csv
├── olist_order_payments_dataset.csv
└── product_category_name_translation.csv
```

## 🏃‍♂️ 快速开始

### 方式1: 运行完整数据管道
```bash
# 进入src目录
cd src

# 运行数据处理管道
python data_pipeline.py

# 运行业务指标计算
python business_metrics.py

# 运行分级模型
python seller_segmentation.py
```

### 方式2: 使用Jupyter Notebook (推荐)
```bash
# 启动Jupyter
jupyter notebook

# 打开分析笔记本
# 1. notebooks/01_data_exploration.ipynb - 数据探索
# 2. notebooks/02_seller_segmentation_analysis.ipynb - 分级分析
```

### 方式3: 运行Streamlit仪表板 (推荐)
```bash
# 启动仪表板
streamlit run dashboard/seller_management_dashboard.py

# 浏览器访问: http://localhost:8501
```

## 📊 项目结构说明

```
Olist_ecommerce_project/
├── README.md                          # 项目介绍
├── requirements.txt                   # Python依赖
├── HOW_TO_RUN.md                     # 运行指南
├── 
├── archive/                          # 原始数据文件
│   ├── olist_sellers_dataset.csv
│   ├── olist_orders_dataset.csv
│   └── ...
├── 
├── src/                              # 核心分析代码
│   ├── business_metrics.py          # 业务指标框架
│   ├── data_pipeline.py             # 数据处理管道
│   └── seller_segmentation.py       # 分级分类模型
├── 
├── notebooks/                        # Jupyter分析笔记本
│   ├── 01_data_exploration.ipynb    # 数据探索分析
│   └── 02_seller_segmentation_analysis.ipynb
├── 
├── dashboard/                        # Streamlit仪表板
│   └── seller_management_dashboard.py
├── 
├── data/                            # 处理后的数据 (自动生成)
│   ├── seller_features_processed.csv
│   ├── data_quality_report.csv
│   └── data_dictionary.csv
├── 
└── reports/                         # 分析报告和文档
    ├── Executive_Summary.md         # 执行摘要
    └── (可视化图表会自动保存到此目录)
```

## 🎯 核心功能演示

### 1. 数据探索分析
**文件**: `notebooks/01_data_exploration.ipynb`

**功能展示**:
- 数据质量检查和清洗
- 卖家业务表现分布分析
- 地理分布和市场机会识别
- 关键业务指标相关性分析

**运行方式**:
```bash
jupyter notebook notebooks/01_data_exploration.ipynb
```

### 2. 卖家分级模型
**文件**: `src/seller_segmentation.py`

**功能展示**:
- 多维度评估体系构建
- 业务规则与机器学习结合
- K-means聚类和监督学习
- 模型性能评估和可视化

**运行方式**:
```bash
cd src
python seller_segmentation.py
```

### 3. 交互式仪表板
**文件**: `dashboard/seller_management_dashboard.py`

**功能展示**:
- 平台总览和关键指标
- 分级分析和模型对比
- 业务洞察和机会识别
- 个体卖家详细分析
- 策略建议和行动计划

**运行方式**:
```bash
streamlit run dashboard/seller_management_dashboard.py
```

## 📈 预期输出结果

### 1. 数据处理结果
运行数据管道后，会在 `data/` 目录生成：
- `seller_features_processed.csv`: 完整的卖家特征数据
- `data_quality_report.csv`: 数据质量评估报告
- `data_dictionary.csv`: 数据字典和字段说明

### 2. 分析报告
- **Executive Summary**: `reports/Executive_Summary.md`
- **技术文档**: 各模块代码中的详细注释
- **可视化图表**: 自动保存的分析图表

### 3. 交互式仪表板
访问 http://localhost:8501 查看：
- 📊 总览仪表板
- 🎯 卖家分级分析
- 📈 业务洞察
- 🔍 个体卖家分析
- 📋 策略建议

## 🔧 故障排查

### 常见问题1: 依赖包安装失败
```bash
# 升级pip
pip install --upgrade pip

# 使用清华源安装
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 常见问题2: 内存不足
```bash
# 如果数据量过大，可以设置采样
# 在代码中找到并修改采样参数
SAMPLE_SIZE = 50000  # 减少处理的数据量
```

### 常见问题3: Streamlit页面无法访问
```bash
# 检查端口占用
lsof -i :8501

# 使用其他端口
streamlit run dashboard/seller_management_dashboard.py --server.port 8502
```

### 常见问题4: 中文字体显示问题
```bash
# 安装中文字体 (macOS)
brew install font-iosevka
# 或在代码中修改字体设置
```

## 🎯 核心技能展示

本项目充分展示了Amazon Global Selling Senior BA岗位要求的核心技能：

### 1. 数据分析与处理
- ✅ 大规模数据ETL管道 (155万条记录)
- ✅ 数据质量检查和清洗
- ✅ 特征工程和衍生指标构建
- ✅ SQL思维和数据建模

### 2. 业务分析与洞察
- ✅ 多维度业务指标框架设计
- ✅ 卖家生命周期管理策略
- ✅ 风险识别和机会挖掘
- ✅ ROI和商业价值评估

### 3. 机器学习与建模
- ✅ 无监督学习 (K-means聚类)
- ✅ 监督学习 (随机森林分类)
- ✅ 模型评估和性能优化
- ✅ 业务规则与算法融合

### 4. 可视化与产品化
- ✅ 交互式仪表板开发
- ✅ 数据可视化最佳实践
- ✅ 用户体验设计
- ✅ 生产就绪的部署方案

### 5. 项目管理与沟通
- ✅ 端到端项目交付
- ✅ 技术文档和用户指南
- ✅ 业务价值沟通
- ✅ 跨团队协作能力

## 📞 联系方式

如有任何问题或建议，欢迎通过以下方式联系：

**项目负责人**: Senior BA Candidate  
**完成时间**: 2024年1月  
**技术栈**: Python, Pandas, Scikit-learn, Streamlit, Plotly  

---

**🎯 展示目标**: 通过本项目展示数据驱动的业务分析能力、技术实现能力和深度商业洞察力，体现Amazon Global Selling Senior Business Analyst岗位所需的核心竞争力。 