<template>
  <div class="alert-history-container">
    <div class="page-header">
      <div class="title-area">
        <h1>告警历史</h1>
        <el-tag v-if="configId" type="info" class="filter-tag">
          {{ configName ? `告警: ${configName}` : `配置ID: ${configId}` }}
          <i class="el-icon-close remove-filter" @click="clearConfigFilter"></i>
        </el-tag>
      </div>
      <el-button @click="backToAlerts">返回告警配置</el-button>
    </div>

    <el-table
      v-loading="loading"
      :data="histories"
      stripe
      style="width: 100%; margin-top: 20px"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column label="告警配置" min-width="180">
        <template slot-scope="scope">
          <el-link 
            type="primary" 
            @click="navigateToConfig(scope.row.alert_config_id)"
          >
            {{ scope.row.alert_name || `告警配置 #${scope.row.alert_config_id}` }}
          </el-link>
        </template>
      </el-table-column>
      <el-table-column label="执行记录" min-width="180">
        <template slot-scope="scope">
          <el-link 
            type="primary" 
            @click="viewExecution(scope.row.execution_id)"
          >
            {{ getExecutionName(scope.row) }}
          </el-link>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template slot-scope="scope">
          <el-tag :type="scope.row.status === 'sent' ? 'success' : 'danger'">
            {{ scope.row.status === 'sent' ? '已发送' : '发送失败' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="sent_at" label="发送时间" width="180" />
      <el-table-column prop="message" label="消息" min-width="240" show-overflow-tooltip />
    </el-table>

    <div class="pagination-container">
      <el-pagination
        :current-page="currentPage"
        :page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'AlertHistoryView',
  data() {
    return {
      // 分页参数
      currentPage: 1,
      pageSize: 20,
      total: 0,
      
      // 数据和状态
      histories: [],
      loading: false,
      configId: null,
      configName: ''
    }
  },
  created() {
    // 从路由参数获取过滤条件
    const queryConfigId = this.$route.query.config_id
    if (queryConfigId) {
      this.configId = parseInt(queryConfigId)
      
      // 加载配置名称
      this.loadConfigName()
    }
    
    this.loadHistories()
  },
  methods: {
    // 加载告警历史记录
    async loadHistories() {
      this.loading = true
      
      try {
        // 计算偏移量
        const offset = (this.currentPage - 1) * this.pageSize
        
        // 构建请求URL
        let url = `/api/alert/history?limit=${this.pageSize}&offset=${offset}`
        
        if (this.configId) {
          url += `&config_id=${this.configId}`
        }
        
        const response = await axios.get(url)
        
        if (response.data.code === 0) {
          this.histories = response.data.data
          
          // 假设API返回总条数，如果没有，则使用当前结果数量
          this.total = response.data.total || this.histories.length
        } else {
          this.$message.error(response.data.message || '获取告警历史记录失败')
        }
      } catch (error) {
        console.error('加载告警历史记录失败:', error)
        this.$message.error('加载告警历史记录失败: ' + error.message)
      } finally {
        this.loading = false
      }
    },
    
    // 加载配置名称
    async loadConfigName() {
      if (!this.configId) return
      
      try {
        const response = await axios.get(`/api/alert/config/${this.configId}`)
        
        if (response.data.code === 0 && response.data.data) {
          this.configName = response.data.data.name
        }
      } catch (error) {
        console.error('加载告警配置信息失败:', error)
      }
    },
    
    // 页面大小改变回调
    handleSizeChange(newSize) {
      this.pageSize = newSize
      this.loadHistories()
    },
    
    // 页码改变回调
    handleCurrentChange(newPage) {
      this.currentPage = newPage
      this.loadHistories()
    },
    
    // 清除配置过滤器
    clearConfigFilter() {
      this.configId = null
      this.configName = ''
      
      // 更新URL参数
      this.$router.replace({
        path: this.$route.path
      })
      
      // 重新加载数据
      this.loadHistories()
    },
    
    // 返回告警配置列表
    backToAlerts() {
      this.$router.push('/alerts')
    },
    
    // 导航到配置详情
    navigateToConfig(id) {
      if (!id) return
      
      // 在当前页面设置过滤器
      this.configId = id
      this.currentPage = 1
      
      // 更新URL参数
      this.$router.replace({
        path: this.$route.path,
        query: { config_id: id }
      })
      
      // 加载配置名称
      this.loadConfigName()
      
      // 重新加载数据
      this.loadHistories()
    },
    
    // 查看执行记录
    viewExecution(id) {
      if (!id) return
      
      this.$router.push(`/history/${id}`)
    },
    
    // 获取执行记录名称
    getExecutionName(record) {
      if (record.script_name) {
        return `脚本: ${record.script_name}`
      } else if (record.chain_name) {
        return `脚本链: ${record.chain_name}`
      } else {
        return `执行记录 #${record.execution_id}`
      }
    }
  }
}
</script>

<style scoped>
.alert-history-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.title-area {
  display: flex;
  align-items: center;
}

.filter-tag {
  margin-left: 15px;
}

.remove-filter {
  cursor: pointer;
  margin-left: 5px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
