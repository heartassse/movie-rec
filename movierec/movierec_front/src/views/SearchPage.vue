<template>
  <div class="page">
    <h1 class="title">电影搜索</h1>
    <p class="desc"></p>

    <div class="panel">
      <div class="search-bar">
        <input v-model="keyword" placeholder="输入关键词（电影名/导演）" @keyup.enter="doSearch" />
        <button class="primary-btn" @click="doSearch">搜索</button>
      </div>

      <div class="filters">
        <div
          class="chip"
          v-for="c in categories"
          :key="c.value"
          :class="{ active: c.value === category }"
          @click="selectCategory(c.value)"
        >
          {{ c.label }} ({{ c.count }})
        </div>

        <div class="spacer"></div>

        <label class="select-label">排序</label>
        <select v-model="sort" class="select" @change="doSearch">
          <option value="default">默认（最新）</option>
          <option value="title">电影名</option>
          <option value="author">导演</option>
          <option value="year">上映年份</option>
        </select>
      </div>

      <div class="result-head">
        <div class="count">共 {{ totalCount }} 条结果{{ keyword ? `（搜索: "${keyword}"）` : '' }}</div>
        <div class="pager">
          <button class="secondary-btn small" :disabled="page <= 1" @click="page--">上一页</button>
          <span class="page-no">{{ page }} / {{ totalPages }}</span>
          <button class="secondary-btn small" :disabled="page >= totalPages" @click="page++">下一页</button>
        </div>
      </div>

      <div v-if="loading" class="empty">
        正在加载电影... {{ allBooks.length > 0 ? `已加载 ${allBooks.length} 部` : '' }}
      </div>
      <div v-else-if="error" class="empty" style="color:#ff6b6b">{{ error }}</div>
      <div v-else-if="paged.length" class="grid">
        <MovieCard v-for="b in paged" :key="b.id" :book="b" @click="go(b.id)" />
      </div>
      <div v-else class="empty">没有匹配的电影，请换个关键词试试。</div>
    </div>
  </div>
</template>

<script>
import MovieCard from '@/components/MovieCard.vue'
import { mockMovies } from '@/mock/data'
import { moviesApi } from '@/api'
import { USE_MOCK } from '@/config'

