<template>
  <div class="history-statistics">
    <div class="chart-controls">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="统计周期">
            <el-select v-model="period" @change="fetchStatistics">
              <el-option label="按小时" value="hour"></el-option>
              <el-option label="按天" value="day"></el-option>
              <el-option label="按周" value="week"></el-option>
              <el-option label="按月" value="month"></el-option>
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="日期范围">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="yyyy-MM-dd"
              @change="fetchStatistics"
            ></el-date-picker>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="类型">
            <el-select v-model="type" @change="fetchStatistics">
              <el-option label="全部" value="all"></el-option>
              <el-option label="脚本" value="script"></el-option>
              <el-option label="脚本链" value="chain"></el-option>
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
    </div>

    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="chart-card" v-loading="loading">
          <div slot="header" class="card-header">
            <h3>执行次数统计</h3>
          </div>
          <v-chart class="chart" :option="executionCountOption" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card class="chart-card" v-loading="loading">
          <div slot="header" class="card-header">
            <h3>成功率统计</h3>
          </div>
          <v-chart class="chart" :option="successRateOption" autoresize />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card" v-loading="loading">
          <div slot="header" class="card-header">
            <h3>平均执行时间</h3>
          </div>
          <v-chart class="chart" :option="executionTimeOption" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="chart-card" v-loading="loading">
          <div slot="header" class="card-header">
            <h3>执行状态分布</h3>
          </div>
          <v-chart class="chart" :option="statusDistributionOption" autoresize />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import axios from 'axios';
import VChart from 'vue-echarts';

export default {
  name: 'HistoryStatistics',
  components: {
    VChart
  },
  data() {
    return {
      loading: false,
      period: 'day',
      dateRange: [],
      type: 'all',
      statistics: [],
      executionCountOption: {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        legend: {
          data: ['总执行次数', '成功次数', '失败次数']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: []
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            name: '总执行次数',
            type: 'bar',
            data: [],
            color: '#409eff'
          },
          {
            name: '成功次数',
            type: 'bar',
            data: [],
            color: '#67c23a'
          },
          {
            name: '失败次数',
            type: 'bar',
            data: [],
            color: '#f56c6c'
          }
        ]
      },
      successRateOption: {
        tooltip: {
          trigger: 'axis',
          formatter: '{b}: {c}%'
        },
        xAxis: {
          type: 'category',
          data: []
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            formatter: '{value}%'
          },
          max: 100
        },
        series: [
          {
            data: [],
            type: 'line',
            smooth: true,
            color: '#67c23a',
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  {
                    offset: 0,
                    color: 'rgba(103, 194, 58, 0.3)'
                  },
                  {
                    offset: 1,
                    color: 'rgba(103, 194, 58, 0.1)'
                  }
                ]
              }
            }
          }
        ]
      },
      executionTimeOption: {
        tooltip: {
          trigger: 'axis',
          formatter: '{b}: {c}秒'
        },
        xAxis: {
          type: 'category',
          data: []
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            formatter: '{value}秒'
          }
        },
        series: [
          {
            data: [],
            type: 'line',
            smooth: true,
            color: '#409eff',
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  {
                    offset: 0,
                    color: 'rgba(64, 158, 255, 0.3)'
                  },
                  {
                    offset: 1,
                    color: 'rgba(64, 158, 255, 0.1)'
                  }
                ]
              }
            }
          }
        ]
      },
      statusDistributionOption: {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b} : {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          data: ['成功', '失败', '执行中']
        },
        series: [
          {
            name: '执行状态',
            type: 'pie',
            radius: '60%',
            center: ['50%', '50%'],
            data: [
              { value: 0, name: '成功', itemStyle: { color: '#67c23a' } },
              { value: 0, name: '失败', itemStyle: { color: '#f56c6c' } },
              { value: 0, name: '执行中', itemStyle: { color: '#409eff' } }
            ],
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }
        ]
      }
    };
  },
  mounted() {
    this.setDefaultDateRange();
    this.fetchStatistics();
  },
  methods: {
    setDefaultDateRange() {
      const end = new Date();
      const start = new Date();
      start.setDate(start.getDate() - 30); // 默认显示最近30天
      
      this.dateRange = [
        this.formatDate(start),
        this.formatDate(end)
      ];
    },
    formatDate(date) {
      const year = date.getFullYear();
      const month = (date.getMonth() + 1).toString().padStart(2, '0');
      const day = date.getDate().toString().padStart(2, '0');
      return `${year}-${month}-${day}`;
    },
    async fetchStatistics() {
      this.loading = true;
      
      try {
        // 构建查询参数
        const params = {
          period: this.period
        };
        
        if (this.dateRange && this.dateRange.length === 2) {
          params.start_date = this.dateRange[0];
          params.end_date = this.dateRange[1];
        }
        
        if (this.type === 'script') {
          // 如果需要，可以添加脚本ID筛选
        } else if (this.type === 'chain') {
          // 如果需要，可以添加脚本链ID筛选
        }
        
        const response = await axios.get('/api/execution/statistics', { params });
        
        if (response.data.code === 0) {
          this.statistics = response.data.data;
          this.updateCharts();
        } else {
          this.$message.error(response.data.message || '获取统计数据失败');
        }
      } catch (error) {
        this.$message.error('获取统计数据失败: ' + error.message);
      } finally {
        this.loading = false;
      }
    },
    updateCharts() {
      if (!this.statistics || !this.statistics.length) {
        return;
      }
      
      // 提取数据
      const timeLabels = this.statistics.map(item => item.time_period);
      const totalCounts = this.statistics.map(item => item.total_count);
      const successCounts = this.statistics.map(item => item.success_count);
      const failedCounts = this.statistics.map(item => item.failed_count);
      const avgTimes = this.statistics.map(item => item.avg_execution_time ? Number(item.avg_execution_time).toFixed(2) : 0);
      
      // 计算成功率
      const successRates = this.statistics.map(item => {
        if (item.total_count > 0) {
          return ((item.success_count / item.total_count) * 100).toFixed(2);
        }
        return 0;
      });
      
      // 更新执行次数图表
      this.executionCountOption.xAxis.data = timeLabels;
      this.executionCountOption.series[0].data = totalCounts;
      this.executionCountOption.series[1].data = successCounts;
      this.executionCountOption.series[2].data = failedCounts;
      
      // 更新成功率图表
      this.successRateOption.xAxis.data = timeLabels;
      this.successRateOption.series[0].data = successRates;
      
      // 更新执行时间图表
      this.executionTimeOption.xAxis.data = timeLabels;
      this.executionTimeOption.series[0].data = avgTimes;
      
      // 更新状态分布图表
      const totalSuccess = successCounts.reduce((sum, current) => sum + parseInt(current), 0);
      const totalFailed = failedCounts.reduce((sum, current) => sum + parseInt(current), 0);
      const totalRunning = totalCounts.reduce((sum, current) => sum + parseInt(current), 0) - totalSuccess - totalFailed;
      
      this.statusDistributionOption.series[0].data = [
        { value: totalSuccess, name: '成功', itemStyle: { color: '#67c23a' } },
        { value: totalFailed, name: '失败', itemStyle: { color: '#f56c6c' } },
        { value: totalRunning, name: '执行中', itemStyle: { color: '#409eff' } }
      ];
    }
  }
};
</script>

<style lang="scss" scoped>
.history-statistics {
  padding: 20px 0;
  
  .chart-controls {
    margin-bottom: 20px;
  }
  
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
}
</style>
