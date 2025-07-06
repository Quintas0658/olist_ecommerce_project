# 📊 Olist E-commerce 数据字典

## 📝 项目概述
- **数据来源**: Olist Brazilian E-commerce Dataset
- **数据时间范围**: 2016-2018年
- **数据规模**: 9个主要数据表，约120MB
- **总记录数**: ~1,556,000 条记录
- **业务场景**: 巴西最大的电商平台多渠道销售数据

---

## 🗃️ 数据表结构总览

| 表名 | 记录数 | 主要用途 | 关键字段 |
|------|--------|---------|----------|
| olist_sellers_dataset | 3,095 | 卖家主档 | seller_id |
| olist_orders_dataset | 99,441 | 订单主档 | order_id, customer_id |
| olist_order_items_dataset | 112,650 | 订单明细 | order_id, seller_id, product_id |
| olist_order_reviews_dataset | 99,224 | 订单评价 | order_id, review_score |
| olist_order_payments_dataset | 103,886 | 支付信息 | order_id, payment_value |
| olist_products_dataset | 32,951 | 产品主档 | product_id |
| olist_customers_dataset | 99,441 | 客户主档 | customer_id |
| olist_geolocation_dataset | 1,000,163 | 地理位置 | zip_code_prefix |
| product_category_name_translation | 71 | 品类翻译 | product_category_name |

---

## 📚 详细表结构说明

### 1. 🏪 卖家表 (olist_sellers_dataset)
**业务含义**: 平台注册卖家的基本信息

| 字段名 | 数据类型 | 业务含义 | 示例值 |
|--------|----------|----------|--------|
| seller_id | VARCHAR(32) | 卖家唯一标识符（主键） | `3442f8959a84dea7ee197c632cb2df15` |
| seller_zip_code_prefix | INTEGER | 卖家邮编前缀 | `13023` |
| seller_city | VARCHAR(50) | 卖家所在城市 | `campinas` |
| seller_state | VARCHAR(2) | 卖家所在州（巴西州代码） | `SP` |

**关键业务指标**:
- 总卖家数: 3,095个
- 活跃卖家数: 3,095个 (100%)
- 主要分布州: SP(59.7%), PR(11.3%), MG(7.9%)

---

### 2. 🛒 订单表 (olist_orders_dataset)
**业务含义**: 平台所有订单的生命周期信息

| 字段名 | 数据类型 | 业务含义 | 示例值 |
|--------|----------|----------|--------|
| order_id | VARCHAR(32) | 订单唯一标识符（主键） | `e481f51cbdc54678b7cc49136f2d6af7` |
| customer_id | VARCHAR(32) | 客户标识符（外键） | `9ef432eb6251297304e76186b10a928d` |
| order_status | VARCHAR(20) | 订单状态 | `delivered`, `shipped`, `canceled` |
| order_purchase_timestamp | TIMESTAMP | 订单创建时间 | `2017-10-02 10:56:33` |
| order_approved_at | TIMESTAMP | 订单审核通过时间 | `2017-10-02 11:07:15` |
| order_delivered_carrier_date | TIMESTAMP | 交付给承运商时间 | `2017-10-04 19:55:00` |
| order_delivered_customer_date | TIMESTAMP | 客户收货时间 | `2017-10-10 21:25:13` |
| order_estimated_delivery_date | TIMESTAMP | 预计交付时间 | `2017-10-18 00:00:00` |

**订单状态分布**:
- `delivered`: 96,478 (97.0%) - 已送达
- `shipped`: 1,107 (1.1%) - 已发货
- `canceled`: 625 (0.6%) - 已取消
- 其他状态: 1,231 (1.2%)

**关键时间指标**:
- 平均审核时长: 10.9小时
- 平均发货时长: 3.0天
- 平均配送时长: 8.5天

---

### 3. 📦 订单明细表 (olist_order_items_dataset)
**业务含义**: 订单中的具体商品信息（一个订单可包含多个商品）

