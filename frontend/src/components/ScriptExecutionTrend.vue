<template>
  <div class="script-execution-trend">
    <el-card class="chart-card" v-loading="loading">
      <div slot="header" class="card-header">
        <h3>任务执行的时延变化趋势</h3>
        <div class="controls">
          <el-select v-model="selectedScript" size="small" placeholder="选择脚本" clearable @change="fetchTrend">
            <el-option
              v-for="script in scripts"
              :key="script.id"
              :label="script.name"
              :value="script.id"
            ></el-option>
          </el-select>
          <el-select v-model="timeRange" size="small" style="margin-left: 10px" @change="fetchTrend">
            <el-option label="最近7天" value="7"></el-option>
            <el-option label="最近30天" value="30"></el-option>
            <el-option label="最近90天" value="90"></el-option>
          </el-select>
        </div>
      </div>
      <!-- 简化图表容器结构 -->
      <div id="trend-chart" style="width: 100%; height: 350px;"></div>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios';
import { mapState } from 'vuex';
import * as echarts from 'echarts';

export default {
  name: 'ScriptExecutionTrend',
  props: {
    scriptId: {
      type: [Number, String],
      default: null
    }
  },
  data() {
    return {
      loading: false,
      selectedScript: null,
      timeRange: '30',
      trendData: [],
      chartInstance: null
    };
  },
  computed: {
    ...mapState(['scripts'])
  },
  mounted() {
    // 在DOM挂载后初始化图表
    this.$nextTick(() => {
      this.initChart();
      
      if (this.scriptId) {
        // 如果有传入scriptId，直接使用
        this.selectedScript = Number(this.scriptId);
        this.fetchTrend();
      } else {
        // 否则回退到原来的逻辑
        this.fetchScripts();
      }
    });
  },
  beforeDestroy() {
    // 组件销毁前清理图表实例
    if (this.chartInstance) {
      this.chartInstance.dispose();
      this.chartInstance = null;
    }
  },
  methods: {
    // 初始化图表
    initChart() {
      // 确保DOM元素存在
      const chartDom = document.getElementById('trend-chart');
      if (!chartDom) {
        console.error('找不到图表DOM元素');
        return;
      }
      
      // 销毁旧实例
      if (this.chartInstance) {
        this.chartInstance.dispose();
      }
      
      // 创建新图表实例
      this.chartInstance = echarts.init(chartDom);
      
      // 设置基本配置
      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'line'
          },
          formatter: '{b}: {c}秒'
        },
        legend: {
          data: ['执行时延']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: [],
          axisPointer: {
            type: 'shadow'
          }
        },
        yAxis: {
          type: 'value',
          name: '执行时延(秒)',
          min: 0,
          axisLabel: {
            formatter: '{value}'
          }
        },
        series: [
          {
            name: '执行时延',
            type: 'line',
            data: [],
            color: '#409eff',
            symbol: 'circle',
            symbolSize: 8,
            smooth: true,
            lineStyle: {
              width: 3
            },
            areaStyle: {
              opacity: 0.2,
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  {
                    offset: 0,
                    color: 'rgba(64, 158, 255, 0.7)'
                  },
                  {
                    offset: 1,
                    color: 'rgba(64, 158, 255, 0.1)'
                  }
                ]
              }
            },
            emphasis: {
              focus: 'series',
              lineStyle: {
                width: 5
              }
            }
          }
        ]
      };
      
      // 设置图表选项
      this.chartInstance.setOption(option);
      
      // 添加窗口大小变化监听
      window.addEventListener('resize', this.resizeChart);
    },
    
    // 响应窗口大小变化
    resizeChart() {
      if (this.chartInstance) {
        this.chartInstance.resize();
      }
    },
    
    fetchScripts() {
      if (this.scriptId) {
        // 如果已有scriptId，直接使用
        this.selectedScript = Number(this.scriptId);
        this.fetchTrend();
        return;
      }
      
      if (this.scripts.length === 0) {
        this.$store.dispatch('fetchScripts').then(() => {
          if (this.scripts.length > 0) {
            this.selectedScript = this.scripts[0].id;
            this.fetchTrend();
          }
        });
      } else {
        this.selectedScript = this.scripts[0].id;
        this.fetchTrend();
      }
    },
    
    async fetchTrend() {
      if (!this.selectedScript) return;
      
      this.loading = true;
      console.log('开始获取脚本趋势数据，scriptId:', this.selectedScript);
      
      try {
        // 计算日期范围
        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(endDate.getDate() - parseInt(this.timeRange));
        
        const params = {
          period: 'day',
          script_id: this.selectedScript,
          start_date: this.formatDate(startDate),
          end_date: this.formatDate(endDate)
        };
        
        console.log('请求参数:', params);
        
        const response = await axios.get('/api/execution/statistics', { params });
        console.log('API响应:', response.data);
        
        if (response.data.code === 0) {
          this.trendData = response.data.data;
          console.log('获取到趋势数据:', this.trendData);
          this.updateChart();
        } else {
          console.error('获取趋势数据失败:', response.data.message);
          this.$message.error(response.data.message || '获取趋势数据失败');
        }
      } catch (error) {
        this.$message.error('获取趋势数据失败: ' + error.message);
      } finally {
        this.loading = false;
      }
    },
    
    formatDate(date) {
      const year = date.getFullYear();
      const month = (date.getMonth() + 1).toString().padStart(2, '0');
      const day = date.getDate().toString().padStart(2, '0');
      return `${year}-${month}-${day}`;
    },
    
    updateChart() {
      if (!this.chartInstance || !this.trendData || !this.trendData.length) {
        console.log('没有图表实例或趋势数据，无法更新图表');
        return;
      }
      
      console.log('开始更新图表数据');
      
      // 提取数据
      const timeLabels = this.trendData.map(item => item.time_period);
      
      // 平均执行时间（秒）
      const avgTimes = this.trendData.map(item => {
        if (item.avg_execution_time) {
          // 确保返回数值而不是字符串
          return parseFloat(Number(item.avg_execution_time).toFixed(2));
        }
        return 0;
      });
      
      // 更新图表数据
      this.chartInstance.setOption({
        xAxis: {
          data: timeLabels
        },
        series: [
          {
            name: '执行时延',
            data: avgTimes
          }
        ]
      });
      
      console.log('图表数据已更新:', {
        timeLabels,
        avgTimes
      });
    }
  }
};
</script>

<style lang="scss" scoped>
.script-execution-trend {
  width: 100%;
}

.chart-card {
  margin-bottom: 20px;
  width: 100%;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    h3 {
      margin: 0;
      font-size: 16px;
      font-weight: 500;
    }
  }
}
</style>
