<template>
  <div class="scheduled-tasks-container">
    <div class="page-header">
      <h1>定时任务</h1>
      <el-button type="primary" @click="openTaskForm()">添加定时任务</el-button>
    </div>

    <el-card class="filter-card">
      <div class="filter-container">
        <el-radio-group v-model="activeFilter" @change="loadTasks">
          <el-radio-button :label="null">全部</el-radio-button>
          <el-radio-button :label="1">已启用</el-radio-button>
          <el-radio-button :label="0">已禁用</el-radio-button>
        </el-radio-group>
      </div>
    </el-card>

    <el-table
      v-loading="loading"
      :data="tasks"
      stripe
      style="width: 100%; margin-top: 20px"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="任务名称" min-width="180" />
      <el-table-column prop="schedule_type" label="调度类型" width="120">
        <template slot-scope="scope">
          {{ getScheduleTypeText(scope.row.schedule_type) }}
        </template>
      </el-table-column>
      <el-table-column prop="cron_expression" label="Cron表达式" min-width="180" />
      <el-table-column label="执行对象" min-width="180">
        <template slot-scope="scope">
          <div v-if="scope.row.script_id">
            <el-link type="primary" @click="viewScript(scope.row.script_id)">
              脚本: {{ scope.row.script_name || `#${scope.row.script_id}` }}
            </el-link>
          </div>
          <div v-else-if="scope.row.chain_id">
            <el-link type="primary" @click="viewChain(scope.row.chain_id)">
              脚本链: {{ scope.row.chain_name || `#${scope.row.chain_id}` }}
            </el-link>
          </div>
          <div v-else>未设置</div>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template slot-scope="scope">
          <el-tag :type="scope.row.is_active ? 'success' : 'info'">
            {{ scope.row.is_active ? '已启用' : '已禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="240">
        <template slot-scope="scope">
          <el-button 
            size="small"
            type="success" 
            plain
            @click="toggleActive(scope.row)"
          >
            {{ scope.row.is_active ? '禁用' : '启用' }}
          </el-button>
          <el-button 
            size="small"
            type="warning" 
            plain
            @click="openTaskForm(scope.row)"
          >
            编辑
          </el-button>
          <el-button 
            size="small"
            type="danger" 
            plain
            @click="confirmDelete(scope.row)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 任务表单对话框 -->
    <el-dialog
      :title="editingTask.id ? '编辑定时任务' : '添加定时任务'"
      :visible.sync="dialogVisible"
      width="60%"
    >
      <el-form 
        :model="editingTask" 
        :rules="rules" 
        ref="taskForm" 
        label-width="120px"
      >
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="editingTask.name" placeholder="请输入任务名称" />
        </el-form-item>
        
        <el-form-item label="执行对象" prop="execution_target">
          <el-radio-group v-model="executionTarget" @change="handleTargetChange">
            <el-radio label="script">脚本</el-radio>
            <el-radio label="chain">脚本链</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item 
          label="选择脚本" 
          prop="script_id" 
          v-if="executionTarget === 'script'"
        >
          <el-select 
            v-model="editingTask.script_id" 
            filterable 
            placeholder="请选择脚本"
            style="width: 100%"
          >
            <el-option 
              v-for="script in scripts" 
              :key="script.id" 
              :label="`${script.name} (${script.language})`" 
              :value="script.id" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item 
          label="选择脚本链" 
          prop="chain_id" 
          v-if="executionTarget === 'chain'"
        >
          <el-select 
            v-model="editingTask.chain_id" 
            filterable 
            placeholder="请选择脚本链"
            style="width: 100%"
          >
            <el-option 
              v-for="chain in chains" 
              :key="chain.id" 
              :label="chain.name" 
              :value="chain.id" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="调度类型" prop="schedule_type">
          <el-select v-model="editingTask.schedule_type" placeholder="请选择调度类型" style="width: 100%">
            <el-option label="Cron表达式" value="cron" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="Cron表达式" prop="cron_expression">
          <el-input v-model="editingTask.cron_expression" placeholder="例如: 0 0 * * * (每天零点执行)" />
          <div class="hint-text">
            Cron表达式格式: 秒 分 时 日 月 星期<br />
            例如:<br />
            "0 0 * * * *" - 每小时整点执行<br />
            "0 0 0 * * *" - 每天零点执行<br />
            "0 0 0 * * 1" - 每周一零点执行<br />
            "0 0 12 1 * *" - 每月1日中午12点执行
          </div>
        </el-form-item>
        
        <el-form-item label="参数" prop="params">
          <el-input 
            v-model="paramsString" 
            type="textarea" 
            :rows="5" 
            placeholder='请以JSON格式输入参数，例如: {"name": "value"}'
          />
          <div class="hint-text">JSON格式的参数，将传递给脚本或脚本链执行</div>
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="editingTask.description" 
            type="textarea" 
            :rows="3" 
            placeholder="请输入任务描述"
          />
        </el-form-item>
        
        <el-form-item label="状态" v-if="editingTask.id">
          <el-switch
            v-model="editingTask.is_active"
            :active-value="1"
            :inactive-value="0"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>
      </el-form>
      
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveTask" :loading="saving">
          保存
        </el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'ScheduledTasksView',
  data() {
    return {
      tasks: [],
      scripts: [],
      chains: [],
      loading: false,
      dialogVisible: false,
      activeFilter: null,
      saving: false,
      executionTarget: 'script',
      paramsString: '',
      
      editingTask: {
        id: null,
        name: '',
        description: '',
        schedule_type: 'cron',
        cron_expression: '',
        script_id: null,
        chain_id: null,
        params: null,
        is_active: 1
      },
      
      rules: {
        name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
        schedule_type: [{ required: true, message: '请选择调度类型', trigger: 'change' }],
        cron_expression: [{ required: true, message: '请输入Cron表达式', trigger: 'blur' }],
        script_id: [{ 
          required: true, 
          message: '请选择脚本', 
          trigger: 'change',
          validator: (rule, value, callback) => {
            if (this.executionTarget === 'script' && !value) {
              callback(new Error('请选择脚本'))
            } else {
              callback()
            }
          }
        }],
        chain_id: [{ 
          required: true, 
          message: '请选择脚本链', 
          trigger: 'change',
          validator: (rule, value, callback) => {
            if (this.executionTarget === 'chain' && !value) {
              callback(new Error('请选择脚本链'))
            } else {
              callback()
            }
          }
        }]
      }
    }
  },
  watch: {
    paramsString: {
      handler(val) {
        if (val) {
          try {
            this.editingTask.params = JSON.parse(val)
          } catch (e) {
            // 不是有效的JSON，保留字符串
            console.log('参数不是有效的JSON格式')
          }
        } else {
          this.editingTask.params = null
        }
      }
    }
  },
  created() {
    this.loadTasks()
    this.loadScripts()
    this.loadChains()
  },
  methods: {
    async loadTasks() {
      this.loading = true
      try {
        let url = '/api/schedule'
        if (this.activeFilter !== null) {
          url += `?is_active=${this.activeFilter}`
        }
        const response = await axios.get(url)
        if (response.data.code === 0) {
          this.tasks = response.data.data
        } else {
          this.$message.error(response.data.message || '获取定时任务列表失败')
        }
      } catch (error) {
        console.error('加载定时任务失败:', error)
        this.$message.error('加载定时任务失败: ' + error.message)
      } finally {
        this.loading = false
      }
    },
    
    async loadScripts() {
      try {
        const response = await axios.get('/api/scripts')
        if (response.data.code === 0) {
          this.scripts = response.data.data
        }
      } catch (error) {
        console.error('加载脚本列表失败:', error)
      }
    },
    
    async loadChains() {
      try {
        const response = await axios.get('/api/chains')
        if (response.data.code === 0) {
          this.chains = response.data.data
        }
      } catch (error) {
        console.error('加载脚本链列表失败:', error)
      }
    },

    getScheduleTypeText(type) {
      const map = {
        'cron': 'Cron表达式',
        'interval': '时间间隔',
        'date': '指定日期'
      }
      return map[type] || type
    },

    openTaskForm(task = null) {
      this.resetForm()
      
      if (task) {
        Object.assign(this.editingTask, task)
        
        // 设置执行目标
        if (task.script_id) {
          this.executionTarget = 'script'
        } else if (task.chain_id) {
          this.executionTarget = 'chain'
        }
        
        // 将参数对象转为JSON字符串
        if (task.params) {
          if (typeof task.params === 'string') {
            try {
              this.paramsString = JSON.stringify(JSON.parse(task.params), null, 2)
            } catch (e) {
              this.paramsString = task.params
            }
          } else {
            this.paramsString = JSON.stringify(task.params, null, 2)
          }
        } else {
          this.paramsString = ''
        }
      }
      
      this.dialogVisible = true
    },

    resetForm() {
      this.editingTask = {
        id: null,
        name: '',
        description: '',
        schedule_type: 'cron',
        cron_expression: '',
        script_id: null,
        chain_id: null,
        params: null,
        is_active: 1
      }
      
      this.executionTarget = 'script'
      this.paramsString = ''
      
      if (this.$refs.taskForm) {
        this.$refs.taskForm.resetFields()
      }
    },
    
    handleTargetChange(target) {
      if (target === 'script') {
        this.editingTask.chain_id = null
      } else {
        this.editingTask.script_id = null
      }
    },

    async saveTask() {
      if (!this.$refs.taskForm) return
      
      this.$refs.taskForm.validate(async (valid) => {
        if (!valid) return
        
        // 检查执行目标是否已选择
        if (!this.editingTask.script_id && !this.editingTask.chain_id) {
          this.$message.warning('请选择脚本或脚本链')
          return
        }
        
        this.saving = true
        
        try {
          // 准备要发送的数据
          const taskData = { ...this.editingTask }
          
          // 处理参数
          if (this.paramsString) {
            try {
              taskData.params = JSON.parse(this.paramsString)
            } catch (e) {
              this.$message.warning('参数格式不正确，请检查JSON格式')
              this.saving = false
              return
            }
          } else {
            taskData.params = null
          }
          
          let response
          
          if (this.editingTask.id) {
            // 更新现有任务
            response = await axios.put(`/api/schedule/${this.editingTask.id}`, taskData)
          } else {
            // 创建新任务
            response = await axios.post('/api/schedule', taskData)
          }
          
          if (response.data.code === 0) {
            this.$message.success(response.data.message || '保存定时任务成功')
            this.dialogVisible = false
            this.loadTasks()
          } else {
            this.$message.error(response.data.message || '保存定时任务失败')
          }
        } catch (error) {
          console.error('保存定时任务失败:', error)
          this.$message.error('保存定时任务失败: ' + error.message)
        } finally {
          this.saving = false
        }
      })
    },

    async toggleActive(task) {
      try {
        const newStatus = task.is_active ? 0 : 1
        const response = await axios.put(`/api/schedule/${task.id}/active`, {
          is_active: newStatus
        })
        
        if (response.data.code === 0) {
          this.$message.success(response.data.message || `定时任务${newStatus ? '启用' : '禁用'}成功`)
          this.loadTasks()
        } else {
          this.$message.error(response.data.message || '操作失败')
        }
      } catch (error) {
        console.error('切换任务状态失败:', error)
        this.$message.error('操作失败: ' + error.message)
      }
    },

    confirmDelete(task) {
      this.$confirm(
        `确定要删除定时任务 "${task.name}" 吗？删除后将无法恢复。`,
        '删除确认',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(async () => {
        try {
          const response = await axios.delete(`/api/schedule/${task.id}`)
          
          if (response.data.code === 0) {
            this.$message.success('删除定时任务成功')
            this.loadTasks()
          } else {
            this.$message.error(response.data.message || '删除定时任务失败')
          }
        } catch (error) {
          console.error('删除定时任务失败:', error)
          this.$message.error('删除定时任务失败: ' + error.message)
        }
      }).catch(() => {})
    },

    viewScript(scriptId) {
      this.$router.push(`/scripts/${scriptId}`)
    },
    
    viewChain(chainId) {
      this.$router.push(`/chains/${chainId}`)
    }
  }
}
</script>

<style scoped>
.scheduled-tasks-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filter-card {
  margin-bottom: 20px;
}

.filter-container {
  display: flex;
  align-items: center;
}

.hint-text {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}
</style>
