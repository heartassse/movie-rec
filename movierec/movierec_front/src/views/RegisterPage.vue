<template>
  <div class="register-page">
    <div class="register-card">
      <div class="card-header">
        <div class="logo-icon">⏱</div>
        <h2 class="title">豆瓣电影数据分析推荐系统</h2>
      </div>

      <div class="welcome-text">
        <h3>创建新账户</h3>
        <p>请填写以下信息完成注册。</p>
      </div>

      <form @submit.prevent="handleRegister" class="register-form">
        <div class="form-field">
          <label>用户名</label>
          <input 
            v-model="username" 
            type="text" 
            placeholder="请输入您的用户名" 
            required 
          />
        </div>

        <div class="form-field">
          <label>密码</label>
          <input 
            v-model="password" 
            type="password" 
            placeholder="请输入您的密码 (至少8位)" 
            required 
          />
        </div>

        <div class="form-field">
          <label>确认密码</label>
          <input 
            v-model="password2" 
            type="password" 
            placeholder="请再次输入密码" 
            required 
          />
        </div>

        <button type="submit" class="register-btn">注册</button>

        <p v-if="error" class="error-msg">{{ error }}</p>
        <p v-if="success" class="success-msg">{{ success }}</p>
      </form>

      <div class="footer-text">
        已经有账号？ 
        <a @click="$router.push('/login')" class="login-link">去登录</a>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'RegisterPage',
  data() {
    return {
      username: '',
      password: '',
      password2: '',
      error: '',
      success: ''
    }
  },
  methods: {
    async handleRegister() {
      this.error = ''
      this.success = ''

      if (this.password !== this.password2) {
        this.error = '注册失败：两次输入的密码不一致。';
        return;
      }

      try {
        await axios.post('/api/auth/register/', {
          username: this.username,
          password: this.password,
          password2: this.password2
        })
        this.success = '注册成功！请前往登录。'
        // 可以在这里延迟几秒再跳转
        setTimeout(() => {
          this.$router.push('/login')
        }, 2000)
      } catch (e) {
        let errorMsg = e.message;
        if (e.response && e.response.data) {
            const errors = Object.entries(e.response.data).map(([field, messages]) => {
                return `${field}: ${messages.join(' ')}`;
            });
            if (errors.length > 0) {
                errorMsg = errors.join('; ');
            }
        }
        this.error = '注册失败：' + errorMsg;
      }
    }
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-card {
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

.register-form {
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

.register-btn {
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
  margin-top: 8px;
}

.register-btn:hover {
  background: #5568d3;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.register-btn:active {
  transform: translateY(0);
}

.error-msg {
  margin-top: 16px;
  padding: 12px;
  background: #fff1f0;
  border: 1px solid #ffccc7;
  border-radius: 6px;
  color: #cf1322;
  font-size: 14px;
  text-align: center;
}

.success-msg {
  margin-top: 16px;
  padding: 12px;
  background: #f6ffed;
  border: 1px solid #b7eb8f;
  border-radius: 6px;
  color: #389e0d;
  font-size: 14px;
  text-align: center;
}

.footer-text {
  text-align: center;
  font-size: 14px;
  color: #666;
  margin-top: 24px;
}

.login-link {
  color: #667eea;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
}

.login-link:hover {
  text-decoration: underline;
}
</style>
