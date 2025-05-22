<template>
  <div class="history-statistics">
    <div class="chart-controls">
      <el-form>
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
      </el-form>
    </div>

    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="chart-card" v-loading="loading">
          <div slot="header" class="card-header">
            <h3>执行次数统计</h3>
          </div>
          <div class="chart" ref="executionCountChart"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card class="chart-card" v-loading="loading">
          <div slot="header" class="card-header">
            <h3>成功率统计</h3>
          </div>
          <div class="chart" ref="successRateChart"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card" v-loading="loading">
          <div slot="header" class="card-header">
            <h3>平均执行时间</h3>
          </div>
          <div class="chart" ref="executionTimeChart"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="chart-card" v-loading="loading">
          <div slot="header" class="card-header">
            <h3>执行状态分布</h3>
          </div>
          <div class="chart" ref="statusDistributionChart"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import axios from 'axios';
import echarts from 'echarts';

export default {
  name: 'HistoryStatistics',
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
    
    // 初始化图表实例
    this.initCharts();
  },
  
  beforeDestroy() {
    // 销毁图表实例，避免内存泄漏
    if (this.charts) {
      Object.values(this.charts).forEach(chart => {
        chart && chart.dispose();
      });
    }
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
        
        console.log('统计API请求参数:', params);
        
        const response = await axios.get('/api/execution/statistics', { params });
        
        console.log('统计API响应:', response.data);
        
        if (response.data.code === 0) {
          this.statistics = response.data.data || [];
          console.log('获取到的统计数据:', this.statistics);
          
          if (!this.statistics || this.statistics.length === 0) {
            console.warn('API返回的统计数据为空');
            this.$message.warning('暂无统计数据');
          } else {
            console.log('获取到的统计数据条目数:', this.statistics.length);
          }
          
          this.updateCharts();
        } else {
          console.error('API返回错误:', response.data.message);
          this.$message.error(response.data.message || '获取统计数据失败');
        }
      } catch (error) {
        console.error('获取统计数据失败:', error);
        this.$message.error('获取统计数据失败: ' + error.message);
      } finally {
        this.loading = false;
      }
    },
    initCharts() {
      // 存储所有图表实例的容器
      this.charts = {
        executionCount: null,
        successRate: null,
        executionTime: null,
        statusDistribution: null
      };
      
      // 确保DOM已渲染完成
      this.$nextTick(() => {
        // 初始化执行次数图表
        if (this.$refs.executionCountChart) {
          this.charts.executionCount = echarts.init(this.$refs.executionCountChart);
          this.charts.executionCount.setOption(this.executionCountOption);
        }
        
        // 初始化成功率图表
        if (this.$refs.successRateChart) {
          this.charts.successRate = echarts.init(this.$refs.successRateChart);
          this.charts.successRate.setOption(this.successRateOption);
        }
        
        // 初始化执行时间图表
        if (this.$refs.executionTimeChart) {
          this.charts.executionTime = echarts.init(this.$refs.executionTimeChart);
          this.charts.executionTime.setOption(this.executionTimeOption);
        }
        
        // 初始化状态分布图表
        if (this.$refs.statusDistributionChart) {
          this.charts.statusDistribution = echarts.init(this.$refs.statusDistributionChart);
          this.charts.statusDistribution.setOption(this.statusDistributionOption);
        }
        
        // 添加窗口调整大小的事件监听
        window.addEventListener('resize', this.resizeCharts);
      });
    },
    
    resizeCharts() {
      // 窗口调整大小时，重新调整图表的大小
      Object.values(this.charts).forEach(chart => {
        chart && chart.resize();
      });
    },
    
    updateCharts() {
      console.log('开始更新图表，统计数据长度:', this.statistics ? this.statistics.length : 0);
      
      if (!this.statistics || !this.statistics.length) {
        console.warn('没有统计数据，图表不会更新');
        return;
      }
      
      try {
        // 提取数据
        const timeLabels = this.statistics.map(item => item.time_period);
        console.log('时间标签:', timeLabels);
        
        const totalCounts = this.statistics.map(item => item.total_count);
        console.log('总执行次数:', totalCounts);
        
        const successCounts = this.statistics.map(item => item.success_count);
        console.log('成功次数:', successCounts);
        
        const failedCounts = this.statistics.map(item => item.failed_count);
        console.log('失败次数:', failedCounts);
        
        const avgTimes = this.statistics.map(item => {
          const value = item.avg_execution_time ? Number(item.avg_execution_time).toFixed(2) : 0;
          return Number(value);
        });
        console.log('平均执行时间:', avgTimes);
        
        // 计算成功率
        const successRates = this.statistics.map(item => {
          if (item.total_count > 0) {
            const rate = ((item.success_count / item.total_count) * 100).toFixed(2);
            return Number(rate);
          }
          return 0;
        });
        console.log('成功率:', successRates);
        
        // 更新执行次数图表选项 (使用Vue响应式方式)
        this.executionCountOption = Object.assign({}, this.executionCountOption, {
          xAxis: {
            ...this.executionCountOption.xAxis,
            data: timeLabels
          },
          series: [
            {
              ...this.executionCountOption.series[0],
              data: totalCounts
            },
            {
              ...this.executionCountOption.series[1],
              data: successCounts
            },
            {
              ...this.executionCountOption.series[2],
              data: failedCounts
            }
          ]
        });
        console.log('执行次数图表选项已更新');
        
        // 更新成功率图表选项 (使用Vue响应式方式)
        this.successRateOption = Object.assign({}, this.successRateOption, {
          xAxis: {
            ...this.successRateOption.xAxis,
            data: timeLabels
          },
          series: [
            {
              ...this.successRateOption.series[0],
              data: successRates
            }
          ]
        });
        console.log('成功率图表选项已更新');
        
        // 更新执行时间图表选项 (使用Vue响应式方式)
        this.executionTimeOption = Object.assign({}, this.executionTimeOption, {
          xAxis: {
            ...this.executionTimeOption.xAxis,
            data: timeLabels
          },
          series: [
            {
              ...this.executionTimeOption.series[0],
              data: avgTimes
            }
          ]
        });
        console.log('执行时间图表选项已更新');
        
        // 更新状态分布图表选项
        const totalSuccess = successCounts.reduce((sum, current) => sum + parseInt(current || 0), 0);
        const totalFailed = failedCounts.reduce((sum, current) => sum + parseInt(current || 0), 0);
        const totalRunning = totalCounts.reduce((sum, current) => sum + parseInt(current || 0), 0) - totalSuccess - totalFailed;
        
        console.log('总成功次数:', totalSuccess);
        console.log('总失败次数:', totalFailed);
        console.log('总运行中次数:', totalRunning);
        
        // 使用Vue响应式方式
        this.statusDistributionOption = Object.assign({}, this.statusDistributionOption, {
          series: [
            {
              ...this.statusDistributionOption.series[0],
              data: [
                { value: totalSuccess, name: '成功', itemStyle: { color: '#67c23a' } },
                { value: totalFailed, name: '失败', itemStyle: { color: '#f56c6c' } },
                { value: totalRunning, name: '执行中', itemStyle: { color: '#409eff' } }
              ]
            }
          ]
        });
        console.log('状态分布图表选项已更新');
        
        // 使用图表实例更新图表
        this.$nextTick(() => {
          if (this.charts.executionCount) {
            this.charts.executionCount.setOption(this.executionCountOption);
          }
          if (this.charts.successRate) {
            this.charts.successRate.setOption(this.successRateOption);
          }
          if (this.charts.executionTime) {
            this.charts.executionTime.setOption(this.executionTimeOption);
          }
          if (this.charts.statusDistribution) {
            this.charts.statusDistribution.setOption(this.statusDistributionOption);
          }
          console.log('所有图表已通过实例更新');
        });
      } catch (error) {
        console.error('更新图表时发生错误:', error);
        this.$message.error('更新图表失败: ' + error.message);
      }
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
