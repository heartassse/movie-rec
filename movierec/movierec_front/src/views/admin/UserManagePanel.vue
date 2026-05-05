<template>
  <div class="user-manage">
    <div class="page-header">
      <div>
        <h2 class="page-title">用户管理</h2>
        <p class="page-desc">查看、创建、编辑和删除用户账号（包括设置管理员权限）</p>
      </div>
      <div class="header-actions">
        <button class="add-btn" @click="showAddForm = !showAddForm">+ 新增用户</button>
      </div>
    </div>

    <!-- 新增用户表单 -->
    <div v-if="showAddForm" class="add-card">
      <h3 class="add-card-title">新增用户</h3>
      <form @submit.prevent="createUser" class="add-form">
        <div class="form-grid">
          <label class="form-label">
            <span>用户名 *</span>
            <input v-model="form.username" placeholder="输入用户名" required class="form-input" />
          </label>
          <label class="form-label">
            <span>邮箱</span>
            <input v-model="form.email" placeholder="输入邮箱（可选）" class="form-input" />
          </label>
          <label class="form-label">
            <span>密码 *</span>
            <input v-model="form.password" placeholder="输入密码" type="password" required class="form-input" />
          </label>
          <label class="form-label checkbox-label">
            <span>权限</span>
            <div class="checkbox-row">
              <label class="check-item">
                <input type="checkbox" v-model="form.is_staff" />
                <span>管理员</span>
              </label>
            </div>
          </label>
        </div>
        <div class="form-actions">
          <button type="button" class="cancel-btn" @click="showAddForm = false">取消</button>
          <button type="submit" class="submit-btn" :disabled="creating">{{ creating ? '创建中...' : '确认创建' }}</button>
        </div>
      </form>
      <p v-if="error && showAddForm" class="error-msg">{{ error }}</p>
    </div>

    <!-- 用户列表 -->
    <div class="list-bar">
      <span class="count-text">共 {{ users.length }} 个用户</span>
      <button class="refresh-btn" @click="fetchUsers">🔄 刷新</button>
    </div>

    <div class="user-table" v-if="users.length">
      <div class="table-header">
        <div class="col-id">ID</div>
        <div class="col-name">用户名</div>
        <div class="col-email">邮箱</div>
        <div class="col-status">状态</div>
        <div class="col-role">角色</div>
        <div class="col-actions">操作</div>
      </div>

      <div class="table-row" v-for="u in users" :key="u.id">
        <div class="col-id">
          <span class="row-id">{{ u.id }}</span>
        </div>
        <div class="col-name">
          <div class="user-avatar">{{ (u.username || '?')[0].toUpperCase() }}</div>
          <span class="user-name-text">{{ u.username }}</span>
        </div>
        <div class="col-email">{{ u.email || '-' }}</div>
        <div class="col-status">
          <span class="status-tag" :class="u.is_active ? 'active' : 'disabled'" @click="toggleActive(u)">
            {{ u.is_active ? '启用' : '禁用' }}
          </span>
        </div>
        <div class="col-role">
          <span class="role-tag" v-if="u.is_superuser">超级管理员</span>
          <span class="role-tag admin" v-else-if="u.is_staff">管理员</span>
          <span class="role-tag user" v-else>普通用户</span>
        </div>
        <div class="col-actions">
          <button class="act-btn act-toggle" @click="toggleStaff(u)">
            {{ u.is_staff ? '取消管理员' : '设为管理员' }}
          </button>
          <button class="act-btn act-delete" @click="deleteUser(u)">删除</button>
        </div>
      </div>
    </div>
    <div v-else class="empty-state">暂无用户数据</div>

    <p v-if="error && !showAddForm" class="error-msg" style="margin-top: 12px;">{{ error }}</p>
  </div>
</template>

<script>
import { adminUsersApi } from '@/api'

export default {
  name: 'UserManagePanel',
  data() {
    return {
      users: [],
      creating: false,
      error: '',
      showAddForm: false,
      form: {
        username: '',
        email: '',
        password: '',
        is_staff: false,
      },
    }
  },
  async mounted() {
    await this.fetchUsers()
  },
  methods: {
    async fetchUsers() {
      try {
        const res = await adminUsersApi.list()
        this.users = Array.isArray(res.data) ? res.data : (res.data.results || [])
      } catch (e) {
        console.error(e)
        this.error = '加载用户列表失败'
      }
    },
    async createUser() {
      this.creating = true
      this.error = ''
      try {
        await adminUsersApi.create({ ...this.form })
        this.form = { username: '', email: '', password: '', is_staff: false }
        this.showAddForm = false
        await this.fetchUsers()
      } catch (e) {
        console.error(e)
        this.error = '创建用户失败'
      } finally {
        this.creating = false
      }
    },
    async toggleActive(user) {
      user.is_active = !user.is_active
      await this.updateUser(user)
    },
    async toggleStaff(user) {
      user.is_staff = !user.is_staff
      await this.updateUser(user)
    },
    async updateUser(user) {
      try {
        await adminUsersApi.update(user.id, {
          username: user.username,
          email: user.email,
          is_active: user.is_active,
          is_staff: user.is_staff,
          is_superuser: user.is_superuser,
        })
      } catch (e) {
        console.error(e)
        this.error = '更新用户失败'
      }
    },
    async deleteUser(user) {
      if (!confirm(`确定要删除用户 ${user.username} 吗？`)) return
      try {
        await adminUsersApi.delete(user.id)
        this.users = this.users.filter(u => u.id !== user.id)
      } catch (e) {
        console.error(e)
        this.error = '删除用户失败'
      }
    },
  },
}
</script>

