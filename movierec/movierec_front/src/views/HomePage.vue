<template>
  <div class="home-page">
    <div v-if="initialLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p class="loading-text">正在加载...</p>
    </div>

    <!-- 大横幅 Hero Banner -->
    <section class="hero-banner" v-show="!initialLoading">
      <swiper
        :modules="modules"
        :autoplay="{ delay: 4000, disableOnInteraction: false }"
        :loop="true"
        :pagination="{ clickable: true }"
        class="banner-swiper"
      >
        <swiper-slide v-for="(slide, i) in bannerSlides" :key="i">
          <div class="banner-slide" :style="{ background: slide.bg }">
            <div class="banner-content">
              <h1 class="banner-title">{{ slide.title }}</h1>
              <p class="banner-sub">{{ slide.sub }}</p>
            </div>
          </div>
        </swiper-slide>
      </swiper>
    </section>

    <!-- 热门推荐 -->
    <section class="section" v-show="!initialLoading">
      <div class="section-header">
        <div>
          <h2 class="section-title">热门推荐</h2>
          <p class="section-desc">追踪热度与口碑评价的影片</p>
        </div>
        <router-link to="/recommend" class="more-link">更多 ›</router-link>
      </div>
      <div class="movie-grid">
        <div
          v-for="book in featuredBooks"
          :key="book.id"
          class="movie-card"
          @click="goDetail(book.id)"
        >
          <div class="card-poster">
            <img :src="getMovieCover(book)" :alt="book.title" loading="lazy" @error="(e) => handleImageError(e, book)" />
            <div class="rating-badge" v-if="book.avg_rating || book.rating_avg">
              评分 {{ (book.avg_rating || book.rating_avg || 0).toFixed(1) }}
            </div>
          </div>
          <div class="card-info">
            <h3 class="card-title">{{ book.title }}</h3>
            <span class="card-genre" v-if="getGenre(book)">{{ getGenre(book) }}</span>
            <div class="card-stats">
              <span class="stat">👁 {{ formatNum(book.view_count || book.rating_count || 0) }}</span>
              <span class="stat">⭐ {{ formatNum(book.comment_count || 0) }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 全部电影 -->
    <section class="section" v-show="!initialLoading">
      <div class="section-header">
        <div>
          <h2 class="section-title">全部电影</h2>
          <p class="section-desc">浏览电影库中的所有电影</p>
        </div>
        <router-link to="/search" class="more-link">搜索更多 ›</router-link>
      </div>
      <div class="movie-grid">
        <div
          v-for="book in displayBooks"
          :key="book.id"
          class="movie-card"
          @click="goDetail(book.id)"
        >
          <div class="card-poster">
            <img :src="getMovieCover(book)" :alt="book.title" loading="lazy" @error="(e) => handleImageError(e, book)" />
            <div class="rating-badge" v-if="book.avg_rating || book.rating_avg">
              评分 {{ (book.avg_rating || book.rating_avg || 0).toFixed(1) }}
            </div>
          </div>
          <div class="card-info">
            <h3 class="card-title">{{ book.title }}</h3>
            <span class="card-genre" v-if="getGenre(book)">{{ getGenre(book) }}</span>
            <div class="card-stats">
              <span class="stat" v-if="book.publication_year">📅 {{ book.publication_year }}</span>
              <span class="stat">{{ book.author || '未知导演' }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="load-more-wrapper" v-if="hasMore">
        <button @click="loadMore" class="load-more-btn" :disabled="loadingMore">
          {{ loadingMore ? '加载中...' : '加载更多电影' }}
        </button>
      </div>
    </section>
  </div>
</template>

<script>
import { Swiper, SwiperSlide } from 'swiper/vue'
import { Autoplay, Pagination } from 'swiper/modules'
import 'swiper/css'
import 'swiper/css/pagination'

import { moviesApi, recommendApi } from '@/api'
import { getMovieCover, handleImageError } from '@/utils/movieCover'

export default {
  name: 'HomePage',
  components: { Swiper, SwiperSlide },
  data() {
    return {
      modules: [Autoplay, Pagination],
      featuredBooks: [],
      displayBooks: [],
      currentPage: 1,
      hasMore: true,
      loadingMore: false,
      initialLoading: true,
      bannerSlides: [
        {
          title: '电影推荐系统',
          sub: 'MOVIE RECOMMENDATION SYSTEM',
          bg: 'linear-gradient(135deg, #1a3a5c 0%, #2a5298 50%, #667eea 100%)',
        },
        {
          title: '发现你喜欢的电影',
          sub: '基于协同过滤的智能推荐引擎',
          bg: 'linear-gradient(135deg, #0d2137 0%, #1a3a5c 50%, #2a5298 100%)',
        },
        {
          title: '探索光影世界',
          sub: '数据驱动的电影数据分析平台',
          bg: 'linear-gradient(135deg, #2a5298 0%, #1a3a5c 50%, #0d2137 100%)',
        },
      ],
    }
  },
  async mounted() {
    await this.loadInitialData()
  },
  methods: {
    async loadInitialData() {
      try {
        const [hotRes, booksRes] = await Promise.all([
          recommendApi.hot(10),
          moviesApi.search({ page: 1, page_size: 20 }),
        ])
        this.featuredBooks = hotRes.data.results || []
        this.displayBooks = booksRes.data.results || []
        this.currentPage = 1
        const totalCount = booksRes.data.count || 0
        this.hasMore = totalCount > this.displayBooks.length
      } catch (err) {
        console.error('加载数据失败:', err)
      } finally {
        this.initialLoading = false
      }
    },
    async loadMore() {
      if (this.loadingMore || !this.hasMore) return
      this.loadingMore = true
      try {
        this.currentPage += 1
        const res = await moviesApi.search({ page: this.currentPage, page_size: 20 })
        const newBooks = res.data.results || []
        const totalCount = res.data.count || 0
        this.displayBooks.push(...newBooks)
        this.hasMore = this.displayBooks.length < totalCount
      } catch (err) {
        console.error('加载更多失败:', err)
      } finally {
        this.loadingMore = false
      }
    },
    goDetail(id) {
      this.$router.push(`/movie/${id}`)
    },
    getMovieCover(book) {
      return getMovieCover(book)
    },
    handleImageError(e, book) {
      handleImageError(e, book)
    },
    getGenre(book) {
      if (!book.description) return ''
      const genres = ['剧情', '喜剧', '动作', '爱情', '科幻', '动画', '悬疑', '惊悚', '恐怖', '犯罪', '奇幻', '战争', '传记', '历史', '音乐', '冒险', '家庭', '武侠', '古装', '纪录']
      const desc = (book.description || '').toLowerCase()
      for (const g of genres) {
        if (desc.includes(g)) return g + '片'
      }
      if (book.author) return ''
      return ''
    },
    formatNum(n) {
      if (!n) return '0'
      if (n >= 10000) return (n / 10000).toFixed(1) + 'w'
      if (n >= 1000) return (n / 1000).toFixed(1) + 'k'
      return String(n)
    },
  },
}
</script>

<style scoped>
.home-page {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px 40px;
  box-sizing: border-box;
}

/* Loading */
.loading-overlay {
  text-align: center;
  padding: 120px 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto 16px;
  border: 3px solid #e8e8e8;
  border-top-color: #1890ff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  color: #999;
  font-size: 14px;
}

/* Hero Banner */
.hero-banner {
  margin-bottom: 28px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
}

.banner-swiper {
  width: 100%;
  height: 320px;
}

.banner-swiper :deep(.swiper-pagination-bullet) {
  background: rgba(255, 255, 255, 0.5);
  width: 10px;
  height: 10px;
}

.banner-swiper :deep(.swiper-pagination-bullet-active) {
  background: #fff;
  width: 28px;
  border-radius: 5px;
}

.banner-slide {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.banner-content {
  text-align: center;
  z-index: 2;
}

.banner-title {
  font-size: 42px;
  font-weight: 800;
  color: #fff;
  margin: 0 0 12px 0;
  letter-spacing: 4px;
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
}

.banner-sub {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
  letter-spacing: 2px;
  font-weight: 300;
}

/* Section */
.section {
  margin-bottom: 32px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 18px;
}

.section-title {
  margin: 0 0 4px 0;
  font-size: 22px;
  font-weight: 700;
  color: #1a1a1a;
}

.section-desc {
  margin: 0;
  font-size: 13px;
  color: #999;
}

.more-link {
  color: #1890ff;
  font-size: 14px;
  text-decoration: none;
  font-weight: 500;
  white-space: nowrap;
  transition: color 0.2s;
}

.more-link:hover {
  color: #40a9ff;
}

/* Movie Grid */
.movie-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
}

/* Movie Card */
.movie-card {
  background: #fff;
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #f0f0f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.movie-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.12);
}

.card-poster {
  position: relative;
  width: 100%;
  aspect-ratio: 2 / 3;
  overflow: hidden;
  background: #f0f0f0;
}

.card-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.movie-card:hover .card-poster img {
  transform: scale(1.06);
}

.rating-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  padding: 3px 8px;
  border-radius: 4px;
  background: rgba(0, 0, 0, 0.65);
  color: #fadb14;
  font-size: 12px;
  font-weight: 600;
  backdrop-filter: blur(4px);
}

.card-info {
  padding: 10px 12px 12px;
}

.card-title {
  margin: 0 0 6px 0;
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-genre {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 3px;
  background: #e6f7ff;
  color: #1890ff;
  font-size: 11px;
  font-weight: 500;
  margin-bottom: 6px;
}

.card-stats {
  display: flex;
  gap: 12px;
  align-items: center;
}

.stat {
  font-size: 12px;
  color: #999;
}

/* Load More */
.load-more-wrapper {
  text-align: center;
  padding: 24px 0 0;
}

.load-more-btn {
  padding: 10px 36px;
  border-radius: 20px;
  border: 1px solid #d9d9d9;
  background: #fff;
  color: #555;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.load-more-btn:hover:not(:disabled) {
  color: #1890ff;
  border-color: #1890ff;
}

.load-more-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Responsive */
@media (max-width: 1100px) {
  .movie-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 860px) {
  .movie-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  .banner-swiper {
    height: 240px;
  }
  .banner-title {
    font-size: 30px;
  }
  .banner-sub {
    font-size: 14px;
  }
}

@media (max-width: 560px) {
  .movie-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }
  .banner-swiper {
    height: 180px;
  }
  .banner-title {
    font-size: 24px;
    letter-spacing: 2px;
  }
  .banner-sub {
    font-size: 12px;
  }
  .home-page {
    padding: 0 12px 24px;
  }
}
</style>
