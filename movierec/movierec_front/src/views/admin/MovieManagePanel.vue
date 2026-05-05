<template>
  <div class="book-manage">
    <div class="page-header">
      <div>
        <h2 class="page-title">电影管理</h2>
        <p class="page-desc">管理电影信息、分类和状态</p>
      </div>
      <div class="header-actions">
        <div class="search-bar">
          <input
            v-model="searchQuery"
            @input="onSearchInput"
            placeholder="搜索电影名称或分类"
            class="search-input"
          />
        </div>
        <button class="add-btn" @click="showAddForm = !showAddForm">+ 新增电影</button>
      </div>
    </div>

    <!-- 新增表单（可折叠） -->
    <div v-if="showAddForm" class="add-card">
      <h3 class="add-card-title">新增电影</h3>
      <form @submit.prevent="createBook" class="add-form">
        <div class="form-grid">
          <label class="form-label">
            <span>电影名 *</span>
            <input v-model="form.title" placeholder="输入电影名称" required class="form-input" />
          </label>
          <label class="form-label">
            <span>导演</span>
            <input v-model="form.author" placeholder="输入导演名称" class="form-input" />
          </label>
          <label class="form-label">
            <span>上映年份</span>
            <input v-model="form.publication_year" placeholder="如：2024" class="form-input" type="text" />
          </label>
          <label class="form-label">
            <span>豆瓣ID</span>
            <input v-model="form.isbn" placeholder="豆瓣电影ID" class="form-input" />
          </label>
        </div>
        <label class="form-label">
          <span>封面URL</span>
          <input v-model="form.cover_url" placeholder="https://..." class="form-input" />
        </label>
        <label class="form-label">
          <span>电影简介</span>
          <textarea v-model="form.description" placeholder="输入电影简介..." class="form-textarea" rows="3"></textarea>
        </label>
        <div class="form-actions">
          <button type="button" class="cancel-btn" @click="showAddForm = false">取消</button>
          <button type="submit" class="submit-btn" :disabled="creating">{{ creating ? '添加中...' : '确认添加' }}</button>
        </div>
      </form>
      <p v-if="error && showAddForm" class="error-msg">{{ error }}</p>
    </div>

    <!-- 列表头 -->
    <div class="list-bar">
      <span class="count-text">共 {{ totalBooks }} 个电影</span>
      <button class="refresh-btn" @click="fetchBooks(currentPage)">🔄 刷新</button>
    </div>

    <!-- 电影列表 -->
    <div class="movie-table" v-if="books.length">
      <div class="table-header">
        <div class="col-num">序号</div>
        <div class="col-info">电影信息</div>
        <div class="col-stats">数据统计</div>
        <div class="col-status">状态</div>
        <div class="col-time">创建时间</div>
        <div class="col-actions">操作</div>
      </div>

      <div class="table-row" v-for="(b, idx) in books" :key="b.id">
        <div class="col-num">
          <span class="row-index" :class="{ 'top-rank': idx < 3 }">{{ (currentPage - 1) * pageSize + idx + 1 }}</span>
        </div>
        <div class="col-info">
          <img
            v-if="b.cover_url"
            :src="b.cover_url"
            class="movie-poster"
            @error="$event.target.style.display='none'"
          />
          <div v-else class="movie-poster-placeholder">🎬</div>
          <div class="movie-meta">
            <div class="movie-name">{{ b.title }}</div>
            <div class="movie-director">{{ b.author || '未知导演' }}</div>
          </div>
        </div>
        <div class="col-stats">
          <div class="stat-line" v-if="b.publication_year">
            <span class="stat-icon">📅</span>
            <span>{{ b.publication_year }} 年</span>
          </div>
          <div class="stat-line" v-if="b.isbn">
            <span class="stat-icon">🆔</span>
            <span>{{ b.isbn }}</span>
          </div>
        </div>
        <div class="col-status">
          <span class="status-tag">上架</span>
        </div>
        <div class="col-time">-</div>
        <div class="col-actions">
          <button class="act-btn act-edit" @click="openEditModal(b)">编辑</button>
          <button class="act-btn act-delete" @click="deleteBook(b)">删除</button>
        </div>
      </div>
    </div>
    <div v-else class="empty-state">暂无电影数据</div>

    <!-- 分页 -->
    <div class="pagination" v-if="totalPages > 1">
      <button class="page-btn" :disabled="currentPage === 1" @click="goToPage(currentPage - 1)">‹ 上一页</button>
      <span class="page-info">第 {{ currentPage }} / {{ totalPages }} 页</span>
      <button class="page-btn" :disabled="currentPage === totalPages" @click="goToPage(currentPage + 1)">下一页 ›</button>
    </div>

    <!-- 编辑模态框 -->
    <div v-if="editingBook" class="modal-overlay" @click.self="closeEditModal">
      <div class="modal-content">
        <h3 class="modal-title">编辑电影详情</h3>
        <div class="modal-form">
          <label class="form-label"><span>电影名 *</span><input v-model="editingBook.title" class="form-input" required /></label>
          <label class="form-label"><span>导演</span><input v-model="editingBook.author" class="form-input" /></label>
          <div style="display: flex; gap: 12px;">
            <label class="form-label" style="flex: 1;"><span>上映年份</span><input v-model="editingBook.publication_year" class="form-input" type="text" placeholder="如：2024" /></label>
            <label class="form-label" style="flex: 1;"><span>豆瓣ID</span><input v-model="editingBook.isbn" class="form-input" /></label>
          </div>
          <label class="form-label"><span>封面URL</span><input v-model="editingBook.cover_url" class="form-input" placeholder="https://..." /></label>
          <label class="form-label"><span>电影简介</span><textarea v-model="editingBook.description" class="form-textarea" rows="4"></textarea></label>
        </div>
        <p v-if="error" class="error-msg">{{ error }}</p>
        <div class="modal-actions">
          <button class="cancel-btn" @click="closeEditModal">取消</button>
          <button class="submit-btn" @click="saveEdit">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { adminMoviesApi } from '@/api'

