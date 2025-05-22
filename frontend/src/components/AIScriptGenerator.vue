<template>
  <div class="ai-script-generator">
    <el-card class="form-card">
      <div slot="header">
        <h3>AI脚本生成器</h3>
      </div>
      
      <el-form :model="form" :rules="rules" ref="form" label-width="120px" size="small">
        <!-- 基本信息 -->
        <el-divider content-position="left">基本信息</el-divider>
        
        <el-form-item label="脚本名称" prop="script_name">
          <el-input v-model="form.script_name" placeholder="输入脚本名称，例如：system_info"></el-input>
        </el-form-item>
        
        <el-form-item label="脚本描述" prop="description">
          <el-input v-model="form.description" placeholder="简短描述脚本功能，例如：获取系统信息并输出"></el-input>
        </el-form-item>
        
        <!-- 生成选项 -->
        <el-divider content-position="left">生成选项</el-divider>
        
        <el-form-item label="使用模板">
          <el-switch v-model="form.use_template"></el-switch>
        </el-form-item>
        
        <template v-if="form.use_template">
          <el-form-item label="脚本语言" prop="template_language">
            <el-select v-model="form.template_language" placeholder="选择脚本语言">
              <el-option label="Python" value="python"></el-option>
              <el-option label="Shell" value="shell"></el-option>
              <el-option label="JavaScript" value="javascript"></el-option>
            </el-select>
          </el-form-item>
          
          <el-form-item label="参数支持" prop="template_has_params">
            <el-select v-model="form.template_has_params" placeholder="选择参数支持方式">
              <el-option label="支持参数" :value="true"></el-option>
              <el-option label="不支持参数" :value="false"></el-option>
            </el-select>
          </el-form-item>
          
          <el-form-item label="输出模式" prop="template_output_mode" v-if="form.template_has_params">
            <el-select v-model="form.template_output_mode" placeholder="选择输出模式">
              <el-option label="JSON输出" value="json"></el-option>
              <el-option label="文件输出" value="file"></el-option>
              <el-option label="无输出" value="none"></el-option>
            </el-select>
          </el-form-item>
        </template>
        
        <template v-else>
          <el-form-item label="脚本类型" prop="script_type">
            <el-select v-model="form.script_type" placeholder="选择脚本类型">
              <el-option label="Python (py)" value="py"></el-option>
              <el-option label="Shell (sh)" value="sh"></el-option>
              <el-option label="JavaScript (js)" value="js"></el-option>
              <el-option label="PowerShell (ps1)" value="ps1"></el-option>
              <el-option label="Batch (bat)" value="bat"></el-option>
            </el-select>
          </el-form-item>
        </template>
        
        <!-- 功能需求 -->
        <el-divider content-position="left">功能需求</el-divider>
        
        <el-form-item label="功能要求" prop="requirements">
          <el-input
            type="textarea"
            v-model="form.requirements"
            :rows="5"
            placeholder="详细描述脚本的功能要求，越详细生成的结果越准确。例如：获取系统CPU、内存、磁盘使用率，以及运行时间和网络连接状态，将结果以JSON格式返回。"
          ></el-input>
        </el-form-item>
        
        <!-- 保存选项 -->
        <el-divider content-position="left">保存选项</el-divider>
        
        <el-form-item label="保存脚本">
          <el-switch v-model="form.save_script"></el-switch>
        </el-form-item>
        
        <!-- 操作按钮 -->
        <el-form-item>
          <el-button type="primary" @click="generateScript" :loading="loading">生成脚本</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 生成结果 -->
    <el-card class="result-card" v-if="scriptResult">
      <div slot="header" class="result-header">
        <h3>生成结果</h3>
        <div>
          <el-button size="mini" type="primary" @click="copyScript" :disabled="!scriptResult.script_content">
            复制脚本
          </el-button>
          <el-button size="mini" type="success" @click="validateScript" :loading="validating" :disabled="!scriptResult.script_content">
            验证脚本
          </el-button>
        </div>
      </div>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="脚本内容" name="content">
          <pre class="script-content">{{ scriptResult.script_content }}</pre>
        </el-tab-pane>
        <el-tab-pane label="验证结果" name="validation" v-if="validationResult">
          <div class="validation-result" v-html="formattedValidation"></div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios';
