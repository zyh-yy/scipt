<template>
  <div id="app">
    <el-container class="main-container">
      <el-header class="main-header">
        <div class="logo">
          <h1>脚本管控平台</h1>
        </div>
        <el-menu
          :default-active="activeIndex"
          class="main-menu"
          mode="horizontal"
          background-color="#3a84ff"
          text-color="#fff"
          active-text-color="#ffd04b"
          router
        >
          <el-menu-item index="/">首页</el-menu-item>
          <el-menu-item index="/scripts">脚本管理</el-menu-item>
          <el-menu-item index="/chains">脚本链管理</el-menu-item>
          <el-menu-item index="/scheduled-tasks">定时任务</el-menu-item>
          <el-menu-item index="/history">执行历史</el-menu-item>
          <el-menu-item index="/alerts">告警管理</el-menu-item>
        </el-menu>
      </el-header>
      
      <el-main class="main-content">
        <router-view />
      </el-main>
      
      <el-footer class="main-footer">
        &copy; 2025 脚本管控平台 - 本科毕业设计
      </el-footer>
    </el-container>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      activeIndex: '/'
    };
  },
  watch: {
    $route: {
      handler(route) {
        this.activeIndex = route.path;
      },
      immediate: true
    }
  }
};
</script>

<style lang="scss">
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
}

#app {
  font-family: "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  height: 100%;
}

.main-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.main-header {
  display: flex;
  align-items: center;
  padding: 0;
  background: linear-gradient(90deg, #3a84ff, #5a9bff);
  color: white;
  height: 60px !important;
  line-height: 60px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.logo {
  width: 200px;
  padding-left: 20px;
  h1 {
    font-size: 20px;
    margin: 0;
  }
}

.main-menu {
  flex: 1;
  border-bottom: none;
  background: transparent !important;
  
  .el-menu-item {
    height: 60px;
    line-height: 60px;
  }
}

.main-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background: #f5f7fa;
}

.main-footer {
  height: 40px !important;
  line-height: 40px;
  text-align: center;
  background: #f5f7fa;
  color: #909399;
  font-size: 12px;
  border-top: 1px solid #e6e6e6;
}

.page-container {
  background: white;
  border-radius: 4px;
  padding: 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.page-title {
  margin-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 10px;
}

.button-container {
  margin-bottom: 20px;
}

.form-container {
  max-width: 800px;
}
</style>
