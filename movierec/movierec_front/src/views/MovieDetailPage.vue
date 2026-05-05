<template>
  <div class="detail-page">
    <div v-if="loading" class="loading-wrap">
      <div class="loading-spinner"></div>
      <p>正在加载...</p>
    </div>
    <div v-else-if="error" class="error-wrap">{{ error }}</div>
    <div v-else class="detail-layout">
      <!-- 头部：封面 + 基本信息 -->
      <header class="detail-header">
        <div class="poster-wrap">
          <img 
            class="poster" 
            :src="coverImage" 
            :alt="book.title"
            @error="handleImageError"
            loading="eager"
          />
        </div>
        <div class="header-info">
          <h1 class="movie-title">{{ book.title }}</h1>
          <div class="meta-tags">
            <span v-if="book.author" class="tag"><span class="tag-label">导演</span>{{ book.author }}</span>
            <span v-if="book.publication_year" class="tag"><span class="tag-label">年份</span>{{ book.publication_year }}</span>
            <span v-if="book.isbn" class="tag"><span class="tag-label">豆瓣</span>{{ book.isbn }}</span>
          </div>

          <!-- 豆瓣评分 -->
          <div class="score-block" v-if="ratingStats">
            <div class="score-main">
              <span class="score-num">{{ ratingStats.average_score }}</span>
              <span class="score-max">/ 5</span>
            </div>
            <div class="score-stars">
              <span v-for="n in 5" :key="n" class="star" :class="{ filled: n <= Math.round(ratingStats.average_score) }">★</span>
            </div>
            <div class="score-count">{{ ratingStats.total_ratings }} 人评价</div>
          </div>

          <!-- 评分分布条 -->
          <div class="dist-bars" v-if="ratingStats && ratingStats.distribution && ratingStats.distribution.length">
            <div v-for="item in ratingStats.distribution" :key="item.star" class="bar-row">
              <span class="bar-label">{{ item.star }}星</span>
              <div class="bar-track">
                <div class="bar-fill" :style="{ width: item.percentage + '%' }"></div>
              </div>
              <span class="bar-pct">{{ item.percentage }}%</span>
            </div>
          </div>

          <!-- 我的评分 -->
          <div class="my-rate">
            <span class="my-rate-label">我的评分</span>
            <div class="my-rate-row">
              <RatingStars v-model="myScore" :disabled="ratingSubmitting" @change="submitRating" />
              <span class="my-rate-text" v-if="myScore">{{ myScore }} 分</span>
              <span class="my-rate-text hint" v-else>点击评分</span>
            </div>
            <p v-if="ratingError" class="my-rate-err">{{ ratingError }}</p>
          </div>
        </div>
      </header>

      <!-- 主体内容区 -->
      <main class="detail-main">
        <div class="main-grid">
          <!-- 简介 -->
          <section class="section desc-section" v-if="book.description">
            <h2 class="section-title">简介</h2>
            <p class="desc-text">{{ book.description }}</p>
          </section>

          <!-- 评论 -->
          <section class="section comments-section">
            <h2 class="section-title">评论区</h2>
            <div class="comment-input">
              <textarea v-model="newComment" placeholder="写下你的观影感受..." rows="3"></textarea>
              <button class="btn-submit" :disabled="commentSubmitting || !newComment.trim()" @click="submitComment">
                发表评论
              </button>
              <p v-if="commentError" class="input-error">{{ commentError }}</p>
            </div>

            <div v-if="commentsLoading" class="loading-inline">加载中...</div>
            <div v-else-if="comments.length === 0" class="empty-tip">暂无评论，来发表第一条吧</div>
            <ul v-else class="comment-list">
              <li class="comment-card" v-for="(c, idx) in comments" :key="c.id || 'c-' + idx">
                <div class="comment-header">
                  <span class="comment-user">{{ c.username || '匿名用户' }}</span>
                  <span class="comment-badge" v-if="c.user_score">★ {{ c.user_score }}</span>
                  <span class="comment-date">{{ formatTime(c.created_at) }}</span>
                </div>
                <p class="comment-body">{{ c.content || '（无内容）' }}</p>
              </li>
            </ul>
            <button v-if="commentsHasMore" class="btn-load-more" :disabled="commentsLoadingMore" @click="loadMoreComments">
              加载更多
            </button>
          </section>

          <!-- 相似电影 -->
          <aside class="section similar-section">
            <h2 class="section-title">相似推荐</h2>
            <div v-if="USE_MOCK" class="similar-placeholder">Mock 模式</div>
            <div v-else-if="similarLoading" class="similar-placeholder">加载中...</div>
            <div v-else-if="similarError" class="similar-placeholder err">{{ similarError }}</div>
            <div v-else-if="!similarBooks.length" class="similar-placeholder">暂无</div>
            <div v-else class="similar-cards">
              <div class="similar-card" v-for="b in similarBooks" :key="b.id" @click="$router.push(`/movie/${b.id}`)">
                <img 
                  :src="getMovieCover(b) || fallbackCover" 
                  :alt="b.title"
                  @error="(e) => handleSimilarImageError(e, b)"
                  loading="lazy"
                />
                <div class="similar-info">
                  <div class="similar-name">{{ b.title }}</div>
                  <div class="similar-author">{{ b.author || '未知' }}</div>
                </div>
              </div>
            </div>
          </aside>
        </div>

        <div class="back-wrap">
          <button class="btn-back" @click="$router.back()">← 返回</button>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import { moviesApi, ratingsApi, recommendApi, invalidateRatingStats } from '@/api'