| 字段名 | 数据类型 | 业务含义 | 示例值 |
|--------|----------|----------|--------|
| order_id | VARCHAR(32) | 订单标识符（外键） | `00010242fe8c5a6d1ba2dd792cb16214` |
| order_item_id | INTEGER | 订单内商品序号 | `1`, `2`, `3` |
| product_id | VARCHAR(32) | 产品标识符（外键） | `4244733e06e7ecb4970a6e2683c13e61` |
| seller_id | VARCHAR(32) | 卖家标识符（外键） | `48436dade18ac8b2bce089ec2a041202` |
| shipping_limit_date | TIMESTAMP | 发货截止时间 | `2017-09-19 03:18:56` |
| price | DECIMAL(10,2) | 商品价格 | `58.90` |
| freight_value | DECIMAL(10,2) | 运费 | `13.29` |

**关键业务指标**:
- 总订单项目: 112,650个
- 平均订单项目数: 1.13个/订单
- 价格范围: R$ 0.85 - R$ 6,735.00
- 运费范围: R$ 0.00 - R$ 409.68

---

### 4. ⭐ 订单评价表 (olist_order_reviews_dataset)
**业务含义**: 客户对订单的评价和反馈

| 字段名 | 数据类型 | 业务含义 | 示例值 |
|--------|----------|----------|--------|
| review_id | VARCHAR(32) | 评价唯一标识符 | `7bc2406110b926393aa56f80a40eba40` |
| order_id | VARCHAR(32) | 订单标识符（外键） | `73fc7af87114b39712e6da79b0a377eb` |
| review_score | INTEGER | 评分（1-5分） | `4` |
| review_comment_title | VARCHAR(100) | 评价标题 | `Produto de qualidade.` |
| review_comment_message | TEXT | 评价内容 | `Muito bom, recomendo.` |
| review_creation_date | TIMESTAMP | 评价创建时间 | `2018-01-18 00:00:00` |
| review_answer_timestamp | TIMESTAMP | 卖家回复时间 | `2018-01-18 21:46:59` |

**评分分布**:
- 5分: 57,328 (57.8%)
- 4分: 19,131 (19.3%)
- 1分: 11,568 (11.7%)
- 3分: 8,287 (8.4%)
- 2分: 2,910 (2.9%)
- **平均评分**: 4.09/5.0

---

### 5. 💳 支付表 (olist_order_payments_dataset)
**业务含义**: 订单的支付方式和金额信息

| 字段名 | 数据类型 | 业务含义 | 示例值 |
|--------|----------|----------|--------|
| order_id | VARCHAR(32) | 订单标识符（外键） | `b81ef226f3fe1789b1e8b2acac839d17` |
| payment_sequential | INTEGER | 支付序号（一个订单可多次支付） | `1`, `2` |
| payment_type | VARCHAR(20) | 支付方式 | `credit_card`, `boleto` |
| payment_installments | INTEGER | 分期数 | `1`, `12` |
| payment_value | DECIMAL(10,2) | 支付金额 | `99.33` |

**支付方式分布**:
- `credit_card`: 76,795 (73.9%)
- `boleto`: 19,784 (19.0%)
- `voucher`: 5,775 (5.6%)
- `debit_card`: 1,529 (1.5%)

**支付金额统计**:
- 平均支付金额: R$ 154.10
- 中位数: R$ 100.00
- 最大单笔: R$ 13,664.10

---

### 6. 🎁 产品表 (olist_products_dataset)
**业务含义**: 平台销售的所有产品信息

