<template>
  <div class="chains">
    <div class="page-container">
      <div class="page-header">
        <h1 class="page-title">脚本链管理</h1>
        <div class="button-container">
          <el-button type="primary" @click="$router.push('/chains/add')">
            <i class="el-icon-plus"></i> 添加脚本链
          </el-button>
        </div>
      </div>

      <el-table
        v-loading="loading"
        :data="chains"
        border
        style="width: 100%"
        empty-text="暂无数据"
      >
        <el-table-column prop="id" label="ID" width="80"></el-table-column>
        <el-table-column prop="name" label="脚本链名称" min-width="150"></el-table-column>
        <el-table-column prop="description" label="描述" min-width="200"></el-table-column>
        <el-table-column label="脚本数量" width="120">
          <template slot-scope="scope">
            {{ scope.row.nodes ? scope.row.nodes.length : 0 }} 个脚本
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template slot-scope="scope">
            {{ formatTime(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250">
          <template slot-scope="scope">
            <el-button
              size="mini"
              type="primary"
              @click="handleView(scope.row)"
            >
              查看
            </el-button>
            <el-button
              size="mini"
              type="success"
              @click="handleExecute(scope.row)"
            >
              执行
            </el-button>
            <el-button
              size="mini"
              type="warning"
              @click="handleEdit(scope.row)"
            >
              编辑
            </el-button>
            <el-button
              size="mini"
              type="danger"
              @click="handleDelete(scope.row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 执行脚本链对话框 -->
    <el-dialog title="执行脚本链" :visible.sync="executeDialogVisible" width="50%">
      <div>
        <p>确认执行脚本链 <strong>{{ currentChain ? currentChain.name : '' }}</strong>？</p>
        
        <div v-if="hasRequiredParams" class="params-form">
          <h3>脚本链参数配置</h3>
          <el-form ref="executeForm" :model="executeParams" label-width="100px">
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
          </el-form>
        </div>
        
        <div class="chain-nodes" v-if="chainScripts.length">
          <h3>脚本链执行顺序</h3>
          <el-steps :active="chainScripts.length" direction="vertical" finish-status="success">
            <el-step 
              v-for="(script, index) in chainScripts" 
              :key="index"
              :title="script.name"
              :description="script.description || '无描述'"
            ></el-step>
          </el-steps>
        </div>
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
import { mapState } from 'vuex';

export default {
  name: 'Chains',
  data() {
    return {
      executeDialogVisible: false,
      resultDialogVisible: false,
      currentChain: null,
      chainScripts: [],
      executeParams: {},
      executing: false,
      executeResult: null,
      allParams: []
    };
  },
  computed: {
    ...mapState(['chains', 'scripts', 'loading']),
    hasRequiredParams() {
      return this.allParams.length > 0;
    }
  },
  created() {
    this.fetchData();
  },
  methods: {
    fetchData() {
      this.$store.dispatch('fetchChains');
      this.$store.dispatch('fetchScripts');
    },
    formatTime(time) {
      if (!time) return '-';
      const date = new Date(time);
      return date.toLocaleString();
    },
    handleView(row) {
      this.$router.push(`/chains/${row.id}`);
    },
    handleEdit(row) {
      this.$router.push(`/chains/${row.id}/edit`);
    },
    handleExecute(row) {
      this.currentChain = row;
      this.executeParams = {};
      this.chainScripts = [];
      this.allParams = [];
      
      // 加载脚本链详情
      this.$axios.get(`/api/chains/${row.id}`)
        .then(response => {
          if (response.data.code === 0) {
            const chain = response.data.data;
            const nodes = chain.nodes || [];
            
            // 按顺序获取脚本详情
            const promises = nodes.map(node => 
              this.$axios.get(`/api/scripts/${node.script_id}`)
            );
            
            Promise.all(promises)
              .then(results => {
                this.chainScripts = results
                  .filter(res => res.data.code === 0)
                  .map(res => res.data.data)
                  .filter(Boolean);
                
                // 收集所有参数
                this.allParams = [];
                this.chainScripts.forEach(script => {
                  if (script.parameters && script.parameters.length) {
                    script.parameters.forEach(param => {
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
                
                this.executeDialogVisible = true;
              })
              .catch(() => {
                this.$message.error('加载脚本详情失败');
              });
          } else {
            this.$message.error(response.data.message || '加载脚本链详情失败');
          }
        })
        .catch(error => {
          this.$message.error('加载脚本链详情失败: ' + error.message);
        });
    },
    handleDelete(row) {
      this.$confirm('此操作将永久删除该脚本链, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.$axios.delete(`/api/chains/${row.id}`)
          .then(response => {
            if (response.data.code === 0) {
              this.$message.success('删除成功');
              this.fetchData();
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
      
      this.$store.dispatch('executeChain', {
        chainId: this.currentChain.id,
        params: this.executeParams
      }).then(result => {
        this.executeResult = {
          success: result.code === 0,
          message: result.message,
          outputs: result.data && result.data.outputs,
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
    },
    getScriptName(scriptId) {
      const script = this.chainScripts.find(s => s.id === parseInt(scriptId));
      return script ? script.name : `脚本 ID: ${scriptId}`;
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

.params-form {
  margin-bottom: 20px;
  
  h3 {
    margin-bottom: 15px;
  }
}

.chain-nodes {
  margin-top: 20px;
  
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
