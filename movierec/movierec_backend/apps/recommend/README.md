# 推荐算法模块

本模块实现了完整的协同过滤推荐算法，包括基于用户的协同过滤（UserCF）和基于物品的协同过滤（ItemCF），以及混合推荐模型。

## 目录结构

```
apps/recommend/
├── algorithms.py          # 核心算法实现
├── views.py              # API视图
├── urls.py               # URL路由
├── management/
│   └── commands/
│       └── eval_recommend.py  # 算法评估命令
└── README.md             # 本文档
```

## 核心算法

### 1. 基于用户的协同过滤（UserCF）

**原理**：通过计算用户之间的兴趣相似度，基于相似用户的评分行为预测目标用户可能感兴趣的书籍。

**相似度计算方法**：

#### 余弦相似度（Cosine Similarity）

```
sim(u,v) = Σ(r_ui * r_vi) / (√Σ(r_ui²) * √Σ(r_vi²))
```

其中：
- `r_ui` 表示用户u对物品i的评分
- 分子是两个用户共同评分物品的评分乘积之和
- 分母是各自评分向量的模长乘积

#### 皮尔逊相关系数（Pearson Correlation）

```
sim(u,v) = Σ((r_ui - r̄_u) * (r_vi - r̄_v)) / (√Σ(r_ui - r̄_u)² * √Σ(r_vi - r̄_v)²)
```

其中：
- `r̄_u` 表示用户u的平均评分
- 考虑了用户评分的偏差，更适合处理评分尺度不同的情况

**推荐流程**：

1. 计算目标用户与所有其他用户的相似度
2. 选取Top-K个最相似的用户作为邻居
3. 基于邻居的评分进行加权预测：
   ```
   pred(u,i) = Σ(sim(u,v) * r_vi) / Σ|sim(u,v)|
   ```
4. 排序返回Top-N推荐

**优化策略**：

- **评分归一化**：使用均值中心化或Z-score归一化，消除用户评分尺度差异
- **最小共同物品数**：只计算有足够共同评分物品的用户相似度（默认≥3）
- **邻居数量限制**：限制K值避免计算开销过大（默认K=30）

### 2. 基于物品的协同过滤（ItemCF）

**原理**：计算物品（书籍）之间的相似度，根据用户对相似书籍的历史评分来预测未评分书籍的偏好程度。

**相似度计算方法**：

#### 调整余弦相似度（Adjusted Cosine Similarity）

```
sim(i,j) = Σ((r_ui - r̄_u) * (r_uj - r̄_u)) / (√Σ(r_ui - r̄_u)² * √Σ(r_uj - r̄_u)²)
```

其中：
- 考虑了用户评分偏差，减去用户平均分后再计算
- 更适合ItemCF场景

**推荐流程**：

1. 对于用户评分的每个物品，找到Top-K个最相似的物品
2. 基于物品相似度和用户评分进行加权预测：
   ```
   pred(u,i) = Σ(sim(i,j) * r_uj) / Σ|sim(i,j)|
   ```
3. 排序返回Top-N推荐

**优化策略**：

- **相似度缓存**：物品相似度计算结果缓存，避免重复计算
- **最小共同用户数**：只计算有足够共同评分用户的物品相似度（默认≥3）
- **数据范围优化**：只查询与目标物品相关的用户评分，减少数据量

### 3. 混合推荐模型（Hybrid）

**原理**：结合UserCF和ItemCF的优势，通过加权融合两种算法的推荐结果。

**融合策略**：

```
score(u,i) = α * score_UserCF(u,i) + β * score_ItemCF(u,i)
```

其中：
- `α` 为UserCF权重（默认0.5）
- `β` 为ItemCF权重（默认0.5）
- `α + β = 1`

**优势**：

- 互补性：UserCF擅长发现新兴趣，ItemCF擅长深度推荐
- 鲁棒性：单一算法失效时，另一算法可以补充
- 灵活性：可根据场景调整权重

## API 接口

### 1. UserCF推荐

```
GET /api/recommend/user/
```

**参数**：
- `limit`: 推荐数量，默认10
- `method`: 相似度方法（cosine/pearson），默认cosine
- `normalize`: 是否归一化（true/false），默认true
- `k`: 邻居数量，默认30

