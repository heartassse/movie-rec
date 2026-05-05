<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h1 class="title">我的活动</h1>
        <p class="desc"></p>
      </div>
      <div class="stats-summary">
        <div class="stat-item">
          <span class="stat-number">{{ myRatings.length }}</span>
          <span class="stat-label">评分</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
          <span class="stat-number">{{ myComments.length }}</span>
          <span class="stat-label">评论</span>
        </div>
      </div>
    </div>

    <!-- 标签切换 -->
    <div class="tabs">
      <div 
        class="tab-item" 
        :class="{ active: activeTab === 'ratings' }"
        @click="activeTab = 'ratings'"
      >
        <span class="tab-icon">⭐</span>
        <span class="tab-text">我的评分</span>
        <span class="tab-count">{{ myRatings.length }}</span>
      </div>
      <div 
        class="tab-item" 
        :class="{ active: activeTab === 'comments' }"
        @click="activeTab = 'comments'"
      >
        <span class="tab-icon">💬</span>
        <span class="tab-text">我的评论</span>
        <span class="tab-count">{{ myComments.length }}</span>
      </div>
    </div>

    <!-- 评分列表 -->
    <div v-show="activeTab === 'ratings'" class="content-section">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>正在加载...</p>
      </div>
      <div v-else-if="error" class="error-state">
        <span class="error-icon">⚠️</span>
        <p>{{ error }}</p>
        <button class="retry-btn" @click="loadData">重试</button>
      </div>
      <div v-else-if="myRatings.length" class="activity-list">
        <div class="activity-card" v-for="r in myRatings" :key="r.book_id || r">
          <div class="card-main">
            <div class="movie-info">
              <h3 class="movie-title">{{ r.title || '未知电影' }}</h3>
              <div class="movie-meta">
                <span class="rating-display">
                  <span class="stars">{{ '★'.repeat(r.score) }}{{ '☆'.repeat(5 - r.score) }}</span>
                  <span class="score-text">{{ r.score }}.0 / 5.0</span>
                </span>
              </div>
              <div class="activity-time" v-if="r.created_at">
                评分时间：{{ formatDate(r.created_at) }}
              </div>
            </div>
          </div>
          <div class="card-actions">
            <button class="action-btn view" @click="goMovie(r.book_id)">
              <span class="btn-icon">👁️</span>查看详情
            </button>
            <button class="action-btn edit" @click="editRating(r)">
              <span class="btn-icon">✏️</span>修改评分
            </button>
          </div>
        </div>
      </div>
      <div v-else class="empty-state">
        <span class="empty-icon">⭐</span>
        <p class="empty-text">暂无评分记录</p>
        <p class="empty-hint">去给喜欢的电影评个分吧！</p>
        <button class="explore-btn" @click="$router.push('/home')">探索电影</button>
      </div>
    </div>

    <!-- 评论列表 -->
    <div v-show="activeTab === 'comments'" class="content-section">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>正在加载...</p>
      </div>
      <div v-else-if="error" class="error-state">
        <span class="error-icon">⚠️</span>
        <p>{{ error }}</p>
        <button class="retry-btn" @click="loadData">重试</button>
      </div>
      <div v-else-if="myComments.length" class="activity-list">
        <div class="activity-card" v-for="c in myComments" :key="c.id || c">
          <div class="card-main">
            <div class="movie-info">
              <h3 class="movie-title">{{ c.title || '未知电影' }}</h3>
              <div class="comment-content">{{ c.content || '（无内容）' }}</div>
              <div class="activity-time" v-if="c.created_at">
                评论时间：{{ formatDate(c.created_at) }}
              </div>
            </div>
          </div>
          <div class="card-actions">
            <button class="action-btn view" @click="goMovie(c.book_id)">
              <span class="btn-icon">👁️</span>查看详情
            </button>
            <button class="action-btn delete" @click="deleteComment(c)">
              <span class="btn-icon">🗑️</span>删除评论
            </button>
          </div>
        </div>
      </div>
      <div v-else class="empty-state">
        <span class="empty-icon">💬</span>
        <p class="empty-text">暂无评论记录</p>
        <p class="empty-hint">去分享你的观影感受吧！</p>
        <button class="explore-btn" @click="$router.push('/home')">探索电影</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ratingsApi } from '@/api'

