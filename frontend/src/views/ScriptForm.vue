<template>
  <div class="script-form">
    <div class="page-container">
      <h1 class="page-title">{{ isEdit ? '编辑脚本' : '添加脚本' }}</h1>
      
      <el-form 
        ref="form" 
        :model="form" 
        :rules="rules" 
        label-width="100px" 
        class="form-container"
        v-loading="loading"
      >
        <el-form-item label="脚本名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入脚本名称"></el-input>
        </el-form-item>
        
        <el-form-item label="脚本描述" prop="description">
          <el-input 
            type="textarea" 
            v-model="form.description" 
            placeholder="请输入脚本描述"
            :rows="4"
          ></el-input>
        </el-form-item>
        
        <el-form-item label="脚本内容" v-if="isEdit">
          <el-input
            type="textarea"
            v-model="form.content"
            :rows="20"
            :autosize="{ minRows: 20, maxRows: 30 }"
            class="code-editor"
            placeholder="脚本内容"
          ></el-input>
          <div class="version-desc" v-if="isEdit">
            <el-form-item label="版本描述" prop="versionDescription">
              <el-input
                type="textarea"
                v-model="form.versionDescription"
                :rows="3"
                placeholder="请输入版本描述，说明此次修改的内容"
              ></el-input>
            </el-form-item>
          </div>
        </el-form-item>
        
      <el-form-item label="脚本类型" v-if="!isEdit">
        <el-select v-model="form.scriptType" placeholder="请选择脚本类型" @change="handleScriptTypeChange">
          <el-option label="Python" value="python"></el-option>
          <el-option label="Shell" value="shell"></el-option>
          <el-option label="Batch" value="batch"></el-option>
          <el-option label="PowerShell" value="powershell"></el-option>
          <el-option label="JavaScript" value="js"></el-option>
        </el-select>
      </el-form-item>
      
      <el-form-item label="是否有参数" v-if="!isEdit">
        <el-switch v-model="form.hasParams" :active-value="true" :inactive-value="false" @change="updateTemplate"></el-switch>
        <span class="param-tip">{{ form.hasParams ? '脚本需要接收参数' : '脚本不需要接收参数' }}</span>
      </el-form-item>
      
      <el-form-item label="输出模式" v-if="!isEdit">
        <el-select v-model="form.outputMode" placeholder="请选择输出模式" @change="updateTemplate">
          <el-option label="JSON格式" value="json"></el-option>
          <el-option label="文件输出" value="file"></el-option>
          <el-option label="无输出" value="none"></el-option>
        </el-select>
        <div class="output-mode-tip">
          <p v-if="form.outputMode === 'json'">脚本将返回JSON格式的数据，可用于脚本链</p>
          <p v-else-if="form.outputMode === 'file'">脚本将输出一个文件路径，系统会读取该文件内容</p>
          <p v-else>脚本不需要返回任何结果</p>
        </div>
      </el-form-item>
      
      <el-form-item label="使用模板" v-if="!isEdit">
        <el-switch v-model="form.useTemplate" @change="handleUseTemplateChange"></el-switch>
        <span class="template-tip">{{ form.useTemplate ? '使用系统提供的模板' : '不使用模板' }}</span>
      </el-form-item>
      
      <el-form-item label="脚本内容" v-if="!isEdit && form.useTemplate">
        <el-input
          type="textarea"
          v-model="form.content"
          :rows="20"
          :autosize="{ minRows: 20, maxRows: 30 }"
          class="code-editor"
          placeholder="脚本模板内容"
        ></el-input>
      </el-form-item>
      
      <el-form-item label="脚本文件" v-if="!isEdit && !form.useTemplate">
        <el-upload
          class="upload-demo"
          ref="upload"
          action="#"
          :auto-upload="false"
          :before-upload="beforeUpload"
          :limit="1"
          :on-exceed="handleExceed"
          :on-change="handleFileChange"
          :file-list="fileList"
        >
          <el-button size="small" type="primary">选择文件</el-button>
          <div slot="tip" class="el-upload__tip">
            支持上传 Python(.py), Shell(.sh), Batch(.bat), PowerShell(.ps1), JavaScript(.js) 文件
          </div>
        </el-upload>
      </el-form-item>
        
        <el-form-item label="参数配置">
          <div class="parameters-header">
            <h3>脚本参数列表</h3>
            <el-button type="primary" size="small" @click="addParam">
              <i class="el-icon-plus"></i> 添加参数
            </el-button>
          </div>
          
          <el-table :data="form.parameters" border style="width: 100%">
            <el-table-column label="参数名称" prop="name" width="150">
              <template slot-scope="scope">
                <el-input v-model="scope.row.name" placeholder="参数名称"></el-input>
              </template>
            </el-table-column>
            
            <el-table-column label="参数描述" prop="description">
              <template slot-scope="scope">
                <el-input v-model="scope.row.description" placeholder="参数描述"></el-input>
              </template>
            </el-table-column>
            
            <el-table-column label="参数类型" prop="param_type" width="150">
              <template slot-scope="scope">
                <el-select v-model="scope.row.param_type" placeholder="参数类型">
                  <el-option label="字符串" value="string"></el-option>
                  <el-option label="数字" value="number"></el-option>
                  <el-option label="布尔值" value="boolean"></el-option>
                  <el-option label="选择框" value="select"></el-option>
                </el-select>
              </template>
            </el-table-column>
            
            <el-table-column label="是否必填" prop="is_required" width="100">
              <template slot-scope="scope">
                <el-switch v-model="scope.row.is_required" :active-value="1" :inactive-value="0"></el-switch>
              </template>
            </el-table-column>
            
            <el-table-column label="默认值" prop="default_value" width="150">
              <template slot-scope="scope">
                <el-input v-model="scope.row.default_value" placeholder="默认值"></el-input>
              </template>
            </el-table-column>
            
            <el-table-column label="操作" width="100">
              <template slot-scope="scope">
                <el-button
                  type="danger"
                  size="mini"
                  @click="removeParam(scope.$index)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="submitForm" :loading="submitting">保存</el-button>
          <el-button @click="cancel">取消</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ScriptForm',
  data() {
    return {
      isEdit: false,
      scriptId: null,
      form: {
        name: '',
        description: '',
        content: '',
        parameters: [],
        versionDescription: '',
        scriptType: 'python',
        hasParams: true,
        outputMode: 'json',
        useTemplate: true
      },
      rules: {
        name: [
          { required: true, message: '请输入脚本名称', trigger: 'blur' },
          { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
        ]
      },
      fileList: [],
      loading: false,
      submitting: false,
      uploadFile: null,
      uploading: false
    };
  },
  created() {
    // 判断是否为编辑模式
    this.scriptId = this.$route.params.id;
    this.isEdit = this.$route.name === 'ScriptEdit';
    
    if (this.isEdit) {
      this.fetchScriptDetail();
    }
  },
  methods: {
    fetchScriptDetail() {
      this.loading = true;
      this.$axios.get(`/api/scripts/${this.scriptId}`)
        .then(response => {
          if (response.data.code === 0) {
            const script = response.data.data;
            this.form.name = script.name;
            this.form.description = script.description;
            this.form.parameters = script.parameters || [];
            
            // 修复参数is_required字段类型
            this.form.parameters.forEach(param => {
              param.is_required = parseInt(param.is_required || 0);
            });
            
            // 获取当前版本内容
            if (script.current_version && script.file_path) {
              this.fetchScriptContent(script);
            }
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
    
    fetchScriptContent(script) {
      this.loading = true;
      
      // 找到当前版本ID
      let currentVersionId = null;
      if (script.versions && script.versions.length > 0) {
        const currentVersion = script.versions.find(v => v.is_current === 1);
        if (currentVersion) {
          currentVersionId = currentVersion.id;
        }
      }
      
      if (!currentVersionId) {
        this.loading = false;
        return;
      }
      
      this.$store.dispatch('fetchVersionContent', {
        scriptId: this.scriptId,
        versionId: currentVersionId
      })
        .then(response => {
          if (response.code === 0) {
            this.form.content = response.data.content;
          } else {
            this.$message.error(response.message || '获取脚本内容失败');
          }
        })
        .catch(error => {
          this.$message.error('获取脚本内容失败: ' + error.message);
        })
        .finally(() => {
          this.loading = false;
        });
    },
    addParam() {
      this.form.parameters.push({
        name: '',
        description: '',
        param_type: 'string',
        is_required: 0,
        default_value: ''
      });
    },
    removeParam(index) {
      this.form.parameters.splice(index, 1);
    },
    beforeUpload(file) {
      const isValidType = file.name.match(/\.(py|sh|bat|ps1|js)$/i);
      if (!isValidType) {
        this.$message.error('请上传支持的脚本文件类型!');
        return false;
      }
      
      const isLt5M = file.size / 1024 / 1024 < 5;
      if (!isLt5M) {
        this.$message.error('文件大小不能超过 5MB!');
        return false;
      }
      
      this.uploadFile = file;
      // 更新文件列表，以便在UI上显示已选择的文件
      this.fileList = [{name: file.name, url: ''}];
      return true;
    },
    handleExceed() {
      this.$message.warning('只能上传一个文件');
    },
    handleFileChange(file) {
      // 文件选择变化时设置uploadFile
      if (file && file.raw) {
        this.uploadFile = file.raw;
      }
    },
    submitForm() {
      this.$refs.form.validate(valid => {
        if (valid) {
          this.submitting = true;
          
          // 检查参数表单是否填写完整
          for (let i = 0; i < this.form.parameters.length; i++) {
            const param = this.form.parameters[i];
            if (!param.name) {
              this.$message.error('参数名称不能为空');
              this.submitting = false;
              return;
            }
          }
          
          if (this.isEdit) {
            this.updateScript();
          } else {
            this.addScript();
          }
        } else {
          return false;
        }
      });
    },
    fetchTemplate() {
      this.loading = true;
      this.$axios.get('/api/scripts/template', {
        params: {
          language: this.form.scriptType,
          has_params: this.form.hasParams,
          output_mode: this.form.outputMode
        }
      })
      .then(response => {
        if (response.data.code === 0) {
          this.form.content = response.data.data.content;
        } else {
          this.$message.error(response.data.message || '获取模板失败');
        }
      })
      .catch(error => {
        this.$message.error('获取模板失败: ' + error.message);
      })
      .finally(() => {
        this.loading = false;
      });
    },
    
    handleScriptTypeChange() {
      this.updateTemplate();
    },
    
    handleUseTemplateChange() {
      if (this.form.useTemplate) {
        this.fetchTemplate();
      } else {
        this.form.content = '';
      }
    },
    
    updateTemplate() {
      if (this.form.useTemplate) {
        this.fetchTemplate();
      }
    },
    
    addScript() {
      // 检查是否有选择文件或使用模板
      if (this.uploadFile == null && !this.form.useTemplate) {
        this.$message.error('请先选择脚本文件或使用模板');
        this.submitting = false;
        return;
      }
      
      const formData = new FormData();
      
      if (this.uploadFile) {
        formData.append('file', this.uploadFile);
      } else if (this.form.useTemplate && this.form.content) {
        // 从模板内容创建文件
        const extension = this.getExtensionByType(this.form.scriptType);
        const blob = new Blob([this.form.content], {type: 'text/plain'});
        formData.append('file', blob, `script_template.${extension}`);
      } else {
        this.$message.error('请提供脚本内容');
        this.submitting = false;
        return;
      }
      
      formData.append('name', this.form.name);
      formData.append('description', this.form.description);
      formData.append('parameters', JSON.stringify(this.form.parameters));
      formData.append('output_mode', this.form.outputMode);
      
      // 发送请求 - 同时上传文件和保存脚本信息
      this.$axios.post('/api/scripts/with-file', formData)
        .then(response => {
          if (response.data.code === 0) {
            this.$message.success('添加脚本成功');
            this.$router.push('/scripts');
          } else {
            this.$message.error(response.data.message || '添加脚本失败');
          }
        })
        .catch(error => {
          this.$message.error('添加脚本失败: ' + error.message);
        })
        .finally(() => {
          this.submitting = false;
        });
    },
    updateScript() {
      // 更新脚本信息和内容
      if (this.form.content) {
        // 有脚本内容，使用updateScriptContent action
        this.$store.dispatch('updateScriptContent', {
          scriptId: this.scriptId,
          content: this.form.content,
          parameters: this.form.parameters,
          description: this.form.versionDescription || '更新脚本内容和参数'
        })
          .then(response => {
            if (response.code === 0) {
              this.$message.success('更新脚本成功');
              this.$router.push('/scripts');
            } else {
              this.$message.error(response.message || '更新脚本失败');
            }
          })
          .catch(error => {
            this.$message.error('更新脚本失败: ' + error.message);
          })
          .finally(() => {
            this.submitting = false;
          });
      } else {
        // 没有脚本内容，使用旧的更新方法
        this.$axios.put(`/api/scripts/${this.scriptId}`, {
          name: this.form.name,
          description: this.form.description,
          parameters: this.form.parameters
        })
          .then(response => {
            if (response.data.code === 0) {
              this.$message.success('更新脚本成功');
              this.$router.push('/scripts');
            } else {
              this.$message.error(response.data.message || '更新脚本失败');
            }
          })
          .catch(error => {
            this.$message.error('更新脚本失败: ' + error.message);
          })
          .finally(() => {
            this.submitting = false;
          });
      }
    },
    getExtensionByType(type) {
      const extensions = {
        python: 'py',
        shell: 'sh',
        batch: 'bat',
        powershell: 'ps1',
        js: 'js'
      };
      return extensions[type] || 'py';
    },
    
    cancel() {
      this.$router.go(-1);
    }
  }
};
</script>

<style lang="scss" scoped>
.parameters-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  
  h3 {
    margin: 0;
  }
}

.code-editor {
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
  line-height: 1.5;
}

.version-desc {
  margin-top: 10px;
}

.param-tip, .template-tip {
  margin-left: 10px;
  color: #606266;
  font-size: 14px;
}

.output-mode-tip {
  margin-top: 5px;
  color: #606266;
  font-size: 13px;
  line-height: 1.4;
  
  p {
    margin: 0;
    padding: 0;
  }
}

.el-select {
  width: 100%;
  max-width: 240px;
}
</style>
