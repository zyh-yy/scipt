<template>
  <div class="search-bar">
    <el-form :inline="true" :model="searchForm" class="search-form">
      <el-form-item>
        <el-input
          v-model="searchForm.keyword"
          :placeholder="placeholder"
          prefix-icon="el-icon-search"
          clearable
          @keyup.enter.native="handleSearch"
        ></el-input>
      </el-form-item>
      
      <el-form-item>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
        <el-button type="text" @click="showAdvanced = !showAdvanced">
          {{ showAdvanced ? '收起' : '高级搜索' }}
          <i :class="showAdvanced ? 'el-icon-arrow-up' : 'el-icon-arrow-down'"></i>
        </el-button>
      </el-form-item>
    </el-form>
    
    <div v-show="showAdvanced" class="advanced-search">
      <el-form :inline="true" :model="searchForm" class="advanced-form">
        <slot name="advanced-fields"></slot>
      </el-form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SearchBar',
  props: {
    placeholder: {
      type: String,
      default: '输入关键词搜索'
    },
    initialSearchForm: {
      type: Object,
      default: () => ({
        keyword: ''
      })
    }
  },
  data() {
    return {
      searchForm: { ...this.initialSearchForm },
      showAdvanced: false
    };
  },
  watch: {
    initialSearchForm: {
      handler(newVal) {
        this.searchForm = { ...newVal };
      },
      deep: true
    }
  },
  methods: {
    handleSearch() {
      this.$emit('search', { ...this.searchForm });
    },
    handleReset() {
      this.searchForm = { keyword: '' };
      Object.keys(this.initialSearchForm).forEach(key => {
        if (key !== 'keyword') {
          this.searchForm[key] = null;
        }
      });
      this.$emit('reset');
      this.$emit('search', { ...this.searchForm });
    }
  }
};
</script>

<style lang="scss" scoped>
.search-bar {
  margin-bottom: 20px;
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
}

.advanced-search {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px dashed #e6e6e6;
}
</style>