import { getMovieCover, handleImageError as handleError } from '@/utils/movieCover'
import fallbackCover from '@/assets/pekora.jpg'
import RatingStars from '@/components/RatingStars.vue'
import { USE_MOCK } from '@/config'

export default {
  name: 'MovieDetailPage',
  components: { RatingStars },
  data() {
    return {
      book: null,
      loading: true,
      error: null,
      fallbackCover,

      ratingStats: null,

      myScore: 0,
      ratingSubmitting: false,
      ratingError: '',

      comments: [],
      commentsPage: 1,
      commentsHasMore: false,
      commentsLoading: true,
      commentsLoadingMore: false,
      newComment: '',
      commentSubmitting: false,
      commentError: '',

      similarBooks: [],
      similarLoading: !USE_MOCK,
      similarError: '',
    }
  },
  computed: {
    coverImage() {
      if (!this.book) return fallbackCover;
      return getMovieCover(this.book) || fallbackCover;
    },
    USE_MOCK() {
      return USE_MOCK;
    },
  },
  watch: {
    '$route.params.id': {
      handler(newId, oldId) {
        if (newId && newId !== oldId) {
          this.loadBookData();
        }
      },
      immediate: false,
    },
  },
  async mounted() {
    await this.loadBookData();
  },
  methods: {
    async loadBookData() {
      this.loading = true;
      this.error = null;
      this.ratingStats = null;
      this.myScore = 0;
      this.comments = [];
      this.commentsPage = 1;
      this.similarBooks = [];
      
      const id = this.$route.params.id;
      try {
        // 第一阶段：加载电影基本信息
        const res = await moviesApi.getById(id);
        this.book = res.data;
        this.loading = false;
        
        // 第二阶段：并行加载评分统计和用户评分（次要信息）
        Promise.all([
          this.fetchRatingStats(),
          this.fetchMyRating(),
        ]).catch(e => console.error('加载评分信息失败:', e));
        
        // 第三阶段：延迟加载评论和相似电影
        setTimeout(() => {
          this.fetchComments(true).catch(e => console.error('加载评论失败:', e));
          this.fetchSimilar().catch(e => console.error('加载相似电影失败:', e));
        }, 100);
        
      } catch (e) {
        this.error = '加载电影详情失败。';
        console.error(e);
        this.loading = false;
      }
    },
    getMovieCover,
    handleImageError(event) {
      handleError(event, this.book);
      if (!event.target.src || event.target.src === this.coverImage) {
        event.target.src = fallbackCover;
      }
    },
    handleSimilarImageError(event, book) {
      handleError(event, book);
      if (!event.target.src) {
        event.target.src = fallbackCover;
      }
    },
    async fetchRatingStats() {
      try {
        const res = await moviesApi.getRatingStats(this.$route.params.id)
        const data = res?.data
        if (data && typeof data === 'object') {
          this.ratingStats = {
            average_score: data.average_score ?? 0,
            total_ratings: data.total_ratings ?? 0,
            distribution: Array.isArray(data.distribution) ? data.distribution : []
          }
        }
      } catch (e) {
        console.error('fetchRatingStats:', e)
        this.ratingStats = { average_score: 0, total_ratings: 0, distribution: [] }
      }
    },
    async fetchMyRating() {
      try {
        const res = await ratingsApi.myRating(this.$route.params.id)
        this.myScore = res.data.score || 0
      } catch (e) {
        console.error(e)
      }
    },
    async submitRating(score) {
      this.ratingError = ''
      this.ratingSubmitting = true
      try {
        await ratingsApi.rate(this.$route.params.id, score)
        this.myScore = score
        invalidateRatingStats(this.$route.params.id)
        await this.fetchRatingStats()
      } catch (e) {
        this.ratingError = '评分失败，请稍后再试。'
        console.error(e)
      } finally {
        this.ratingSubmitting = false
      }
    },
    async fetchComments(reset = false) {
      if (reset) {
        this.commentsPage = 1
        this.comments = []
        this.commentsHasMore = false
        this.commentsLoading = true
        this.commentError = ''
      }
      try {
        const res = await ratingsApi.listComments(this.$route.params.id, this.commentsPage, 5)
        const data = res?.data || {}
        const results = Array.isArray(data.results) ? data.results : []
        const count = Number(data.count) || 0
        const page = Number(data.page) || 1
        const pageSize = Number(data.page_size) || 5

        this.comments = reset ? results : [...(this.comments || []), ...results]
        this.commentsHasMore = page * pageSize < count
      } catch (e) {
        this.commentError = '加载评论失败，请稍后重试。' + (e.response?.status === 401 ? '（请先登录）' : '')
        console.error('fetchComments:', e)
      } finally {
        this.commentsLoading = false
      }
    },
    async loadMoreComments() {
      if (this.commentsLoadingMore) return
      this.commentsLoadingMore = true
      try {
        this.commentsPage += 1
        await this.fetchComments(false)
      } finally {
        this.commentsLoadingMore = false
      }
    },
    async submitComment() {
      this.commentError = ''
      const content = this.newComment.trim()
      if (!content) return

      this.commentSubmitting = true
      try {
        await ratingsApi.createComment(this.$route.params.id, content)
        this.newComment = ''
        await this.fetchComments(true)
      } catch (e) {
        this.commentError = '发表评论失败，请稍后再试。'
        console.error(e)
      } finally {
        this.commentSubmitting = false
      }
    },
    formatTime(isoString) {
      try {
        const d = new Date(isoString)
        return d.toLocaleString()
      } catch {
        return isoString
      }
    },
    async fetchSimilar() {
      if (USE_MOCK) return
      this.similarLoading = true
      this.similarError = ''
      try {
        const res = await recommendApi.similar(this.$route.params.id, 4) // 减少为4本
        this.similarBooks = res.data?.results || []
      } catch (e) {
        this.similarError = '相似电影暂不可用'
        console.error(e)
      } finally {
        this.similarLoading = false
      }
    },
  },
}
</script>

