<template>
  <div class="script-analyzer">
    <el-card class="analyzer-card">
      <div slot="header">
        <h3>脚本分析工具</h3>
      </div>
      
      <el-form :model="form" :rules="rules" ref="form" label-width="120px" size="small">
        <!-- 脚本选择 -->
        <el-form-item label="脚本ID" prop="scriptId" v-if="!directAnalysis">
          <el-input-number v-model="form.scriptId" :min="1" placeholder="输入要分析的脚本ID"></el-input-number>
        </el-form-item>
        
        <el-form-item label="分析类型" prop="analysisType">
          <el-select v-model="form.analysisType" placeholder="选择分析类型">
            <el-option label="一般分析" value="general"></el-option>
            <el-option label="性能分析" value="performance"></el-option>
            <el-option label="安全分析" value="security"></el-option>
            <el-option label="可读性分析" value="readability"></el-option>
            <el-option label="最佳实践" value="best_practices"></el-option>
          </el-select>
        </el-form-item>
        
        <!-- 操作按钮 -->
        <el-form-item>
          <el-button type="primary" @click="analyzeScript" :loading="loading">分析脚本</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 分析结果 -->
    <el-card class="result-card" v-if="analysisResult">
      <div slot="header" class="result-header">
        <h3>分析结果</h3>
        <div>
          <el-button size="mini" type="primary" @click="copyAnalysisResult">
            复制结果
          </el-button>
        </div>
      </div>
      
      <div class="analysis-result" v-html="formattedAnalysis"></div>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios';
import { marked } from 'marked';

export default {
  name: 'ScriptAnalyzer',
  props: {
    directAnalysis: {
      type: Boolean,
      default: false
    },
    scriptId: {
      type: Number,
      default: null
    },
    scriptContent: {
      type: String,
      default: null
    },
    scriptType: {
      type: String,
      default: null
    },
    requirements: {
      type: String,
      default: null
    }
  },
  data() {
    return {
      form: {
        scriptId: this.scriptId || null,
        analysisType: 'general'
      },
      rules: {
        scriptId: [
          { required: true, message: '请输入脚本ID', trigger: 'blur', type: 'number' }
        ],
        analysisType: [
          { required: true, message: '请选择分析类型', trigger: 'change' }
        ]
      },
      loading: false,
      analysisResult: null
    };
  },
  computed: {
    formattedAnalysis() {
      if (!this.analysisResult) return '';
      return marked(this.analysisResult);
    }
  },
  methods: {
    analyzeScript() {
      // 如果是直接分析模式（从其他组件传入脚本内容）
      if (this.directAnalysis && this.scriptContent) {
        this.directAnalyzeScript();
        return;
      }
      
      // 通过ID分析已保存的脚本
      this.$refs.form.validate(valid => {
        if (valid) {
          this.loading = true;
          
          axios.get(`/api/scripts/ai/analyze/${this.form.scriptId}?type=${this.form.analysisType}`)
            .then(response => {
              if (response.data.success) {
                this.analysisResult = response.data.analysis_result;
                this.$message.success('脚本分析成功');
              } else {
                this.$message.error(`分析失败: ${response.data.error}`);
              }
            })
            .catch(error => {
              this.$message.error(`请求错误: ${error.message}`);
              console.error('分析脚本错误:', error);
            })
            .finally(() => {
              this.loading = false;
            });
        } else {
          this.$message.warning('请填写完整信息');
          return false;
        }
      });
    },
    directAnalyzeScript() {
      this.loading = true;
      
      // 构建分析请求
      const payload = {
        script_content: this.scriptContent,
        script_type: this.scriptType,
        requirements: this.requirements,
        analysis_type: this.form.analysisType
      };
      
      // 后端需要补充直接分析脚本内容的API，这里使用现有的validate API作为替代
      axios.post('/api/scripts/ai/validate', payload)
        .then(response => {
          if (response.data.success) {
            this.analysisResult = response.data.validation_result;
            this.$message.success('脚本分析成功');
          } else {
            this.$message.error(`分析失败: ${response.data.error}`);
          }
        })
        .catch(error => {
          this.$message.error(`请求错误: ${error.message}`);
          console.error('分析脚本错误:', error);
        })
        .finally(() => {
          this.loading = false;
        });
    },
    copyAnalysisResult() {
      if (!this.analysisResult) {
        this.$message.warning('没有可复制的分析结果');
        return;
      }
      
      const textarea = document.createElement('textarea');
      textarea.value = this.analysisResult;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      
      this.$message.success('分析结果已复制到剪贴板');
    },
    resetForm() {
      this.$refs.form.resetFields();
      this.analysisResult = null;
    }
  }
};
</script>

<style scoped>
.script-analyzer {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.analyzer-card, .result-card {
  width: 100%;
  margin-bottom: 20px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.analysis-result {
  padding: 15px;
  max-height: 500px;
  overflow-y: auto;
}

.analysis-result :deep(h1),
.analysis-result :deep(h2),
.analysis-result :deep(h3) {
  margin-top: 16px;
  margin-bottom: 8px;
  font-weight: 600;
}

.analysis-result :deep(ul),
.analysis-result :deep(ol) {
  padding-left: 20px;
  margin-top: 8px;
  margin-bottom: 8px;
}

.analysis-result :deep(pre) {
  background-color: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
  margin: 12px 0;
}

.analysis-result :deep(code) {
  background-color: #f5f7fa;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: monospace;
}

.analysis-result :deep(p) {
  margin: 8px 0;
}

.analysis-result :deep(blockquote) {
  border-left: 4px solid #e0e0e0;
  padding-left: 16px;
  margin: 8px 0;
  color: #666;
}

.analysis-result :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 16px 0;
}

.analysis-result :deep(th),
.analysis-result :deep(td) {
  border: 1px solid #e0e0e0;
  padding: 8px;
  text-align: left;
}

.analysis-result :deep(th) {
  background-color: #f5f7fa;
}
</style>
