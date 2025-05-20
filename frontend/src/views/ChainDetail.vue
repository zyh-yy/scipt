<template>
  <div class="chain-detail">
    <div class="page-container" v-loading="loading">
      <div class="page-header">
        <h1 class="page-title">脚本链详情</h1>
        <div class="button-container">
          <el-button @click="$router.push('/chains')">返回列表</el-button>
          <el-button type="primary" @click="handleExecute">执行脚本链</el-button>
          <el-button type="warning" @click="handleEdit">编辑脚本链</el-button>
          <el-button type="danger" @click="handleDelete">删除脚本链</el-button>
        </div>
      </div>
      
      <el-card v-if="chain" class="detail-card">
        <div slot="header">
          <span>{{ chain.name }}</span>
        </div>
        
        <el-descriptions :column="2" border>
          <el-descriptions-item label="脚本链ID">{{ chain.id }}</el-descriptions-item>
          <el-descriptions-item label="节点数量">{{ chain.nodes ? chain.nodes.length : 0 }} 个脚本</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatTime(chain.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatTime(chain.updated_at) }}</el-descriptions-item>
          <el-descriptions-item label="脚本链描述" :span="2">
            {{ chain.description || '暂无描述' }}
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="nodes-section" v-if="chain.nodes && chain.nodes.length">
          <h3>脚本链节点列表</h3>
          <el-steps direction="vertical" :active="chain.nodes.length" finish-status="success">
            <el-step 
              v-for="(node, index) in chain.nodes" 
              :key="index"
              :title="`${index+1}. ${node.script_name}`"
            >
              <div slot="description">
                <div>类型: <el-tag size="mini" :type="getFileTypeTag(node.file_type)">{{ node.file_type }}</el-tag></div>
                <div v-if="nodeDetails[node.script_id]">
                  <div class="param-list" v-if="nodeDetails[node.script_id].parameters && nodeDetails[node.script_id].parameters.length">
                    <div class="param-title">参数:</div>
                    <el-tag
                      v-for="param in nodeDetails[node.script_id].parameters"
                      :key="param.id"
                      size="mini"
                      :type="param.is_required ? 'danger' : 'info'"
                      class="param-tag"
                    >
                      {{ param.name }}{{ param.is_required ? ' (必填)' : '' }}
                    </el-tag>
                  </div>
                  <div class="script-desc">{{ nodeDetails[node.script_id].description || '无描述' }}</div>
                </div>
                <div v-else>
                  <el-button size="mini" type="text" @click="loadScriptDetail(node.script_id)">加载脚本详情</el-button>
                </div>
              </div>
            </el-step>
          </el-steps>
        </div>
        <el-empty v-else description="没有配置脚本节点"></el-empty>
      </el-card>
      
      <el-empty v-else description="未找到脚本链信息"></el-empty>
    </div>
    
    <!-- 执行脚本链对话框 -->
    <el-dialog title="执行脚本链" :visible.sync="executeDialogVisible" width="50%">
      <div>
        <p>确认执行脚本链 <strong>{{ chain ? chain.name : '' }}</strong>？</p>
        
        <el-form ref="executeForm" :model="executeParams" label-width="100px">
          <!-- Docker执行选项 -->
          <el-form-item label="执行方式">
            <el-switch
              v-model="useDocker"
              active-text="Docker容器"
              inactive-text="本地执行"
              active-color="#13ce66"
            ></el-switch>
            <div class="execution-mode-desc">
              <small>{{ useDocker ? '在Docker容器中隔离执行脚本链' : '直接在主机上执行脚本链' }}</small>
            </div>
          </el-form-item>
          
          <div v-if="hasRequiredParams" class="params-form">
            <h3>脚本链参数配置</h3>
            <el-form-item 
              v-for="param in allParams" 
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
          </div>
        </el-form>
      </div>
      <div slot="footer" class="dialog-footer">
        <el-button @click="executeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmExecute" :loading="executing">执行</el-button>
      </div>
    </el-dialog>

    <!-- 执行结果对话框 -->
    <el-dialog title="执行结果" :visible.sync="resultDialogVisible" width="70%">
      <div v-loading="executing">
        <el-alert
          v-if="executeResult"
          :title="executeResult.success ? '执行成功' : '执行失败'"
          :type="executeResult.success ? 'success' : 'error'"
          :description="executeResult.message"
          show-icon
          :closable="false"
        ></el-alert>
        
        <div v-if="executeResult && executeResult.outputs" class="chain-results">
          <h3>各脚本执行结果</h3>
          <el-collapse accordion>
            <el-collapse-item
              v-for="(output, scriptId) in executeResult.outputs"
              :key="scriptId"
              :title="getScriptName(scriptId)"
              :name="scriptId"
            >
              <el-tag :type="output.success ? 'success' : 'danger'">
                {{ output.success ? '成功' : '失败' }}
              </el-tag>
              
              <div v-if="output.output" class="result-output">
                <h4>输出:</h4>
                <pre>{{ output.output }}</pre>
              </div>
              
              <div v-if="output.error" class="result-error">
                <h4>错误:</h4>
                <pre>{{ output.error }}</pre>
              </div>
            </el-collapse-item>
          </el-collapse>
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
export default {
  name: 'ChainDetail',
  data() {
    return {
      chainId: null,
      chain: null,
      nodeDetails: {},
      loading: false,
      executeDialogVisible: false,
      resultDialogVisible: false,
      executeParams: {},
      executing: false,
      executeResult: null,
      allParams: [],
      useDocker: true // 默认使用Docker执行
    };
  },
  computed: {
    hasRequiredParams() {
      return this.allParams.length > 0;
    }
  },
  created() {
    this.chainId = this.$route.params.id;
    this.fetchChainDetail();
  },
  methods: {
    fetchChainDetail() {
      this.loading = true;
      this.$axios.get(`/api/chains/${this.chainId}`)
        .then(response => {
          if (response.data.code === 0) {
            this.chain = response.data.data;
            
            // 预加载所有脚本详情
            if (this.chain && this.chain.nodes) {
              this.chain.nodes.forEach(node => {
                this.loadScriptDetail(node.script_id);
              });
            }
          } else {
            this.$message.error(response.data.message || '获取脚本链详情失败');
            this.$router.push('/chains');
          }
        })
        .catch(error => {
          this.$message.error('获取脚本链详情失败: ' + error.message);
          this.$router.push('/chains');
        })
        .finally(() => {
          this.loading = false;
        });
    },
    loadScriptDetail(scriptId) {
      if (this.nodeDetails[scriptId]) return;
      
      this.$axios.get(`/api/scripts/${scriptId}`)
        .then(response => {
          if (response.data.code === 0) {
            this.$set(this.nodeDetails, scriptId, response.data.data);
          }
        })
        .catch(() => {
          this.$set(this.nodeDetails, scriptId, { description: '加载失败' });
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
    handleEdit() {
      this.$router.push(`/chains/${this.chainId}/edit`);
    },
    handleExecute() {
      this.executeParams = {};
      this.allParams = [];
      
      // 收集所有参数
      if (this.chain && this.chain.nodes) {
        this.chain.nodes.forEach(node => {
          const scriptDetail = this.nodeDetails[node.script_id];
          if (scriptDetail && scriptDetail.parameters) {
            scriptDetail.parameters.forEach(param => {
              // 检查是否已经有相同名称的参数
              const existingParam = this.allParams.find(p => p.name === param.name);
              if (!existingParam) {
                this.allParams.push(param);
                // 初始化默认值
                if (param.default_value) {
                  this.executeParams[param.name] = param.default_value;
                }
              }
            });
          }
        });
      }
      
      this.executeDialogVisible = true;
    },
    handleDelete() {
      this.$confirm('此操作将永久删除该脚本链, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.$axios.delete(`/api/chains/${this.chainId}`)
          .then(response => {
            if (response.data.code === 0) {
              this.$message.success('删除成功');
              this.$router.push('/chains');
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
      
      // 添加执行方式参数
      const params = {
        ...this.executeParams,
        use_docker: this.useDocker
      };
      
      this.$store.dispatch('executeChain', {
        chainId: this.chainId,
        params: params
      }).then(result => {
        if (result.code === 0) {
          // 提交成功，显示提示
          this.$message.success('脚本链执行请求已提交，请在执行记录中查看结果');
          
          // 可选：导航到执行历史详情页
          if (result.data && result.data.history_id) {
            this.$router.push(`/history/${result.data.history_id}`);
          }
        } else {
          this.$message.error(result.message || '提交执行请求失败');
        }
      }).catch(error => {
        this.$message.error('提交执行请求失败: ' + error.message);
      }).finally(() => {
        this.executing = false;
      });
    },
    viewExecutionHistory() {
      if (this.executeResult && this.executeResult.history_id) {
        this.$router.push(`/history/${this.executeResult.history_id}`);
        this.resultDialogVisible = false;
      }
    },
    getScriptName(scriptId) {
      if (!this.chain || !this.chain.nodes) return `脚本 ID: ${scriptId}`;
      
      const node = this.chain.nodes.find(n => n.script_id === parseInt(scriptId));
      return node ? node.script_name : `脚本 ID: ${scriptId}`;
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

.nodes-section {
  margin-top: 20px;
  
  h3 {
    margin-bottom: 15px;
  }
}

.script-desc {
  margin-top: 5px;
  color: #606266;
}

.param-list {
  margin: 5px 0;
  
  .param-title {
    margin-bottom: 5px;
  }
  
  .param-tag {
    margin-right: 5px;
    margin-bottom: 5px;
  }
}

.params-form {
  margin-bottom: 20px;
  
  h3 {
    margin-bottom: 15px;
  }
}

.chain-results {
  margin-top: 20px;
  
  h3 {
    margin-bottom: 15px;
  }
  
  .el-collapse-item {
    margin-bottom: 10px;
  }
}

.result-output, .result-error {
  margin-top: 15px;
  
  h4 {
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
