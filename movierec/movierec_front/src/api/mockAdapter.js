import { USE_MOCK } from '@/config'
import {
  mockMovies,
  mockRecommend,
  mockMyRating,
  mockComments,
} from '@/mock/data'

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function wrap(data) {
  return { data }
}

export async function maybeMockMoviesGetAll(realCall) {
  if (!USE_MOCK) return realCall()
  await delay(200)
  return wrap({ count: mockMovies.length, results: mockMovies })
}

export async function maybeMockMoviesGetById(id, realCall) {
  if (!USE_MOCK) return realCall()
  await delay(150)
  const book = mockMovies.find((b) => String(b.id) === String(id))
  if (!book) throw new Error('mock book not found')
  return wrap(book)
}

export async function maybeMockRecommendHot(limit, realCall) {
  if (!USE_MOCK) return realCall(limit)
  await delay(120)
  return wrap({ ...mockRecommend, limit })
}

export async function maybeMockRecommendForUser(limit, realCall) {
  if (!USE_MOCK) return realCall(limit)
  await delay(120)
  return wrap({ ...mockRecommend, limit })
}

export async function maybeMockRecommendSimilar(book_id, limit, realCall) {
  if (!USE_MOCK) return realCall(book_id, limit)
  await delay(120)
  // 简单返回 mockRecommend 作为占位
  return wrap({ ...mockRecommend, limit })
}

export async function maybeMockMyRating(book_id, realCall) {
  if (!USE_MOCK) return realCall(book_id)
  await delay(80)
  return wrap(mockMyRating)
}

export async function maybeMockListComments(book_id, page, page_size, realCall) {
  if (!USE_MOCK) return realCall(book_id, page, page_size)
  await delay(120)
  return wrap({ ...mockComments, page, page_size })
}

export async function maybeMockCreateComment(book_id, content, realCall) {
  if (!USE_MOCK) return realCall(book_id, content)
  await delay(120)
  // 简单模拟：把新评论插到最前
  mockComments.results.unshift({
    id: Math.max(...mockComments.results.map((x) => x.id)) + 1,
    book: Number(book_id),
    user: 1,
    username: 'demo_user',
    content,
    created_at: new Date().toISOString(),
  })
  mockComments.count += 1
  return wrap(mockComments.results[0])
}

export async function maybeMockRate(book_id, score, realCall) {
  if (!USE_MOCK) return realCall(book_id, score)
  await delay(120)
  return wrap({ id: 1, book: Number(book_id), user: 1, score })
}
