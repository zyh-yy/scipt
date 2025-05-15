<template>
  <div class="script-count-chart">
    <el-card class="chart-card" v-loading="loading">
      <div slot="header" class="card-header">
        <h3>脚本数量变化</h3>
        <el-select 
          v-model="timeRange" 
          size="small" 
          @change="fetchData"
        >
          <el-option label="最近30天" value="30"></el-option>
          <el-option label="最近90天" value="90"></el-option>
          <el-option label="最近半年" value="180"></el-option>
          <el-option label="最近一年" value="365"></el-option>
        </el-select>
      </div>
      <v-chart class="chart" :option="chartOption" autoresize />
    </el-card>
  </div>
</template>

<script>
import axios from 'axios';
import VChart from 'vue-echarts';

export default {
  name: 'ScriptCountChart',
  components: {
    VChart
  },
  data() {
    return {
      loading: false,
      timeRange: '90',
      chartOption: {
        title: {
          text: '脚本数量变化',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        legend: {
          data: ['新增脚本', '累计脚本'],
          bottom: 10
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          top: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: [],
          axisLabel: {
            rotate: 45
          }
        },
        yAxis: [
          {
            type: 'value',
            name: '新增数量',
            position: 'left',
            axisLine: {
              lineStyle: {
                color: '#E6A23C'
              }
            },
            axisLabel: {
              formatter: '{value}'
            }
          },
          {
            type: 'value',
            name: '累计数量',
            position: 'right',
            axisLine: {
              lineStyle: {
                color: '#409EFF'
              }
            },
            axisLabel: {
              formatter: '{value}'
            }
          }
        ],
        series: [
          {
            name: '新增脚本',
            type: 'bar',
            data: [],
            itemStyle: {
              color: '#E6A23C'
            }
          },
          {
            name: '累计脚本',
            type: 'line',
            yAxisIndex: 1,
            data: [],
            symbol: 'circle',
            symbolSize: 8,
            itemStyle: {
              color: '#409EFF'
            },
            lineStyle: {
              width: 3
            }
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
        
        // 获取脚本列表
        const response = await axios.get('/api/scripts');
        
        if (response.data.code === 0) {
          this.processData(response.data.data);
        } else {
          this.$message.error(response.data.message || '获取脚本数据失败');
        }
      } catch (error) {
        this.$message.error('获取脚本数据失败: ' + error.message);
      } finally {
        this.loading = false;
      }
    },
    processData(scripts) {
      if (!scripts || !scripts.length) {
        return;
      }
      
      // 先解析创建时间，并按时间排序
      const scriptsWithTime = scripts.map(script => {
        return {
          ...script,
          created_time: new Date(script.created_at)
        };
      }).sort((a, b) => a.created_time - b.created_time);
      
      // 确定日期范围和间隔
      const days = parseInt(this.timeRange);
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(endDate.getDate() - days);
      
      // 决定日期分组方式
      let interval = 'day';
      let format = 'MM-DD';
      
      if (days > 120) {
        interval = 'week';
        format = 'yyyy-MM-DD';
      } else if (days > 60) {
        interval = 'week';
        format = 'MM-DD';
      }
      
      // 根据间隔创建日期分组
      const dateGroups = [];
      const currentDate = new Date(startDate);
      
      while (currentDate <= endDate) {
        const dateKey = this.formatDate(currentDate, format);
        dateGroups.push({
          date: new Date(currentDate),
          dateKey,
          count: 0
        });
        
        // 根据间隔增加日期
        if (interval === 'day') {
          currentDate.setDate(currentDate.getDate() + 1);
        } else if (interval === 'week') {
          currentDate.setDate(currentDate.getDate() + 7);
        }
      }
      
      // 统计每个时间段内的新增脚本数量
      scriptsWithTime.forEach(script => {
        if (script.created_time >= startDate && script.created_time <= endDate) {
          // 找到脚本创建时间对应的日期组
          for (let i = 0; i < dateGroups.length; i++) {
            // 如果是最后一个组或者创建时间小于下一个组的日期，则计入当前组
            if (i === dateGroups.length - 1 || script.created_time < dateGroups[i + 1].date) {
              dateGroups[i].count++;
              break;
            }
          }
        }
      });
      
      // 处理累计数
      let totalCount = scriptsWithTime.filter(s => s.created_time < startDate).length;
      const cumulativeCounts = [];
      
      dateGroups.forEach(group => {
        totalCount += group.count;
        cumulativeCounts.push(totalCount);
      });
      
      // 更新图表数据
      this.chartOption.xAxis.data = dateGroups.map(g => g.dateKey);
      this.chartOption.series[0].data = dateGroups.map(g => g.count);
      this.chartOption.series[1].data = cumulativeCounts;
      
      // 更新标题
      this.chartOption.title.text = `脚本数量变化 (${this.formatDate(startDate, 'yyyy-MM-dd')} 至 ${this.formatDate(endDate, 'yyyy-MM-dd')})`;
    },
    formatDate(date, format = 'yyyy-MM-dd') {
      const year = date.getFullYear();
      const month = (date.getMonth() + 1).toString().padStart(2, '0');
      const day = date.getDate().toString().padStart(2, '0');
      
      if (format === 'yyyy-MM-dd') {
        return `${year}-${month}-${day}`;
      } else if (format === 'MM-DD') {
        return `${month}-${day}`;
      } else if (format === 'yyyy-MM') {
        return `${year}-${month}`;
      }
      
      return `${year}-${month}-${day}`;
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
    margin-top: 10px;
  }
}
</style>