<style scoped>
.user-manage {
  color: #333;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-title {
  margin: 0 0 4px 0;
  font-size: 22px;
  font-weight: 700;
  color: #1a1a1a;
}

.page-desc {
  margin: 0;
  color: #999;
  font-size: 14px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.add-btn {
  padding: 9px 20px;
  border-radius: 8px;
  border: none;
  background: #1890ff;
  color: #fff;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.add-btn:hover { background: #40a9ff; }

.add-card {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.add-card-title {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #333;
  font-weight: 600;
}

.add-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.form-label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 13px;
  color: #666;
  font-weight: 500;
}

.form-input {
  padding: 9px 12px;
  border-radius: 6px;
  border: 1px solid #d9d9d9;
  background: #fff;
  color: #333;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
}

.checkbox-row {
  display: flex;
  gap: 16px;
  padding-top: 4px;
}

.check-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #555;
  cursor: pointer;
}

.check-item input[type="checkbox"] {
  accent-color: #1890ff;
  width: 16px;
  height: 16px;
}

.form-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  padding-top: 8px;
}

.cancel-btn {
  padding: 8px 20px;
  border-radius: 6px;
  border: 1px solid #d9d9d9;
  background: #fff;
  color: #666;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn:hover { border-color: #bbb; color: #333; }

.submit-btn {
  padding: 8px 20px;
  border-radius: 6px;
  border: none;
  background: #1890ff;
  color: #fff;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.submit-btn:hover { background: #40a9ff; }
.submit-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.error-msg {
  color: #ff4d4f;
  font-size: 13px;
  margin-top: 8px;
}

/* List Bar */
.list-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.count-text { color: #999; font-size: 14px; }

.refresh-btn {
  padding: 6px 14px;
  border-radius: 6px;
  border: 1px solid #d9d9d9;
  background: #fff;
  color: #666;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.refresh-btn:hover { border-color: #1890ff; color: #1890ff; }

/* User Table */
.user-table {
  background: #fff;
  border-radius: 10px;
  border: 1px solid #e8e8e8;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}

.table-header {
  display: flex;
  align-items: center;
  padding: 14px 20px;
  background: #fafafa;
  border-bottom: 1px solid #e8e8e8;
  font-size: 13px;
  font-weight: 600;
  color: #666;
}

.table-row {
  display: flex;
  align-items: center;
  padding: 14px 20px;
  border-bottom: 1px solid #f5f5f5;
  transition: background 0.15s;
}

.table-row:last-child { border-bottom: none; }
.table-row:hover { background: #fafafa; }

.col-id { width: 60px; flex-shrink: 0; }
.col-name { flex: 1; min-width: 140px; display: flex; align-items: center; gap: 10px; }
.col-email { flex: 1; min-width: 160px; color: #666; font-size: 13px; }
.col-status { width: 80px; flex-shrink: 0; text-align: center; }
.col-role { width: 120px; flex-shrink: 0; text-align: center; }
.col-actions { width: 200px; flex-shrink: 0; display: flex; gap: 8px; justify-content: flex-end; }

.row-id {
  color: #999;
  font-size: 13px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #1890ff;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
}

.user-name-text {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.status-tag {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.status-tag.active {
  background: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

.status-tag.disabled {
  background: #fff2f0;
  color: #ff4d4f;
  border: 1px solid #ffa39e;
}

.role-tag {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  background: #f9f0ff;
  color: #722ed1;
  border: 1px solid #d3adf7;
}

.role-tag.admin {
  background: #e6f7ff;
  color: #1890ff;
  border: 1px solid #91d5ff;
}

.role-tag.user {
  background: #f5f5f5;
  color: #999;
  border: 1px solid #d9d9d9;
}

.act-btn {
  padding: 5px 12px;
  border-radius: 4px;
  border: none;
  background: transparent;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.act-toggle { color: #1890ff; }
.act-toggle:hover { background: rgba(24,144,255,0.08); }
.act-delete { color: #ff4d4f; }
.act-delete:hover { background: rgba(255,77,79,0.06); }

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #bfbfbf;
  font-size: 15px;
  background: #fff;
  border-radius: 10px;
  border: 1px solid #e8e8e8;
}

@media (max-width: 900px) {
  .table-header { display: none; }
  .table-row { flex-wrap: wrap; gap: 8px; }
  .col-actions { width: auto; }
  .form-grid { grid-template-columns: 1fr; }
  .page-header { flex-direction: column; }
}
</style>
