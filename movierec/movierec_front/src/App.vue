<template>
  <div id="app-container">
    <SnowfallEffect />

    <!-- 用户界面侧边栏 -->
    <aside class="user-sidebar" v-if="showNav && isLoggedIn">
      <div class="sidebar-brand">
        <div class="brand-icon">🎬</div>
        <span class="brand-text">电影推荐系统</span>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/home" class="nav-item">
          <span class="nav-icon">🏠</span><span>首页</span>
        </router-link>
        <router-link to="/recommend" class="nav-item">
          <span class="nav-icon">💡</span><span>推荐</span>
        </router-link>
        <router-link to="/search" class="nav-item">
          <span class="nav-icon">🔍</span><span>搜索</span>
        </router-link>
        <router-link to="/visualize" class="nav-item">
          <span class="nav-icon">📊</span><span>可视化</span>
        </router-link>
        <router-link to="/wordcloud" class="nav-item">
          <span class="nav-icon">☁️</span><span>词云</span>
        </router-link>
        <div class="nav-divider"></div>
        <router-link to="/activity" class="nav-item">
          <span class="nav-icon">📝</span><span>我的活动</span>
        </router-link>
        <router-link to="/profile" class="nav-item">
          <span class="nav-icon">👤</span><span>个人中心</span>
        </router-link>
        <a v-if="isAdmin" href="#" class="nav-item" @click.prevent="$router.push({ name: 'admin', query: { tab: 'dashboard' } })">
          <span class="nav-icon">⚙️</span><span>管理后台</span>
        </a>
        <a href="#" class="nav-item" @click.prevent="logout">
          <span class="nav-icon">🚪</span><span>退出登录</span>
        </a>
      </nav>
    </aside>

    <main :class="{ 'with-sidebar': showNav && isLoggedIn, 'admin-main': isAdminView, 'login-view': !showNav }">
      <router-view />
    </main>
  </div>
</template>

<script>
import SnowfallEffect from './components/SnowfallEffect.vue'

export default {
  components: {
    SnowfallEffect,
  },
  data() {
    return {
      isLoggedIn: false,
      isAdmin: false,
    }
  },
  computed: {
    showNav() {
      if (this.$route.name === 'login' || this.$route.name === 'register') return false
      if (this.$route.path.startsWith('/admin')) return false
      return true
    },
    isAdminView() {
      return this.$route.path.startsWith('/admin')
    },
  },
  watch: {
    $route() {
      this.checkLoginStatus()
    },
  },
  created() {
    this.checkLoginStatus()
  },
  methods: {
    checkLoginStatus() {
      this.isLoggedIn = !!localStorage.getItem('access')
      this.isAdmin = localStorage.getItem('is_admin') === '1'
    },
    logout() {
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
      localStorage.removeItem('is_admin')
      this.isLoggedIn = false
      this.isAdmin = false
      this.$router.push('/login')
    },
  },
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app-container {
  position: relative;
  z-index: 1;
  background: #f0f2f5;
  min-height: 100vh;
  display: flex;
}

/* 用户侧边栏样式 */
.user-sidebar {
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
  text-decoration: none;
}

.nav-item:hover {
  color: #fff;
  background: rgba(255,255,255,0.06);
}

.nav-item.router-link-active {
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

/* Main Content */
main {
  min-height: 100vh;
  box-sizing: border-box;
  background: #f0f2f5;
  width: 100%;
}

main.with-sidebar {
  margin-left: 220px;
  padding: 24px;
}

main.login-view {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

main.admin-main {
  padding: 0;
  margin-left: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .user-sidebar {
    width: 60px;
  }
  
  .brand-text, 
  .nav-item span:not(.nav-icon) {
    display: none;
  }
  
  .nav-item {
    justify-content: center;
    padding: 12px;
  }
  
  main.with-sidebar {
    margin-left: 60px;
  }
}

@media (prefers-reduced-motion: reduce) {
  * {
    transition: none !important;
  }
}
</style>
