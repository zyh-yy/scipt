<template>
  <div class="history-detail">
    <div class="page-container" v-loading="loading">
      <div class="page-header">
        <h1 class="page-title">执行详情</h1>
        <div class="button-container">
          <el-button @click="$router.push('/history')">
            <i class="el-icon-back"></i> 返回列表
          </el-button>
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

export default {
  name: 'HistoryDetail',
  data() {
    return {
      history: null,
      localLoading: false
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
  methods: {
    async fetchData() {
      // 先从store中查找
      const historyFromStore = this.historyById(this.historyId);
      
      if (historyFromStore) {
        this.history = historyFromStore;
      } else {
        this.localLoading = true;
        try {
          const response = await axios.get(`/api/execution/history/${this.historyId}`);
          if (response.data.code === 0) {
            this.history = response.data.data;
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
}

.error-display {
  background-color: #fef0f0;
  border-color: #fbc4c4;
  color: #f56c6c;
}
</style>
