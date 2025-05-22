<template>
  <div class="script-analyzer-page">
    <h1>脚本分析工具</h1>
    <p class="description">使用AI模型分析脚本代码，提供质量、性能、安全性和最佳实践建议。</p>
    
    <ScriptAnalyzer :scriptId="scriptId" />
  </div>
</template>

<script>
import ScriptAnalyzer from '@/components/ScriptAnalyzer.vue'

export default {
  name: 'ScriptAnalyzerView',
  components: {
    ScriptAnalyzer
  },
  data() {
    return {
      scriptId: null
    };
  },
  created() {
    // 从路由查询参数中获取脚本ID
    if (this.$route.query.scriptId) {
      this.scriptId = Number(this.$route.query.scriptId);
    }
  }
}
</script>

<style scoped>
.script-analyzer-page {
  padding: 20px;
}

h1 {
  color: #333;
  margin-bottom: 10px;
}

.description {
  color: #666;
  margin-bottom: 30px;
  font-size: 16px;
}
</style>
