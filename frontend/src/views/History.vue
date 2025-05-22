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
        <search-bar 
          placeholder="搜索执行历史(ID、名称)" 
          :initial-search-form="searchForm"
          @search="handleSearch"
          @reset="resetSearch"
        >
          <template v-slot:advanced-fields>
            <el-form-item label="执行类型">
              <el-select v-model="searchForm.execType" clearable placeholder="选择执行类型">
                <el-option label="脚本" value="script"></el-option>
                <el-option label="脚本链" value="chain"></el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="执行状态">
              <el-select v-model="searchForm.status" clearable placeholder="选择执行状态">
                <el-option label="执行中" value="running"></el-option>
                <el-option label="已完成" value="completed"></el-option>
                <el-option label="失败" value="failed"></el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="执行时间">
              <el-date-picker
                v-model="searchForm.dateRange"
                type="datetimerange"
                range-separator="至"
                start-placeholder="开始时间"
                end-placeholder="结束时间"
                value-format="yyyy-MM-dd HH:mm:ss"
              ></el-date-picker>
            </el-form-item>
          </template>
        </search-bar>

        <el-table
          v-loading="loading"
          :data="filteredHistories"
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
import SearchBar from '@/components/SearchBar.vue';

export default {
  name: 'History',
  components: {
    HistoryStatistics,
    ScriptExecutionTimeChart,
    ChainExecutionTimeChart,
    ScriptCountChart,
    SearchBar
  },
  data() {
    return {
      currentView: 'list', // 默认显示列表视图
      searchForm: {
        keyword: '',
        execType: '',
        status: '',
        dateRange: []
      }
    };
  },
  computed: {
    ...mapState(['histories', 'loading']),
    filteredHistories() {
      if (!this.histories) return [];
      
      return this.histories.filter(history => {
        // 关键词搜索
        const keyword = this.searchForm.keyword.toLowerCase();
        if (keyword) {
          const id = String(history.id);
          const scriptName = (history.script_name || '').toLowerCase();
          const chainName = (history.chain_name || '').toLowerCase();
          
          if (!id.includes(keyword) && 
              !scriptName.includes(keyword) && 
              !chainName.includes(keyword)) {
            return false;
          }
        }
        
        // 执行类型过滤
        if (this.searchForm.execType) {
          if (this.searchForm.execType === 'script' && !history.script_id) {
            return false;
          }
          if (this.searchForm.execType === 'chain' && !history.chain_id) {
            return false;
          }
        }
        
        // 状态过滤
        if (this.searchForm.status && history.status !== this.searchForm.status) {
          return false;
        }
        
        // 日期范围过滤
        if (this.searchForm.dateRange && this.searchForm.dateRange.length === 2) {
          const startDate = new Date(this.searchForm.dateRange[0]);
          const endDate = new Date(this.searchForm.dateRange[1]);
          const historyDate = new Date(history.start_time);
          
          if (historyDate < startDate || historyDate > endDate) {
            return false;
          }
        }
        
        return true;
      });
    }
  },
  created() {
    this.fetchData();
  },
  methods: {
    fetchData() {
      this.$store.dispatch('fetchHistories');
    },
    handleSearch(formData) {
      this.searchForm = { ...formData };
    },
    resetSearch() {
      this.searchForm = {
        keyword: '',
        execType: '',
        status: '',
        dateRange: []
      };
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
