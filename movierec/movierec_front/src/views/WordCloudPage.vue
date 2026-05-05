<template>
  <div class="page">
    <h1 class="title">词云分析</h1>
    <p class="desc"></p>

    <div class="panel">
      <div class="controls">
        <label>
          数据源：
          <select v-model="source" @change="loadWordCloud" class="source-select">
            <option value="titles">电影标题</option>
            <option value="descriptions">电影简介</option>
            <option value="comments">用户评论</option>
            <option value="authors">导演名称</option>
          </select>
        </label>
        <span class="info">共 {{ totalWords }} 个词</span>
      </div>

      <div ref="wordcloudChart" class="chart"></div>
      
      <p v-if="loading" class="loading-text">加载中...</p>
      <p v-if="error" class="error-text">{{ error }}</p>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import 'echarts-wordcloud'
import { recommendApi } from '@/api'

export default {
  name: 'WordCloudPage',
  data() {
    return {
      source: 'titles',
      chart: null,
      loading: false,
      error: '',
      totalWords: 0,
    }
  },
  mounted() {
    this.loadWordCloud()
    window.addEventListener('resize', this.resizeChart)
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.resizeChart)
    this.disposeChart()
  },
  methods: {
    disposeChart() {
      if (this.chart) {
        try {
          this.chart.dispose()
        } catch {
          // ignore
        }
        this.chart = null
      }
    },
    resizeChart() {
      if (this.chart) {
        this.chart.resize()
      }
    },
    async loadWordCloud() {
      this.loading = true
      this.error = ''
      
      try {
        const res = await recommendApi.wordcloud(this.source, 150)
        const data = res.data.data || []
        this.totalWords = res.data.total_words || 0
        
        this.renderWordCloud(data)
      } catch (e) {
        console.error(e)
        this.error = '加载词云数据失败，请稍后重试'
        this.renderWordCloud([])
      } finally {
        this.loading = false
      }
    },
    renderWordCloud(data) {
      this.disposeChart()
      
      const el = this.$refs.wordcloudChart
      if (!el) return
      
      this.chart = echarts.init(el)
      
      this.chart.setOption({
        backgroundColor: 'transparent',
        tooltip: {
          show: true,
          backgroundColor: '#fff',
          borderColor: '#e8e8e8',
          textStyle: { color: '#333' },
        },
        series: [{
          type: 'wordCloud',
          shape: 'circle',
          left: 'center',
          top: 'center',
          width: '90%',
          height: '90%',
          right: null,
          bottom: null,
          sizeRange: [14, 60],
          rotationRange: [-45, 45],
          rotationStep: 45,
          gridSize: 8,
          drawOutOfBound: false,
          layoutAnimation: true,
          textStyle: {
            fontFamily: 'sans-serif',
            fontWeight: 'bold',
            color: function () {
              const colors = [
                '#1890ff', '#52c41a', '#faad14', '#13c2c2',
                '#722ed1', '#eb2f96', '#fa8c16', '#2f54eb',
                '#a0d911', '#fa541c', '#1da57a', '#597ef7'
              ]
              return colors[Math.floor(Math.random() * colors.length)]
            }
          },
          emphasis: {
            focus: 'self',
            textStyle: {
              textShadowBlur: 10,
              textShadowColor: '#333'
            }
          },
          data: data
        }]
      })
    }
  }
}
</script>

<style scoped>
.page {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 20px;
  box-sizing: border-box;
}
.title {
  color: #333;
  margin: 0 0 4px 0;
  font-size: 24px;
  font-weight: 700;
}
.desc {
  color: #999;
  margin: 0 0 16px 0;
  font-size: 14px;
}
.panel {
  padding: 24px;
  border-radius: 8px;
  background-color: #fff;
  border: 1px solid #f0f0f0;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  min-height: 500px;
}
.controls {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.controls label {
  color: #333;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.source-select {
  padding: 8px 14px;
  border-radius: 8px;
  border: 1px solid #d9d9d9;
  background-color: #fff;
  color: #333;
  font-size: 14px;
  cursor: pointer;
}
.source-select:hover {
  border-color: #1890ff;
  background-color: #e6f7ff;
}
.info {
  color: #999;
  font-size: 13px;
}
.chart {
  height: 450px;
  width: 100%;
}
.loading-text {
  color: #999;
  text-align: center;
  margin-top: 20px;
}
.error-text {
  color: #ff4d4f;
  text-align: center;
  margin-top: 20px;
}
</style>