**示例**：
```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/recommend/user/?limit=10&method=pearson&k=30"
```

### 2. ItemCF推荐（相似书籍）

```
GET /api/recommend/similar/
```

**参数**：
- `book_id`: 目标书籍ID（必需）
- `limit`: 推荐数量，默认10
- `method`: 相似度方法（cosine/pearson），默认cosine
- `adjusted`: 是否使用调整余弦（true/false），默认true
- `k`: 邻居数量，默认20

**示例**：
```bash
curl "http://localhost:8000/api/recommend/similar/?book_id=123&limit=10&adjusted=true"
```

### 3. 混合推荐

```
GET /api/recommend/hybrid/
```

**参数**：
- `limit`: 推荐数量，默认10
- `user_weight`: UserCF权重，默认0.5
- `item_weight`: ItemCF权重，默认0.5
- `method`: 相似度方法（cosine/pearson），默认cosine

**示例**：
```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/recommend/hybrid/?limit=10&user_weight=0.6&item_weight=0.4"
```

### 4. 热门书籍（冷启动）

```
GET /api/recommend/hot/
```

**参数**：
- `limit`: 返回数量，默认10

**示例**：
```bash
curl "http://localhost:8000/api/recommend/hot/?limit=20"
```

## 算法评估

使用管理命令评估推荐算法性能：

```bash
# 评估UserCF（余弦相似度）
python manage.py eval_recommend --method usercf --similarity cosine --k 10

# 评估ItemCF（皮尔逊相关系数）
python manage.py eval_recommend --method itemcf --similarity pearson --k 10

# 自定义参数
python manage.py eval_recommend \
  --method usercf \
  --similarity cosine \
  --k 10 \
  --test-ratio 0.2 \
  --min-ratings 5
```

**评估指标**：

1. **Precision@K**：推荐列表中用户实际喜欢的比例
   ```
   Precision@K = |推荐且喜欢| / |推荐|
   ```

2. **Recall@K**：用户喜欢的物品中被推荐出来的比例
   ```
   Recall@K = |推荐且喜欢| / |喜欢|
   ```

3. **F1-Score**：Precision和Recall的调和平均
   ```
   F1 = 2 * (Precision * Recall) / (Precision + Recall)
   ```

4. **Coverage**：推荐系统能够推荐的物品占总物品的比例
   ```
   Coverage = |推荐过的物品| / |所有物品|
   ```

## 性能优化

### 1. 缓存机制

- 使用Django内置缓存系统
- 热门推荐缓存5分钟
- 用户推荐缓存2分钟
- 相似书籍缓存5分钟
- 物品相似度计算结果缓存

### 2. 数据范围优化

- ItemCF只查询与目标书籍相关的用户评分
- 减少不必要的数据库查询
- 使用批量查询和预加载

### 3. 算法优化

- 最小共同项数过滤（用户/物品）
- Top-K邻居限制
- 评分归一化减少计算误差

## 冷启动问题处理

### 1. 新用户冷启动

- 返回热门书籍推荐
- 基于用户注册信息推荐（如有）
- 引导用户快速评分

### 2. 新物品冷启动

- 基于物品属性（作者、出版年份、简介）推荐
- 混合推荐中降低ItemCF权重

### 3. 数据稀疏问题

- 使用皮尔逊相关系数处理评分尺度差异
- 设置最小共同项数阈值
- 混合推荐提高鲁棒性

## 技术栈

- **Python 3.8+**
- **Django 4.x**
- **Django REST Framework**
- **数学库**：内置math模块
- **数据结构**：defaultdict, Counter

## 参考文献

1. Sarwar, B., et al. (2001). "Item-based collaborative filtering recommendation algorithms"
2. Resnick, P., et al. (1994). "GroupLens: an open architecture for collaborative filtering"
3. Koren, Y., et al. (2009). "Matrix factorization techniques for recommender systems"

## 未来改进方向

1. **深度学习推荐**：引入神经网络模型（如NCF、DeepFM）
2. **内容推荐**：基于书籍标签、简介的内容推荐
3. **时间衰减**：考虑评分时间，近期评分权重更高
4. **隐式反馈**：利用浏览、收藏等隐式行为
5. **上下文感知**：考虑时间、地点等上下文信息
6. **多目标优化**：平衡准确性、多样性、新颖性
