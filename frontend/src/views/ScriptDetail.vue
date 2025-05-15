<template>
  <div class="script-detail">
    <div class="page-container" v-loading="loading">
      <div class="page-header">
        <h1 class="page-title">脚本详情</h1>
        <div class="button-container">
          <el-button @click="$router.push('/scripts')">
            <i class="el-icon-back"></i> 返回列表
          </el-button>
        </div>
      </div>
      
      <!-- 脚本执行趋势图表 -->
      <script-execution-trend />
      
      <el-card v-if="script" class="detail-card">
        <div slot="header">
          <span>{{ script.name }}</span>
        </div>
        
        <el-descriptions :column="2" border>
          <el-descriptions-item label="脚本ID">{{ script.id }}</el-descriptions-item>
          <el-descriptions-item label="脚本类型">
            <el-tag :type="getFileTypeTag(script.file_type)">{{ script.file_type }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatTime(script.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatTime(script.updated_at) }}</el-descriptions-item>
          <el-descriptions-item label="脚本描述" :span="2">
            {{ script.description || '暂无描述' }}
          </el-descriptions-item>
          <el-descriptions-item label="文件路径" :span="2">
            {{ script.file_path }}
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="parameters-section" v-if="script.parameters && script.parameters.length">
          <h3>参数列表</h3>
          <el-table :data="script.parameters" border style="width: 100%">
            <el-table-column prop="name" label="参数名称" width="150"></el-table-column>
            <el-table-column prop="description" label="参数描述" min-width="200"></el-table-column>
            <el-table-column prop="param_type" label="参数类型" width="100">
              <template slot-scope="scope">
                {{ getParamTypeText(scope.row.param_type) }}
              </template>
            </el-table-column>
            <el-table-column prop="is_required" label="是否必填" width="100">
              <template slot-scope="scope">
                <el-tag :type="scope.row.is_required ? 'danger' : 'info'">
                  {{ scope.row.is_required ? '必填' : '选填' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="default_value" label="默认值" width="150">
              <template slot-scope="scope">
                {{ scope.row.default_value || '-' }}
              </template>
            </el-table-column>
          </el-table>
        </div>
        <el-empty v-else description="没有配置参数"></el-empty>
      </el-card>
      
      <el-empty v-else description="未找到脚本信息"></el-empty>
    </div>
    
    <!-- 执行脚本对话框 -->
    <el-dialog title="执行脚本" :visible.sync="executeDialogVisible" width="50%">
      <div v-if="script && script.parameters && script.parameters.length">
        <el-form ref="executeForm" :model="executeParams" label-width="100px">
          <el-form-item 
            v-for="param in script.parameters" 
            :key="param.id"
            :label="param.name"
            :prop="param.name"
            :required="param.is_required === 1"
          >
            <el-input 
              v-if="param.param_type === 'string'" 
              v-model="executeParams[param.name]"
              :placeholder="param.description"
            ></el-input>
            <el-input-number 
              v-else-if="param.param_type === 'number'" 
              v-model="executeParams[param.name]"
              :placeholder="param.description"
            ></el-input-number>
            <el-select
              v-else-if="param.param_type === 'select'"
              v-model="executeParams[param.name]"
              :placeholder="param.description"
            >
              <el-option
                v-for="(option, idx) in param.options"
                :key="idx"
                :label="option"
                :value="option"
              ></el-option>
            </el-select>
            <el-switch
              v-else-if="param.param_type === 'boolean'"
              v-model="executeParams[param.name]"
            ></el-switch>
          </el-form-item>
        </el-form>
      </div>
      <div v-else>
        <p>该脚本没有需要配置的参数</p>
      </div>
      <div slot="footer" class="dialog-footer">
        <el-button @click="executeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmExecute" :loading="executing">执行</el-button>
      </div>
    </el-dialog>

    <!-- 执行结果对话框 -->
    <el-dialog title="执行结果" :visible.sync="resultDialogVisible" width="60%">
      <div v-loading="executing">
        <el-alert
          v-if="executeResult"
          :title="executeResult.success ? '执行成功' : '执行失败'"
          :type="executeResult.success ? 'success' : 'error'"
          :description="executeResult.message"
          show-icon
          :closable="false"
        ></el-alert>
        
        <div v-if="executeResult && executeResult.output" class="result-output">
          <h3>输出:</h3>
          <pre>{{ executeResult.output }}</pre>
        </div>
        
        <div v-if="executeResult && executeResult.error" class="result-error">
          <h3>错误:</h3>
          <pre>{{ executeResult.error }}</pre>
        </div>
      </div>
      <div slot="footer" class="dialog-footer">
        <el-button @click="resultDialogVisible = false">关闭</el-button>
        <el-button 
          type="primary" 
          @click="viewExecutionHistory"
          v-if="executeResult && executeResult.history_id"
        >
          查看执行记录
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import ScriptExecutionTrend from '@/components/ScriptExecutionTrend.vue';

export default {
  name: 'ScriptDetail',
  components: {
    ScriptExecutionTrend
  },
  data() {
    return {
      scriptId: null,
      script: null,
      loading: false,
      executeDialogVisible: false,
      resultDialogVisible: false,
      executeParams: {},
      executing: false,
      executeResult: null
    };
  },
  created() {
    this.scriptId = this.$route.params.id;
    this.fetchScriptDetail();
  },
  methods: {
    fetchScriptDetail() {
      this.loading = true;
      this.$axios.get(`/api/scripts/${this.scriptId}`)
        .then(response => {
          if (response.data.code === 0) {
            this.script = response.data.data;
          } else {
            this.$message.error(response.data.message || '获取脚本详情失败');
            this.$router.push('/scripts');
          }
        })
        .catch(error => {
          this.$message.error('获取脚本详情失败: ' + error.message);
          this.$router.push('/scripts');
        })
        .finally(() => {
          this.loading = false;
        });
    },
    formatTime(time) {
      if (!time) return '-';
      const date = new Date(time);
      return date.toLocaleString();
    },
    getFileTypeTag(type) {
      switch (type) {
        case 'py':
          return 'primary';
        case 'sh':
          return 'success';
        case 'bat':
          return 'warning';
        case 'ps1':
          return 'danger';
        case 'js':
          return 'info';
        default:
          return '';
      }
    },
    getParamTypeText(type) {
      switch (type) {
        case 'string':
          return '字符串';
        case 'number':
          return '数字';
        case 'boolean':
          return '布尔值';
        case 'select':
          return '选择框';
        default:
          return type;
      }
    },
    handleEdit() {
      this.$router.push(`/scripts/${this.scriptId}/edit`);
    },
    handleExecute() {
      this.executeParams = {};
      
      // 初始化参数默认值
      if (this.script && this.script.parameters) {
        this.script.parameters.forEach(param => {
          if (param.default_value) {
            this.executeParams[param.name] = param.default_value;
          }
        });
      }
      
      this.executeDialogVisible = true;
    },
    handleDelete() {
      this.$confirm('此操作将永久删除该脚本, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.$axios.delete(`/api/scripts/${this.scriptId}`)
          .then(response => {
            if (response.data.code === 0) {
              this.$message.success('删除成功');
              this.$router.push('/scripts');
            } else {
              this.$message.error(response.data.message || '删除失败');
            }
          })
          .catch(error => {
            this.$message.error('删除失败: ' + error.message);
          });
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消删除'
        });          
      });
    },
    confirmExecute() {
      this.executing = true;
      this.executeDialogVisible = false;
      this.resultDialogVisible = true;
      this.executeResult = null;
      
      this.$store.dispatch('executeScript', {
        scriptId: this.scriptId,
        params: this.executeParams
      }).then(result => {
        this.executeResult = {
          success: result.code === 0,
          message: result.message,
          output: result.data && result.data.output,
          error: result.data && result.data.error,
          history_id: result.data && result.data.history_id
        };
      }).catch(error => {
        this.executeResult = {
          success: false,
          message: '执行请求失败',
          error: error.message
        };
      }).finally(() => {
        this.executing = false;
      });
    },
    viewExecutionHistory() {
      if (this.executeResult && this.executeResult.history_id) {
        this.$router.push(`/history/${this.executeResult.history_id}`);
        this.resultDialogVisible = false;
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
}

.parameters-section {
  margin-top: 20px;
  
  h3 {
    margin-bottom: 15px;
  }
}

.result-output, .result-error {
  margin-top: 20px;
  
  h3 {
    margin-bottom: 10px;
  }
  
  pre {
    background-color: #f5f7fa;
    border: 1px solid #e6e6e6;
    border-radius: 4px;
    padding: 15px;
    overflow-x: auto;
    white-space: pre-wrap;
    word-wrap: break-word;
    max-height: 300px;
    overflow-y: auto;
  }
}

.result-error pre {
  background-color: #fef0f0;
  border-color: #fbc4c4;
}
</style>
