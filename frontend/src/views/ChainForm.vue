<template>
  <div class="chain-form">
    <div class="page-container">
      <h1 class="page-title">{{ isEdit ? '编辑脚本链' : '添加脚本链' }}</h1>
      
      <el-form 
        ref="form" 
        :model="form" 
        :rules="rules" 
        label-width="100px" 
        class="form-container"
        v-loading="loading"
      >
        <el-form-item label="脚本链名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入脚本链名称"></el-input>
        </el-form-item>
        
        <el-form-item label="脚本链描述" prop="description">
          <el-input 
            type="textarea" 
            v-model="form.description" 
            placeholder="请输入脚本链描述"
            :rows="4"
          ></el-input>
        </el-form-item>
        
        <el-form-item label="脚本节点">
          <div class="nodes-header">
            <h3>脚本链节点列表</h3>
            <el-button type="primary" size="small" @click="showScriptSelector">
              <i class="el-icon-plus"></i> 添加脚本
            </el-button>
          </div>
          
          <el-empty v-if="!form.nodes.length" description="请添加脚本节点"></el-empty>
          
          <el-table v-else :data="form.nodes" border style="width: 100%">
            <el-table-column type="index" label="序号" width="80"></el-table-column>
            <el-table-column prop="script_name" label="脚本名称" min-width="150"></el-table-column>
            <el-table-column prop="script_description" label="脚本描述" min-width="200">
              <template slot-scope="scope">
                {{ scope.row.script_description || '无描述' }}
              </template>
            </el-table-column>
            <el-table-column prop="file_type" label="类型" width="100">
              <template slot-scope="scope">
                <el-tag :type="getFileTypeTag(scope.row.file_type)">
                  {{ scope.row.file_type }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="220">
              <template slot-scope="scope">
                <el-button
                  size="mini"
                  icon="el-icon-top"
                  @click="moveUp(scope.$index)"
                  :disabled="scope.$index === 0"
                  circle
                ></el-button>
                <el-button
                  size="mini"
                  icon="el-icon-bottom"
                  @click="moveDown(scope.$index)"
                  :disabled="scope.$index === form.nodes.length - 1"
                  circle
                ></el-button>
                <el-button
                  size="mini"
                  type="danger"
                  icon="el-icon-delete"
                  @click="removeNode(scope.$index)"
                  circle
                ></el-button>
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
    
    <!-- 脚本选择对话框 -->
    <el-dialog title="选择脚本" :visible.sync="scriptSelectorVisible" width="70%">
      <el-table
        v-loading="scriptsLoading"
        :data="availableScripts"
        border
        style="width: 100%"
        height="400px"
        @row-click="handleScriptClick"
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
      </el-table>
      
      <div slot="footer" class="dialog-footer">
        <span class="hint-text">点击表格行选择脚本</span>
        <el-button @click="scriptSelectorVisible = false">关闭</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'ChainForm',
  data() {
    return {
      isEdit: false,
      chainId: null,
      form: {
        name: '',
        description: '',
        nodes: []
      },
      rules: {
        name: [
          { required: true, message: '请输入脚本链名称', trigger: 'blur' },
          { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
        ]
      },
      loading: false,
      submitting: false,
      scriptSelectorVisible: false,
      availableScripts: [],
      scriptsLoading: false
    };
  },
  created() {
    // 判断是否为编辑模式
    this.chainId = this.$route.params.id;
    this.isEdit = this.$route.name === 'ChainEdit';
    
    if (this.isEdit) {
      this.fetchChainDetail();
    }
    
    // 获取可用脚本列表
    this.fetchScripts();
  },
  methods: {
    fetchChainDetail() {
      this.loading = true;
      this.$axios.get(`/api/chains/${this.chainId}`)
        .then(response => {
          if (response.data.code === 0) {
            const chain = response.data.data;
            this.form.name = chain.name;
            this.form.description = chain.description;
            
            // 处理节点
            if (chain.nodes && chain.nodes.length) {
              this.form.nodes = chain.nodes.map(node => ({
                script_id: node.script_id,
                script_name: node.script_name,
                script_description: node.script_description,
                file_type: node.file_type,
                node_order: node.node_order
              }));
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
    fetchScripts() {
      this.scriptsLoading = true;
      this.$axios.get('/api/scripts')
        .then(response => {
          if (response.data.code === 0) {
            this.availableScripts = response.data.data || [];
          } else {
            this.$message.error(response.data.message || '获取脚本列表失败');
          }
        })
        .catch(error => {
          this.$message.error('获取脚本列表失败: ' + error.message);
        })
        .finally(() => {
          this.scriptsLoading = false;
        });
    },
    showScriptSelector() {
      this.scriptSelectorVisible = true;
    },
    handleScriptClick(row) {
      // 检查是否已经添加过该脚本
      const exists = this.form.nodes.some(node => node.script_id === row.id);
      if (exists) {
        this.$message.warning('该脚本已添加到脚本链中');
        return;
      }
      
      // 添加到节点列表
      this.form.nodes.push({
        script_id: row.id,
        script_name: row.name,
        script_description: row.description,
        file_type: row.file_type,
        node_order: this.form.nodes.length + 1
      });
      
      this.scriptSelectorVisible = false;
      this.$message.success(`已添加脚本: ${row.name}`);
    },
    moveUp(index) {
      if (index === 0) return;
      
      const temp = this.form.nodes[index];
      this.form.nodes.splice(index, 1);
      this.form.nodes.splice(index - 1, 0, temp);
      
      // 更新顺序
      this.updateNodeOrder();
    },
    moveDown(index) {
      if (index === this.form.nodes.length - 1) return;
      
      const temp = this.form.nodes[index];
      this.form.nodes.splice(index, 1);
      this.form.nodes.splice(index + 1, 0, temp);
      
      // 更新顺序
      this.updateNodeOrder();
    },
    removeNode(index) {
      this.form.nodes.splice(index, 1);
      
      // 更新顺序
      this.updateNodeOrder();
    },
    updateNodeOrder() {
      // 更新节点顺序
      this.form.nodes.forEach((node, index) => {
        node.node_order = index + 1;
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
    submitForm() {
      this.$refs.form.validate(valid => {
        if (valid) {
          if (!this.form.nodes.length) {
            this.$message.error('请至少添加一个脚本节点');
            return;
          }
          
          this.submitting = true;
          
          if (this.isEdit) {
            this.updateChain();
          } else {
            this.addChain();
          }
        } else {
          return false;
        }
      });
    },
    addChain() {
      // 准备节点数据
      const nodes = this.form.nodes.map(node => ({
        script_id: node.script_id
      }));
      
      // 发送请求
      this.$axios.post('/api/chains', {
        name: this.form.name,
        description: this.form.description,
        nodes: nodes
      })
        .then(response => {
          if (response.data.code === 0) {
            this.$message.success('添加脚本链成功');
            this.$router.push('/chains');
          } else {
            this.$message.error(response.data.message || '添加脚本链失败');
          }
        })
        .catch(error => {
          this.$message.error('添加脚本链失败: ' + error.message);
        })
        .finally(() => {
          this.submitting = false;
        });
    },
    updateChain() {
      // 准备节点数据
      const nodes = this.form.nodes.map(node => ({
        script_id: node.script_id
      }));
      
      // 发送请求
      this.$axios.put(`/api/chains/${this.chainId}`, {
        name: this.form.name,
        description: this.form.description,
        nodes: nodes
      })
        .then(response => {
          if (response.data.code === 0) {
            this.$message.success('更新脚本链成功');
            this.$router.push('/chains');
          } else {
            this.$message.error(response.data.message || '更新脚本链失败');
          }
        })
        .catch(error => {
          this.$message.error('更新脚本链失败: ' + error.message);
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
.nodes-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  
  h3 {
    margin: 0;
  }
}

.hint-text {
  color: #909399;
  margin-right: 15px;
}
</style>