export default {
  name: 'SearchPage',
  components: { MovieCard },
  data() {
    return {
      keyword: '',
      category: 'all',
      sort: 'default',
      page: 1,
      pageSize: 12,
      // 分类列表（根据实际数据动态生成）
      categories: [
        { label: '全部', value: 'all', count: 0 },
        { label: '剧情', value: 'drama', count: 0 },
        { label: '喜剧', value: 'comedy', count: 0 },
        { label: '动作', value: 'action', count: 0 },
        { label: '爱情', value: 'romance', count: 0 },
        { label: '科幻', value: 'scifi', count: 0 },
        { label: '悬疑', value: 'thriller', count: 0 },
        { label: '动画', value: 'animation', count: 0 },
      ],
      // 数据源
      allBooks: [],
      books: [],
      loading: false,
      error: '',
    }
  },
  computed: {
    filtered() {
      const kw = this.keyword.trim().toLowerCase()
      let list = this.books

      // 分类筛选（基于电影名和描述的关键词匹配）
      if (this.category !== 'all') {
        list = list.filter((b) => {
          const title = (b.title || '').toLowerCase()
          const desc = (b.description || '').toLowerCase()
          const author = (b.author || '').toLowerCase()
          const text = `${title} ${desc} ${author}`

          const categoryKeywords = {
            drama: ['剧情', 'drama', '文艺', '家庭'],
            comedy: ['喜剧', 'comedy', '搞笑', '幽默'],
            action: ['动作', 'action', '冒险', '战争', '武侠'],
            romance: ['爱情', 'romance', '浪漫', '情感'],
            scifi: ['科幻', 'sci-fi', '奇幻', '魔幻'],
            thriller: ['悬疑', 'thriller', '犯罪', '惊悚', '推理'],
            animation: ['动画', 'animation', '动漫', '卡通'],
          }

          const keywords = categoryKeywords[this.category] || []
          return keywords.some((kw) => text.includes(kw))
        })
      }

      // 关键词搜索
      if (kw) {
        list = list.filter((b) => {
          const t = (b.title || '').toLowerCase()
          const a = (b.author || '').toLowerCase()
          const i = (b.isbn || '').toLowerCase()
          const d = (b.description || '').toLowerCase()
          return t.includes(kw) || a.includes(kw) || i.includes(kw) || d.includes(kw)
        })
      }

      // 排序
      if (this.sort === 'title') {
        list = [...list].sort((x, y) => (x.title || '').localeCompare(y.title || ''))
      } else if (this.sort === 'author') {
        list = [...list].sort((x, y) => (x.author || '').localeCompare(y.author || ''))
      } else if (this.sort === 'year') {
        list = [...list].sort((x, y) => (y.publication_year || 0) - (x.publication_year || 0))
      }

      return list
    },
    totalCount() {
      return this.filtered.length
    },
    totalPages() {
      return Math.max(1, Math.ceil(this.filtered.length / this.pageSize))
    },
    paged() {
      const p = Math.min(this.page, this.totalPages)
      const start = (p - 1) * this.pageSize
      const end = start + this.pageSize
      return this.filtered.slice(start, end)
    },
  },
  watch: {
    keyword() {
      this.page = 1
      if (!this.keyword.trim()) {
        this.books = this.allBooks
      }
    },
    category() {
      this.page = 1
      this.updateCategoryCounts()
    },
    sort() {
      this.page = 1
    },
    page() {
      if (this.page < 1) this.page = 1
      if (this.page > this.totalPages) this.page = this.totalPages
    },
  },
  async mounted() {
    // 检查 URL 参数中是否有搜索关键词
    const urlParams = new URLSearchParams(window.location.search)
    const queryKeyword = urlParams.get('q')
    if (queryKeyword) {
      this.keyword = queryKeyword
    }
    
    await this.loadBooks()
    
    // 如果有搜索关键词，执行搜索
    if (this.keyword) {
      await this.doSearch()
    }
  },
  methods: {
    async loadBooks() {
      this.loading = true
      this.error = ''
      try {
        if (USE_MOCK) {
          this.allBooks = mockMovies
          this.books = mockMovies
        } else {
          // 加载全部电影数据供搜索筛选
          const res = await moviesApi.search({ page: 1, page_size: 50000 })
          this.allBooks = res.data.results || []
          this.books = res.data.results || []
          
          // 更新分类计数
          this.updateCategoryCounts()
          
          console.log(`已加载 ${this.allBooks.length} 部电影`)
        }
      } catch (e) {
        this.error = '加载电影失败，请稍后再试。'
        console.error(e)
      } finally {
        this.loading = false
      }
    },
    updateCategoryCounts() {
      // 更新每个分类的电影数量
      this.categories.forEach((cat) => {
        if (cat.value === 'all') {
          cat.count = this.allBooks.length
        } else {
          const categoryKeywords = {
            drama: ['剧情', 'drama', '文艺', '家庭'],
            comedy: ['喜剧', 'comedy', '搞笑', '幽默'],
            action: ['动作', 'action', '冒险', '战争', '武侠'],
            romance: ['爱情', 'romance', '浪漫', '情感'],
            scifi: ['科幻', 'sci-fi', '奇幻', '魔幻'],
            thriller: ['悬疑', 'thriller', '犯罪', '惊悚', '推理'],
            animation: ['动画', 'animation', '动漫', '卡通'],
          }

          const keywords = categoryKeywords[cat.value] || []
          cat.count = this.allBooks.filter((b) => {
            const title = (b.title || '').toLowerCase()
            const desc = (b.description || '').toLowerCase()
            const author = (b.author || '').toLowerCase()
            const text = `${title} ${desc} ${author}`
            return keywords.some((kw) => text.includes(kw))
          }).length
        }
      })
    },
    async doSearch() {
      this.page = 1
      
      if (USE_MOCK) {
        // Mock 模式下使用本地过滤
        return
      }

      this.loading = true
      this.error = ''
      try {
        let ordering = '-created_at'
        if (this.sort === 'title') {
          ordering = 'title'
        } else if (this.sort === 'author') {
          ordering = 'author'
        } else if (this.sort === 'year') {
          ordering = '-publication_year'
        }

        const res = await moviesApi.search({
          search: this.keyword.trim() || undefined,
          ordering,
        })
        
        this.books = res.data.results || []
        
        // 如果有关键词搜索，更新分类计数
        if (this.keyword.trim()) {
          this.updateCategoryCounts()
        }
      } catch (e) {
        this.error = '搜索失败，请稍后再试。'
        console.error(e)
      } finally {
        this.loading = false
      }
    },
    selectCategory(c) {
      this.category = c
      if (!this.keyword.trim()) {
        // 如果没有搜索关键词，使用全部电影
        this.books = this.allBooks
      }
    },
    go(id) {
      this.$router.push(`/movie/${id}`)
    },
  },
}
</script>

