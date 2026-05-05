"""
推荐算法核心模块

实现基于协同过滤的推荐算法，包括：
1. 基于用户的协同过滤（UserCF）
2. 基于物品的协同过滤（ItemCF）
3. 多种相似度计算方法（余弦相似度、皮尔逊相关系数）
4. 评分归一化、加权平均等优化策略
"""

import math
from collections import defaultdict
from typing import Dict, List, Tuple, Optional


class SimilarityCalculator:
    """相似度计算器：实现多种相似度计算方法"""
    
    @staticmethod
    def cosine_similarity(vec1: Dict[int, float], vec2: Dict[int, float]) -> float:
        """
        余弦相似度计算
        
        公式：sim(u,v) = Σ(r_ui * r_vi) / (√Σ(r_ui²) * √Σ(r_vi²))
        
        Args:
            vec1: 用户/物品1的评分向量 {item_id: score}
            vec2: 用户/物品2的评分向量 {item_id: score}
            
        Returns:
            相似度值 [0, 1]
        """
        if not vec1 or not vec2:
            return 0.0
        
        # 找到共同评分的物品
        common_items = set(vec1.keys()) & set(vec2.keys())
        if not common_items:
            return 0.0
        
        # 计算分子：共同物品的评分乘积之和
        numerator = sum(vec1[item] * vec2[item] for item in common_items)
        
        # 计算分母：各自评分平方和的平方根
        denominator1 = math.sqrt(sum(score ** 2 for score in vec1.values()))
        denominator2 = math.sqrt(sum(score ** 2 for score in vec2.values()))
        
        if denominator1 == 0 or denominator2 == 0:
            return 0.0
        
        return numerator / (denominator1 * denominator2)
    
    @staticmethod
    def pearson_correlation(vec1: Dict[int, float], vec2: Dict[int, float]) -> float:
        """
        皮尔逊相关系数计算
        
        公式：sim(u,v) = Σ((r_ui - r̄_u) * (r_vi - r̄_v)) / (√Σ(r_ui - r̄_u)² * √Σ(r_vi - r̄_v)²)
        
        Args:
            vec1: 用户/物品1的评分向量 {item_id: score}
            vec2: 用户/物品2的评分向量 {item_id: score}
            
        Returns:
            相似度值 [-1, 1]，归一化到 [0, 1]
        """
        if not vec1 or not vec2:
            return 0.0
        
        # 找到共同评分的物品
        common_items = set(vec1.keys()) & set(vec2.keys())
        if len(common_items) < 2:  # 皮尔逊系数至少需要2个共同项
            return 0.0
        
        # 计算平均分
        avg1 = sum(vec1[item] for item in common_items) / len(common_items)
        avg2 = sum(vec2[item] for item in common_items) / len(common_items)
        
        # 计算分子：协方差
        numerator = sum((vec1[item] - avg1) * (vec2[item] - avg2) for item in common_items)
        
        # 计算分母：标准差乘积
        denominator1 = math.sqrt(sum((vec1[item] - avg1) ** 2 for item in common_items))
        denominator2 = math.sqrt(sum((vec2[item] - avg2) ** 2 for item in common_items))
        
        if denominator1 == 0 or denominator2 == 0:
            return 0.0
        
        correlation = numerator / (denominator1 * denominator2)
        
        # 归一化到 [0, 1]
        return (correlation + 1) / 2
    
    @staticmethod
    def adjusted_cosine_similarity(vec1: Dict[int, float], vec2: Dict[int, float], 
                                   user_avg: Optional[Dict[int, float]] = None) -> float:
        """
        调整余弦相似度（用于ItemCF）
        
        考虑用户评分偏差，减去用户平均分后再计算余弦相似度
        
        Args:
            vec1: 物品1的评分向量 {user_id: score}
            vec2: 物品2的评分向量 {user_id: score}
            user_avg: 用户平均分字典 {user_id: avg_score}
            
        Returns:
            相似度值 [0, 1]
        """
        if not vec1 or not vec2 or not user_avg:
            return SimilarityCalculator.cosine_similarity(vec1, vec2)
        
        common_users = set(vec1.keys()) & set(vec2.keys())
        if not common_users:
            return 0.0
        
        # 调整评分：减去用户平均分
        adjusted_vec1 = {u: vec1[u] - user_avg.get(u, 0) for u in common_users}
        adjusted_vec2 = {u: vec2[u] - user_avg.get(u, 0) for u in common_users}
        
        # 计算余弦相似度
        numerator = sum(adjusted_vec1[u] * adjusted_vec2[u] for u in common_users)
        denominator1 = math.sqrt(sum(v ** 2 for v in adjusted_vec1.values()))
        denominator2 = math.sqrt(sum(v ** 2 for v in adjusted_vec2.values()))
        
        if denominator1 == 0 or denominator2 == 0:
            return 0.0
        
        return numerator / (denominator1 * denominator2)


