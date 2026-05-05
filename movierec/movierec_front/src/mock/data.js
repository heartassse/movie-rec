import booksData from './movies.json'

export const mockMovies = booksData

export const mockRecommend = {
  limit: 10,
  results: mockMovies.filter(b => b.cover_url).slice(0, 10),
}

// 用户评分（示例）
export const mockMyRating = {
  score: 4,
}

// 评论数据（示例）
export const mockComments = {
  count: 2,
  page: 1,
  page_size: 10,
  results: [
    {
      id: 1,
      book: 1,
      user: 1,
      username: 'demo_user',
      content: '很喜欢这种氛围。',
      created_at: new Date().toISOString(),
    },
    {
      id: 2,
      book: 1,
      user: 2,
      username: 'reader_2',
      content: '文字很细腻，值得一读。',
      created_at: new Date(Date.now() - 3600 * 1000).toISOString(),
    },
  ],
}
