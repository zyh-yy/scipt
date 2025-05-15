<template>
  <div class="scripts">
    <div class="page-container">
      <div class="page-header">
        <h1 class="page-title">脚本管理</h1>
        <div class="button-container">
          <el-button type="primary" @click="$router.push('/scripts/add')">
            <i class="el-icon-plus"></i> 添加脚本
          </el-button>
        </div>
      </div>

      <el-table
        v-loading="loading"
        :data="scripts"
        border
        style="width: 100%"
        empty-text="暂无数据"
      >
        <el-table-column prop="id" label="ID" width="80"></el-table-column>
        <el-table-column prop="name" label="脚本名称" min-width="150"></el-table-column>
        <el-table-column prop="description" label="描述" min-width="200"></el-table-column>
        <el-table-column prop="file_type" label="类型" width="100">
          <template slot-scope="scope">
            <el-tag :type="getFileTypeTag(scope.row.file_type)">
              {{ scope.row.file_type }}
            </el-tag>
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

    <!-- 执行脚本对话框 -->
    <el-dialog title="执行脚本" :visible.sync="executeDialogVisible" width="50%">
      <div v-if="currentScript && currentScript.parameters && currentScript.parameters.length">
        <el-form ref="executeForm" :model="executeParams" label-width="100px">
          <el-form-item 
            v-for="param in currentScript.parameters" 
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
import { mapState } from 'vuex';

export default {
  name: 'Scripts',
  data() {
    return {
      executeDialogVisible: false,
      resultDialogVisible: false,
      currentScript: null,
      executeParams: {},
      executing: false,
      executeResult: null
    };
  },
  computed: {
    ...mapState(['scripts', 'loading'])
  },
  created() {
    this.fetchData();
  },
  methods: {
    fetchData() {
      this.$store.dispatch('fetchScripts');
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
    handleView(row) {
      this.$router.push(`/scripts/${row.id}`);
    },
    handleEdit(row) {
      this.$router.push(`/scripts/${row.id}/edit`);
    },
    handleExecute(row) {
      this.currentScript = row;
      this.executeParams = {};
      
      // 初始化参数默认值
      if (row.parameters) {
        row.parameters.forEach(param => {
          if (param.default_value) {
            this.executeParams[param.name] = param.default_value;
          }
        });
      }
      
      this.executeDialogVisible = true;
    },
    handleDelete(row) {
      this.$confirm('此操作将永久删除该脚本, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.$axios.delete(`/api/scripts/${row.id}`)
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
      
      this.$store.dispatch('executeScript', {
        scriptId: this.currentScript.id,
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
