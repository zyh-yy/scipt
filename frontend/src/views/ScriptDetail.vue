<template>
  <div class="script-detail">
    <div class="page-container" v-loading="loading">
      <div class="page-header">
        <h1 class="page-title">脚本详情</h1>
        <div class="button-container">
          <el-button @click="$router.push('/scripts')">
            <i class="el-icon-back"></i> 返回列表
          </el-button>
          <el-button type="primary" @click="handleExecute">
            <i class="el-icon-video-play"></i> 执行脚本
          </el-button>
          <el-button type="success" @click="handleEdit">
            <i class="el-icon-edit"></i> 编辑脚本
          </el-button>
          <el-button @click="showVersionHistory">
            <i class="el-icon-time"></i> 版本历史
          </el-button>
          <el-button type="danger" @click="handleDelete">
            <i class="el-icon-delete"></i> 删除脚本
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
      <div>
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
              <small>{{ useDocker ? '在Docker容器中隔离执行脚本' : '直接在主机上执行脚本' }}</small>
            </div>
          </el-form-item>
          
          <!-- 脚本参数 -->
          <template v-if="script && script.parameters && script.parameters.length">
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
          </template>
          <div v-else>
            <p>该脚本没有需要配置的参数</p>
          </div>
        </el-form>
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

    <!-- 版本历史对话框 -->
    <el-dialog title="脚本版本历史" :visible.sync="versionDialogVisible" width="70%">
      <el-table 
        :data="versionHistory" 
        border
        v-loading="versionLoading"
        @row-click="selectVersion"
        highlight-current-row>
        <el-table-column prop="version" label="版本号" width="120"></el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template slot-scope="scope">
            {{ formatTime(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200"></el-table-column>
        <el-table-column prop="is_current" label="当前版本" width="100">
          <template slot-scope="scope">
            <el-tag type="success" v-if="scope.row.is_current === 1">当前</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template slot-scope="scope">
            <el-button 
              type="text" 
              size="small" 
              @click.stop="viewVersionContent(scope.row)"
            >查看</el-button>
            <el-button 
              type="text" 
              size="small" 
              @click.stop="compareWithSelected(scope.row)"
              :disabled="!selectedVersion || selectedVersion.id === scope.row.id"
            >比较</el-button>
            <el-button 
              type="text" 
              size="small" 
              @click.stop="rollbackToVersion(scope.row)"
              :disabled="scope.row.is_current === 1"
            >回滚</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div slot="footer" class="dialog-footer">
        <el-button @click="versionDialogVisible = false">关闭</el-button>
      </div>
    </el-dialog>

    <!-- 版本内容对话框 -->
    <el-dialog :title="versionContentTitle" :visible.sync="contentDialogVisible" width="80%" custom-class="version-content-dialog">
      <div v-loading="contentLoading">
        <pre class="version-content" v-if="versionContent">{{ versionContent }}</pre>
      </div>
    </el-dialog>

    <!-- 版本比较对话框 -->
    <el-dialog title="版本比较" :visible.sync="compareDialogVisible" width="90%" custom-class="version-compare-dialog">
      <div v-loading="compareLoading">
        <div class="version-compare-info" v-if="compareResult">
          <div>
            <strong>版本 1:</strong> {{ compareResult.version1.version }} ({{ formatTime(compareResult.version1.created_at) }})
          </div>
          <div>
            <strong>版本 2:</strong> {{ compareResult.version2.version }} ({{ formatTime(compareResult.version2.created_at) }})
          </div>
        </div>
        <div class="version-compare-content" v-if="compareResult && compareResult.diff_html" v-html="compareResult.diff_html"></div>
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
      executeResult: null,
      useDocker: true, // 默认使用Docker执行
      
      // 版本历史相关
      versionDialogVisible: false,
      versionHistory: [],
      versionLoading: false,
      selectedVersion: null,
      
      // 版本内容相关
      contentDialogVisible: false,
      versionContent: null,
      contentLoading: false,
      versionContentTitle: "版本内容",
      
      // 版本比较相关
      compareDialogVisible: false,
      compareLoading: false,
      compareResult: null
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
      
      // 添加执行方式参数
      const params = {
        ...this.executeParams,
        use_docker: this.useDocker
      };
      
      this.$store.dispatch('executeScript', {
        scriptId: this.scriptId,
        params: params
      }).then(result => {
        if (result.code === 0) {
          // 提交成功，显示提示
          this.$message.success('脚本执行请求已提交，请在执行记录中查看结果');
          
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
    
    // 版本历史相关方法
    showVersionHistory() {
      this.versionDialogVisible = true;
      this.fetchVersionHistory();
    },
    
    fetchVersionHistory() {
      this.versionLoading = true;
      this.$store.dispatch('fetchScriptVersions', this.scriptId)
        .then(response => {
          if (response.code === 0) {
            this.versionHistory = response.data;
          } else {
            this.$message.error(response.message || '获取版本历史失败');
          }
        })
        .catch(error => {
          this.$message.error('获取版本历史失败: ' + error.message);
        })
        .finally(() => {
          this.versionLoading = false;
        });
    },
    
    selectVersion(row) {
      this.selectedVersion = row;
    },
    
    viewVersionContent(version) {
      this.contentLoading = true;
      this.contentDialogVisible = true;
      this.versionContentTitle = `版本 ${version.version} (${this.formatTime(version.created_at)})`;
      
      this.$store.dispatch('fetchVersionContent', {
        scriptId: this.scriptId,
        versionId: version.id
      })
        .then(response => {
          if (response.code === 0) {
            this.versionContent = response.data.content;
          } else {
            this.$message.error(response.message || '获取版本内容失败');
          }
        })
        .catch(error => {
          this.$message.error('获取版本内容失败: ' + error.message);
        })
        .finally(() => {
          this.contentLoading = false;
        });
    },
    
    compareWithSelected(version) {
      if (!this.selectedVersion || this.selectedVersion.id === version.id) {
        this.$message.warning('请先选择一个不同的版本进行比较');
        return;
      }
      
      this.compareLoading = true;
      this.compareDialogVisible = true;
      
      this.$store.dispatch('compareVersions', {
        scriptId: this.scriptId,
        versionId1: this.selectedVersion.id,
        versionId2: version.id
      })
        .then(response => {
          if (response.code === 0) {
            this.compareResult = response.data;
          } else {
            this.$message.error(response.message || '比较版本失败');
          }
        })
        .catch(error => {
          this.$message.error('比较版本失败: ' + error.message);
        })
        .finally(() => {
          this.compareLoading = false;
        });
    },
    
    rollbackToVersion(version) {
      if (version.is_current === 1) {
        this.$message.info('该版本已经是当前版本');
        return;
      }
      
      this.$confirm(`确定要回滚到版本 ${version.version} 吗?`, '回滚确认', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.$store.dispatch('rollbackVersion', {
          scriptId: this.scriptId,
          versionId: version.id
        })
          .then(response => {
            if (response.code === 0) {
              this.$message.success('回滚成功');
              this.fetchScriptDetail();
              this.fetchVersionHistory();
            } else {
              this.$message.error(response.message || '回滚失败');
            }
          })
          .catch(error => {
            this.$message.error('回滚失败: ' + error.message);
          });
      }).catch(() => {
        this.$message.info('已取消回滚');
      });
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

/* 版本历史和比较相关样式 */
.version-content {
  background-color: #f5f7fa;
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  padding: 15px;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 500px;
  overflow-y: auto;
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
  line-height: 1.5;
}

.version-compare-info {
  margin-bottom: 15px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.version-compare-content {
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  padding: 0;
  overflow-x: auto;
  max-height: 600px;
  overflow-y: auto;
}

/* 覆盖difflib生成的HTML表格样式 */
:deep(.version-compare-content table) {
  width: 100%;
  border-collapse: collapse;
}

:deep(.version-compare-content td) {
  padding: 2px 5px;
  white-space: pre-wrap;
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
  line-height: 1.5;
}

:deep(.version-compare-content .diff_add) {
  background-color: #e6ffed;
}

:deep(.version-compare-content .diff_chg) {
  background-color: #fff5b1;
}

:deep(.version-compare-content .diff_sub) {
  background-color: #ffdce0;
}

.button-container {
  display: flex;
  gap: 10px;
}
</style>