class RatingNormalizer:
    """评分归一化处理器"""
    
    @staticmethod
    def normalize_ratings(ratings: Dict[int, Dict[int, float]]) -> Tuple[Dict[int, Dict[int, float]], Dict[int, float]]:
        """
        Z-score归一化：(r - μ) / σ
        
        Args:
            ratings: 评分矩阵 {user_id: {item_id: score}}
            
        Returns:
            (归一化后的评分矩阵, 用户平均分字典)
        """
        normalized = {}
        user_avg = {}
        
        for user_id, items in ratings.items():
            if not items:
                continue
            
            scores = list(items.values())
            avg = sum(scores) / len(scores)
            std = math.sqrt(sum((s - avg) ** 2 for s in scores) / len(scores))
            
            user_avg[user_id] = avg
            
            if std == 0:
                normalized[user_id] = {item_id: 0.0 for item_id in items}
            else:
                normalized[user_id] = {
                    item_id: (score - avg) / std 
                    for item_id, score in items.items()
                }
        
        return normalized, user_avg
    
    @staticmethod
    def mean_centering(ratings: Dict[int, Dict[int, float]]) -> Tuple[Dict[int, Dict[int, float]], Dict[int, float]]:
        """
        均值中心化：r - μ
        
        Args:
            ratings: 评分矩阵 {user_id: {item_id: score}}
            
        Returns:
            (中心化后的评分矩阵, 用户平均分字典)
        """
        centered = {}
        user_avg = {}
        
        for user_id, items in ratings.items():
            if not items:
                continue
            
            avg = sum(items.values()) / len(items)
            user_avg[user_id] = avg
            centered[user_id] = {
                item_id: score - avg 
                for item_id, score in items.items()
            }
        
        return centered, user_avg


