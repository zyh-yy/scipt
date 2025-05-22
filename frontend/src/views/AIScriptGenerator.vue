<template>
  <div class="ai-script-generator-page">
    <h1>AI脚本生成器</h1>
    <p class="description">利用大模型API自动生成满足系统要求的脚本，快速创建功能完善的脚本文件。</p>
    
    <AIScriptGenerator />
  </div>
</template>

<script>
import AIScriptGenerator from '@/components/AIScriptGenerator.vue'

export default {
  name: 'AIScriptGeneratorView',
  components: {
    AIScriptGenerator
  }
}
</script>

<style scoped>
.ai-script-generator-page {
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
