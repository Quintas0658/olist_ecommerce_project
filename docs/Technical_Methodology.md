# Olist Seller Segmentation Project – README

❓ **Business Problem**

Olist 平台希望在有限资源下扶持对 GMV 增长最有潜力的卖家，问题在于：如何通过历史数据科学识别这些关键卖家？

---

🎯 **Objective**

构建卖家画像，完成多维度分群分析，识别高潜力与风险卖家，并为平台资源配置提供策略建议。

---

🔧 **Data Preparation**

使用 6 张核心表构建卖家画像（seller profile），涵盖销量、评分、发货时效、品类分布、客户分布等指标。

| 表名 | 用途 | 关键字段 |
|------|------|----------|
| order_items | 销量与价格 | seller_id, price, freight_value |
| orders | 订单状态与时间 | order_id, order_status, order_purchase_timestamp |
| order_reviews | 评分与评论 | review_score, review_comment_title |
| sellers | 卖家信息 | seller_id, seller_state |
| products | 商品信息 | product_category_name, product_id |
| customers | 客户信息 | customer_zip_code_prefix, customer_state |

**常用 SQL 类型与处理策略：**

- **JOIN 多表关联**：基于 order_id 和 seller_id 聚合；
- **GROUP BY + 聚合函数**：用于计算 GMV、订单数、平均评分等；
- **CASE WHEN**：处理缺失值与异常值；
- **时间处理**：提取月、年字段用于增长率等动态指标计算；
- **数据清洗**：去重、过滤缺失、统一编码格式。

---

🧠 **Modeling**

采用规则分群法（基于业务阈值），可选聚类方法用于辅助分析。

**特征维度示例：**
- **销售能力**：GMV、订单数、客单价
- **服务质量**：评分、差评率
- **履约效率**：平均发货时长、延迟率
- **多样性与风险**：品类数、客户分布、订单波动性

**分层逻辑：**
```python
def classify_seller_tier(gmv, orders, rating):
    if gmv >= 50000 and orders >= 200 and rating >= 4.0:
        return 'Platinum'
    elif gmv >= 10000 and orders >= 50 and rating >= 3.5:
        return 'Gold'
    elif gmv >= 2000 and orders >= 10 and rating >= 3.0:
        return 'Silver'
    elif gmv >= 500 and orders >= 3 and rating >= 2.5:
        return 'Bronze'
    else:
        return 'Basic'
```

---

📊 **Dashboard Insight**

**层级画像展示（示例模块）：**

| 角色 | 关注点 | 功能设计 |
|------|-------|----------|
| 高管 | 整体 KPI、趋势 | 简化图表、核心指标 |
| 分析师 | 深度分析、钻取 | 多维筛选、详细数据 |
| 运营 | 层级变化、名单 | 流转矩阵、操作指标 |

**示例分析模块：**
- **层级分布与 GMV 占比**
- **月度轨迹**：卖家升降级路径图
- **高潜力卖家识别**：结合评分 + 品类 + 成长率
- **雷达图**：展示各层级卖家的多维能力画像

---

💡 **Recommendation**

- **高潜力群体**：重点推广资源（首页推荐、广告位、专属服务）
- **风险群体**：加强监管、降低曝光，甚至限制履约能力
- **成熟群体**：以稳定性与规模效应为主，保持扶持但避免过度投入

---

✨ **技术亮点**

| 模块 | 技术手段 |
|------|----------|
| 数据处理 | SQL 聚合 + Pandas |
| 特征构建 | 自定义指标 + 多表合并 |
| 建模 | 规则分类 + KMeans 聚类（可选） |
| 可视化 | Seaborn + Plotly + Streamlit |
| 部署 | Streamlit Cloud 一键部署 |

**补充说明：**

- 结果具备可解释性，支持直接对接业务运营
- 每月可重新分级，满足动态监测和策略调整需求

---

**🌐 在线体验**：[https://olistecommerce.streamlit.app/](https://olistecommerce.streamlit.app/) 