<style scoped>
.detail-page {
  width: 100%;
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px;
  box-sizing: border-box;
}

.loading-wrap, .error-wrap {
  text-align: center;
  padding: 80px 20px;
  color: #666;
}
.loading-spinner {
  width: 48px;
  height: 48px;
  margin: 0 auto 16px;
  border: 4px solid #f0f0f0;
  border-top-color: #1890ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* 头部：海报 + 信息 */
.detail-header {
  display: flex;
  gap: 32px;
  padding: 28px 32px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
  margin-bottom: 24px;
}

.poster-wrap {
  flex-shrink: 0;
}
.poster {
  width: 240px;
  height: 340px;
  object-fit: cover;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}

.header-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.movie-title {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color: #1a1a1a;
  line-height: 1.3;
}

.meta-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}
.tag {
  font-size: 14px;
  color: #666;
}
.tag-label {
  color: #999;
  margin-right: 6px;
}

/* 评分块 */
.score-block {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #fff9e6 0%, #fff7ed 100%);
  border-radius: 12px;
  border: 1px solid #ffe7ba;
}

.score-main {
  display: flex;
  align-items: baseline;
}
.score-num {
  font-size: 36px;
  font-weight: 800;
  color: #fa8c16;
}
.score-max {
  font-size: 18px;
  color: #bfbfbf;
  margin-left: 4px;
}

.score-stars {
  display: flex;
  gap: 2px;
}
.star {
  font-size: 16px;
  color: #e8e8e8;
}
.star.filled {
  color: #faad14;
}

.score-count {
  font-size: 13px;
  color: #999;
}

.dist-bars {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-width: 280px;
}
.bar-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.bar-label {
  width: 28px;
  font-size: 12px;
  color: #666;
}
.bar-track {
  flex: 1;
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #faad14, #ff7a45);
  border-radius: 4px;
  transition: width 0.4s;
}
.bar-pct {
  width: 36px;
  font-size: 11px;
  color: #999;
  text-align: right;
}