export default {
  name: 'MovieManagePanel',
  data() {
    return {
      books: [],
      totalBooks: 0,
      currentPage: 1,
      pageSize: 20,
      creating: false,
      error: '',
      searchQuery: '',
      searchTimeout: null,
      showAddForm: false,
      form: {
        title: '',
        author: '',
        publication_year: '',
        isbn: '',
        description: '',
        cover_url: '',
      },
      editingBook: null,
    }
  },
  computed: {
    totalPages() {
      return Math.ceil(this.totalBooks / this.pageSize)
    },
  },
  async mounted() {
    await this.fetchBooks()
  },
  methods: {
    async fetchBooks(page = 1) {
      try {
        const res = await adminMoviesApi.list(page, this.pageSize, this.searchQuery)
        if (Array.isArray(res.data)) {
          this.books = res.data
          this.totalBooks = res.data.length
        } else {
          this.books = res.data.results || []
          this.totalBooks = res.data.count || 0
        }
        this.currentPage = page
      } catch (e) {
        console.error(e)
        this.error = '加载电影列表失败'
      }
    },
    onSearchInput() {
      if (this.searchTimeout) clearTimeout(this.searchTimeout)
      this.searchTimeout = setTimeout(() => {
        this.currentPage = 1
        this.fetchBooks(1)
      }, 500)
    },
    async goToPage(page) {
      if (page < 1 || page > this.totalPages) return
      await this.fetchBooks(page)
    },
    async createBook() {
      this.creating = true
      this.error = ''
      try {
        const payload = {
          title: this.form.title.trim(),
          author: this.form.author?.trim() || '',
          publication_year: this.form.publication_year?.trim() ? parseInt(this.form.publication_year.trim(), 10) : null,
          isbn: this.form.isbn?.trim() || null,
          description: this.form.description?.trim() || '',
          cover_url: this.form.cover_url?.trim() || null,
        }
        if (isNaN(payload.publication_year)) payload.publication_year = null
        await adminMoviesApi.create(payload)
        Object.keys(this.form).forEach(k => this.form[k] = '')
        this.showAddForm = false
        await this.fetchBooks(1)
      } catch (e) {
        console.error(e)
        if (e.response?.data) {
          const errors = e.response.data
          this.error = typeof errors === 'object' ? Object.values(errors).flat().join('; ') : errors.toString()
        } else {
          this.error = '新增电影失败'
        }
      } finally {
        this.creating = false
      }
    },
    openEditModal(book) {
      this.editingBook = { ...book, publication_year: book.publication_year?.toString() || '' }
      this.error = ''
    },
    closeEditModal() {
      this.editingBook = null
      this.error = ''
    },
    async saveEdit() {
      if (!this.editingBook) return
      this.error = ''
      try {
        const payload = {
          title: this.editingBook.title?.trim() || '',
          author: this.editingBook.author?.trim() || '',
          publication_year: this.editingBook.publication_year?.trim() ? parseInt(this.editingBook.publication_year.trim(), 10) : null,
          isbn: this.editingBook.isbn?.trim() || null,
          description: this.editingBook.description?.trim() || '',
          cover_url: this.editingBook.cover_url?.trim() || null,
        }
        if (isNaN(payload.publication_year)) payload.publication_year = null
        await adminMoviesApi.update(this.editingBook.id, payload)
        await this.fetchBooks(this.currentPage)
        this.closeEditModal()
      } catch (e) {
        console.error(e)
        if (e.response?.data) {
          const errors = e.response.data
          this.error = typeof errors === 'object' ? Object.values(errors).flat().join('; ') : errors.toString()
        } else {
          this.error = '保存失败'
        }
      }
    },
    async deleteBook(book) {
      if (!confirm(`确定要删除《${book.title}》吗？\n\n删除后将同时删除该电影的所有评分和评论数据。`)) return
      try {
        await adminMoviesApi.delete(book.id)
        this.totalBooks -= 1
        await this.fetchBooks(this.currentPage)
      } catch (e) {
        console.error(e)
        this.error = '删除电影失败'
      }
    },
  },
}
</script>

