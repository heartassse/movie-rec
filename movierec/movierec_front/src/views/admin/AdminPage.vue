<template>
  <div class="admin-layout">
    <aside class="sidebar">
      <div class="sidebar-brand">
        <div class="brand-icon">🎬</div>
        <span class="brand-text">电影推荐系统</span>
      </div>
      <nav class="sidebar-nav">
        <div class="nav-item" :class="{ active: activeTab === 'dashboard' }" @click="switchTab('dashboard')">
          <span class="nav-icon">📊</span><span>仪表板</span>
        </div>
        <div class="nav-item" :class="{ active: activeTab === 'users' }" @click="switchTab('users')">
          <span class="nav-icon">👤</span><span>用户管理</span>
        </div>
        <div class="nav-item" :class="{ active: activeTab === 'books' }" @click="switchTab('books')">
          <span class="nav-icon">🎬</span><span>电影管理</span>
        </div>
        <div class="nav-divider"></div>
        <div class="nav-item" @click="backToUser">
          <span class="nav-icon">↩</span><span>返回用户端</span>
        </div>
        <div class="nav-item" @click="logout">
          <span class="nav-icon">🚪</span><span>退出登录</span>
        </div>
      </nav>
    </aside>

    <div class="admin-body">
      <header class="admin-header">
        <div class="breadcrumb">
          <span class="bc-prefix">管理端</span>
          <span class="bc-sep">/</span>
          <span class="bc-current">{{ tabLabel }}</span>
        </div>
        <div class="header-right">
          <span class="admin-user">admin</span>
        </div>
      </header>

      <main class="admin-content">
        <div v-if="activeTab === 'dashboard'" class="dashboard">
          <h2 class="page-title">数据概览</h2>
          <p class="page-desc">系统运行状态和关键指标</p>

          <div class="stats-row">
            <div class="stat-card">
              <div class="stat-icon" style="background: #e6f7ff; color: #1890ff;">👤</div>
              <div class="stat-info">
                <div class="stat-label">总用户数</div>
                <div class="stat-value">{{ stats.users }}</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon" style="background: #f6ffed; color: #52c41a;">🎬</div>
              <div class="stat-info">
                <div class="stat-label">总电影数</div>
                <div class="stat-value">{{ stats.books }}</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon" style="background: #fff7e6; color: #fa8c16;">💬</div>
              <div class="stat-info">
                <div class="stat-label">总评论数</div>
                <div class="stat-value">{{ stats.comments }}</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon" style="background: #f9f0ff; color: #722ed1;">⭐</div>
              <div class="stat-info">
                <div class="stat-label">总评分数</div>
                <div class="stat-value">{{ stats.ratings }}</div>
              </div>
            </div>
          </div>

          <div class="dashboard-grid">
            <div class="dash-card">
              <div class="dash-card-header">
                <h3>🔥 热门电影</h3>
              </div>
              <div class="dash-list">
                <div class="dash-list-item" v-for="(m, i) in hotMovies" :key="m.id">
                  <span class="rank-badge" :class="'rank-' + (i + 1)">{{ i + 1 }}</span>
                  <span class="dash-item-title">{{ m.title }}</span>
                  <span class="dash-item-meta">{{ m.author || '未知' }}</span>
                </div>
                <div v-if="!hotMovies.length" class="dash-empty">暂无数据</div>
              </div>
            </div>
            <div class="dash-card">
              <div class="dash-card-header">
                <h3>📊 系统状态</h3>
              </div>
              <div class="sys-status">
                <div class="sys-item">
                  <div class="sys-label">数据更新时间</div>
                  <div class="sys-value">{{ currentTime }}</div>
                </div>
                <div class="sys-item">
                  <div class="sys-label">系统版本</div>
                  <div class="sys-value">v1.0.0</div>
                </div>
                <div class="sys-item">
                  <div class="sys-label">运行状态</div>
                  <div class="sys-value" style="color: #52c41a;">正常运行</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-show="activeTab === 'users'">
          <UserManagePanel />
        </div>
        <div v-show="activeTab === 'books'">
          <MovieManagePanel />
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import UserManagePanel from './UserManagePanel.vue'
import MovieManagePanel from './MovieManagePanel.vue'
import { recommendApi, moviesApi } from '@/api'

