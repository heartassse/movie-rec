<template>
  <div class="book-card" @click="$emit('click', book)">
    <img 
      :src="coverImage" 
      :alt="book.title" 
      class="book-cover"
      @error="handleImageError"
    />
    <div class="book-info">
      <h3 class="book-title">{{ book.title }}</h3>
      <p class="book-author">{{ book.author || '未知导演' }}</p>
    </div>
  </div>
</template>

<script>
import { getMovieCover, handleImageError as handleError } from '@/utils/movieCover';
import defaultCover from '@/assets/pekora.jpg'; 

export default {
  name: 'MovieCard',
  emits: ['click'],
  props: {
    book: {
      type: Object,
      required: true,
    },
  },
  computed: {
    coverImage() {
      // 使用智能封面获取函数
      return getMovieCover(this.book) || defaultCover;
    },
  },
  methods: {
    handleImageError(event) {
      // 使用工具函数处理图片加载失败
      handleError(event, this.book);
      // 如果所有方案都失败，使用默认图片
      if (!event.target.src || event.target.src === this.coverImage) {
        event.target.src = defaultCover;
      }
    },
  },
};
</script>

<style scoped>
.book-card {
  width: 190px;
  margin: 8px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  background-color: #ffffff;
  color: #333;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
  border: 1px solid #f0f0f0;
}

.book-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

.book-cover {
  width: 100%;
  height: 260px;
  object-fit: cover;
  transition: transform 0.3s;
}

.book-card:hover .book-cover {
  transform: scale(1.03);
}

.book-info {
  padding: 10px 12px;
}

.book-title {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 4px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: #333;
}

.book-author {
  font-size: 12px;
  color: #999;
  margin: 0;
}
</style>