<style scoped>
.page { width: 100%; max-width: 1200px; margin: 0 auto; padding: 20px; box-sizing: border-box; }
.title { color: #333; margin: 0 0 4px 0; font-size: 24px; font-weight: 700; }
.desc { color: #999; margin: 0 0 16px 0; font-size: 14px; }
.panel { padding: 20px; border-radius: 8px; background: #fff; border: 1px solid #f0f0f0; box-shadow: 0 1px 4px rgba(0,0,0,0.04); }
.search-bar { display: flex; gap: 10px; }
.search-bar input { flex: 1; padding: 10px 14px; border-radius: 4px; border: 1px solid #d9d9d9; background: #fff; color: #333; font-size: 14px; }
.search-bar input:focus { outline: none; border-color: #1890ff; box-shadow: 0 0 0 2px rgba(24,144,255,0.1); }
.primary-btn { padding: 10px 20px; border-radius: 4px; border: none; background: #1890ff; color: #fff; font-weight: 500; cursor: pointer; font-size: 14px; }
.primary-btn:hover { background: #40a9ff; }
.filters { margin-top: 14px; display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
.spacer { flex: 1; }
.select-label { color: #666; font-size: 13px; }
.select { padding: 8px 12px; border-radius: 4px; border: 1px solid #d9d9d9; background: #fff; color: #333; font-size: 13px; }
.chip { padding: 6px 14px; border-radius: 16px; background: #fafafa; border: 1px solid #e8e8e8; color: #666; cursor: pointer; transition: all 0.2s; font-size: 13px; }
.chip:hover { border-color: #1890ff; color: #1890ff; }
.chip.active { border-color: #1890ff; color: #1890ff; background: #e6f7ff; font-weight: 600; }
.result-head { margin-top: 14px; display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap; }
.count { color: #666; font-size: 14px; }
.pager { display: flex; align-items: center; gap: 8px; }
.page-no { color: #666; font-size: 14px; }
.secondary-btn.small { padding: 6px 12px; border-radius: 4px; background: #fff; border: 1px solid #d9d9d9; color: #333; cursor: pointer; font-size: 13px; }
.secondary-btn.small:hover { color: #1890ff; border-color: #1890ff; }
.secondary-btn.small:disabled { opacity: 0.4; cursor: not-allowed; }
.grid { margin-top: 12px; display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; }
.empty { margin-top: 16px; color: #bfbfbf; font-size: 14px; }
.hint { margin-top: 16px; color: #bfbfbf; font-size: 13px; }
</style>