class UserCF:
    """基于用户的协同过滤推荐算法"""
    
    def __init__(self, similarity_method: str = 'cosine', normalize: bool = True, 
                 k_neighbors: int = 30, min_common_items: int = 3):
        """
        初始化UserCF推荐器
        
        Args:
            similarity_method: 相似度计算方法 ('cosine' 或 'pearson')
            normalize: 是否进行评分归一化
            k_neighbors: 选取的最相似邻居数量
            min_common_items: 计算相似度的最小共同物品数
        """
        self.similarity_method = similarity_method
        self.normalize = normalize
        self.k_neighbors = k_neighbors
        self.min_common_items = min_common_items
        self.user_items = {}  # {user_id: {item_id: score}}
        self.user_avg = {}  # {user_id: avg_score}
    
    def fit(self, ratings: List[Dict]) -> None:
        """
        训练模型：构建用户-物品评分矩阵
        
        Args:
            ratings: 评分列表 [{'user_id': int, 'item_id': int, 'score': float}, ...]
        """
        self.user_items = defaultdict(dict)
        
        for rating in ratings:
            user_id = rating['user_id']
            item_id = rating['item_id']
            score = float(rating['score'])
            self.user_items[user_id][item_id] = score
        
        # 评分归一化
        if self.normalize:
            self.user_items, self.user_avg = RatingNormalizer.mean_centering(dict(self.user_items))
        else:
            self.user_avg = {
                uid: sum(items.values()) / len(items) if items else 0
                for uid, items in self.user_items.items()
            }
    
    def _calculate_similarity(self, vec1: Dict[int, float], vec2: Dict[int, float]) -> float:
        """计算两个用户的相似度"""
        # 检查共同物品数量
        common = set(vec1.keys()) & set(vec2.keys())
        if len(common) < self.min_common_items:
            return 0.0
        
        if self.similarity_method == 'pearson':
            return SimilarityCalculator.pearson_correlation(vec1, vec2)
        else:
            return SimilarityCalculator.cosine_similarity(vec1, vec2)
    
    def recommend(self, user_id: int, top_n: int = 10, 
                 exclude_rated: bool = True) -> List[Tuple[int, float]]:
        """
        为指定用户生成推荐列表
        
        Args:
            user_id: 目标用户ID
            top_n: 返回Top-N推荐
            exclude_rated: 是否排除用户已评分的物品
            
        Returns:
            推荐列表 [(item_id, predicted_score), ...]
        """
        if user_id not in self.user_items:
            return []
        
        target_vec = self.user_items[user_id]
        
        # 1. 计算与所有其他用户的相似度
        similarities = []
        for uid, vec in self.user_items.items():
            if uid == user_id:
                continue
            
            sim = self._calculate_similarity(target_vec, vec)
            if sim > 0:
                similarities.append((uid, sim))
        
        # 2. 选取Top-K相似用户
        similarities.sort(key=lambda x: x[1], reverse=True)
        neighbors = similarities[:self.k_neighbors]
        
        if not neighbors:
            return []
        
        # 3. 加权预测评分
        predictions = defaultdict(float)
        sim_sums = defaultdict(float)
        
        for neighbor_id, similarity in neighbors:
            neighbor_vec = self.user_items[neighbor_id]
            
            for item_id, score in neighbor_vec.items():
                # 排除已评分物品
                if exclude_rated and item_id in target_vec:
                    continue
                
                # 加权累加
                predictions[item_id] += similarity * score
                sim_sums[item_id] += similarity
        
        # 4. 计算最终预测分数
        final_predictions = []
        for item_id, weighted_sum in predictions.items():
            if sim_sums[item_id] > 0:
                predicted_score = weighted_sum / sim_sums[item_id]
                
                # 如果进行了归一化，需要还原到原始评分范围
                if self.normalize and user_id in self.user_avg:
                    predicted_score += self.user_avg[user_id]
                
                final_predictions.append((item_id, predicted_score))
        
        # 5. 排序返回Top-N
        final_predictions.sort(key=lambda x: x[1], reverse=True)
        return final_predictions[:top_n]


