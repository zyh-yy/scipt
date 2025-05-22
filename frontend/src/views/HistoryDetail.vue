<template>
  <div class="history-detail">
    <div class="page-container" v-loading="loading">
      <!-- 添加脚本执行时间变化图表 -->
      <script-execution-time-chart v-if="history && history.script_id" :script-id="history.script_id" />
      <div class="page-header">
        <h1 class="page-title">执行详情</h1>
        <div class="button-container">
          <el-button @click="$router.push('/history')">
            <i class="el-icon-back"></i> 返回列表
          </el-button>
          <!-- 添加轮询控制按钮 -->
          <el-tooltip :content="pollingEnabled ? '停止自动刷新' : '开始自动刷新'" placement="top">
            <el-button 
              type="primary" 
              :icon="pollingEnabled ? 'el-icon-video-pause' : 'el-icon-refresh'"
              @click="togglePolling"
              v-if="history && history.status === 'running'">
              {{ pollingEnabled ? '停止轮询' : '开始轮询' }}
            </el-button>
          </el-tooltip>
          <el-tag v-if="pollingEnabled" type="success">自动刷新: {{ pollingIntervalSeconds }}秒</el-tag>
        </div>
      </div>

      <template v-if="history">
        <el-card class="detail-card">
          <div slot="header" class="card-header">
            <h2>基本信息</h2>
          </div>
          
          <el-descriptions border :column="2">
            <el-descriptions-item label="ID">{{ history.id }}</el-descriptions-item>
            <el-descriptions-item label="类型">
              <el-tag type="primary" v-if="history.script_id">脚本</el-tag>
              <el-tag type="success" v-else-if="history.chain_id">脚本链</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="名称">
              {{ history.script_name || history.chain_name || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="getStatusType(history.status)">
                {{ getStatusText(history.status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="开始时间">{{ formatTime(history.start_time) }}</el-descriptions-item>
            <el-descriptions-item label="结束时间">{{ formatTime(history.end_time) }}</el-descriptions-item>
            <el-descriptions-item label="执行时长" :span="2">
              {{ calculateDuration(history.start_time, history.end_time) }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card class="detail-card" v-if="history.params">
          <div slot="header" class="card-header">
            <h2>执行参数</h2>
          </div>
          
          <pre class="params-display">{{ formatParams(history.params) }}</pre>
        </el-card>

        <el-card class="detail-card" v-if="history.output">
          <div slot="header" class="card-header">
            <h2>执行输出</h2>
          </div>
          
          <pre class="output-display">{{ formatOutput(history.output) }}</pre>
        </el-card>

        <el-card class="detail-card" v-if="history.error">
          <div slot="header" class="card-header">
            <h2>错误信息</h2>
          </div>
          
          <pre class="error-display">{{ history.error }}</pre>
        </el-card>
      </template>

      <el-empty v-else description="未找到执行历史记录"></el-empty>
    </div>
  </div>
</template>

<script>
import { mapState, mapGetters } from 'vuex';
import axios from 'axios';
import ScriptExecutionTimeChart from '@/components/ScriptExecutionTimeChart.vue';

export default {
  name: 'HistoryDetail',
  components: {
    ScriptExecutionTimeChart
  },
  data() {
    return {
      history: null,
      localLoading: false,
      pollingEnabled: false,
      pollingIntervalSeconds: 5,
      pollingTimer: null,
      previousOutput: '',
      newContentMarker: null,
      autoScrollOutput: true
    };
  },
  computed: {
    ...mapState(['loading']),
    ...mapGetters(['historyById']),
    historyId() {
      return parseInt(this.$route.params.id);
    },
    isLoading() {
      return this.loading || this.localLoading;
    }
  },
  created() {
    this.fetchData();
  },
  
  mounted() {
    // 页面挂载后添加监听器，用于自动滚动
    this.$nextTick(() => {
      window.addEventListener('beforeunload', this.cleanup);
    });
  },
  
  beforeDestroy() {
    this.cleanup();
  },
  methods: {
    async fetchData() {
      // 先从store中查找
      const historyFromStore = this.historyById(this.historyId);
      
      if (historyFromStore) {
        this.history = historyFromStore;
        // 如果状态是执行中，自动开始轮询
        if (this.history && this.history.status === 'running') {
          this.startPolling();
        }
      } else {
        this.localLoading = true;
        try {
          const response = await axios.get(`/api/execution/history/${this.historyId}`);
          if (response.data.code === 0) {
            this.history = response.data.data;
            // 保存当前输出以便之后比较
            this.previousOutput = this.history.output || '';
            
            // 如果状态是执行中，自动开始轮询
            if (this.history && this.history.status === 'running') {
              this.startPolling();
            }
          } else {
            this.$message.error(response.data.message || '获取执行历史详情失败');
          }
        } catch (error) {
          this.$message.error('获取执行历史详情失败: ' + error.message);
        } finally {
          this.localLoading = false;
        }
      }
    },
    
    async refreshData() {
      if (!this.historyId) return;
      
      try {
        const response = await axios.get(`/api/execution/history/${this.historyId}`);
        if (response.data.code === 0) {
          const newData = response.data.data;
          
          // 判断是否有新内容
          const hasNewOutput = newData.output && this.history.output !== newData.output;
          
          // 更新历史数据
          this.history = newData;
          
          // 如果脚本执行结束，停止轮询
          if (this.history.status !== 'running' && this.pollingEnabled) {
            this.stopPolling();
            this.$message.success('脚本执行已完成，停止自动刷新');
          }
          
          // 如果有新输出，高亮显示并滚动到底部
          if (hasNewOutput) {
            this.$nextTick(() => {
              // 标记新内容
              this.markNewContent();
              
              // 自动滚动到底部
              if (this.autoScrollOutput) {
                this.scrollToBottom();
              }
            });
          }
          
          // 保存当前输出以便下次比较
          this.previousOutput = this.history.output || '';
        }
      } catch (error) {
        console.error('刷新执行历史详情失败:', error);
        // 如果出现错误，不要立即停止轮询，可能是临时网络问题
      }
    },
    
    startPolling() {
      if (this.pollingTimer) {
        clearInterval(this.pollingTimer);
      }
      
      this.pollingEnabled = true;
      this.pollingTimer = setInterval(this.refreshData, this.pollingIntervalSeconds * 1000);
      this.$message.success(`已开始自动刷新，间隔 ${this.pollingIntervalSeconds} 秒`);
    },
    
    stopPolling() {
      if (this.pollingTimer) {
        clearInterval(this.pollingTimer);
        this.pollingTimer = null;
      }
      this.pollingEnabled = false;
    },
    
    togglePolling() {
      if (this.pollingEnabled) {
        this.stopPolling();
        this.$message.info('已停止自动刷新');
      } else {
        this.startPolling();
      }
    },
    
    scrollToBottom() {
      const outputElement = document.querySelector('.output-display');
      if (outputElement) {
        outputElement.scrollTop = outputElement.scrollHeight;
      }
    },
    
    markNewContent() {
      // 查找新增内容并高亮标记
      if (this.previousOutput && this.history.output) {
        // 先清除之前的标记
        if (this.newContentMarker) {
          clearTimeout(this.newContentMarker);
        }
        
        // 获取输出元素
        const outputElement = document.querySelector('.output-display');
        if (!outputElement) return;
        
        // 为新内容添加高亮样式类
        outputElement.classList.add('has-new-content');
        
        // 设置定时器，5秒后移除高亮效果
        this.newContentMarker = setTimeout(() => {
          outputElement.classList.remove('has-new-content');
        }, 5000);
      }
    },
    
    cleanup() {
      // 清理轮询定时器
      this.stopPolling();
      // 清理内容标记定时器
      if (this.newContentMarker) {
        clearTimeout(this.newContentMarker);
      }
      // 移除事件监听器
      window.removeEventListener('beforeunload', this.cleanup);
    },
    formatTime(time) {
      if (!time) return '-';
      const date = new Date(time);
      return date.toLocaleString();
    },
    getStatusType(status) {
      switch (status) {
        case 'running':
          return 'info';
        case 'completed':
          return 'success';
        case 'failed':
          return 'danger';
        default:
          return 'warning';
      }
    },
    getStatusText(status) {
      switch (status) {
        case 'running':
          return '执行中';
        case 'completed':
          return '已完成';
        case 'failed':
          return '失败';
        default:
          return '未知';
      }
    },
    calculateDuration(start, end) {
      if (!start || !end) return '-';
      
      const startTime = new Date(start).getTime();
      const endTime = new Date(end).getTime();
      
      if (isNaN(startTime) || isNaN(endTime)) return '-';
      
      const durationMs = endTime - startTime;
      if (durationMs < 0) return '-';
      
      // 转换为人类可读格式
      const seconds = Math.floor(durationMs / 1000);
      const minutes = Math.floor(seconds / 60);
      const hours = Math.floor(minutes / 60);
      
      if (hours > 0) {
        return `${hours}小时 ${minutes % 60}分钟 ${seconds % 60}秒`;
      } else if (minutes > 0) {
        return `${minutes}分钟 ${seconds % 60}秒`;
      } else {
        return `${seconds}秒`;
      }
    },
    formatParams(params) {
      if (!params) return '';
      
      try {
        if (typeof params === 'string') {
          params = JSON.parse(params);
        }
        return JSON.stringify(params, null, 2);
      } catch (e) {
        return String(params);
      }
    },
    formatOutput(output) {
      if (!output) return '';
      
      try {
        // 尝试解析JSON
        if (typeof output === 'string' && (output.startsWith('{') || output.startsWith('['))) {
          const parsed = JSON.parse(output);
          return JSON.stringify(parsed, null, 2);
        }
        return output;
      } catch (e) {
        return output;
      }
    }
  }
};
</script>

<style lang="scss" scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  
  .button-container {
    display: flex;
    align-items: center;
    gap: 10px;
  }
}

.detail-card {
  margin-bottom: 20px;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    h2 {
      margin: 0;
      font-size: 18px;
    }
  }
}

.params-display, .output-display, .error-display {
  margin: 0;
  padding: 15px;
  background-color: #f5f7fa;
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow-x: auto;
  max-height: 400px;
  overflow-y: auto;
  transition: background-color 0.3s ease;
}

.output-display.has-new-content {
  background-color: #f0f9eb;
  border-color: #c2e7b0;
  animation: highlight-flash 1s ease;
}

@keyframes highlight-flash {
  0% { background-color: #f0f9eb; }
  50% { background-color: #e1f3d8; }
  100% { background-color: #f0f9eb; }
}

.error-display {
  background-color: #fef0f0;
  border-color: #fbc4c4;
  color: #f56c6c;
}

.auto-scroll-toggle {
  font-size: 12px;
  margin-top: 5px;
  text-align: right;
}
</style>