export default {
  name: 'AdminPage',
  components: { UserManagePanel, MovieManagePanel },
  data() {
    return {
      stats: { users: 0, books: 0, comments: 0, ratings: 0 },
      hotMovies: [],
      currentTime: new Date().toLocaleString(),
    }
  },
  computed: {
    activeTab() {
      const tab = this.$route.query.tab
      if (tab === 'books' || tab === 'users') return tab
      return 'dashboard'
    },
    tabLabel() {
      const map = { dashboard: '仪表板', users: '用户管理', books: '电影管理' }
      return map[this.activeTab] || '仪表板'
    },
  },
  async mounted() {
    await this.loadDashboard()
  },
  methods: {
    switchTab(tab) {
      this.$router.replace({ name: 'admin', query: { tab } })
    },
    backToUser() {
      this.$router.push('/home')
    },
    logout() {
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
      localStorage.removeItem('is_admin')
      this.$router.push('/login')
    },
    async loadDashboard() {
      try {
        const res = await recommendApi.stats()
        const s = res.data || {}
        this.stats = {
          users: s.total_users || 0,
          books: s.total_books || 0,
          comments: s.total_comments || 0,
          ratings: s.total_ratings || 0,
        }
        const hotRes = await recommendApi.hot(5)
        this.hotMovies = hotRes.data?.results || []
      } catch (e) {
        console.error('Dashboard load error:', e)
      }
    },
  },
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
  background: #f0f2f5;
}

.sidebar {
  width: 220px;
  min-height: 100vh;
  background: linear-gradient(180deg, #1a3a5c 0%, #0d2137 100%);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 100;
}

.sidebar-brand {
  padding: 20px 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}

.brand-icon {
  width: 36px;
  height: 36px;
  background: rgba(255,255,255,0.12);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.brand-text {
  color: #fff;
  font-size: 16px;
  font-weight: 700;
}

.sidebar-nav {
  padding: 12px 0;
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 11px 20px;
  color: rgba(255,255,255,0.65);
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
  margin: 2px 8px;
  border-radius: 6px;
}

.nav-item:hover {
  color: #fff;
  background: rgba(255,255,255,0.06);
}

.nav-item.active {
  color: #fff;
  background: #1890ff;
}

.nav-icon {
  font-size: 16px;
  width: 20px;
  text-align: center;
}

.nav-divider {
  height: 1px;
  background: rgba(255,255,255,0.06);
  margin: 12px 20px;
}

.admin-body {
  flex: 1;
  margin-left: 220px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.admin-header {
  height: 56px;
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 50;
}

.breadcrumb {
  font-size: 14px;
  color: #999;
}

.bc-current {
  color: #333;
}

.bc-sep {
  margin: 0 8px;
  color: #d9d9d9;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.admin-user {
  color: #333;
  font-size: 14px;
  font-weight: 500;
}

.admin-content {
  padding: 24px;
  flex: 1;
}

/* Dashboard */
.page-title {
  margin: 0 0 4px 0;
  font-size: 22px;
  font-weight: 700;
  color: #333;
}

.page-desc {
  margin: 0 0 20px 0;
  color: #999;
  font-size: 14px;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  border: 1px solid #f0f0f0;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  flex-shrink: 0;
}

.stat-label {
  color: #999;
  font-size: 13px;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #333;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.dash-card {
  background: #fff;
  border-radius: 8px;
  border: 1px solid #f0f0f0;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  overflow: hidden;
}

.dash-card-header {
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.dash-card-header h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #333;
}

.dash-list {
  padding: 8px 12px;
}

.dash-list-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 8px;
  border-bottom: 1px solid #f9f9f9;
}

.dash-list-item:last-child {
  border-bottom: none;
}

.rank-badge {
  width: 22px;
  height: 22px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: #fff;
  background: #d9d9d9;
  flex-shrink: 0;
}

.rank-1 { background: #1890ff; }
.rank-2 { background: #40a9ff; }
.rank-3 { background: #69c0ff; }

.dash-item-title {
  flex: 1;
  font-size: 14px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dash-item-meta {
  color: #bfbfbf;
  font-size: 12px;
}

.dash-empty {
  padding: 20px;
  text-align: center;
  color: #bfbfbf;
  font-size: 14px;
}

.sys-status {
  padding: 16px 20px;
}

.sys-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f9f9f9;
}

.sys-item:last-child {
  border-bottom: none;
}

.sys-label {
  color: #999;
  font-size: 14px;
}

.sys-value {
  color: #333;
  font-size: 14px;
  font-weight: 500;
}

@media (max-width: 1200px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .sidebar {
    width: 60px;
  }
  .brand-text, .nav-item span:not(.nav-icon) {
    display: none;
  }
  .admin-body {
    margin-left: 60px;
  }
  .nav-item {
    justify-content: center;
    padding: 12px;
  }
  .stats-row {
    grid-template-columns: 1fr;
  }
}
</style>
