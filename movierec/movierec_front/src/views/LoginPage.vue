<template>
  <div class="login-page">
    <div class="login-card">
      <div class="card-header">
        <div class="logo-icon">⏱</div>
        <h2 class="title">豆瓣电影数据分析推荐系统</h2>
      </div>

      <div class="welcome-text">
        <h3>你好 欢迎！</h3>
        <p>请输入你的详细信息。</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-field" :class="{ 'has-error': error }">
          <label>用户名</label>
          <input 
            v-model="username" 
            type="text" 
            placeholder="请输入您的用户名" 
            required 
            @input="error = ''"
          />
        </div>

        <div class="form-field" :class="{ 'has-error': error }">
          <label>密码</label>
          <input 
            v-model="password" 
            type="password" 
            placeholder="请输入您的密码" 
            required 
            @input="error = ''"
          />
        </div>

        <div class="form-options">
          <label class="remember-checkbox">
            <input type="checkbox" id="remember" />
            <span>记住我</span>
          </label>
        </div>

        <button type="submit" class="login-btn">登录</button>

        <p v-if="error" class="error-msg">{{ error }}</p>
      </form>

      <div class="footer-text">
        还没有账号？ 
        <a @click="$router.push('/register')" class="register-link">注册</a>
      </div>
    </div>
  </div>
</template>

<script>
import { authApi } from '@/api'

export default {
  name: 'LoginPage',
  data() {
    return {
      username: '',
      password: '',
      error: ''
    }
  },
  methods: {
    async handleLogin() {
      this.error = ''
      
      // 前端验证
      if (!this.username.trim()) {
        this.error = '请输入用户名'
        return
      }
      if (!this.password) {
        this.error = '请输入密码'
        return
      }

      try {
        const res = await authApi.login({
          username: this.username,
          password: this.password
        })
        localStorage.setItem('access', res.data.access)
        localStorage.setItem('refresh', res.data.refresh)

        // 获取当前用户信息，判断是否为管理员
        try {
          const meRes = await authApi.me()
          const me = meRes.data || {}
          const isAdmin = !!(me.is_staff || me.is_superuser)
          if (isAdmin) {
            localStorage.setItem('is_admin', '1')
            this.$router.push('/admin')
            return
          } else {
            localStorage.removeItem('is_admin')
          }
        } catch (e) {
          console.error('fetch /auth/me/ failed', e)
        }

        // 普通用户进入用户界面
        this.$router.push('/home')
      } catch (e) {
        // 更友好的错误提示
        if (e.response) {
          const status = e.response.status
          const data = e.response.data
          
          if (status === 401) {
            this.error = '❌ 用户名或密码错误，请重新输入'
          } else if (status === 400) {
            if (data.detail) {
              this.error = '❌ ' + data.detail
            } else if (data.username) {
              this.error = '❌ 用户名：' + data.username.join(', ')
            } else if (data.password) {
              this.error = '❌ 密码：' + data.password.join(', ')
            } else {
              this.error = '❌ 登录失败，请检查输入信息'
            }
          } else if (status === 500) {
            this.error = '❌ 服务器错误，请稍后再试'
          } else {
            this.error = '❌ 登录失败：' + (data.detail || '未知错误')
          }
        } else if (e.request) {
          this.error = '❌ 无法连接到服务器，请检查网络连接'
        } else {
          this.error = '❌ 登录失败：' + e.message
        }
      }
    }
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 420px;
  background: #ffffff;
  border-radius: 12px;
  padding: 40px 32px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.card-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto 16px;
  background: #f0f0f0;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.welcome-text {
  margin-bottom: 28px;
}

.welcome-text h3 {
  font-size: 24px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 8px 0;
}

.welcome-text p {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.login-form {
  margin-bottom: 24px;
}

.form-field {
  margin-bottom: 20px;
}

.form-field label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
}

.form-field input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  color: #333;
  box-sizing: border-box;
  transition: all 0.3s;
}

.form-field input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-field input::placeholder {
  color: #999;
}

.form-field.has-error input {
  border-color: #ff4d4f;
  background: #fff1f0;
}

.form-field.has-error input:focus {
  border-color: #ff4d4f;
  box-shadow: 0 0 0 3px rgba(255, 77, 79, 0.1);
}

.form-options {
  margin-bottom: 24px;
}

.remember-checkbox {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 14px;
  color: #666;
}

.remember-checkbox input {
  margin-right: 8px;
  cursor: pointer;
}

.remember-checkbox span {
  user-select: none;
}

.login-btn {
  width: 100%;
  padding: 14px;
  background: #667eea;
  border: none;
  border-radius: 8px;
  color: #ffffff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.login-btn:hover {
  background: #5568d3;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.login-btn:active {
  transform: translateY(0);
}

.error-msg {
  margin-top: 16px;
  padding: 14px 16px;
  background: #fff1f0;
  border: 1px solid #ffccc7;
  border-left: 4px solid #ff4d4f;
  border-radius: 6px;
  color: #cf1322;
  font-size: 14px;
  text-align: left;
  animation: shake 0.4s;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-8px); }
  75% { transform: translateX(8px); }
}

.footer-text {
  text-align: center;
  font-size: 14px;
  color: #666;
  margin-top: 24px;
}

.register-link {
  color: #667eea;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
}

.register-link:hover {
  text-decoration: underline;
}
</style>

