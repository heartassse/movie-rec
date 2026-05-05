/**
 * 简单的内存缓存工具
 * 用于缓存 API 请求结果，减少重复请求
 */

class SimpleCache {
  constructor(ttl = 5 * 60 * 1000) { // 默认缓存 5 分钟
    this.cache = new Map()
    this.ttl = ttl
  }

  set(key, value) {
    this.cache.set(key, {
      value,
      timestamp: Date.now()
    })
  }

  get(key) {
    const item = this.cache.get(key)
    if (!item) return null

    // 检查是否过期
    if (Date.now() - item.timestamp > this.ttl) {
      this.cache.delete(key)
      return null
    }

    return item.value
  }

  has(key) {
    return this.get(key) !== null
  }

  clear() {
    this.cache.clear()
  }

  delete(key) {
    this.cache.delete(key)
  }
}

// 创建全局缓存实例
export const apiCache = new SimpleCache(5 * 60 * 1000) // 5 分钟缓存

// 缓存装饰器函数
export function withCache(cacheKey, apiCall) {
  return async (...args) => {
    const key = typeof cacheKey === 'function' ? cacheKey(...args) : cacheKey
    
    // 检查缓存
    const cached = apiCache.get(key)
    if (cached) {
      console.log(`[Cache Hit] ${key}`)
      return cached
    }

    // 调用 API
    console.log(`[Cache Miss] ${key}`)
    const result = await apiCall(...args)
    
    // 存入缓存
    apiCache.set(key, result)
    return result
  }
}
