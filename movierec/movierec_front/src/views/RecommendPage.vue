<template>
  <div class="page">
    <h1 class="title">推荐</h1>
    <p class="desc"></p>

    <div class="panel">
      <h2 class="subtitle">推荐列表</h2>
      <div v-if="loading" class="state">正在加载推荐...</div>
      <div v-else-if="error" class="state error">{{ error }}</div>
      <div v-else-if="!recommendBooks.length" class="state">暂无推荐，试试多评分/评论以获得更好结果。</div>
      <div v-else class="grid">
        <MovieCard v-for="b in recommendBooks" :key="b.id" :book="b" @click="go(b.id)" />
      </div>
    </div>
  </div>
</template>

<script>
import MovieCard from '@/components/MovieCard.vue'
import { recommendApi } from '@/api'
import { USE_MOCK } from '@/config'

export default {
  name: 'RecommendPage',
  components: { MovieCard },
  data() {
    return {
      recommendBooks: [],
      loading: true,
      error: '',
    }
  },
  async mounted() {
    this.loading = true
    this.error = ''
    try {
      const isLoggedIn = !!localStorage.getItem('access')
      // 登录且非 Mock 时尝试个性化
      if (isLoggedIn && !USE_MOCK) {
        try {
          const res = await recommendApi.forUser(10)
          const list = res.data?.results || []
          if (list.length) {
            this.recommendBooks = list
            this.loading = false
            return
          }
        } catch (err) {
          console.warn('forUser fallback to hot', err)
        }
      }

      // 回退热门
      const hotRes = await recommendApi.hot(10)
      this.recommendBooks = hotRes.data.results || []
    } catch (e) {
      this.error = '无法加载推荐，请稍后再试。'
      this.recommendBooks = []
      console.error(e)
    } finally {
      this.loading = false
    }
  },
  methods: {
    go(id) {
      this.$router.push(`/movie/${id}`)
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
  box-sizing: border-box;
}
.title { color: #333; margin: 0 0 4px 0; font-size: 24px; font-weight: 700; }
.desc { color: #999; margin: 0 0 16px 0; font-size: 14px; }
.panel {
  padding: 20px;
  border-radius: 8px;
  background: #fff;
  border: 1px solid #f0f0f0;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.subtitle { color: #333; margin: 0 0 14px 0; font-size: 18px; font-weight: 600; }
.grid { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; }
.state { color: #999; text-align: center; padding: 30px 0; }
.state.error { color: #ff4d4f; }
</style>
