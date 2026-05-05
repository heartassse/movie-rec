/**
 * 电影封面工具函数
 */

function isDoubanImage(url) {
  if (!url) return false
  return url.includes('doubanio.com') || url.includes('douban.com')
}

export function getProxiedImage(url) {
  if (!url) return null
  return `/api/books/image-proxy/?url=${encodeURIComponent(url)}`
}

/**
 * 根据电影名生成彩色渐变封面（SVG data URL）
 */
export function generateGradientCover(title) {
  if (!title) return null

  const palettes = [
    ['#1a3a5c', '#2a5298'],
    ['#4a1942', '#c74b50'],
    ['#0f3443', '#34e89e'],
    ['#200122', '#6f0000'],
    ['#1d4350', '#a43931'],
    ['#0b486b', '#f56217'],
    ['#3a1c71', '#d76d77'],
    ['#403b4a', '#e7e9bb'],
    ['#141e30', '#243b55'],
    ['#0f2027', '#2c5364'],
    ['#1c1c1c', '#e74c3c'],
    ['#0c0c1d', '#5c258d'],
  ]

  const code = title.split('').reduce((s, c) => s + c.charCodeAt(0), 0)
  const [c1, c2] = palettes[code % palettes.length]

  const displayTitle = title.length > 6 ? title.substring(0, 6) : title
  const lines = displayTitle.length > 3
    ? [displayTitle.substring(0, 3), displayTitle.substring(3)]
    : [displayTitle]

  const textElements = lines.map((line, i) => {
    const y = lines.length === 1 ? 210 : 190 + i * 40
    return `<text x="150" y="${y}" font-family="PingFang SC,Microsoft YaHei,sans-serif" font-size="36" font-weight="bold" fill="white" text-anchor="middle" dominant-baseline="middle">${line}</text>`
  }).join('')

  const svg = `<svg width="300" height="420" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color:${c1}"/>
        <stop offset="100%" style="stop-color:${c2}"/>
      </linearGradient>
    </defs>
    <rect width="300" height="420" fill="url(#g)"/>
    <rect x="20" y="20" width="260" height="380" rx="8" fill="none" stroke="rgba(255,255,255,0.12)" stroke-width="1"/>
    <text x="150" y="120" font-family="PingFang SC,Microsoft YaHei,sans-serif" font-size="60" fill="rgba(255,255,255,0.15)" text-anchor="middle" dominant-baseline="middle">🎬</text>
    ${textElements}
    <text x="150" y="340" font-family="PingFang SC,Microsoft YaHei,sans-serif" font-size="13" fill="rgba(255,255,255,0.35)" text-anchor="middle">MOVIE</text>
  </svg>`

  return 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svg)))
}

/**
 * 智能获取封面：优先级 cover_url > 渐变占位
 */
export function getMovieCover(book) {
  if (book.cover_url) {
    if (isDoubanImage(book.cover_url)) {
      return getProxiedImage(book.cover_url)
    }
    return book.cover_url
  }

  if (book.title) {
    return generateGradientCover(book.title)
  }

  return generateGradientCover('未知电影')
}

/**
 * 图片加载失败时的回退
 */
export function handleImageError(event, book) {
  const img = event.target
  if (book.title) {
    img.src = generateGradientCover(book.title)
  } else {
    img.src = generateGradientCover('未知电影')
  }
}
