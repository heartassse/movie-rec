<template>
  <div class="page">
    <h1 class="title">数据可视化</h1>
    <p class="desc"></p>

    <div class="grid">
      <div class="panel">
        <h2 class="subtitle">用户评分分布</h2>
        <div ref="ratingChart" class="chart"></div>
      </div>

      <div class="panel">
        <h2 class="subtitle">好评最多的电影 Top10（平均分≥4.0）</h2>
        <div ref="topRatedChart" class="chart"></div>
      </div>

      <div class="panel">
        <h2 class="subtitle">最受欢迎的电影 Top10（评分人数最多）</h2>
        <div ref="popularChart" class="chart"></div>
      </div>

      <div class="panel">
        <h2 class="subtitle">评论最多的电影 Top10</h2>
        <div ref="commentedChart" class="chart"></div>
      </div>

      <div class="panel">
        <h2 class="subtitle">电影评分分布</h2>
        <div ref="scoreDistChart" class="chart"></div>
      </div>

      <div class="panel">
        <h2 class="subtitle">上映年代分布</h2>
        <div ref="yearChart" class="chart"></div>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import { mockStats } from '@/mock/stats'
import { recommendApi } from '@/api'
import { USE_MOCK } from '@/config'

export default {
  name: 'VisualizePage',
  data() {
    return {
      charts: [],
    }
  },
  mounted() {
    this.renderCharts()
    window.addEventListener('resize', this.resizeCharts)
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.resizeCharts)
    this.disposeCharts()
  },
  methods: {
    disposeCharts() {
      this.charts.forEach((c) => {
        try {
          c.dispose()
        } catch {
          // ignore
        }
      })
      this.charts = []
    },
    resizeCharts() {
      this.charts.forEach((c) => c.resize())
    },
    async renderCharts() {
      this.disposeCharts()

      let stats = mockStats
      if (!USE_MOCK) {
        try {
          console.log('正在获取统计数据...')
          const res = await recommendApi.stats()
          console.log('API响应:', res.data)
          stats = res.data || mockStats
          
          // 检查数据完整性
          if (!stats.topRated) console.warn('topRated 数据缺失')
          if (!stats.mostPopular) console.warn('mostPopular 数据缺失')
          if (!stats.topCommented) console.warn('topCommented 数据缺失')
          if (!stats.movieScoreDistribution && !stats.bookScoreDistribution) console.warn('movieScoreDistribution 数据缺失')
          
        } catch (e) {
          console.error('获取统计数据失败:', e)
          stats = mockStats
        }
      }

      const commonGridConfig = { left: 100, right: 30, top: 20, bottom: 30 }
      const commonAxisLabel = { color: '#666', fontSize: 12 }
      const commonSplitLine = { lineStyle: { color: '#f0f0f0' } }

      // 1. 用户评分分布
      const ratingEl = this.$refs.ratingChart
      const ratingChart = echarts.init(ratingEl)
      this.charts.push(ratingChart)
      ratingChart.setOption({
        backgroundColor: 'transparent',
        grid: { left: 50, right: 20, top: 20, bottom: 30 },
        xAxis: {
          type: 'category',
          data: (stats.ratingDistribution || []).map((x) => `${x.score}星`),
          axisLabel: commonAxisLabel,
          axisLine: { lineStyle: { color: '#e8e8e8' } },
        },
        yAxis: {
          type: 'value',
          axisLabel: commonAxisLabel,
          splitLine: commonSplitLine,
        },
        series: [
          {
            type: 'bar',
            data: (stats.ratingDistribution || []).map((x) => x.count),
            itemStyle: { color: '#1890ff', borderRadius: [6, 6, 0, 0] },
          },
        ],
      })

      // 2. 好评最多的电影 Top10
      const topRatedEl = this.$refs.topRatedChart
      if (topRatedEl) {
        const topRatedChart = echarts.init(topRatedEl)
        this.charts.push(topRatedChart)
        const topRatedData = stats.topRated || []
        
        if (topRatedData.length === 0) {
          console.warn('好评电影数据为空')
        }
        
        topRatedChart.setOption({
        backgroundColor: 'transparent',
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' },
          formatter: (params) => {
            const data = params[0]
            const item = topRatedData[topRatedData.length - 1 - data.dataIndex]
            return `${item.title}<br/>平均分: ${item.avg_score} 星<br/>评分人数: ${item.rating_count}`
          },
        },
        grid: commonGridConfig,
        xAxis: {
          type: 'value',
          axisLabel: commonAxisLabel,
          splitLine: commonSplitLine,
        },
        yAxis: {
          type: 'category',
          data: topRatedData.map((x) => x.title.length > 15 ? x.title.substring(0, 15) + '...' : x.title).reverse(),
          axisLabel: commonAxisLabel,
          axisLine: { lineStyle: { color: '#e8e8e8' } },
        },
        series: [
          {
            type: 'bar',
            data: topRatedData.map((x) => x.avg_score).reverse(),
            itemStyle: { color: '#faad14', borderRadius: [0, 6, 6, 0] },
          },
        ],
        })
      }

      // 3. 最受欢迎的电影 Top10
      const popularEl = this.$refs.popularChart
      if (popularEl) {
        const popularChart = echarts.init(popularEl)
        this.charts.push(popularChart)
        const popularData = stats.mostPopular || []
        popularChart.setOption({
        backgroundColor: 'transparent',
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' },
        },
        grid: commonGridConfig,
        xAxis: {
          type: 'value',
          axisLabel: commonAxisLabel,
          splitLine: commonSplitLine,
        },
        yAxis: {
          type: 'category',
          data: popularData.map((x) => x.title.length > 15 ? x.title.substring(0, 15) + '...' : x.title).reverse(),
          axisLabel: commonAxisLabel,
          axisLine: { lineStyle: { color: '#e8e8e8' } },
        },
        series: [
          {
            type: 'bar',
            data: popularData.map((x) => x.count).reverse(),
            itemStyle: { color: '#52c41a', borderRadius: [0, 6, 6, 0] },
          },
        ],
        })
      }

      // 4. 评论最多的电影 Top10
      const commentedEl = this.$refs.commentedChart
      if (commentedEl) {
        const commentedChart = echarts.init(commentedEl)
        this.charts.push(commentedChart)
        const commentedData = stats.topCommented || []
        commentedChart.setOption({
        backgroundColor: 'transparent',
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' },
        },
        grid: commonGridConfig,
        xAxis: {
          type: 'value',
          axisLabel: commonAxisLabel,
          splitLine: commonSplitLine,
        },
        yAxis: {
          type: 'category',
          data: commentedData.map((x) => x.title.length > 15 ? x.title.substring(0, 15) + '...' : x.title).reverse(),
          axisLabel: commonAxisLabel,
          axisLine: { lineStyle: { color: '#e8e8e8' } },
        },
        series: [
          {
            type: 'bar',
            data: commentedData.map((x) => x.count).reverse(),
            itemStyle: { color: '#13c2c2', borderRadius: [0, 6, 6, 0] },
          },
        ],
        })
      }

      // 5. 电影评分分布
      const scoreDistEl = this.$refs.scoreDistChart
      if (scoreDistEl) {
        const scoreDistChart = echarts.init(scoreDistEl)
        this.charts.push(scoreDistChart)
        scoreDistChart.setOption({
        backgroundColor: 'transparent',
        grid: { left: 80, right: 20, top: 20, bottom: 30 },
        xAxis: {
          type: 'category',
          data: (stats.movieScoreDistribution || stats.bookScoreDistribution || []).map((x) => x.range),
          axisLabel: { ...commonAxisLabel, rotate: 15 },
          axisLine: { lineStyle: { color: '#e8e8e8' } },
        },
        yAxis: {
          type: 'value',
          axisLabel: commonAxisLabel,
          splitLine: commonSplitLine,
        },
        series: [
          {
            type: 'bar',
            data: (stats.movieScoreDistribution || stats.bookScoreDistribution || []).map((x) => x.count),
            itemStyle: { color: '#722ed1', borderRadius: [6, 6, 0, 0] },
          },
        ],
        })
      }

      // 6. 上映年代分布
      const yearEl = this.$refs.yearChart
      if (yearEl) {
        const yearChart = echarts.init(yearEl)
        this.charts.push(yearChart)
        yearChart.setOption({
        backgroundColor: 'transparent',
        tooltip: {
          trigger: 'item',
          formatter: '{b}: {c} ({d}%)',
        },
        legend: {
          top: 10,
          textStyle: { color: '#666' },
        },
        series: [
          {
            type: 'pie',
            radius: ['35%', '60%'],
            avoidLabelOverlap: true,
            label: { color: '#333' },
            labelLine: { lineStyle: { color: '#d9d9d9' } },
            data: stats.yearDistribution || stats.categoryShare || [],
          },
        ],
        })
      }
      
      console.log('所有图表渲染完成')
    },
  },
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
.grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}
.panel {
  padding: 20px;
  border-radius: 16px;
  background-color: #fff;
  border: 1px solid #f0f0f0;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.subtitle {
  color: #333;
  margin: 0 0 16px 0;
  font-size: 17px;
  font-weight: 600;
}
.chart {
  height: 350px;
}
@media (min-width: 900px) {
  .grid {
    grid-template-columns: 1fr 1fr;
  }
  .chart {
    height: 380px;
  }
}
</style>