import { marked } from 'marked';

export default {
  name: 'AIScriptGenerator',
  data() {
    return {
      form: {
        script_name: '',
        description: '',
        script_type: 'py',
        requirements: '',
        use_template: true,
        template_language: 'python',
        template_has_params: true,
        template_output_mode: 'json',
        save_script: true
      },
      rules: {
        script_name: [
          { required: true, message: '请输入脚本名称', trigger: 'blur' },
          { min: 3, max: 50, message: '长度在 3 到 50 个字符', trigger: 'blur' }
        ],
        description: [
          { required: true, message: '请输入脚本描述', trigger: 'blur' },
          { min: 5, max: 200, message: '长度在 5 到 200 个字符', trigger: 'blur' }
        ],
        script_type: [
          { required: true, message: '请选择脚本类型', trigger: 'change' }
        ],
        template_language: [
          { required: true, message: '请选择脚本语言', trigger: 'change' }
        ],
        requirements: [
          { required: true, message: '请输入功能要求', trigger: 'blur' },
          { min: 10, message: '请详细描述功能要求，至少10个字符', trigger: 'blur' }
        ]
      },
      loading: false,
      validating: false,
      scriptResult: null,
      validationResult: null,
      activeTab: 'content'
    };
  },
  computed: {
    formattedValidation() {
      if (!this.validationResult) return '';
      return marked(this.validationResult);
    }
  },
  methods: {
    generateScript() {
      this.$refs.form.validate(valid => {
        if (valid) {
          this.loading = true;
          
          const payload = { ...this.form };
          
          axios.post('/api/scripts/ai/generate', payload)
            .then(response => {
              if (response.data.success) {
                this.scriptResult = response.data;
                this.$message.success('脚本生成成功');
                
                if (this.form.save_script) {
                  this.$message({
                    message: `脚本已保存，ID: ${response.data.script_id}`,
                    type: 'success'
                  });
                }
              } else {
                this.$message.error(`生成失败: ${response.data.error}`);
              }
            })
            .catch(error => {
              this.$message.error(`请求错误: ${error.message}`);
              console.error('生成脚本错误:', error);
            })
            .finally(() => {
              this.loading = false;
            });
        } else {
          this.$message.warning('请填写完整的表单信息');
          return false;
        }
      });
    },
    validateScript() {
      if (!this.scriptResult || !this.scriptResult.script_content) {
        this.$message.warning('请先生成脚本再验证');
        return;
      }
      
      this.validating = true;
      
      const payload = {
        script_content: this.scriptResult.script_content,
        script_type: this.form.script_type,
        requirements: this.form.requirements
      };
      
      axios.post('/api/scripts/ai/validate', payload)
        .then(response => {
          if (response.data.success) {
            this.validationResult = response.data.validation_result;
            this.activeTab = 'validation';
            this.$message.success('脚本验证完成');
          } else {
            this.$message.error(`验证失败: ${response.data.error}`);
          }
        })
        .catch(error => {
          this.$message.error(`请求错误: ${error.message}`);
          console.error('验证脚本错误:', error);
        })
        .finally(() => {
          this.validating = false;
        });
    },
    copyScript() {
      if (!this.scriptResult || !this.scriptResult.script_content) {
        this.$message.warning('没有可复制的脚本内容');
        return;
      }
      
      const textarea = document.createElement('textarea');
      textarea.value = this.scriptResult.script_content;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      
      this.$message.success('脚本内容已复制到剪贴板');
    },
    resetForm() {
      this.$refs.form.resetFields();
      this.scriptResult = null;
      this.validationResult = null;
    }
  }
};
</script>

<style scoped>
.ai-script-generator {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-card, .result-card {
  width: 100%;
  margin-bottom: 20px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.script-content {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  font-family: monospace;
  white-space: pre-wrap;
  max-height: 400px;
  overflow-y: auto;
}

.validation-result {
  padding: 15px;
  max-height: 400px;
  overflow-y: auto;
}

.validation-result :deep(ul) {
  padding-left: 20px;
}

.validation-result :deep(code) {
  background-color: #f5f7fa;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: monospace;
}

.el-divider {
  margin: 16px 0;
}
</style>
