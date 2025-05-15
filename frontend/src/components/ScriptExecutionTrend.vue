<template>
  <div class="script-execution-trend">
    <el-card class="chart-card" v-loading="loading">
      <div slot="header" class="card-header">
        <h3>脚本执行趋势</h3>
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
      <v-chart class="chart" :option="trendOption" autoresize />
    </el-card>
  </div>
</template>

<script>
import axios from 'axios';
import { mapState } from 'vuex';
import VChart from 'vue-echarts';

export default {
  name: 'ScriptExecutionTrend',
  components: {
    VChart
  },
  data() {
    return {
      loading: false,
      selectedScript: null,
      timeRange: '30',
      trendData: [],
      trendOption: {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        legend: {
          data: ['执行次数', '成功率', '平均执行时间']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: [
          {
            type: 'category',
            data: [],
            axisPointer: {
              type: 'shadow'
            }
          }
        ],
        yAxis: [
          {
            type: 'value',
            name: '执行次数',
            min: 0,
            axisLabel: {
              formatter: '{value}'
            }
          },
          {
            type: 'value',
            name: '百分比/时间',
            min: 0,
            max: 100,
            axisLabel: {
              formatter: '{value}'
            }
          }
        ],
        series: [
          {
            name: '执行次数',
            type: 'bar',
            data: [],
            color: '#409eff'
          },
          {
            name: '成功率',
            type: 'line',
            yAxisIndex: 1,
            data: [],
            color: '#67c23a',
            symbol: 'circle',
            symbolSize: 8
          },
          {
            name: '平均执行时间',
            type: 'line',
            yAxisIndex: 1,
            data: [],
            color: '#e6a23c',
            symbol: 'triangle',
            symbolSize: 8
          }
        ]
      }
    };
  },
  computed: {
    ...mapState(['scripts'])
  },
  mounted() {
    this.fetchScripts();
  },
  methods: {
    fetchScripts() {
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
        
        const response = await axios.get('/api/execution/statistics', { params });
        
        if (response.data.code === 0) {
          this.trendData = response.data.data;
          this.updateChart();
        } else {
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
      if (!this.trendData || !this.trendData.length) {
        this.trendOption.xAxis[0].data = [];
        this.trendOption.series[0].data = [];
        this.trendOption.series[1].data = [];
        this.trendOption.series[2].data = [];
        return;
      }
      
      // 提取数据
      const timeLabels = this.trendData.map(item => item.time_period);
      const totalCounts = this.trendData.map(item => item.total_count);
      
      // 计算成功率
      const successRates = this.trendData.map(item => {
        if (item.total_count > 0) {
          return ((item.success_count / item.total_count) * 100).toFixed(2);
        }
        return 0;
      });
      
      // 平均执行时间（秒）
      const avgTimes = this.trendData.map(item => {
        if (item.avg_execution_time) {
          // 如果平均执行时间超过100秒，进行缩放以便在图表上显示
          const time = Number(item.avg_execution_time);
          return time > 100 ? 100 : time.toFixed(2);
        }
        return 0;
      });
      
      // 更新图表
      this.trendOption.xAxis[0].data = timeLabels;
      this.trendOption.series[0].data = totalCounts;
      this.trendOption.series[1].data = successRates;
      this.trendOption.series[2].data = avgTimes;
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
  }
  
  .chart {
    height: 300px;
  }
}
</style>
