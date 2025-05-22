<template>
  <div class="chain-execution-time-chart">
    <el-card class="chart-card" v-loading="loading">
      <div slot="header" class="card-header">
        <h3>任务链执行时间变化</h3>
        <div class="controls">
          <el-select 
            v-model="selectedChain" 
            size="small" 
            placeholder="选择任务链" 
            clearable 
            @change="fetchData"
          >
            <el-option
              v-for="chain in chains"
              :key="chain.id"
              :label="chain.name"
              :value="chain.id"
            ></el-option>
          </el-select>
          <el-select 
            v-model="timeRange" 
            size="small" 
            style="margin-left: 10px" 
            @change="fetchData"
          >
            <el-option label="最近7天" value="7"></el-option>
            <el-option label="最近30天" value="30"></el-option>
            <el-option label="最近90天" value="90"></el-option>
          </el-select>
        </div>
      </div>
      
      <el-empty v-if="!selectedChain" description="请选择任务链"></el-empty>
      <div v-else id="chain-time-chart" style="width: 100%; height: 300px; margin-top: 10px;"></div>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios';
import { mapState } from 'vuex';
import * as echarts from 'echarts';

export default {
  name: 'ChainExecutionTimeChart',
  data() {
    return {
      loading: false,
      selectedChain: null,
      timeRange: '30',
      executionData: [],
      chartInstance: null
    };
  },
  computed: {
    ...mapState(['chains'])
  },
  mounted() {
    this.$nextTick(() => {
      this.fetchChains();
    });
  },
  beforeDestroy() {
    if (this.chartInstance) {
      this.chartInstance.dispose();
      window.removeEventListener('resize', this.resizeChart);
    }
  },
  methods: {
    initChart() {
      // 确保DOM元素存在
      const chartDom = document.getElementById('chain-time-chart');
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
        title: {
          text: '执行时间变化',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          formatter: function(params) {
            const time = params[0].value[0];
            const duration = params[0].value[1];
            return `${time}<br/>执行时间: ${duration.toFixed(2)}秒`;
          },
          axisPointer: {
            animation: false
          }
        },
        xAxis: {
          type: 'time',
          splitLine: {
            show: false
          }
        },
        yAxis: {
          type: 'value',
          name: '执行时间(秒)',
          splitLine: {
            show: false
          }
        },
        series: [{
          name: '执行时间',
          type: 'line',
          showSymbol: true,
          symbolSize: 8,
          hoverAnimation: false,
          data: [],
          lineStyle: {
            width: 2,
            color: '#67C23A'
          },
          itemStyle: {
            color: '#67C23A'
          },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [{
                offset: 0,
                color: 'rgba(103,194,58,0.4)'
              }, {
                offset: 1,
                color: 'rgba(103,194,58,0.1)'
              }]
            }
          }
        }]
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
    
    fetchChains() {
      if (this.chains.length === 0) {
        this.$store.dispatch('fetchChains').then(() => {
          if (this.chains.length > 0) {
            this.selectedChain = this.chains[0].id;
            this.initChart();
            this.fetchData();
          }
        });
      } else if (this.chains.length > 0) {
        this.selectedChain = this.chains[0].id;
        this.initChart();
        this.fetchData();
      }
    },
    
    async fetchData() {
      if (!this.selectedChain) return;
      
      this.loading = true;
      
      try {
        // 计算日期范围
        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(endDate.getDate() - parseInt(this.timeRange));
        
        const params = {
          chain_id: this.selectedChain,
          start_date: this.formatDate(startDate),
          end_date: this.formatDate(endDate)
        };
        
        const response = await axios.get('/api/execution/history', { params });
        
        if (response.data.code === 0) {
          this.processData(response.data.data);
        } else {
          this.$message.error(response.data.message || '获取执行时间数据失败');
        }
      } catch (error) {
        this.$message.error('获取执行时间数据失败: ' + error.message);
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
    
    processData(data) {
      if (!this.chartInstance) {
        this.initChart();
      }
      
      // 过滤出当前选择的任务链的执行历史
      const chainHistories = data.filter(item => 
        item.chain_id === this.selectedChain && 
        item.status === 'completed' &&
        item.execution_time
      );
      
      // 根据开始时间排序
      chainHistories.sort((a, b) => new Date(a.start_time) - new Date(b.start_time));
      
      // 准备图表数据
      const chartData = chainHistories.map(item => {
        return [
          item.start_time,
          parseFloat(item.execution_time)
        ];
      });
      
      // 更新标题
      const foundChain = this.chains.find(c => c.id === this.selectedChain);
      const chainName = foundChain ? foundChain.name : '未知任务链';
      
      // 更新图表数据
      this.chartInstance.setOption({
        title: {
          text: `${chainName} - 执行时间变化`
        },
        series: [{
          name: '执行时间',
          data: chartData
        }]
      });
    }
  }
};
</script>

<style lang="scss" scoped>
.chart-card {
  margin-bottom: 20px;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    h3 {
      margin: 0;
      font-size: 16px;
      font-weight: 500;
    }
    
    .controls {
      display: flex;
      align-items: center;
    }
  }
}
</style>
