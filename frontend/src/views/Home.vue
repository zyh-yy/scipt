<template>
  <div class="home">
    <div class="page-container">
      <h1 class="page-title">脚本管控平台</h1>
      
      <!-- 状态统计卡片 -->
      <execution-status-card />
      
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card class="dashboard-card">
            <div slot="header" class="card-header">
              <span><i class="el-icon-document"></i> 脚本管理</span>
              <el-button
                type="text"
                @click="$router.push('/scripts')"
              >查看全部</el-button>
            </div>
            <div class="card-body">
              <el-empty v-if="!scripts.length" description="暂无脚本"></el-empty>
              <ul v-else class="dashboard-list">
                <li v-for="script in scripts.slice(0, 5)" :key="script.id">
                  <router-link :to="`/scripts/${script.id}`">{{ script.name }}</router-link>
                  <span class="time">{{ formatTime(script.created_at) }}</span>
                </li>
              </ul>
            </div>
            <div class="card-footer">
              <el-button type="primary" size="small" @click="$router.push('/scripts/add')">
                <i class="el-icon-plus"></i> 添加脚本
              </el-button>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card class="dashboard-card">
            <div slot="header" class="card-header">
              <span><i class="el-icon-share"></i> 脚本链管理</span>
              <el-button
                type="text"
                @click="$router.push('/chains')"
              >查看全部</el-button>
            </div>
            <div class="card-body">
              <el-empty v-if="!chains.length" description="暂无脚本链"></el-empty>
              <ul v-else class="dashboard-list">
                <li v-for="chain in chains.slice(0, 5)" :key="chain.id">
                  <router-link :to="`/chains/${chain.id}`">{{ chain.name }}</router-link>
                  <span class="time">{{ formatTime(chain.created_at) }}</span>
                </li>
              </ul>
            </div>
            <div class="card-footer">
              <el-button type="primary" size="small" @click="$router.push('/chains/add')">
                <i class="el-icon-plus"></i> 添加脚本链
              </el-button>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card class="dashboard-card">
            <div slot="header" class="card-header">
              <span><i class="el-icon-time"></i> 执行历史</span>
              <el-button
                type="text"
                @click="$router.push('/history')"
              >查看全部</el-button>
            </div>
            <div class="card-body">
              <el-empty v-if="!histories.length" description="暂无执行历史"></el-empty>
              <ul v-else class="dashboard-list">
                <li v-for="history in histories.slice(0, 5)" :key="history.id">
                  <router-link :to="`/history/${history.id}`">
                    {{ history.script_name || history.chain_name || '未知任务' }}
                  </router-link>
                  <el-tag size="mini" :type="getStatusType(history.status)">
                    {{ getStatusText(history.status) }}
                  </el-tag>
                  <span class="time">{{ formatTime(history.start_time) }}</span>
                </li>
              </ul>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <div class="system-info">
        <h2>系统信息</h2>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="系统名称">脚本管控平台</el-descriptions-item>
          <el-descriptions-item label="版本">1.0.0</el-descriptions-item>
          <el-descriptions-item label="前端框架">Vue.js</el-descriptions-item>
          <el-descriptions-item label="后端框架">Flask</el-descriptions-item>
          <el-descriptions-item label="数据库">SQLite</el-descriptions-item>
          <el-descriptions-item label="支持脚本类型">
            <el-tag size="mini" type="primary">Python</el-tag>
            <el-tag size="mini" type="success">Shell</el-tag>
            <el-tag size="mini" type="warning">Batch</el-tag>
            <el-tag size="mini" type="danger">PowerShell</el-tag>
            <el-tag size="mini" type="info">JavaScript</el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import ExecutionStatusCard from '@/components/ExecutionStatusCard.vue';

export default {
  name: 'Home',
  components: {
    ExecutionStatusCard
  },
  computed: {
    ...mapState(['scripts', 'chains', 'histories', 'loading'])
  },
  created() {
    this.fetchData();
  },
  methods: {
    fetchData() {
      this.$store.dispatch('fetchScripts');
      this.$store.dispatch('fetchChains');
      this.$store.dispatch('fetchHistories');
    },
    formatTime(time) {
      if (!time) return '-';
      const date = new Date(time);
      return date.toLocaleString();
    },
    getStatusType(status) {
      switch (status) {
        case 'completed':
          return 'success';
        case 'failed':
          return 'danger';
        case 'running':
          return 'warning';
        default:
          return 'info';
      }
    },
    getStatusText(status) {
      switch (status) {
        case 'completed':
          return '成功';
        case 'failed':
          return '失败';
        case 'running':
          return '执行中';
        default:
          return '未知';
      }
    }
  }
};
</script>

<style lang="scss" scoped>
.dashboard-card {
  margin-bottom: 20px;
  height: 350px;
  display: flex;
  flex-direction: column;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .card-body {
    flex: 1;
    overflow-y: auto;
  }
}

.dashboard-list {
  list-style: none;
  padding: 0;
  
  li {
    padding: 10px 0;
    border-bottom: 1px solid #ebeef5;
    display: flex;
    align-items: center;
    
    &:last-child {
      border-bottom: none;
    }
    
    a {
      color: #3a84ff;
      text-decoration: none;
      flex: 1;
      
      &:hover {
        text-decoration: underline;
      }
    }
    
    .el-tag {
      margin: 0 10px;
    }
    
    .time {
      color: #909399;
      font-size: 12px;
    }
  }
}

.system-info {
  margin-top: 20px;
  
  h2 {
    font-size: 18px;
    margin-bottom: 15px;
  }
  
  .el-tag {
    margin-right: 5px;
  }
}
</style>
