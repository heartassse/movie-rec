import axios from 'axios'
import { apiCache, withCache } from '@/utils/cache'

/** 评分/评论变更后清除相关缓存 */
export function invalidateRatingStats(bookId) {
  apiCache.delete(`rating-stats:${bookId}`)
}

import {
  maybeMockMoviesGetAll,
  maybeMockMoviesGetById,
  maybeMockRecommendHot,
  maybeMockRecommendForUser,
  maybeMockRecommendSimilar,
  maybeMockMyRating,
  maybeMockListComments,
  maybeMockCreateComment,
  maybeMockRate,
} from '@/api/mockAdapter'

const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      const refreshToken = localStorage.getItem('refresh')
      if (refreshToken) {
        try {
          const res = await axios.post('/api/auth/refresh/', { refresh: refreshToken })
          const newAccessToken = res.data.access
          localStorage.setItem('access', newAccessToken)
          
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
          return apiClient(originalRequest)
        } catch (refreshError) {
          localStorage.removeItem('access')
          localStorage.removeItem('refresh')
          localStorage.removeItem('is_admin')
          window.location.href = '/login'
          return Promise.reject(refreshError)
        }
      } else {
        localStorage.removeItem('access')
        localStorage.removeItem('refresh')
        localStorage.removeItem('is_admin')
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

export const moviesApi = {
  getAll() {
    return maybeMockMoviesGetAll(() => 
      withCache('books:all', () => apiClient.get('/books/'))()
    )
  },
  getById(id) {
    return maybeMockMoviesGetById(id, () => 
      withCache(`books:${id}`, () => apiClient.get(`/books/${id}/`))()
    )
  },
  search(params) {
    // params: { search, ordering, page }
    // 搜索不缓存，保证实时性
    return apiClient.get('/books/', { params })
  },
  getRatingStats(id) {
    return withCache(`rating-stats:${id}`, () => apiClient.get(`/books/${id}/rating-stats/`))()
  },
}

export const ratingsApi = {
  rate(book_id, score) {
    return maybeMockRate(book_id, score, (b, s) => apiClient.post('/ratings/rate/', { book_id: b, score: s }))
  },
  myRating(book_id) {
    return maybeMockMyRating(book_id, (b) => apiClient.get('/ratings/my-rating/', { params: { book_id: b } }))
  },
  listComments(book_id, page = 1, page_size = 10) {
    return maybeMockListComments(
      book_id,
      page,
      page_size,
      (b, p, ps) => apiClient.get('/ratings/comments/', { params: { book_id: b, page: p, page_size: ps } })
    )
  },
  createComment(book_id, content) {
    return maybeMockCreateComment(
      book_id,
      content,
      (b, c) => apiClient.post('/ratings/comments/create/', { book_id: b, content: c })
    )
  },
  myRatings(limit = 50) {
    return apiClient.get('/ratings/my/ratings/', { params: { limit } })
  },
  myComments(limit = 50) {
    return apiClient.get('/ratings/my/comments/', { params: { limit } })
  },
}

export const recommendApi = {
  hot(limit = 10) {
    return maybeMockRecommendHot(limit, (l) => 
      withCache(`recommend:hot:${l}`, () => apiClient.get('/recommend/hot/', { params: { limit: l } }))()
    )
  },
  forUser(limit = 10) {
    return maybeMockRecommendForUser(limit, (l) => apiClient.get('/recommend/user/', { params: { limit: l } }))
  },
  similar(book_id, limit = 6) {
    return maybeMockRecommendSimilar(book_id, limit, (b, l) =>
      withCache(`recommend:similar:${b}:${l}`, () => 
        apiClient.get('/recommend/similar/', { params: { book_id: b, limit: l } })
      )()
    )
  },
  stats() {
    return withCache('recommend:stats', () => apiClient.get('/recommend/stats/'))()
  },
  wordcloud(source = 'titles', limit = 100) {
    return withCache(`wordcloud:${source}:${limit}`, () => 
      apiClient.get('/recommend/wordcloud/', { params: { source, limit } })
    )()
  },
}

export const authApi = {
  login(credentials) {
    return apiClient.post('/auth/login/', credentials)
  },
  register(data) {
    return apiClient.post('/auth/register/', data)
  },
  me() {
    return apiClient.get('/auth/me/')
  },
}

// 管理员专用接口（仅管理员登录后可调用）
export const adminUsersApi = {
  list() {
    return apiClient.get('/auth/admin/users/')
  },
  create(payload) {
    return apiClient.post('/auth/admin/users/', payload)
  },
  update(id, payload) {
    return apiClient.put(`/auth/admin/users/${id}/`, payload)
  },
  delete(id) {
    return apiClient.delete(`/auth/admin/users/${id}/`)
  },
}

export const adminMoviesApi = {
  list(page = 1, pageSize = 50, search = '') {
    const params = { page, page_size: pageSize }
    if (search) {
      params.search = search
    }
    return apiClient.get('/books/admin/', { params })
  },
  create(payload) {
    return apiClient.post('/books/admin/', payload)
  },
  update(id, payload) {
    return apiClient.put(`/books/admin/${id}/`, payload)
  },
  delete(id) {
    return apiClient.delete(`/books/admin/${id}/`)
  },
}

export default apiClient