<style scoped>
.book-manage {
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

.search-bar {
  position: relative;
}

.search-input {
  padding: 9px 14px;
  border-radius: 8px;
  border: 1px solid #d9d9d9;
  background: #fff;
  color: #333;
  font-size: 14px;
  width: 220px;
  transition: border-color 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #1890ff;
}

.search-input::placeholder {
  color: #bfbfbf;
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
  white-space: nowrap;
  transition: background 0.2s;
}

.add-btn:hover {
  background: #40a9ff;
}

/* Add Form Card */
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

.form-textarea {
  width: 100%;
  padding: 9px 12px;
  border-radius: 6px;
  border: 1px solid #d9d9d9;
  background: #fff;
  color: #333;
  font-size: 14px;
  resize: vertical;
  font-family: inherit;
  box-sizing: border-box;
  transition: border-color 0.2s;
}

.form-textarea:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
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

.cancel-btn:hover {
  border-color: #bbb;
  color: #333;
}

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

.submit-btn:hover {
  background: #40a9ff;
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

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

.count-text {
  color: #999;
  font-size: 14px;
}

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

.refresh-btn:hover {
  border-color: #1890ff;
  color: #1890ff;
}

/* Movie Table */
.movie-table {
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
  padding: 16px 20px;
  border-bottom: 1px solid #f5f5f5;
  transition: background 0.15s;
}

.table-row:last-child {
  border-bottom: none;
}

.table-row:hover {
  background: #fafafa;
}

.col-num { width: 60px; flex-shrink: 0; text-align: center; }
.col-info { flex: 1; min-width: 200px; display: flex; align-items: center; gap: 12px; }
.col-stats { width: 180px; flex-shrink: 0; }
.col-status { width: 80px; flex-shrink: 0; text-align: center; }
.col-time { width: 120px; flex-shrink: 0; color: #999; font-size: 13px; }
.col-actions { width: 140px; flex-shrink: 0; display: flex; gap: 8px; justify-content: flex-end; }

.row-index {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  background: #f0f0f0;
  color: #999;
}

.row-index.top-rank {
  background: #1890ff;
  color: #fff;
}

.movie-poster {
  width: 50px;
  height: 70px;
  object-fit: cover;
  border-radius: 6px;
  flex-shrink: 0;
  background: #f5f5f5;
}

.movie-poster-placeholder {
  width: 50px;
  height: 70px;
  border-radius: 6px;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.movie-meta {
  min-width: 0;
}

.movie-name {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 240px;
}

.movie-director {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.stat-line {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #666;
  margin-bottom: 2px;
}

.stat-icon {
  font-size: 12px;
}

.status-tag {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  background: #e6f7ff;
  color: #1890ff;
  border: 1px solid #91d5ff;
}

.act-btn {
  padding: 5px 12px;
  border-radius: 4px;
  border: none;
  background: transparent;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.act-edit {
  color: #1890ff;
}

.act-edit:hover {
  background: rgba(24,144,255,0.08);
}

.act-delete {
  color: #ff4d4f;
}

.act-delete:hover {
  background: rgba(255,77,79,0.06);
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #bfbfbf;
  font-size: 15px;
  background: #fff;
  border-radius: 10px;
  border: 1px solid #e8e8e8;
}

/* Pagination */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 20px;
}

.page-btn {
  padding: 8px 18px;
  border-radius: 6px;
  border: 1px solid #d9d9d9;
  background: #fff;
  color: #555;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  border-color: #1890ff;
  color: #1890ff;
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-info {
  color: #999;
  font-size: 14px;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.45);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
}

.modal-content {
  background: #fff;
  border-radius: 12px;
  padding: 28px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 8px 32px rgba(0,0,0,0.12);
}

.modal-title {
  margin: 0 0 20px 0;
  font-size: 18px;
  color: #333;
  font-weight: 600;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

@media (max-width: 900px) {
  .table-header { display: none; }
  .table-row { flex-wrap: wrap; gap: 8px; }
  .col-num { width: 30px; }
  .col-stats, .col-status, .col-time { width: auto; }
  .form-grid { grid-template-columns: 1fr; }
  .page-header { flex-direction: column; }
}
</style>