.my-rate {
  padding: 12px 0;
}
.my-rate-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}
.my-rate-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.my-rate-text {
  font-size: 14px;
  color: #1890ff;
  font-weight: 500;
}
.my-rate-text.hint {
  color: #999;
}
.my-rate-err {
  margin: 8px 0 0 0;
  font-size: 13px;
  color: #ff4d4f;
}

/* 主体区 */
.detail-main {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
  padding: 28px 32px;
}

.main-grid {
  display: grid;
  grid-template-columns: 1fr 280px;
  gap: 32px;
}

.section {
  margin-bottom: 24px;
}
.section-title {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  padding-bottom: 8px;
  border-bottom: 2px solid #1890ff;
  display: inline-block;
}

.desc-text {
  margin: 0;
  font-size: 15px;
  color: #666;
  line-height: 1.8;
}

/* 评论区 */
.comment-input textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  color: #333;
  resize: vertical;
  box-sizing: border-box;
}
.comment-input textarea:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24,144,255,0.1);
}
.btn-submit {
  margin-top: 12px;
  padding: 10px 24px;
  background: #1890ff;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}
.btn-submit:hover:not(:disabled) {
  background: #40a9ff;
}
.btn-submit:disabled {
  background: #bfbfbf;
  cursor: not-allowed;
}
.input-error {
  margin: 8px 0 0 0;
  font-size: 13px;
  color: #ff4d4f;
}

.loading-inline, .empty-tip {
  padding: 24px;
  text-align: center;
  color: #999;
  font-size: 14px;
}

.comment-list {
  list-style: none;
  margin: 16px 0 0 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.comment-card {
  padding: 16px;
  background: #fafafa;
  border-radius: 10px;
  border: 1px solid #f0f0f0;
}
.comment-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}
.comment-user {
  font-weight: 600;
  font-size: 14px;
  color: #333;
}
.comment-badge {
  padding: 2px 8px;
  background: #fff7e6;
  color: #faad14;
  font-size: 12px;
  font-weight: 600;
  border-radius: 4px;
}
.comment-date {
  margin-left: auto;
  font-size: 12px;
  color: #bfbfbf;
}
.comment-body {
  margin: 0;
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  white-space: pre-wrap;
}

.btn-load-more {
  margin-top: 16px;
  width: 100%;
  padding: 10px;
  background: #fff;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  color: #666;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}
.btn-load-more:hover:not(:disabled) {
  color: #1890ff;
  border-color: #1890ff;
}
.btn-load-more:disabled {
  cursor: not-allowed;
}

/* 相似推荐侧栏 */
.similar-section {
  grid-column: 2;
  grid-row: 1 / -1;
}

.similar-placeholder {
  padding: 20px;
  text-align: center;
  color: #bfbfbf;
  font-size: 14px;
}
.similar-placeholder.err {
  color: #ff4d4f;
}

.similar-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.similar-card {
  display: flex;
  gap: 12px;
  padding: 10px;
  border-radius: 10px;
  border: 1px solid #f0f0f0;
  cursor: pointer;
  transition: all 0.3s;
}
.similar-card:hover {
  border-color: #1890ff;
  box-shadow: 0 4px 12px rgba(24,144,255,0.15);
}
.similar-card img {
  width: 64px;
  height: 96px;
  object-fit: cover;
  border-radius: 6px;
  flex-shrink: 0;
}
.similar-info {
  flex: 1;
  min-width: 0;
}
.similar-name {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.similar-author {
  font-size: 12px;
  color: #999;
}

.back-wrap {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}
.btn-back {
  padding: 10px 20px;
  background: #fff;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  color: #666;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}
.btn-back:hover {
  color: #1890ff;
  border-color: #1890ff;
}

@media (max-width: 900px) {
  .main-grid {
    grid-template-columns: 1fr;
  }
  .similar-section {
    grid-column: 1;
    grid-row: auto;
  }
  .similar-cards {
    flex-direction: row;
    flex-wrap: wrap;
  }
  .similar-card {
    width: calc(50% - 6px);
    flex-direction: column;
  }
  .similar-card img {
    width: 100%;
    height: 140px;
  }
}

@media (max-width: 768px) {
  .detail-header {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  .poster {
    width: 200px;
    height: 280px;
  }
  .dist-bars {
    max-width: 100%;
  }
  .score-block {
    flex-wrap: wrap;
    justify-content: center;
  }
  .main-grid {
    padding: 0;
  }
}
</style>