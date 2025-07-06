"""
卖家分级分类模型

使用机器学习方法进行卖家细分，结合业务规则和数据驱动的聚类分析，
构建多维度的卖家分级体系。
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, silhouette_score
from sklearn.pipeline import Pipeline

import warnings
warnings.filterwarnings('ignore')

from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class SellerSegmentationModel:
    """卖家分级分类模型类"""
    
    def __init__(self, random_state: int = 42):
        """
        初始化分级模型
        
        Args:
            random_state: 随机种子
        """
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=0.95, random_state=random_state)
        self.clustering_models = {}
        self.classification_model = None
        self.feature_importance = None
        self.segmentation_results = None
        
        # 业务规则配置
        self.business_rules = {
            'high_value_threshold': {'revenue': 10000, 'orders': 50},
            'quality_threshold': {'rating': 4.0, 'positive_rate': 0.8},
            'risk_threshold': {'negative_rate': 0.3, 'risk_score': 0.7}
        }
        
    def fit_segmentation_model(self, seller_data: pd.DataFrame, 
                             segmentation_features: List[str] = None) -> Dict:
        """
        训练卖家分级模型
        
        Args:
            seller_data: 卖家特征数据
            segmentation_features: 用于分级的特征列表
            
        Returns:
            模型训练结果
        """
        logger.info("🎯 开始训练卖家分级模型...")
        
        # 准备数据
        X, feature_names = self._prepare_segmentation_data(seller_data, segmentation_features)
        
        # 方法1: 基于业务规则的分级
        business_segments = self._business_rule_segmentation(seller_data)
        
        # 方法2: K-means聚类
        kmeans_segments = self._kmeans_segmentation(X, n_clusters=5)
        
        # 方法3: 混合分级方法
        hybrid_segments = self._hybrid_segmentation(seller_data, X, business_segments, kmeans_segments)
        
        # 评估分级效果
        evaluation_results = self._evaluate_segmentation(X, hybrid_segments, feature_names)
        
        # 保存结果
        self.segmentation_results = {
            'business_segments': business_segments,
            'kmeans_segments': kmeans_segments,
            'hybrid_segments': hybrid_segments,
            'feature_names': feature_names,
            'evaluation': evaluation_results
        }
        
        # 训练分类器用于新卖家预测
        self._train_segment_classifier(X, hybrid_segments, feature_names)
        
        logger.info("✅ 卖家分级模型训练完成")
        
        return self.segmentation_results
    
    def _prepare_segmentation_data(self, seller_data: pd.DataFrame, 
                                 feature_cols: List[str] = None) -> Tuple[np.ndarray, List[str]]:
        """准备分级数据"""
        
        # 筛选活跃卖家
        active_sellers = seller_data[seller_data['total_orders'] > 0].copy()
        
        # 选择分级特征
        if feature_cols is None:
            feature_cols = [
                'total_revenue', 'total_orders', 'avg_order_value', 'unique_products',
                'avg_review_score', 'positive_rate', 'negative_rate', 'total_reviews',
                'freight_ratio', 'avg_items_per_order', 'business_maturity_score',
                'risk_score', 'growth_potential_score'
            ]
        
        # 筛选存在的特征
        available_features = [col for col in feature_cols if col in active_sellers.columns]
        
        # 准备特征矩阵
        X = active_sellers[available_features].fillna(0)
        
        # 对数变换处理偏态分布
        log_transform_cols = ['total_revenue', 'total_orders', 'total_reviews']
        for col in log_transform_cols:
            if col in X.columns:
                X[col] = np.log1p(X[col])
        
        # 标准化
        X_scaled = self.scaler.fit_transform(X)
        
        logger.info(f"  📊 分级数据准备完成: {X_scaled.shape[0]} 个卖家, {X_scaled.shape[1]} 个特征")
        
        return X_scaled, available_features
    
    def _business_rule_segmentation(self, seller_data: pd.DataFrame) -> pd.Series:
        """基于业务规则的分级"""
        logger.info("  🏢 应用业务规则分级...")
        
        segments = []
        
        for _, seller in seller_data.iterrows():
            # 检查高价值卖家
            if (seller.get('total_revenue', 0) >= self.business_rules['high_value_threshold']['revenue'] and
                seller.get('total_orders', 0) >= self.business_rules['high_value_threshold']['orders'] and
                seller.get('avg_review_score', 0) >= self.business_rules['quality_threshold']['rating']):
                segments.append('Platinum')
                
            # 检查优质卖家
            elif (seller.get('total_revenue', 0) >= 5000 and
                  seller.get('avg_review_score', 0) >= 4.0 and
                  seller.get('positive_rate', 0) >= 0.75):
                segments.append('Gold')
                
            # 检查标准卖家
            elif (seller.get('total_revenue', 0) >= 1000 and
                  seller.get('total_orders', 0) >= 10 and
                  seller.get('avg_review_score', 0) >= 3.5):
                segments.append('Silver')
                
            # 检查风险卖家
            elif (seller.get('negative_rate', 0) >= self.business_rules['risk_threshold']['negative_rate'] or
                  seller.get('risk_score', 0) >= self.business_rules['risk_threshold']['risk_score']):
                segments.append('Risk')
                
            # 其他卖家
            else:
                segments.append('Bronze')
        
        segments_series = pd.Series(segments, index=seller_data.index)
        logger.info(f"    ✅ 业务规则分级完成: {segments_series.value_counts().to_dict()}")
        
        return segments_series
    
    def _kmeans_segmentation(self, X: np.ndarray, n_clusters: int = 5) -> pd.Series:
        """K-means聚类分级"""
        logger.info(f"  🎯 K-means聚类分级 (k={n_clusters})...")
        
        # 训练K-means模型
        kmeans = KMeans(n_clusters=n_clusters, random_state=self.random_state, n_init=10)
        cluster_labels = kmeans.fit_predict(X)
        
        # 保存模型
        self.clustering_models['kmeans'] = kmeans
        
        # 计算聚类质量
        silhouette = silhouette_score(X, cluster_labels)
        logger.info(f"    📊 轮廓系数: {silhouette:.3f}")
        
        # 为聚类分配业务标签
        cluster_segments = self._assign_cluster_labels(X, cluster_labels, kmeans.cluster_centers_)
        
        return pd.Series(cluster_segments)
    
    def _assign_cluster_labels(self, X: np.ndarray, cluster_labels: np.ndarray, 
                             centers: np.ndarray) -> List[str]:
        """为聚类分配业务含义的标签"""
        
        # 计算每个聚类的特征均值
        cluster_profiles = []
        for i in range(len(centers)):
            cluster_mask = cluster_labels == i
            cluster_data = X[cluster_mask]
            
            profile = {
                'cluster_id': i,
                'size': len(cluster_data),
                'revenue_score': centers[i][0],  # 假设第一个特征是收入相关
                'quality_score': centers[i][4] if len(centers[i]) > 4 else 0,  # 评分相关
                'center': centers[i]
            }
            cluster_profiles.append(profile)
        
        # 根据收入和质量排序
        cluster_profiles.sort(key=lambda x: (x['revenue_score'], x['quality_score']), reverse=True)
        
        # 分配标签
        tier_names = ['Platinum', 'Gold', 'Silver', 'Bronze', 'Basic']
        label_mapping = {}
        
        for i, profile in enumerate(cluster_profiles):
            label_mapping[profile['cluster_id']] = tier_names[min(i, len(tier_names)-1)]
        
        # 映射标签
        segments = [label_mapping[label] for label in cluster_labels]
        
        return segments
    
    def _hybrid_segmentation(self, seller_data: pd.DataFrame, X: np.ndarray,
                           business_segments: pd.Series, kmeans_segments: pd.Series) -> pd.Series:
        """混合分级方法"""
        logger.info("  🔄 混合分级方法...")
        
        # 结合业务规则和聚类结果
        hybrid_segments = []
        
        for i, (business_seg, kmeans_seg) in enumerate(zip(business_segments, kmeans_segments)):
            # 高价值卖家优先使用业务规则
            if business_seg in ['Platinum', 'Gold']:
                hybrid_segments.append(business_seg)
            
            # 风险卖家优先标记
            elif business_seg == 'Risk':
                hybrid_segments.append('Risk')
            
            # 其他情况综合考虑
            else:
                # 如果聚类结果显示为高等级，但业务规则不是，进行调整
                if kmeans_seg in ['Platinum', 'Gold'] and business_seg in ['Bronze', 'Silver']:
                    hybrid_segments.append('Silver')  # 保守调整
                else:
                    hybrid_segments.append(kmeans_seg)
        
        hybrid_series = pd.Series(hybrid_segments, index=seller_data.index)
        logger.info(f"    ✅ 混合分级完成: {hybrid_series.value_counts().to_dict()}")
        
        return hybrid_series
    
    def _evaluate_segmentation(self, X: np.ndarray, segments: pd.Series, 
                             feature_names: List[str]) -> Dict:
        """评估分级效果"""
        logger.info("  📊 评估分级效果...")
        
        # 计算各等级的特征均值
        X_df = pd.DataFrame(X, columns=feature_names, index=segments.index)
        X_df['segment'] = segments
        
        segment_profiles = X_df.groupby('segment').mean()
        
        # 计算组间差异
        segment_std = X_df.groupby('segment').std().mean(axis=1)
        
        # 计算分离度指标
        total_variance = X_df[feature_names].var().sum()
        within_variance = X_df.groupby('segment')[feature_names].apply(
            lambda x: x.var().sum()
        ).mean()
        between_variance = total_variance - within_variance
        
        separation_ratio = between_variance / within_variance if within_variance > 0 else 0
        
        evaluation = {
            'segment_profiles': segment_profiles,
            'segment_sizes': segments.value_counts().to_dict(),
            'separation_ratio': separation_ratio,
            'within_variance': within_variance,
            'between_variance': between_variance
        }
        
        logger.info(f"    📈 分离度比率: {separation_ratio:.3f}")
        
        return evaluation
    
    def _train_segment_classifier(self, X: np.ndarray, segments: pd.Series, 
                                feature_names: List[str]) -> None:
        """训练分级分类器"""
        logger.info("  🤖 训练分级分类器...")
        
        # 编码标签
        le = LabelEncoder()
        y_encoded = le.fit_transform(segments)
        
        # 分割训练测试集
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=self.random_state, stratify=y_encoded
        )
        
        # 训练随机森林分类器
        rf_classifier = RandomForestClassifier(
            n_estimators=100, random_state=self.random_state, max_depth=10
        )
        rf_classifier.fit(X_train, y_train)
        
        # 评估模型
        y_pred = rf_classifier.predict(X_test)
        accuracy = (y_pred == y_test).mean()
        
        # 特征重要性
        feature_importance = pd.DataFrame({
            'feature': feature_names,
            'importance': rf_classifier.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # 保存模型和结果
        self.classification_model = {
            'model': rf_classifier,
            'label_encoder': le,
            'accuracy': accuracy,
            'feature_importance': feature_importance
        }
        
        logger.info(f"    🎯 分类器准确率: {accuracy:.3f}")
        logger.info(f"    🔍 Top 3 重要特征: {list(feature_importance.head(3)['feature'])}")
    
    def predict_seller_segment(self, seller_features: pd.DataFrame) -> pd.Series:
        """预测新卖家的分级"""
        if self.classification_model is None:
            raise ValueError("模型尚未训练，请先调用 fit_segmentation_model")
        
        # 准备特征
        X_new = seller_features[self.segmentation_results['feature_names']].fillna(0)
        
        # 对数变换
        log_transform_cols = ['total_revenue', 'total_orders', 'total_reviews']
        for col in log_transform_cols:
            if col in X_new.columns:
                X_new[col] = np.log1p(X_new[col])
        
        # 标准化
        X_scaled = self.scaler.transform(X_new)
        
        # 预测
        predictions = self.classification_model['model'].predict(X_scaled)
        segment_labels = self.classification_model['label_encoder'].inverse_transform(predictions)
        
        return pd.Series(segment_labels, index=seller_features.index)
    
    def visualize_segmentation(self, seller_data: pd.DataFrame, save_plots: bool = True) -> None:
        """可视化分级结果"""
        logger.info("📊 生成分级可视化...")
        
        if self.segmentation_results is None:
            raise ValueError("请先运行分级模型")
        
        # 获取分级结果
        segments = self.segmentation_results['hybrid_segments']
        X = seller_data[self.segmentation_results['feature_names']].fillna(0)
        
        # 1. PCA降维可视化
        self._plot_pca_segments(X, segments, save_plots)
        
        # 2. 业务指标对比
        self._plot_segment_comparison(seller_data, segments, save_plots)
        
        # 3. 分级分布
        self._plot_segment_distribution(segments, save_plots)
        
        # 4. 特征重要性
        if self.classification_model:
            self._plot_feature_importance(save_plots)
    
    def _plot_pca_segments(self, X: pd.DataFrame, segments: pd.Series, save_plots: bool) -> None:
        """PCA降维可视化"""
        # PCA降维到2D
        pca_2d = PCA(n_components=2, random_state=self.random_state)
        X_pca = pca_2d.fit_transform(StandardScaler().fit_transform(X))
        
        # 创建可视化
        fig = px.scatter(
            x=X_pca[:, 0], y=X_pca[:, 1], color=segments,
            title='卖家分级PCA可视化',
            labels={'x': f'PC1 ({pca_2d.explained_variance_ratio_[0]:.1%})',
                   'y': f'PC2 ({pca_2d.explained_variance_ratio_[1]:.1%})'},
            color_discrete_map={
                'Platinum': '#FFD700', 'Gold': '#FFA500', 'Silver': '#C0C0C0',
                'Bronze': '#CD7F32', 'Basic': '#808080', 'Risk': '#FF0000'
            }
        )
        
        fig.update_layout(width=800, height=600)
        fig.show()
        
        if save_plots:
            fig.write_html('reports/pca_segmentation.html')
    
    def _plot_segment_comparison(self, seller_data: pd.DataFrame, segments: pd.Series, save_plots: bool) -> None:
        """分级业务指标对比"""
        # 合并数据
        plot_data = seller_data.copy()
        plot_data['segment'] = segments
        
        # 关键指标
        key_metrics = ['total_revenue', 'total_orders', 'avg_review_score', 'unique_products']
        
        # 创建子图
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('各分级卖家业务指标对比', fontsize=16, fontweight='bold')
        
        for i, metric in enumerate(key_metrics):
            ax = axes[i//2, i%2]
            
            # 箱线图
            plot_data.boxplot(column=metric, by='segment', ax=ax)
            ax.set_title(f'{metric} 分级对比')
            ax.set_xlabel('卖家分级')
            ax.set_ylabel(metric)
            ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.show()
        
        if save_plots:
            plt.savefig('reports/segment_comparison.png', dpi=300, bbox_inches='tight')
    
    def _plot_segment_distribution(self, segments: pd.Series, save_plots: bool) -> None:
        """分级分布图"""
        segment_counts = segments.value_counts()
        
        fig = px.pie(
            values=segment_counts.values,
            names=segment_counts.index,
            title='卖家分级分布',
            color_discrete_map={
                'Platinum': '#FFD700', 'Gold': '#FFA500', 'Silver': '#C0C0C0',
                'Bronze': '#CD7F32', 'Basic': '#808080', 'Risk': '#FF0000'
            }
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(width=600, height=500)
        fig.show()
        
        if save_plots:
            fig.write_html('reports/segment_distribution.html')
    
    def _plot_feature_importance(self, save_plots: bool) -> None:
        """特征重要性图"""
        if not self.classification_model:
            return
        
        importance_df = self.classification_model['feature_importance'].head(10)
        
        fig = px.bar(
            importance_df, x='importance', y='feature',
            orientation='h',
            title='卖家分级模型特征重要性 Top 10',
            labels={'importance': '重要性', 'feature': '特征'}
        )
        
        fig.update_layout(height=500, width=700)
        fig.show()
        
        if save_plots:
            fig.write_html('reports/feature_importance.html')
    
    def generate_segmentation_report(self, seller_data: pd.DataFrame) -> Dict:
        """生成分级报告"""
        logger.info("📋 生成分级报告...")
        
        if self.segmentation_results is None:
            raise ValueError("请先运行分级模型")
        
        segments = self.segmentation_results['hybrid_segments']
        
        # 各分级的业务表现
        segment_summary = seller_data.groupby(segments).agg({
            'total_revenue': ['count', 'sum', 'mean', 'median'],
            'total_orders': ['sum', 'mean'],
            'avg_review_score': 'mean',
            'positive_rate': 'mean',
            'unique_products': 'mean'
        }).round(2)
        
        # 重命名列
        segment_summary.columns = [
            'seller_count', 'total_gmv', 'avg_revenue', 'median_revenue',
            'total_orders', 'avg_orders', 'avg_rating', 'avg_positive_rate', 'avg_products'
        ]
        
        # 计算贡献占比
        segment_summary['gmv_contribution'] = (
            segment_summary['total_gmv'] / segment_summary['total_gmv'].sum() * 100
        ).round(1)
        
        # 生成业务洞察
        insights = self._generate_business_insights(segment_summary, segments)
        
        report = {
            'segment_summary': segment_summary,
            'insights': insights,
            'model_performance': {
                'accuracy': self.classification_model['accuracy'] if self.classification_model else None,
                'separation_ratio': self.segmentation_results['evaluation']['separation_ratio']
            }
        }
        
        return report
    
    def _generate_business_insights(self, segment_summary: pd.DataFrame, segments: pd.Series) -> Dict:
        """生成业务洞察"""
        insights = {}
        
        # 高价值卖家洞察
        high_value_segments = ['Platinum', 'Gold']
        high_value_count = sum(segment_summary.loc[seg, 'seller_count'] 
                              for seg in high_value_segments if seg in segment_summary.index)
        high_value_gmv = sum(segment_summary.loc[seg, 'total_gmv'] 
                            for seg in high_value_segments if seg in segment_summary.index)
        
        insights['high_value_sellers'] = {
            'count': high_value_count,
            'percentage': high_value_count / len(segments) * 100,
            'gmv_contribution': high_value_gmv / segment_summary['total_gmv'].sum() * 100
        }
        
        # 风险卖家洞察
        if 'Risk' in segment_summary.index:
            risk_info = segment_summary.loc['Risk']
            insights['risk_sellers'] = {
                'count': risk_info['seller_count'],
                'avg_rating': risk_info['avg_rating'],
                'revenue_impact': risk_info['gmv_contribution']
            }
        
        # 成长机会
        if 'Silver' in segment_summary.index and 'Bronze' in segment_summary.index:
            growth_potential = (
                segment_summary.loc['Silver', 'seller_count'] + 
                segment_summary.loc['Bronze', 'seller_count']
            )
            insights['growth_opportunity'] = {
                'potential_sellers': growth_potential,
                'current_contribution': (
                    segment_summary.loc['Silver', 'gmv_contribution'] + 
                    segment_summary.loc['Bronze', 'gmv_contribution']
                )
            }
        
        return insights


# 工具函数
def run_segmentation_analysis(seller_data: pd.DataFrame) -> Tuple[SellerSegmentationModel, Dict]:
    """运行完整的分级分析"""
    
    # 创建模型
    model = SellerSegmentationModel()
    
    # 训练模型
    results = model.fit_segmentation_model(seller_data)
    
    # 生成可视化
    model.visualize_segmentation(seller_data)
    
    # 生成报告
    report = model.generate_segmentation_report(seller_data)
    
    return model, report


if __name__ == "__main__":
    # 演示用法
    print("🎯 卖家分级分类模型演示")
    print("请先运行数据处理管道获取卖家特征数据") 