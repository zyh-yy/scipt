<template>
  <div class="history">
    <div class="page-container">
      <div class="page-header">
        <h1 class="page-title">执行历史</h1>
        <div class="view-switch">
          <el-radio-group v-model="currentView" size="small">
            <el-radio-button label="list">列表视图</el-radio-button>
            <el-radio-button label="stats">统计视图</el-radio-button>
          </el-radio-group>
        </div>
      </div>

      <div v-if="currentView === 'stats'">
        <history-statistics />
        
        <el-row :gutter="20" style="margin-top: 20px;">
          <el-col :span="12">
            <script-execution-time-chart />
          </el-col>
          <el-col :span="12">
            <chain-execution-time-chart />
          </el-col>
        </el-row>
        
        <script-count-chart style="margin-top: 20px;" />
      </div>
      
      <div v-else>

        <el-table
          v-loading="loading"
          :data="histories"
          border
          style="width: 100%"
          empty-text="暂无数据"
        >
        <el-table-column prop="id" label="ID" width="80"></el-table-column>
        <el-table-column label="执行类型" width="120">
          <template slot-scope="scope">
            <el-tag type="primary" v-if="scope.row.script_id">脚本</el-tag>
            <el-tag type="success" v-else-if="scope.row.chain_id">脚本链</el-tag>
            <el-tag v-else>未知</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="名称" min-width="150">
          <template slot-scope="scope">
            {{ scope.row.script_name || scope.row.chain_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template slot-scope="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="start_time" label="开始时间" width="180">
          <template slot-scope="scope">
            {{ formatTime(scope.row.start_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="end_time" label="结束时间" width="180">
          <template slot-scope="scope">
            {{ formatTime(scope.row.end_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template slot-scope="scope">
            <el-button
              size="mini"
              type="primary"
              @click="handleView(scope.row)"
            >
              查看详情
            </el-button>
          </template>
        </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex';
import HistoryStatistics from '@/components/HistoryStatistics.vue';
import ScriptExecutionTimeChart from '@/components/ScriptExecutionTimeChart.vue';
import ChainExecutionTimeChart from '@/components/ChainExecutionTimeChart.vue';
import ScriptCountChart from '@/components/ScriptCountChart.vue';

export default {
  name: 'History',
  components: {
    HistoryStatistics,
    ScriptExecutionTimeChart,
    ChainExecutionTimeChart,
    ScriptCountChart
  },
  data() {
    return {
      currentView: 'list' // 默认显示列表视图
    };
  },
  computed: {
    ...mapState(['histories', 'loading'])
  },
  created() {
    this.fetchData();
  },
  methods: {
    fetchData() {
      this.$store.dispatch('fetchHistories');
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
    handleView(row) {
      this.$router.push(`/history/${row.id}`);
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
</style>
