# 🎬 影视推荐系统

> 基于Django + Vue3的现代化影视推荐平台  
> 支持事件驱动推荐、可解释推荐、观看进度管理  
> **数据源均来源于对豆瓣爬虫获取**

---

## 🚀 快速启动（复制粘贴这些命令）

```powershell
# 1. 进入后端目录
cd movierec\movierec_backend

# 2. 创建数据库（首次需要）
mysql -u root -p -e "CREATE DATABASE movierec_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 3. 执行迁移（首次需要）
python manage.py migrate

# 4. 导入数据（使用 SQL 文件）
mysql -u root -p movierec_dev < ..\数据源\movierec_电影推荐系统.sql

# 5. 启动后端
python manage.py runserver
```

**新开终端，启动前端**：
```powershell
cd movierec\movierec_front
npm install  # 首次需要
npm run dev
```

### 🎉 访问系统

- **前端**：http://localhost:5173/explore
- **后台**：http://127.0.0.1:8000/admin/（用户名：admin，密码：admin123）

**预计总时间**：20分钟（含数据导入）

---

## 📊 数据集

**本系统所有数据源均来源于对豆瓣爬虫获取。**

### 豆瓣电影数据集（945万条）

- **位置**：`数据源/`
- **规模**：
  - 📽️ 140,502部电影
  - 👥 639,125名用户
  - ⭐ 4,169,420条评分
  - 💬  4,428,475条评论
- **来源**：通过爬虫从豆瓣电影官网采集（2019年）

---

## 🎯 核心功能

- 🎬 **影视浏览**：搜索、筛选、分页
- 📺 **观看管理**：想看/在看/看过
- ⏯️ **播放进度**：断点续播
- 🤖 **智能推荐**：热门/相似/个性化
- 💡 **推荐理由**："因为你看过《X》"
- 📊 **数据分析**：用户行为、热度趋势

---

## 🛠️ 技术栈

- **后端**：Django 4.2 + Django REST Framework + MySQL 8.0
- **前端**：Vue 3 + Vite + Vue Router + Axios
- **推荐算法**：
  - 协同过滤（UserCF/ItemCF）
  - 内容推荐（Jaccard相似度）
  - 事件驱动推荐（时间衰减）
  - 可解释推荐

---

## 📚 文档导航

- **movierec_crawler/README.md** - 豆瓣电影爬虫使用说明
- **movierec_crawler/USAGE.md** - 爬虫进阶用法
- **movierec_backend/apps/recommend/README.md** - 推荐算法说明
- **推荐效果评估结果分析.md** - 推荐算法评估报告

---

## ⚡ 常用命令

### 数据导入（SQL）

```powershell
# 创建数据库后，使用 SQL 文件导入
mysql -u root -p -e "CREATE DATABASE movierec_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p movierec_dev < 数据源\movierec_电影推荐系统.sql
```

### 数据导出（备份）

```powershell
python db_export.py
# 或指定输出文件：python db_export.py --output movierec_backup.sql
```

---

## 🐛 常见问题

### Q1：命令找不到？

确保在正确的目录：
```powershell
cd movierec\movierec_backend
```

### Q2：SQL 导入失败？

确保数据库已创建，且 SQL 文件编码为 utf8mb4。

### Q3：数据库未创建？

```powershell
mysql -u root -p -e "CREATE DATABASE movierec_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
python manage.py migrate
```

---

## 📞 获取帮助

- **爬虫使用**：查看 `movierec_crawler/README.md`
- **推荐算法**：查看 `movierec_backend/apps/recommend/README.md`

---

## 🎓 学术价值

- ✅ 数据源全部来自对豆瓣爬虫获取，945万条真实数据（国内最大公开数据集）
- ✅ 事件驱动推荐（创新点）
- ✅ 可解释推荐（提升用户信任）
- ✅ 多路召回融合（工程实践）

---

## 📁 项目结构

```
movie-rec/
├── movierec/
│   ├── movierec_backend/     # Django 后端
│   ├── movierec_front/       # Vue3 前端
│   ├── movierec_crawler/     # 豆瓣电影爬虫（Scrapy）
│   ├── 数据源/               # SQL 数据文件
│   │   └── movierec_电影推荐系统.sql
│   └── README.md             # 子项目文档
├── README.md                 # 本文档
└── .gitignore
```

---

## 📊 推荐算法效果

本系统实现了多种推荐算法，并通过离线评估验证了推荐效果：

| 算法 | Precision@10 | Recall@10 | F1-Score | Coverage |
|------|-------------|-----------|----------|----------|
| UserCF (cosine) | 1.05% | 5.39% | 0.0176 | 7.10% |
| ItemCF (pearson) | 0.47% | 2.81% | 0.0081 | 10.36% |

**主要结论**：
- UserCF 在准确性上优于 ItemCF
- ItemCF 在多样性（覆盖率）上更好
- 建议采用混合策略兼顾准确性与多样性

详细评估报告请查看 `movierec/推荐效果评估结果分析.md`

---

## 🚦 许可证

本项目仅用于学术研究目的，数据来源于豆瓣公开信息，请遵守相关法律法规。

---

**🎬 现在就开始使用吧！**

**推荐命令**：
```powershell
cd movierec\movierec_backend
mysql -u root -p movierec_dev < ..\数据源\movierec_电影推荐系统.sql
```
