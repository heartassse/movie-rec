<template>
  <div class="page">
    <h1 class="title">个人中心</h1>
    <p class="desc"></p>

    <!-- 基本信息面板 -->
    <div class="panel info-panel">
      <div class="panel-header">
        <h2 class="subtitle">基本信息</h2>
        <button v-if="!editMode" class="edit-btn" @click="enterEditMode">
          <span class="btn-icon">✏️</span>编辑资料
        </button>
      </div>

      <div v-if="!editMode" class="info-view">
        <div class="info-row">
          <span class="info-label">用户ID</span>
          <span class="info-value">{{ userInfo.id || '-' }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">用户名</span>
          <span class="info-value">{{ userInfo.username || '-' }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">邮箱</span>
          <span class="info-value">{{ userInfo.email || '未设置' }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">注册时间</span>
          <span class="info-value">{{ formatDate(userInfo.date_joined) }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">账号状态</span>
          <span class="info-value">
            <span class="status-badge" :class="userInfo.is_active ? 'active' : 'inactive'">
              {{ userInfo.is_active ? '正常' : '已禁用' }}
            </span>
          </span>
        </div>
        <div class="info-row">
          <span class="info-label">账号类型</span>
          <span class="info-value">
            <span class="role-badge" v-if="userInfo.is_superuser">超级管理员</span>
            <span class="role-badge" v-else-if="userInfo.is_staff">管理员</span>
            <span class="role-badge normal" v-else>普通用户</span>
          </span>
        </div>
      </div>

      <div v-else class="info-edit">
        <div class="form-field">
          <label>用户ID</label>
          <input type="text" :value="userInfo.id" disabled class="disabled-input" />
          <span class="field-hint">用户ID不可修改</span>
        </div>
        <div class="form-field">
          <label>用户名</label>
          <input v-model="editForm.username" type="text" placeholder="请输入用户名" />
        </div>
        <div class="form-field">
          <label>邮箱</label>
          <input v-model="editForm.email" type="email" placeholder="请输入邮箱地址" />
        </div>
        <div class="form-field">
          <label>新密码</label>
          <input v-model="editForm.password" type="password" placeholder="留空则不修改密码" />
          <span class="field-hint">至少8位字符</span>
        </div>
        <div class="form-field">
          <label>确认密码</label>
          <input v-model="editForm.password2" type="password" placeholder="再次输入新密码" />
        </div>

        <div class="form-actions">
          <button class="cancel-btn" @click="cancelEdit">取消</button>
          <button class="save-btn" @click="saveProfile" :disabled="saving">
            {{ saving ? '保存中...' : '保存修改' }}
          </button>
        </div>

        <p v-if="editError" class="error-msg">{{ editError }}</p>
        <p v-if="editSuccess" class="success-msg">{{ editSuccess }}</p>
      </div>
    </div>

    <!-- 快捷入口 -->
    <div class="quick-links">
      <router-link to="/activity" class="quick-link-card">
        <div class="link-icon">📝</div>
        <div class="link-info">
          <div class="link-title">我的活动</div>
          <div class="link-desc">查看评分和评论记录</div>
        </div>
        <div class="link-arrow">→</div>
      </router-link>
      <router-link to="/home" class="quick-link-card">
        <div class="link-icon">🎬</div>
        <div class="link-info">
          <div class="link-title">探索电影</div>
          <div class="link-desc">发现更多精彩内容</div>
        </div>
        <div class="link-arrow">→</div>
      </router-link>
    </div>
  </div>
</template>

<script>
import { authApi } from '@/api'
import axios from 'axios'

export default {
  name: 'ProfilePage',
  data() {
    return {
      userInfo: {},
      editMode: false,
      editForm: {
        username: '',
        email: '',
        password: '',
        password2: ''
      },
      saving: false,
      editError: '',
      editSuccess: '',
      loading: true,
      error: '',
    }
  },
  async mounted() {
    await this.loadUserData()
  },
  methods: {
    async loadUserData() {
      this.loading = true
      this.error = ''
      try {
        const meRes = await authApi.me()
        this.userInfo = meRes.data || {}
      } catch (e) {
        this.error = '无法加载个人数据，请稍后再试'
        console.error(e)
      } finally {
        this.loading = false
      }
    },
    enterEditMode() {
      this.editMode = true
      this.editForm = {
        username: this.userInfo.username || '',
        email: this.userInfo.email || '',
        password: '',
        password2: ''
      }
      this.editError = ''
      this.editSuccess = ''
    },
    cancelEdit() {
      this.editMode = false
      this.editError = ''
      this.editSuccess = ''
    },
    async saveProfile() {
      this.editError = ''
      this.editSuccess = ''

      // 验证
      if (!this.editForm.username.trim()) {
        this.editError = '用户名不能为空'
        return
      }

      if (this.editForm.password || this.editForm.password2) {
        if (this.editForm.password !== this.editForm.password2) {
          this.editError = '两次输入的密码不一致'
          return
        }
        if (this.editForm.password.length < 8) {
          this.editError = '密码至少需要8位字符'
          return
        }
      }

      this.saving = true

      try {
        const payload = {
          username: this.editForm.username.trim(),
          email: this.editForm.email.trim() || null,
        }

        if (this.editForm.password) {
          payload.password = this.editForm.password
        }

        // 调用更新接口（需要后端支持）
        await axios.put(`/api/auth/me/`, payload)

        this.editSuccess = '个人信息更新成功！'
        
        // 重新加载用户数据
        setTimeout(async () => {
          await this.loadUserData()
          this.editMode = false
        }, 1500)

      } catch (e) {
        let errorMsg = '更新失败，请稍后再试'
        if (e.response && e.response.data) {
          const errors = Object.entries(e.response.data).map(([field, messages]) => {
            return `${field}: ${Array.isArray(messages) ? messages.join(' ') : messages}`
          })
          if (errors.length > 0) {
            errorMsg = errors.join('; ')
          }
        }
        this.editError = errorMsg
      } finally {
        this.saving = false
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

.title {
  color: #333;
  margin: 0 0 4px 0;
  font-size: 24px;
  font-weight: 700;
}

.desc {
  color: #999;
  margin: 0 0 20px 0;
  font-size: 14px;
}

.panel {
  padding: 24px;
  border-radius: 8px;
  background: #fff;
  border: 1px solid #f0f0f0;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  margin-bottom: 20px;
}

.info-panel {
  padding: 0;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
}

.subtitle {
  color: #333;
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.edit-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #1890ff;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.edit-btn:hover {
  background: #40a9ff;
}

.btn-icon {
  font-size: 16px;
}

.info-view {
  padding: 24px;
}

.info-row {
  display: flex;
  align-items: center;
  padding: 14px 0;
  border-bottom: 1px solid #f5f5f5;
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  width: 120px;
  color: #999;
  font-size: 14px;
  font-weight: 500;
}

.info-value {
  flex: 1;
  color: #333;
  font-size: 14px;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active {
  background: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

.status-badge.inactive {
  background: #fff1f0;
  color: #ff4d4f;
  border: 1px solid #ffccc7;
}

.role-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  background: #e6f7ff;
  color: #1890ff;
  border: 1px solid #91d5ff;
}

.role-badge.normal {
  background: #fafafa;
  color: #666;
  border: 1px solid #d9d9d9;
}

.info-edit {
  padding: 24px;
}

.form-field {
  margin-bottom: 20px;
}

.form-field label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.form-field input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  font-size: 14px;
  color: #333;
  box-sizing: border-box;
  transition: all 0.3s;
}

.form-field input:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
}

.form-field input.disabled-input {
  background: #f5f5f5;
  color: #999;
  cursor: not-allowed;
}

.field-hint {
  display: block;
  margin-top: 6px;
  font-size: 12px;
  color: #999;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.cancel-btn,
.save-btn {
  flex: 1;
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.cancel-btn {
  background: #fff;
  color: #333;
  border: 1px solid #d9d9d9;
}

.cancel-btn:hover {
  color: #1890ff;
  border-color: #1890ff;
}

.save-btn {
  background: #1890ff;
  color: #fff;
  border: none;
}

.save-btn:hover:not(:disabled) {
  background: #40a9ff;
}

.save-btn:disabled {
  background: #91d5ff;
  cursor: not-allowed;
}

.error-msg {
  margin-top: 16px;
  padding: 12px;
  background: #fff1f0;
  border: 1px solid #ffccc7;
  border-radius: 6px;
  color: #cf1322;
  font-size: 14px;
}

.success-msg {
  margin-top: 16px;
  padding: 12px;
  background: #f6ffed;
  border: 1px solid #b7eb8f;
  border-radius: 6px;
  color: #389e0d;
  font-size: 14px;
}

.quick-links {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.quick-link-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #f0f0f0;
  text-decoration: none;
  transition: all 0.3s;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}

.quick-link-card:hover {
  border-color: #1890ff;
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.15);
  transform: translateY(-2px);
}

.link-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.link-info {
  flex: 1;
}

.link-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.link-desc {
  font-size: 13px;
  color: #999;
}

.link-arrow {
  font-size: 20px;
  color: #bfbfbf;
  transition: all 0.3s;
}

.quick-link-card:hover .link-arrow {
  color: #1890ff;
  transform: translateX(4px);
}

@media (max-width: 768px) {
  .quick-links {
    grid-template-columns: 1fr;
  }
}
</style>
