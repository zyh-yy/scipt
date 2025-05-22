<template>
  <div class="script-execution-time-chart">
    <el-card class="chart-card" v-loading="loading">
      <div slot="header" class="card-header">
        <h3>脚本执行时间变化</h3>
        <div class="controls">
          <el-select 
            v-model="selectedScript" 
            size="small" 
            placeholder="选择脚本" 
            clearable 
            @change="fetchData"
          >
            <el-option
              v-for="script in scripts"
              :key="script.id"
              :label="script.name"
              :value="script.id"
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
      
      <el-empty v-if="!selectedScript" description="请选择脚本"></el-empty>
      <div v-else id="script-time-chart" style="width: 100%; height: 300px; margin-top: 10px;"></div>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios';
import { mapState } from 'vuex';
import * as echarts from 'echarts';

export default {
  name: 'ScriptExecutionTimeChart',
  data() {
    return {
      loading: false,
      selectedScript: null,
      timeRange: '30',
      executionData: [],
      chartInstance: null
    };
  },
  computed: {
    ...mapState(['scripts'])
  },
  mounted() {
    this.$nextTick(() => {
      this.fetchScripts();
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
      const chartDom = document.getElementById('script-time-chart');
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
            color: '#409EFF'
          },
          itemStyle: {
            color: '#409EFF'
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
                color: 'rgba(64,158,255,0.4)'
              }, {
                offset: 1,
                color: 'rgba(64,158,255,0.1)'
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
    
    fetchScripts() {
      if (this.scripts.length === 0) {
        this.$store.dispatch('fetchScripts').then(() => {
          if (this.scripts.length > 0) {
            this.selectedScript = this.scripts[0].id;
            this.initChart();
            this.fetchData();
          }
        });
      } else if (this.scripts.length > 0) {
        this.selectedScript = this.scripts[0].id;
        this.initChart();
        this.fetchData();
      }
    },
    
    async fetchData() {
      if (!this.selectedScript) return;
      
      this.loading = true;
      
      try {
        // 计算日期范围
        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(endDate.getDate() - parseInt(this.timeRange));
        
        const params = {
          script_id: this.selectedScript,
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
      
      // 过滤出当前选择的脚本的执行历史
      const scriptHistories = data.filter(item => 
        item.script_id === this.selectedScript && 
        item.status === 'completed' &&
        item.execution_time
      );
      
      // 根据开始时间排序
      scriptHistories.sort((a, b) => new Date(a.start_time) - new Date(b.start_time));
      
      // 准备图表数据
      const chartData = scriptHistories.map(item => {
        return [
          item.start_time,
          parseFloat(item.execution_time)
        ];
      });
      
      // 更新标题
      const foundScript = this.scripts.find(s => s.id === this.selectedScript);
      const scriptName = foundScript ? foundScript.name : '未知脚本';
      
      // 更新图表数据
      this.chartInstance.setOption({
        title: {
          text: `${scriptName} - 执行时间变化`
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