class ItemCF:
    """基于物品的协同过滤推荐算法"""
    
    def __init__(self, similarity_method: str = 'cosine', use_adjusted: bool = True,
                 k_neighbors: int = 20, min_common_users: int = 3):
        """
        初始化ItemCF推荐器
        
        Args:
            similarity_method: 相似度计算方法 ('cosine' 或 'pearson')
            use_adjusted: 是否使用调整余弦相似度
            k_neighbors: 选取的最相似物品数量
            min_common_users: 计算相似度的最小共同用户数
        """
        self.similarity_method = similarity_method
        self.use_adjusted = use_adjusted
        self.k_neighbors = k_neighbors
        self.min_common_users = min_common_users
        self.item_users = {}  # {item_id: {user_id: score}}
        self.user_avg = {}  # {user_id: avg_score}
        self.similarity_cache = {}  # 相似度缓存
    
    def fit(self, ratings: List[Dict]) -> None:
        """
        训练模型：构建物品-用户评分矩阵
        
        Args:
            ratings: 评分列表 [{'user_id': int, 'item_id': int, 'score': float}, ...]
        """
        self.item_users = defaultdict(dict)
        user_items = defaultdict(dict)
        
        for rating in ratings:
            user_id = rating['user_id']
            item_id = rating['item_id']
            score = float(rating['score'])
            self.item_users[item_id][user_id] = score
            user_items[user_id][item_id] = score
        
        # 计算用户平均分（用于调整余弦相似度）
        self.user_avg = {
            uid: sum(items.values()) / len(items) if items else 0
            for uid, items in user_items.items()
        }
    
    def _calculate_similarity(self, item_id1: int, item_id2: int) -> float:
        """计算两个物品的相似度（带缓存）"""
        # 检查缓存
        cache_key = tuple(sorted([item_id1, item_id2]))
        if cache_key in self.similarity_cache:
            return self.similarity_cache[cache_key]
        
        vec1 = self.item_users.get(item_id1, {})
        vec2 = self.item_users.get(item_id2, {})
        
        # 检查共同用户数量
        common = set(vec1.keys()) & set(vec2.keys())
        if len(common) < self.min_common_users:
            self.similarity_cache[cache_key] = 0.0
            return 0.0
        
        # 选择相似度计算方法
        if self.use_adjusted and self.similarity_method == 'cosine':
            sim = SimilarityCalculator.adjusted_cosine_similarity(vec1, vec2, self.user_avg)
        elif self.similarity_method == 'pearson':
            sim = SimilarityCalculator.pearson_correlation(vec1, vec2)
        else:
            sim = SimilarityCalculator.cosine_similarity(vec1, vec2)
        
        self.similarity_cache[cache_key] = sim
        return sim
    
    def get_similar_items(self, item_id: int, top_n: int = 10) -> List[Tuple[int, float]]:
        """
        获取与指定物品最相似的物品列表
        
        Args:
            item_id: 目标物品ID
            top_n: 返回Top-N相似物品
            
        Returns:
            相似物品列表 [(item_id, similarity), ...]
        """
        if item_id not in self.item_users:
            return []
        
        similarities = []
        for iid in self.item_users.keys():
            if iid == item_id:
                continue
            
            sim = self._calculate_similarity(item_id, iid)
            if sim > 0:
                similarities.append((iid, sim))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_n]
    
    def recommend(self, user_id: int, user_rated_items: Dict[int, float], 
                 top_n: int = 10, exclude_rated: bool = True) -> List[Tuple[int, float]]:
        """
        为指定用户生成推荐列表
        
        Args:
            user_id: 目标用户ID
            user_rated_items: 用户已评分物品 {item_id: score}
            top_n: 返回Top-N推荐
            exclude_rated: 是否排除用户已评分的物品
            
        Returns:
            推荐列表 [(item_id, predicted_score), ...]
        """
        if not user_rated_items:
            return []
        
        # 1. 对于用户评分的每个物品，找到相似物品
        predictions = defaultdict(float)
        sim_sums = defaultdict(float)
        
        for rated_item_id, user_score in user_rated_items.items():
            # 获取相似物品
            similar_items = self.get_similar_items(rated_item_id, self.k_neighbors)
            
            for similar_item_id, similarity in similar_items:
                # 排除已评分物品
                if exclude_rated and similar_item_id in user_rated_items:
                    continue
                
                # 加权累加
                predictions[similar_item_id] += similarity * user_score
                sim_sums[similar_item_id] += similarity
        
        # 2. 计算最终预测分数
        final_predictions = []
        for item_id, weighted_sum in predictions.items():
            if sim_sums[item_id] > 0:
                predicted_score = weighted_sum / sim_sums[item_id]
                final_predictions.append((item_id, predicted_score))
        
        # 3. 排序返回Top-N
        final_predictions.sort(key=lambda x: x[1], reverse=True)
        return final_predictions[:top_n]


class HybridRecommender:
    """混合推荐模型：结合UserCF和ItemCF"""
    
    def __init__(self, user_cf: UserCF, item_cf: ItemCF, 
                 user_weight: float = 0.5, item_weight: float = 0.5):
        """
        初始化混合推荐器
        
        Args:
            user_cf: UserCF推荐器实例
            item_cf: ItemCF推荐器实例
            user_weight: UserCF的权重
            item_weight: ItemCF的权重
        """
        self.user_cf = user_cf
        self.item_cf = item_cf
        self.user_weight = user_weight
        self.item_weight = item_weight
    
    def recommend(self, user_id: int, user_rated_items: Dict[int, float], 
                 top_n: int = 10) -> List[Tuple[int, float]]:
        """
        生成混合推荐列表
        
        Args:
            user_id: 目标用户ID
            user_rated_items: 用户已评分物品 {item_id: score}
            top_n: 返回Top-N推荐
            
        Returns:
            推荐列表 [(item_id, predicted_score), ...]
        """
        # 获取UserCF推荐
        user_cf_recs = self.user_cf.recommend(user_id, top_n * 2)
        
        # 获取ItemCF推荐
        item_cf_recs = self.item_cf.recommend(user_id, user_rated_items, top_n * 2)
        
        # 合并推荐结果
        combined_scores = defaultdict(float)
        
        for item_id, score in user_cf_recs:
            combined_scores[item_id] += self.user_weight * score
        
        for item_id, score in item_cf_recs:
            combined_scores[item_id] += self.item_weight * score
        
        # 排序返回Top-N
        final_recs = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        return final_recs[:top_n]