| 字段名 | 数据类型 | 业务含义 | 示例值 |
|--------|----------|----------|--------|
| product_id | VARCHAR(32) | 产品唯一标识符（主键） | `1e9e8ef04dbcff4541ed26657ea517e5` |
| product_category_name | VARCHAR(50) | 产品品类（葡萄牙语） | `perfumaria`, `artes` |
| product_name_lenght | INTEGER | 产品名称长度（字符数） | `40` |
| product_description_lenght | INTEGER | 产品描述长度（字符数） | `287` |
| product_photos_qty | INTEGER | 产品图片数量 | `3` |
| product_weight_g | DECIMAL(10,2) | 产品重量（克） | `225.00` |
| product_length_cm | DECIMAL(10,2) | 产品长度（厘米） | `16.10` |
| product_height_cm | DECIMAL(10,2) | 产品高度（厘米） | `10.00` |
| product_width_cm | DECIMAL(10,2) | 产品宽度（厘米） | `14.00` |

**产品品类分布** (Top 10):
1. `cama_mesa_banho`: 3,029个
2. `beleza_saude`: 2,444个
3. `esporte_lazer`: 2,867个
4. `informatica_acessorios`: 1,639个
5. `moveis_decoracao`: 1,499个

---

### 7. 👥 客户表 (olist_customers_dataset)
**业务含义**: 平台注册客户信息

| 字段名 | 数据类型 | 业务含义 | 示例值 |
|--------|----------|----------|--------|
| customer_id | VARCHAR(32) | 客户订单标识符 | `06b8999e2fba1a1fbc88172c00ba8bc7` |
| customer_unique_id | VARCHAR(32) | 客户唯一标识符 | `861eff4711a542e4b93843c6dd7febb0` |
| customer_zip_code_prefix | INTEGER | 客户邮编前缀 | `14409` |
| customer_city | VARCHAR(50) | 客户城市 | `franca` |
| customer_state | VARCHAR(2) | 客户州代码 | `SP` |

**客户地域分布** (Top 5):
- SP: 41,746 (41.9%)
- RJ: 12,852 (12.9%)
- MG: 11,635 (11.7%)
- RS: 5,466 (5.5%)
- PR: 5,045 (5.1%)

---

## 🔗 表关系图

```
客户表 (customers)
    ↓ customer_id
订单表 (orders) ←→ order_id ←→ 评价表 (reviews)
    ↓ order_id                    ↓ order_id
订单明细表 (order_items) ←→ order_id ←→ 支付表 (payments)
    ↓ seller_id  ↓ product_id
卖家表 (sellers)   产品表 (products)
    ↓ zip_code        ↓ category_name
地理位置表 (geolocation)  品类翻译表 (translation)
```

---

## 📊 构建的卖家画像指标体系

基于原始数据，我们构建了31维度的卖家画像：

### 销售表现指标
- `total_gmv`: 总销售额
- `avg_order_value`: 平均订单价值
- `unique_orders`: 独立订单数
- `total_items`: 总商品销量

### 客户满意度指标
- `avg_review_score`: 平均评分
- `bad_review_rate`: 差评率(%)
- `review_count`: 评价数量

### 运营效率指标
- `avg_shipping_days`: 平均发货天数
- `delivery_success_rate`: 成功交付率(%)
- `avg_freight`: 平均运费

### 业务发展指标
- `category_count`: 经营品类数
- `active_days`: 活跃天数
- `order_frequency`: 订单频率

### 衍生商业指标
- `revenue_per_order`: 单均收入
- `items_per_order`: 单均商品数
- `is_active`: 活跃标记

---

## ⚠️ 数据质量说明

### 数据完整性
- **无缺失值**: 所有关键字段经过清洗，缺失值已填充为0或合理默认值
- **数据一致性**: 时间字段统一为UTC格式，金额统一为巴西雷亚尔(R$)
- **外键完整性**: 99.8%的外键关联完整，少量孤立记录已标记

### 数据限制
- **时间范围**: 2016-2018年数据，不包含最新趋势
- **地域限制**: 仅限巴西市场数据
- **匿名化**: 所有个人和商户信息已脱敏处理

### 分析建议
- 适用于历史趋势分析和模式识别
- 适用于卖家分级和运营策略制定
- 不适用于实时业务决策
- 建议结合最新数据进行验证

---

**文档版本**: v1.0  
**更新时间**: 2024年7月  
**负责人**: Business Analyst  
**审核**: Data Team 