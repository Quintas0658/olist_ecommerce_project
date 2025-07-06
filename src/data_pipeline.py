"""
Olist卖家数据处理管道

实现端到端的数据处理流程，从原始数据到分析就绪的特征数据集。
展示数据工程、ETL和特征工程能力。
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OlistDataPipeline:
    """Olist数据处理管道类"""
    
    def __init__(self, data_path: str = "archive/"):
        """
        初始化数据管道
        
        Args:
            data_path: 原始数据文件路径
        """
        self.data_path = Path(data_path)
        self.processed_data = {}
        self.data_quality_report = {}
        
        # 数据文件映射
        self.data_files = {
            'sellers': 'olist_sellers_dataset.csv',
            'orders': 'olist_orders_dataset.csv',
            'order_items': 'olist_order_items_dataset.csv',
            'reviews': 'olist_order_reviews_dataset.csv',
            'products': 'olist_products_dataset.csv',
            'customers': 'olist_customers_dataset.csv',
            'payments': 'olist_order_payments_dataset.csv',
            'category_translation': 'product_category_name_translation.csv'
        }
    
    def run_full_pipeline(self, save_output: bool = True) -> Dict[str, pd.DataFrame]:
        """
        运行完整的数据处理管道
        
        Args:
            save_output: 是否保存处理后的数据
            
        Returns:
            处理后的数据字典
        """
        logger.info("🚀 开始运行Olist数据处理管道...")
        
        # 步骤1: 数据加载
        self._load_raw_data()
        
        # 步骤2: 数据质量检查
        self._perform_data_quality_check()
        
        # 步骤3: 数据清洗
        self._clean_data()
        
        # 步骤4: 特征工程
        seller_features = self._build_seller_features()
        
        # 步骤5: 数据验证
        self._validate_processed_data(seller_features)
        
        # 步骤6: 保存处理后的数据
        if save_output:
            self._save_processed_data(seller_features)
        
        logger.info("✅ 数据处理管道执行完成!")
        
        return {
            'seller_features': seller_features,
            'data_quality_report': self.data_quality_report
        }
    
    def _load_raw_data(self) -> None:
        """加载原始数据文件"""
        logger.info("📊 加载原始数据文件...")
        
        for table_name, filename in self.data_files.items():
            file_path = self.data_path / filename
            try:
                df = pd.read_csv(file_path)
                self.processed_data[table_name] = df
                logger.info(f"  ✅ {table_name}: {df.shape[0]:,} 行 x {df.shape[1]} 列")
            except FileNotFoundError:
                logger.warning(f"  ⚠️ 文件未找到: {filename}")
            except Exception as e:
                logger.error(f"  ❌ 加载 {filename} 时出错: {str(e)}")
    
    def _perform_data_quality_check(self) -> None:
        """执行数据质量检查"""
        logger.info("🔍 执行数据质量检查...")
        
        quality_report = {}
        
        for table_name, df in self.processed_data.items():
            table_report = {
                'row_count': len(df),
                'column_count': len(df.columns),
                'missing_values': df.isnull().sum().to_dict(),
                'missing_percentage': (df.isnull().sum() / len(df) * 100).round(2).to_dict(),
                'duplicate_rows': df.duplicated().sum(),
                'data_types': df.dtypes.astype(str).to_dict()
            }
            
            # 检查关键字段
            if table_name == 'sellers' and 'seller_id' in df.columns:
                table_report['unique_sellers'] = df['seller_id'].nunique()
                table_report['duplicate_seller_ids'] = df['seller_id'].duplicated().sum()
            
            if table_name == 'orders' and 'order_id' in df.columns:
                table_report['unique_orders'] = df['order_id'].nunique()
                table_report['order_status_distribution'] = df['order_status'].value_counts().to_dict() if 'order_status' in df.columns else {}
            
            quality_report[table_name] = table_report
            
            # 记录关键质量问题
            high_missing_cols = [col for col, pct in table_report['missing_percentage'].items() if pct > 30]
            if high_missing_cols:
                logger.warning(f"  ⚠️ {table_name} 中缺失值超过30%的列: {high_missing_cols}")
        
        self.data_quality_report = quality_report
        logger.info("  ✅ 数据质量检查完成")
    
    def _clean_data(self) -> None:
        """数据清洗"""
        logger.info("🧹 开始数据清洗...")
        
        # 清洗订单数据
        if 'orders' in self.processed_data:
            orders = self.processed_data['orders'].copy()
            
            # 转换日期列
            date_columns = [col for col in orders.columns if 'date' in col.lower() or 'timestamp' in col.lower()]
            for col in date_columns:
                try:
                    orders[col] = pd.to_datetime(orders[col])
                except:
                    logger.warning(f"    ⚠️ 无法转换日期列: {col}")
            
            # 筛选有效订单状态
            valid_statuses = ['delivered', 'shipped', 'processing', 'invoiced', 'approved']
            if 'order_status' in orders.columns:
                before_count = len(orders)
                orders = orders[orders['order_status'].isin(valid_statuses)]
                after_count = len(orders)
                logger.info(f"    📦 筛选有效订单: {before_count:,} → {after_count:,}")
            
            self.processed_data['orders'] = orders
        
        # 清洗订单商品数据
        if 'order_items' in self.processed_data:
            order_items = self.processed_data['order_items'].copy()
            
            # 移除价格异常的记录
            if 'price' in order_items.columns:
                before_count = len(order_items)
                order_items = order_items[(order_items['price'] > 0) & (order_items['price'] < 10000)]
                after_count = len(order_items)
                logger.info(f"    💰 筛选合理价格区间: {before_count:,} → {after_count:,}")
            
            # 转换日期列
            if 'shipping_limit_date' in order_items.columns:
                try:
                    order_items['shipping_limit_date'] = pd.to_datetime(order_items['shipping_limit_date'])
                except:
                    logger.warning("    ⚠️ 无法转换 shipping_limit_date")
            
            self.processed_data['order_items'] = order_items
        
        # 清洗评价数据
        if 'reviews' in self.processed_data:
            reviews = self.processed_data['reviews'].copy()
            
            # 筛选有效评分
            if 'review_score' in reviews.columns:
                before_count = len(reviews)
                reviews = reviews[reviews['review_score'].between(1, 5)]
                after_count = len(reviews)
                logger.info(f"    ⭐ 筛选有效评分(1-5): {before_count:,} → {after_count:,}")
            
            # 转换日期列
            date_cols = ['review_creation_date', 'review_answer_timestamp']
            for col in date_cols:
                if col in reviews.columns:
                    try:
                        reviews[col] = pd.to_datetime(reviews[col])
                    except:
                        logger.warning(f"    ⚠️ 无法转换日期列: {col}")
            
            self.processed_data['reviews'] = reviews
        
        logger.info("  ✅ 数据清洗完成")
    
    def _build_seller_features(self) -> pd.DataFrame:
        """构建卖家特征数据集"""
        logger.info("🔧 构建卖家特征数据集...")
        
        # 获取基础数据
        sellers = self.processed_data['sellers'].copy()
        orders = self.processed_data['orders'].copy()
        order_items = self.processed_data['order_items'].copy()
        reviews = self.processed_data['reviews'].copy()
        products = self.processed_data.get('products', pd.DataFrame())
        
        # 合并订单和订单商品数据
        order_detail = orders.merge(order_items, on='order_id', how='inner')
        logger.info(f"  📊 订单详情数据: {len(order_detail):,} 条记录")
        
        # 1. 基础业务指标
        logger.info("  🏢 计算基础业务指标...")
        business_metrics = self._calculate_business_metrics(order_detail)
        
        # 2. 客户满意度指标
        logger.info("  😊 计算客户满意度指标...")
        satisfaction_metrics = self._calculate_satisfaction_metrics(reviews, order_items)
        
        # 3. 运营效率指标
        logger.info("  ⚡ 计算运营效率指标...")
        efficiency_metrics = self._calculate_efficiency_metrics(order_detail, orders)
        
        # 4. 商品组合指标
        logger.info("  📦 计算商品组合指标...")
        product_metrics = self._calculate_product_metrics(order_items, products)
        
        # 5. 时间序列指标
        logger.info("  📈 计算时间序列指标...")
        temporal_metrics = self._calculate_temporal_metrics(order_detail)
        
        # 合并所有指标
        seller_features = sellers.copy()
        
        # 按顺序合并指标
        for metrics_df, name in [
            (business_metrics, "业务指标"),
            (satisfaction_metrics, "满意度指标"),
            (efficiency_metrics, "效率指标"),
            (product_metrics, "商品指标"),
            (temporal_metrics, "时间序列指标")
        ]:
            seller_features = seller_features.merge(
                metrics_df, left_on='seller_id', right_index=True, how='left'
            )
            logger.info(f"    ✅ 合并{name}: {len(metrics_df)} 个卖家")
        
        # 填充缺失值
        numeric_columns = seller_features.select_dtypes(include=[np.number]).columns
        seller_features[numeric_columns] = seller_features[numeric_columns].fillna(0)
        
        # 添加衍生特征
        seller_features = self._add_derived_features(seller_features)
        
        logger.info(f"  ✅ 卖家特征构建完成: {seller_features.shape}")
        
        return seller_features
    
    def _calculate_business_metrics(self, order_detail: pd.DataFrame) -> pd.DataFrame:
        """计算基础业务指标"""
        metrics = order_detail.groupby('seller_id').agg({
            'order_id': 'nunique',                    # 总订单数
            'price': ['sum', 'mean', 'count'],        # 销售额、客单价、商品件数
            'freight_value': 'sum',                   # 总运费
            'product_id': 'nunique',                  # 商品SKU数
            'order_item_id': 'sum'                    # 总销售数量
        }).round(2)
        
        # 重命名列
        metrics.columns = [
            'total_orders', 'total_revenue', 'avg_order_value', 'total_items_sold',
            'total_freight', 'unique_products', 'total_quantity'
        ]
        
        # 计算衍生指标
        metrics['avg_items_per_order'] = metrics['total_items_sold'] / metrics['total_orders']
        metrics['avg_price_per_item'] = metrics['total_revenue'] / metrics['total_items_sold']
        metrics['freight_ratio'] = metrics['total_freight'] / metrics['total_revenue']
        metrics['revenue_per_sku'] = metrics['total_revenue'] / metrics['unique_products']
        
        return metrics
    
    def _calculate_satisfaction_metrics(self, reviews: pd.DataFrame, order_items: pd.DataFrame) -> pd.DataFrame:
        """计算客户满意度指标"""
        # 合并评价和卖家信息
        review_seller = reviews.merge(
            order_items[['order_id', 'seller_id']], 
            on='order_id', 
            how='inner'
        )
        
        # 基础满意度指标
        satisfaction_metrics = review_seller.groupby('seller_id').agg({
            'review_score': ['mean', 'count', 'std'],
            'review_id': 'count'
        }).round(3)
        
        satisfaction_metrics.columns = [
            'avg_review_score', 'total_reviews', 'review_score_std', 'review_count_check'
        ]
        satisfaction_metrics = satisfaction_metrics.drop('review_count_check', axis=1)
        
        # 计算满意度分布
        review_distribution = review_seller.groupby('seller_id')['review_score'].apply(
            lambda x: pd.Series({
                'score_1_rate': (x == 1).mean(),
                'score_2_rate': (x == 2).mean(),
                'score_3_rate': (x == 3).mean(),
                'score_4_rate': (x == 4).mean(),
                'score_5_rate': (x == 5).mean(),
                'positive_rate': (x >= 4).mean(),
                'negative_rate': (x <= 2).mean()
            })
        )
        
        # 合并满意度指标
        satisfaction_metrics = satisfaction_metrics.merge(
            review_distribution, left_index=True, right_index=True, how='left'
        )
        
        return satisfaction_metrics
    
    def _calculate_efficiency_metrics(self, order_detail: pd.DataFrame, orders: pd.DataFrame) -> pd.DataFrame:
        """计算运营效率指标"""
        # 订单履约相关指标
        order_status_metrics = orders.groupby('customer_id').agg({
            'order_status': lambda x: (x == 'delivered').mean()
        }).rename(columns={'order_status': 'delivery_rate'})
        
        # 按卖家聚合运营效率
        efficiency_metrics = order_detail.groupby('seller_id').agg({
            'freight_value': 'mean',           # 平均运费
            'price': 'std',                   # 价格稳定性
        }).round(3)
        
        efficiency_metrics.columns = ['avg_freight_per_order', 'price_volatility']
        
        # 计算价格稳定性指标（变异系数）
        price_stats = order_detail.groupby('seller_id')['price'].agg(['mean', 'std'])
        efficiency_metrics['price_cv'] = (price_stats['std'] / price_stats['mean']).fillna(0)
        
        return efficiency_metrics
    
    def _calculate_product_metrics(self, order_items: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
        """计算商品组合指标"""
        # 商品多样性指标
        product_diversity = order_items.groupby('seller_id').agg({
            'product_id': ['nunique', 'count'],
            'price': ['min', 'max']
        })
        
        product_diversity.columns = [
            'unique_products_sold', 'total_products_sold', 
            'min_price', 'max_price'
        ]
        
        # 价格范围
        product_diversity['price_range'] = product_diversity['max_price'] - product_diversity['min_price']
        product_diversity['price_range_ratio'] = product_diversity['max_price'] / product_diversity['min_price']
        
        # 商品周转率
        product_diversity['product_turnover'] = product_diversity['total_products_sold'] / product_diversity['unique_products_sold']
        
        return product_diversity
    
    def _calculate_temporal_metrics(self, order_detail: pd.DataFrame) -> pd.DataFrame:
        """计算时间序列指标"""
        # 确保有时间列
        if 'order_purchase_timestamp' not in order_detail.columns:
            # 如果没有时间戳，返回空的DataFrame
            empty_metrics = pd.DataFrame(index=order_detail['seller_id'].unique())
            empty_metrics['days_active'] = 365  # 默认值
            empty_metrics['avg_orders_per_month'] = 0
            return empty_metrics
        
        # 转换时间戳
        order_detail['order_date'] = pd.to_datetime(order_detail['order_purchase_timestamp']).dt.date
        
        # 计算活跃天数和订单频率
        temporal_metrics = order_detail.groupby('seller_id').agg({
            'order_date': ['min', 'max', 'nunique'],
            'order_id': 'nunique'
        })
        
        temporal_metrics.columns = ['first_order_date', 'last_order_date', 'active_days', 'unique_orders']
        
        # 计算活跃期间长度（天）
        temporal_metrics['days_span'] = (
            pd.to_datetime(temporal_metrics['last_order_date']) - 
            pd.to_datetime(temporal_metrics['first_order_date'])
        ).dt.days + 1
        
        # 订单频率指标
        temporal_metrics['avg_orders_per_month'] = temporal_metrics['unique_orders'] / (temporal_metrics['days_span'] / 30)
        temporal_metrics['avg_gap_between_orders'] = temporal_metrics['days_span'] / temporal_metrics['unique_orders']
        
        return temporal_metrics[['days_span', 'active_days', 'avg_orders_per_month', 'avg_gap_between_orders']]
    
    def _add_derived_features(self, seller_features: pd.DataFrame) -> pd.DataFrame:
        """添加衍生特征"""
        logger.info("  🎯 添加衍生特征...")
        
        # 1. 业务成熟度评分
        seller_features['business_maturity_score'] = (
            np.log1p(seller_features['total_orders']) * 0.3 +
            np.log1p(seller_features['unique_products']) * 0.2 +
            np.minimum(seller_features.get('days_span', 365) / 365, 1) * 0.3 +
            np.minimum(seller_features['total_reviews'] / 50, 1) * 0.2
        )
        
        # 2. 风险评分（越低越好）
        seller_features['risk_score'] = (
            (5 - seller_features['avg_review_score'].fillna(3)) / 4 * 0.4 +
            seller_features['negative_rate'].fillna(0.2) * 0.3 +
            np.minimum(seller_features['freight_ratio'].fillna(0.15) / 0.3, 1) * 0.2 +
            np.minimum(seller_features.get('price_cv', 0.5), 1) * 0.1
        )
        
        # 3. 成长潜力评分
        revenue_rank = seller_features['total_revenue'].rank(pct=True)
        order_rank = seller_features['total_orders'].rank(pct=True)
        
        seller_features['growth_potential_score'] = (
            (1 - revenue_rank) * 0.3 +  # 低收入=高潜力
            np.minimum(seller_features['unique_products'] / 20, 1) * 0.2 +
            seller_features['avg_review_score'].fillna(3) / 5 * 0.3 +
            np.minimum(seller_features.get('avg_orders_per_month', 1), 5) / 5 * 0.2
        )
        
        # 4. 分类标签
        seller_features['seller_size'] = pd.cut(
            seller_features['total_revenue'],
            bins=[0, 1000, 5000, 20000, np.inf],
            labels=['Micro', 'Small', 'Medium', 'Large']
        )
        
        seller_features['activity_level'] = pd.cut(
            seller_features['total_orders'],
            bins=[0, 5, 20, 100, np.inf],
            labels=['Inactive', 'Low', 'Medium', 'High']
        )
        
        return seller_features
    
    def _validate_processed_data(self, seller_features: pd.DataFrame) -> None:
        """验证处理后的数据"""
        logger.info("✅ 验证处理后的数据...")
        
        # 基础验证
        assert len(seller_features) > 0, "卖家特征数据为空"
        assert 'seller_id' in seller_features.columns, "缺少seller_id列"
        
        # 数据合理性检查
        numeric_cols = seller_features.select_dtypes(include=[np.number]).columns
        
        # 检查是否有异常值
        for col in ['total_revenue', 'total_orders', 'avg_review_score']:
            if col in seller_features.columns:
                q99 = seller_features[col].quantile(0.99)
                outliers = (seller_features[col] > q99 * 10).sum()
                if outliers > 0:
                    logger.warning(f"  ⚠️ {col} 存在 {outliers} 个极端异常值")
        
        # 检查评分范围
        if 'avg_review_score' in seller_features.columns:
            invalid_scores = seller_features[
                (seller_features['avg_review_score'] < 1) | 
                (seller_features['avg_review_score'] > 5)
            ]
            if len(invalid_scores) > 0:
                logger.warning(f"  ⚠️ 发现 {len(invalid_scores)} 个无效评分")
        
        logger.info(f"  ✅ 数据验证完成: {seller_features.shape}")
    
    def _save_processed_data(self, seller_features: pd.DataFrame) -> None:
        """保存处理后的数据"""
        logger.info("💾 保存处理后的数据...")
        
        # 创建data目录
        output_dir = Path('data')
        output_dir.mkdir(exist_ok=True)
        
        # 保存卖家特征数据
        seller_features.to_csv(output_dir / 'seller_features_processed.csv', index=False)
        logger.info(f"  ✅ 卖家特征数据保存至: {output_dir / 'seller_features_processed.csv'}")
        
        # 保存数据质量报告
        quality_report_df = pd.DataFrame(self.data_quality_report).T
        quality_report_df.to_csv(output_dir / 'data_quality_report.csv')
        logger.info(f"  ✅ 数据质量报告保存至: {output_dir / 'data_quality_report.csv'}")
        
        # 保存数据字典
        data_dictionary = self._generate_data_dictionary(seller_features)
        data_dictionary.to_csv(output_dir / 'data_dictionary.csv', index=False)
        logger.info(f"  ✅ 数据字典保存至: {output_dir / 'data_dictionary.csv'}")
    
    def _generate_data_dictionary(self, seller_features: pd.DataFrame) -> pd.DataFrame:
        """生成数据字典"""
        data_dict = []
        
        # 定义字段描述
        field_descriptions = {
            'seller_id': '卖家唯一标识符',
            'seller_zip_code_prefix': '卖家邮编前缀',
            'seller_city': '卖家城市',
            'seller_state': '卖家州',
            'total_orders': '总订单数',
            'total_revenue': '总销售额(R$)',
            'avg_order_value': '平均订单价值(R$)',
            'total_items_sold': '总销售商品件数',
            'total_freight': '总运费(R$)',
            'unique_products': '商品SKU数量',
            'total_quantity': '总销售数量',
            'avg_items_per_order': '平均每单商品件数',
            'avg_price_per_item': '平均商品单价(R$)',
            'freight_ratio': '运费占销售额比例',
            'revenue_per_sku': '每SKU平均收入(R$)',
            'avg_review_score': '平均客户评分(1-5)',
            'total_reviews': '总评价数量',
            'review_score_std': '评分标准差',
            'positive_rate': '好评率(4-5分)',
            'negative_rate': '差评率(1-2分)',
            'business_maturity_score': '业务成熟度评分(0-1)',
            'risk_score': '风险评分(0-1，越低越好)',
            'growth_potential_score': '成长潜力评分(0-1)',
            'seller_size': '卖家规模分类',
            'activity_level': '活跃度等级'
        }
        
        for col in seller_features.columns:
            dtype = str(seller_features[col].dtype)
            description = field_descriptions.get(col, '待补充描述')
            
            data_dict.append({
                'Field': col,
                'Type': dtype,
                'Description': description,
                'Non_Null_Count': seller_features[col].count(),
                'Null_Count': seller_features[col].isnull().sum(),
                'Unique_Values': seller_features[col].nunique() if dtype != 'object' else 'N/A'
            })
        
        return pd.DataFrame(data_dict)


def main():
    """主函数 - 演示数据管道使用"""
    # 初始化数据管道
    pipeline = OlistDataPipeline()
    
    # 运行完整管道
    results = pipeline.run_full_pipeline(save_output=True)
    
    # 显示结果摘要
    seller_features = results['seller_features']
    print(f"\n🎯 数据管道执行结果:")
    print(f"  📊 处理后的卖家数量: {len(seller_features):,}")
    print(f"  📋 特征数量: {len(seller_features.columns)}")
    print(f"  🎯 活跃卖家: {(seller_features['total_orders'] > 0).sum():,}")
    print(f"  💰 平台总GMV: R$ {seller_features['total_revenue'].sum():,.2f}")
    
    return seller_features

if __name__ == "__main__":
    main() 