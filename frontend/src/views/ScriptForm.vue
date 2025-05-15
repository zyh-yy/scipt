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
        
        <el-form-item label="脚本文件" prop="file" v-if="!isEdit">
          <el-upload
            class="upload-demo"
            ref="upload"
            action="#"
            :http-request="handleUpload"
            :before-upload="beforeUpload"
            :limit="1"
            :on-exceed="handleExceed"
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
        parameters: []
      },
      rules: {
        name: [
          { required: true, message: '请输入脚本名称', trigger: 'blur' },
          { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
        ],
        file: [
          { required: true, message: '请上传脚本文件', trigger: 'change' }
        ]
      },
      fileList: [],
      loading: false,
      submitting: false,
      uploadFile: null,
      uploadedFileInfo: null,
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
      return true;
    },
    handleExceed() {
      this.$message.warning('只能上传一个文件');
    },
    handleUpload(options) {
      // 选择文件后，立即上传文件
      const formData = new FormData();
      formData.append('file', options.file);
      
      this.uploading = true;
      
      this.$axios.post('/api/scripts/upload-file', formData)
        .then(response => {
          if (response.data.code === 0) {
            this.uploadedFileInfo = response.data.data;
            this.$message.success('文件上传成功');
            return { status: true };
          } else {
            this.$message.error(response.data.message || '上传文件失败');
            return { status: false };
          }
        })
        .catch(error => {
          this.$message.error('上传文件失败: ' + error.message);
          return { status: false };
        })
        .finally(() => {
          this.uploading = false;
        });
      
      // 返回上传状态
      return { status: true };
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
    addScript() {
      // 检查是否有上传的文件信息
      if (!this.uploadedFileInfo) {
        this.$message.error('请先选择并上传脚本文件');
        this.submitting = false;
        return;
      }
      
      // 使用已上传文件的信息
      const data = {
        name: this.form.name,
        description: this.form.description,
        file_path: this.uploadedFileInfo.file_path,
        file_type: this.uploadedFileInfo.file_type,
        parameters: this.form.parameters
      };
      
      // 发送请求 - 传递脚本信息和文件ID
      this.$axios.post('/api/scripts', data)
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
      // 更新脚本信息
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
</style>
