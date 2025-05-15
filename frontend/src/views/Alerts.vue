<template>
  <div class="alerts-container">
    <div class="page-header">
      <h1>告警配置</h1>
      <el-button type="primary" @click="openAlertForm()">添加告警</el-button>
    </div>

    <el-card class="filter-card">
      <div class="filter-container">
        <el-radio-group v-model="activeFilter" @change="loadAlertConfigs">
          <el-radio-button :label="null">全部</el-radio-button>
          <el-radio-button :label="1">已启用</el-radio-button>
          <el-radio-button :label="0">已禁用</el-radio-button>
        </el-radio-group>
      </div>
    </el-card>

    <el-table
      v-loading="loading"
      :data="alertConfigs"
      stripe
      style="width: 100%; margin-top: 20px"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="告警名称" min-width="180" />
      <el-table-column prop="alert_type_text" label="告警类型" width="120" />
      <el-table-column label="告警条件" min-width="200">
        <template slot-scope="scope">
          <div>{{ formatCondition(scope.row) }}</div>
        </template>
      </el-table-column>
      <el-table-column label="通知方式" width="120">
        <template slot-scope="scope">
          <div>{{ scope.row.notification_type === 'email' ? '邮件' : '其他' }}</div>
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
            type="primary" 
            plain
            @click="viewHistory(scope.row.id)"
          >
            历史记录
          </el-button>
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
            @click="openAlertForm(scope.row)"
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

    <!-- 告警配置表单对话框 -->
    <el-dialog
      :title="editingAlert.id ? '编辑告警配置' : '添加告警配置'"
      :visible.sync="dialogVisible"
      width="60%"
    >
      <el-form 
        :model="editingAlert" 
        :rules="rules" 
        ref="alertForm" 
        label-width="120px"
      >
        <el-form-item label="告警名称" prop="name">
          <el-input v-model="editingAlert.name" placeholder="请输入告警名称" />
        </el-form-item>
        
        <el-form-item label="告警类型" prop="alert_type">
          <el-select v-model="editingAlert.alert_type" placeholder="请选择告警类型" style="width: 100%">
            <el-option label="脚本执行失败" value="script_failed" />
            <el-option label="脚本执行超时" value="script_timeout" />
            <el-option label="链式任务失败" value="chain_failed" />
            <el-option label="系统资源告警" value="system_resource" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="告警条件" required>
          <el-row :gutter="10">
            <el-col :span="8">
              <el-form-item prop="condition_type">
                <el-select v-model="editingAlert.condition_type" placeholder="条件类型" style="width: 100%">
                  <el-option label="连续次数" value="consecutive_count" />
                  <el-option label="CPU使用率" value="cpu_usage" v-if="editingAlert.alert_type === 'system_resource'" />
                  <el-option label="内存使用率" value="memory_usage" v-if="editingAlert.alert_type === 'system_resource'" />
                  <el-option label="磁盘使用率" value="disk_usage" v-if="editingAlert.alert_type === 'system_resource'" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="16">
              <el-form-item prop="condition_value">
                <el-input v-model="editingAlert.condition_value" placeholder="条件值">
                  <template slot="append" v-if="editingAlert.condition_type && editingAlert.condition_type.includes('usage')">%</template>
                  <template slot="append" v-else>次</template>
                </el-input>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form-item>
        
        <el-form-item label="通知方式" prop="notification_type">
          <el-select v-model="editingAlert.notification_type" placeholder="请选择通知方式" style="width: 100%">
            <el-option label="邮件通知" value="email" />
          </el-select>
        </el-form-item>
        
        <el-form-item 
          label="收件人" 
          prop="notification_config.recipients"
          v-if="editingAlert.notification_type === 'email'"
        >
          <el-input 
            v-model="editingAlert.notification_config.recipients" 
            placeholder="多个收件人请用逗号分隔" 
          />
          <div class="hint-text">多个收件人请用逗号分隔</div>
        </el-form-item>
        
        <el-form-item 
          label="SMTP服务器" 
          prop="notification_config.smtp_server"
          v-if="editingAlert.notification_type === 'email'"
        >
          <el-input v-model="editingAlert.notification_config.smtp_server" placeholder="例如: smtp.example.com" />
        </el-form-item>
        
        <el-form-item 
          label="SMTP端口" 
          prop="notification_config.smtp_port"
          v-if="editingAlert.notification_type === 'email'"
        >
          <el-input-number v-model="editingAlert.notification_config.smtp_port" :min="1" :max="65535" />
        </el-form-item>
        
        <el-form-item 
          label="SMTP用户名" 
          prop="notification_config.username"
          v-if="editingAlert.notification_type === 'email'"
        >
          <el-input v-model="editingAlert.notification_config.username" placeholder="例如: user@example.com" />
        </el-form-item>
        
        <el-form-item 
          label="SMTP密码" 
          prop="notification_config.password"
          v-if="editingAlert.notification_type === 'email'"
        >
          <el-input 
            v-model="editingAlert.notification_config.password"
            placeholder="SMTP密码" 
            show-password
          />
        </el-form-item>
        
        <el-form-item 
          label="发件人" 
          prop="notification_config.sender"
          v-if="editingAlert.notification_type === 'email'"
        >
          <el-input v-model="editingAlert.notification_config.sender" placeholder="例如: Script Platform <noreply@example.com>" />
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="editingAlert.description" 
            type="textarea" 
            :rows="3" 
            placeholder="请输入告警配置描述"
          />
        </el-form-item>
        
        <el-form-item label="状态" v-if="editingAlert.id">
          <el-switch
            v-model="editingAlert.is_active"
            :active-value="1"
            :inactive-value="0"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>
      </el-form>
      
      <div class="dialog-footer" v-if="editingAlert.notification_type === 'email'">
        <el-button 
          type="primary" 
          plain
          @click="testEmail" 
          :loading="testingEmail"
        >
          测试邮件配置
        </el-button>
      </div>
      
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveAlertConfig" :loading="saving">
          保存
        </el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'AlertsView',
  data() {
    return {
      alertConfigs: [],
      loading: false,
      dialogVisible: false,
      activeFilter: null,
      saving: false,
      testingEmail: false,
      
      editingAlert: {
        id: null,
        name: '',
        description: '',
        alert_type: '',
        condition_type: '',
        condition_value: '',
        notification_type: 'email',
        notification_config: {
          smtp_server: '',
          smtp_port: 587,
          username: '',
          password: '',
          sender: '',
          recipients: ''
        },
        is_active: 1
      },
      
      rules: {
        name: [{ required: true, message: '请输入告警名称', trigger: 'blur' }],
        alert_type: [{ required: true, message: '请选择告警类型', trigger: 'change' }],
        condition_type: [{ required: true, message: '请选择条件类型', trigger: 'change' }],
        condition_value: [{ required: true, message: '请输入条件值', trigger: 'blur' }],
        notification_type: [{ required: true, message: '请选择通知方式', trigger: 'change' }],
        'notification_config.smtp_server': [
          { required: true, message: '请输入SMTP服务器', trigger: 'blur' }
        ],
        'notification_config.smtp_port': [
          { required: true, message: '请输入SMTP端口', trigger: 'blur' }
        ],
        'notification_config.username': [
          { required: true, message: '请输入SMTP用户名', trigger: 'blur' }
        ],
        'notification_config.password': [
          { required: true, message: '请输入SMTP密码', trigger: 'blur' }
        ],
        'notification_config.sender': [
          { required: true, message: '请输入发件人', trigger: 'blur' }
        ],
        'notification_config.recipients': [
          { required: true, message: '请输入收件人', trigger: 'blur' }
        ]
      }
    }
  },
  created() {
    this.loadAlertConfigs()
  },
  methods: {
    async loadAlertConfigs() {
      this.loading = true
      try {
        let url = '/api/alert/config'
        if (this.activeFilter !== null) {
          url += `?is_active=${this.activeFilter}`
        }
        const response = await axios.get(url)
        if (response.data.code === 0) {
          this.alertConfigs = response.data.data.map(config => ({
            ...config,
            alert_type_text: this.getAlertTypeText(config.alert_type)
          }))
        } else {
          this.$message.error(response.data.message || '获取告警配置列表失败')
        }
      } catch (error) {
        console.error('加载告警配置失败:', error)
        this.$message.error('加载告警配置失败: ' + error.message)
      } finally {
        this.loading = false
      }
    },

    getAlertTypeText(type) {
      const map = {
        'script_failed': '脚本执行失败',
        'script_timeout': '脚本执行超时',
        'chain_failed': '链式任务失败',
        'system_resource': '系统资源告警'
      }
      return map[type] || type
    },

    formatCondition(config) {
      if (!config.condition_type || !config.condition_value) {
        return '未设置'
      }

      const conditionTypeMap = {
        'consecutive_count': '连续',
        'cpu_usage': 'CPU使用率 >',
        'memory_usage': '内存使用率 >',
        'disk_usage': '磁盘使用率 >'
      }

      const unit = config.condition_type.includes('usage') ? '%' : '次'
      return `${conditionTypeMap[config.condition_type] || config.condition_type} ${config.condition_value}${unit}`
    },

    openAlertForm(alert = null) {
      this.resetForm()
      
      if (alert) {
        Object.keys(this.editingAlert).forEach(key => {
          if (key === 'notification_config' && alert[key]) {
            try {
              // 解析通知配置
              const config = typeof alert[key] === 'string' 
                ? JSON.parse(alert[key]) 
                : alert[key]
              
              // 确保所有属性都存在
              this.editingAlert[key] = {
                smtp_server: '',
                smtp_port: 587,
                username: '',
                password: '',
                sender: '',
                recipients: '',
                ...config
              }
            } catch (e) {
              console.error('解析通知配置失败:', e)
              this.editingAlert[key] = {
                smtp_server: '',
                smtp_port: 587,
                username: '',
                password: '',
                sender: '',
                recipients: ''
              }
            }
          } else if (alert[key] !== undefined) {
            this.editingAlert[key] = alert[key]
          }
        })
      }
      
      this.dialogVisible = true
    },

    resetForm() {
      this.editingAlert = {
        id: null,
        name: '',
        description: '',
        alert_type: '',
        condition_type: '',
        condition_value: '',
        notification_type: 'email',
        notification_config: {
          smtp_server: '',
          smtp_port: 587,
          username: '',
          password: '',
          sender: '',
          recipients: ''
        },
        is_active: 1
      }
      
      if (this.$refs.alertForm) {
        this.$refs.alertForm.resetFields()
      }
    },

    async saveAlertConfig() {
      if (!this.$refs.alertForm) return
      
      this.$refs.alertForm.validate(async (valid) => {
        if (!valid) return
        
        this.saving = true
        
        try {
          // 准备要发送的数据
          const alertData = { ...this.editingAlert }
          
          // 确保notification_config是字符串
          if (typeof alertData.notification_config === 'object') {
            alertData.notification_config = JSON.stringify(alertData.notification_config)
          }
          
          let response
          
          if (this.editingAlert.id) {
            // 更新现有配置
            response = await axios.put(`/api/alert/config/${this.editingAlert.id}`, alertData)
          } else {
            // 创建新配置
            response = await axios.post('/api/alert/config', alertData)
          }
          
          if (response.data.code === 0) {
            this.$message.success(response.data.message || '保存告警配置成功')
            this.dialogVisible = false
            this.loadAlertConfigs()
          } else {
            this.$message.error(response.data.message || '保存告警配置失败')
          }
        } catch (error) {
          console.error('保存告警配置失败:', error)
          this.$message.error('保存告警配置失败: ' + error.message)
        } finally {
          this.saving = false
        }
      })
    },

    async testEmail() {
      if (!this.editingAlert.notification_config) return
      
      const config = this.editingAlert.notification_config
      
      // 验证必填字段
      if (!config.smtp_server || !config.smtp_port || !config.username || 
          !config.password || !config.sender || !config.recipients) {
        this.$message.warning('请填写完整的邮件配置信息')
        return
      }
      
      this.testingEmail = true
      
      try {
        const response = await axios.post('/api/alert/test-email', {
          smtp_server: config.smtp_server,
          smtp_port: config.smtp_port,
          username: config.username,
          password: config.password,
          sender: config.sender,
          recipients: config.recipients
        })
        
        if (response.data.code === 0) {
          this.$message.success('测试邮件发送成功，请检查收件箱')
        } else {
          this.$message.error(response.data.message || '测试邮件发送失败')
        }
      } catch (error) {
        console.error('测试邮件发送失败:', error)
        const errorMsg = error.response && error.response.data && error.response.data.message 
          ? error.response.data.message 
          : error.message;
        this.$message.error('测试邮件发送失败: ' + errorMsg);
      } finally {
        this.testingEmail = false
      }
    },

    async toggleActive(alert) {
      try {
        const newStatus = alert.is_active ? 0 : 1
        const response = await axios.put(`/api/alert/config/${alert.id}/active`, {
          is_active: newStatus
        })
        
        if (response.data.code === 0) {
          this.$message.success(response.data.message || `告警配置${newStatus ? '启用' : '禁用'}成功`)
          this.loadAlertConfigs()
        } else {
          this.$message.error(response.data.message || '操作失败')
        }
      } catch (error) {
        console.error('切换告警状态失败:', error)
        this.$message.error('操作失败: ' + error.message)
      }
    },

    confirmDelete(alert) {
      this.$confirm(
        `确定要删除告警配置 "${alert.name}" 吗？删除后将无法恢复。`,
        '删除确认',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(async () => {
        try {
          const response = await axios.delete(`/api/alert/config/${alert.id}`)
          
          if (response.data.code === 0) {
            this.$message.success('删除告警配置成功')
            this.loadAlertConfigs()
          } else {
            this.$message.error(response.data.message || '删除告警配置失败')
          }
        } catch (error) {
          console.error('删除告警配置失败:', error)
          this.$message.error('删除告警配置失败: ' + error.message)
        }
      }).catch(() => {})
    },

    viewHistory(configId) {
      this.$router.push(`/alert/history?config_id=${configId}`)
    }
  }
}
</script>

<style scoped>
.alerts-container {
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

.dialog-footer {
  margin-top: 20px;
  text-align: right;
}

.hint-text {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}
</style>