export default {
  name: 'MyActivityPage',
  data() {
    return {
      activeTab: 'ratings',
      myRatings: [],
      myComments: [],
      loading: true,
      error: '',
    }
  },
  async mounted() {
    await this.loadData()
  },
  methods: {
    async loadData() {
      this.loading = true
      this.error = ''
      try {
        const [rRes, cRes] = await Promise.all([
          ratingsApi.myRatings(100),
          ratingsApi.myComments(100),
        ])
        this.myRatings = Array.isArray(rRes?.data?.results) ? rRes.data.results : []
        this.myComments = Array.isArray(cRes?.data?.results) ? cRes.data.results : []
      } catch (e) {
        this.error = e.response?.status === 401 ? '请先登录' : '无法加载数据，请稍后再试'
        console.error('loadData:', e)
      } finally {
        this.loading = false
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    goMovie(id) {
      this.$router.push(`/movie/${id}`)
    },
    editRating(rating) {
      // 跳转到电影详情页进行修改
      this.$router.push(`/movie/${rating.book_id}`)
    },
    async deleteComment(comment) {
      if (!confirm(`确定要删除这条评论吗？\n\n"${comment.content}"`)) {
        return
      }
      
      try {
        // 这里需要后端提供删除评论的接口
        // await ratingsApi.deleteComment(comment.id)
        alert('删除评论功能需要后端API支持')
        // 删除成功后重新加载
        // await this.loadData()
      } catch (e) {
        alert('删除失败：' + (e.response?.data?.detail || e.message))
      }
    }
  },
}
</script>

<style scoped>
.page {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f0f0f0;
}

.title {
  color: #333;
  margin: 0 0 4px 0;
  font-size: 28px;
  font-weight: 700;
}

.desc {
  color: #999;
  margin: 0;
  font-size: 14px;
}

.stats-summary {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 12px 24px;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #f0f0f0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-number {
  font-size: 24px;
  font-weight: 700;
  color: #1890ff;
}

.stat-label {
  font-size: 12px;
  color: #999;
}

.stat-divider {
  width: 1px;
  height: 32px;
  background: #e8e8e8;
}

.tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  background: #fff;
  padding: 8px;
  border-radius: 12px;
  border: 1px solid #f0f0f0;
}

.tab-item {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 20px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 15px;
  font-weight: 500;
  color: #666;
}

.tab-item:hover {
  background: #f5f5f5;
  color: #333;
}

.tab-item.active {
  background: #1890ff;
  color: #fff;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.3);
}

.tab-icon {
  font-size: 18px;
}

.tab-count {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  background: rgba(0,0,0,0.1);
}

.tab-item.active .tab-count {
  background: rgba(255,255,255,0.25);
}

.content-section {
  min-height: 400px;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.activity-card {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #f0f0f0;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  transition: all 0.3s;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}

.activity-card:hover {
  border-color: #1890ff;
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.15);
  transform: translateY(-2px);
}

.card-main {
  flex: 1;
}

.movie-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0 0 12px 0;
}

.movie-meta {
  margin-bottom: 8px;
}

.rating-display {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stars {
  font-size: 16px;
  color: #fadb14;
}

.score-text {
  font-size: 14px;
  font-weight: 600;
  color: #1890ff;
}

.comment-content {
  padding: 12px 16px;
  background: #fafafa;
  border-left: 3px solid #1890ff;
  border-radius: 6px;
  color: #666;
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 8px;
}

.activity-time {
  font-size: 12px;
  color: #bfbfbf;
}

.card-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  white-space: nowrap;
}

.action-btn.view {
  background: #fff;
  color: #1890ff;
  border: 1px solid #1890ff;
}

.action-btn.view:hover {
  background: #1890ff;
  color: #fff;
}

.action-btn.edit {
  background: #fff;
  color: #52c41a;
  border: 1px solid #52c41a;
}

.action-btn.edit:hover {
  background: #52c41a;
  color: #fff;
}

.action-btn.delete {
  background: #fff;
  color: #ff4d4f;
  border: 1px solid #ff4d4f;
}

.action-btn.delete:hover {
  background: #ff4d4f;
  color: #fff;
}

.btn-icon {
  font-size: 14px;
}

.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f0f0f0;
  border-top-color: #1890ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-icon,
.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.error-state p,
.loading-state p {
  color: #999;
  font-size: 14px;
  margin: 0;
}

.retry-btn {
  margin-top: 16px;
  padding: 8px 24px;
  background: #1890ff;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.retry-btn:hover {
  background: #40a9ff;
}

.empty-text {
  font-size: 18px;
  font-weight: 600;
  color: #666;
  margin: 0 0 8px 0;
}

.empty-hint {
  font-size: 14px;
  color: #999;
  margin: 0 0 20px 0;
}

.explore-btn {
  padding: 10px 32px;
  background: #1890ff;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.explore-btn:hover {
  background: #40a9ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.4);
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 16px;
  }

  .activity-card {
    flex-direction: column;
    align-items: stretch;
  }

  .card-actions {
    width: 100%;
  }

  .action-btn {
    flex: 1;
    justify-content: center;
  }
}
</style>
