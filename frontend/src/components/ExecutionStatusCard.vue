<template>
  <div class="execution-status-card">
    <el-card class="chart-card" shadow="hover" v-loading="loading">
      <div slot="header" class="card-header">
        <h3>执行状态统计</h3>
        <el-select v-model="timeRange" size="small" @change="fetchData">
          <el-option label="最近7天" value="7"></el-option>
          <el-option label="最近30天" value="30"></el-option>
          <el-option label="最近90天" value="90"></el-option>
        </el-select>
      </div>
      
      <div class="chart-container">
        <div class="stats-summary">
          <div class="stat-item success">
            <div class="stat-value">{{ successCount }}</div>
            <div class="stat-label">成功</div>
          </div>
          <div class="stat-item failed">
            <div class="stat-value">{{ failedCount }}</div>
            <div class="stat-label">失败</div>
          </div>
          <div class="stat-item total">
            <div class="stat-value">{{ totalCount }}</div>
            <div class="stat-label">总计</div>
          </div>
          <div class="stat-item rate">
            <div class="stat-value">{{ successRate }}%</div>
            <div class="stat-label">成功率</div>
          </div>
        </div>
        
        <v-chart class="pie-chart" :option="chartOption" autoresize />
      </div>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios';
import VChart from 'vue-echarts';

export default {
  name: 'ExecutionStatusCard',
  components: {
    VChart
  },
  data() {
    return {
      loading: false,
      timeRange: '30',
      statistics: [],
      successCount: 0,
      failedCount: 0,
      totalCount: 0,
      successRate: '0.00',
      chartOption: {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'horizontal',
          bottom: 0,
          data: ['成功', '失败', '执行中']
        },
        series: [
          {
            name: '执行状态',
            type: 'pie',
            radius: ['50%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              show: false,
              position: 'center'
            },
            emphasis: {
              label: {
                show: true,
                fontSize: '18',
                fontWeight: 'bold'
              }
            },
            labelLine: {
              show: false
            },
            data: [
              { value: 0, name: '成功', itemStyle: { color: '#67c23a' } },
              { value: 0, name: '失败', itemStyle: { color: '#f56c6c' } },
              { value: 0, name: '执行中', itemStyle: { color: '#409eff' } }
            ]
          }
        ]
      }
    };
  },
  mounted() {
    this.fetchData();
  },
  methods: {
    async fetchData() {
      this.loading = true;
      
      try {
        // 计算日期范围
        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(endDate.getDate() - parseInt(this.timeRange));
        
        const params = {
          period: 'day',
          start_date: this.formatDate(startDate),
          end_date: this.formatDate(endDate)
        };
        
        const response = await axios.get('/api/execution/statistics', { params });
        
        if (response.data.code === 0) {
          this.statistics = response.data.data;
          this.processData();
        } else {
          this.$message.error(response.data.message || '获取统计数据失败');
        }
      } catch (error) {
        this.$message.error('获取统计数据失败: ' + error.message);
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
    processData() {
      if (!this.statistics || !this.statistics.length) {
        this.successCount = 0;
        this.failedCount = 0;
        this.totalCount = 0;
        this.successRate = '0.00';
        this.updateChart(0, 0, 0);
        return;
      }
      
      // 计算总数
      this.successCount = this.statistics.reduce((sum, item) => sum + parseInt(item.success_count || 0), 0);
      this.failedCount = this.statistics.reduce((sum, item) => sum + parseInt(item.failed_count || 0), 0);
      this.totalCount = this.successCount + this.failedCount;
      
      // 计算成功率
      if (this.totalCount > 0) {
        this.successRate = ((this.successCount / this.totalCount) * 100).toFixed(2);
      } else {
        this.successRate = '0.00';
      }
      
      // 计算执行中的数量
      const runningCount = this.statistics.reduce((sum, item) => {
        const total = parseInt(item.total_count || 0);
        const success = parseInt(item.success_count || 0);
        const failed = parseInt(item.failed_count || 0);
        return sum + (total - success - failed);
      }, 0);
      
      // 更新图表
      this.updateChart(this.successCount, this.failedCount, runningCount);
    },
    updateChart(success, failed, running) {
      this.chartOption.series[0].data = [
        { value: success, name: '成功', itemStyle: { color: '#67c23a' } },
        { value: failed, name: '失败', itemStyle: { color: '#f56c6c' } },
        { value: running, name: '执行中', itemStyle: { color: '#409eff' } }
      ];
    }
  }
};
</script>

<style lang="scss" scoped>
.execution-status-card {
  margin-bottom: 20px;
  
  .chart-card {
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
    
    .chart-container {
      display: flex;
      
      .stats-summary {
        width: 40%;
        display: flex;
        flex-wrap: wrap;
        
        .stat-item {
          width: 50%;
          padding: 15px;
          text-align: center;
          
          .stat-value {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 5px;
          }
          
          .stat-label {
            font-size: 14px;
            color: #909399;
          }
          
          &.success .stat-value {
            color: #67c23a;
          }
          
          &.failed .stat-value {
            color: #f56c6c;
          }
          
          &.rate .stat-value {
            color: #409eff;
          }
          
          &.total .stat-value {
            color: #e6a23c;
          }
        }
      }
      
      .pie-chart {
        flex: 1;
        height: 200px;
      }
    }
  }
}
</style>
