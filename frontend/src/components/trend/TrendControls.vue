<template>
  <div class="trend-controls">
    <el-select 
      v-model="selectedScriptId" 
      size="small" 
      placeholder="选择脚本" 
      clearable 
      @change="handleScriptChange"
    >
      <el-option
        v-for="script in scripts"
        :key="script.id"
        :label="script.name"
        :value="script.id"
      ></el-option>
    </el-select>
    <el-select 
      v-model="selectedTimeRange" 
      size="small" 
      style="margin-left: 10px" 
      @change="handleTimeRangeChange"
    >
      <el-option label="最近7天" value="7"></el-option>
      <el-option label="最近30天" value="30"></el-option>
      <el-option label="最近90天" value="90"></el-option>
    </el-select>
  </div>
</template>

<script>
export default {
  name: 'TrendControls',
  props: {
    scripts: {
      type: Array,
      required: true
    },
    scriptId: {
      type: [Number, String],
      default: null
    },
    timeRange: {
      type: String,
      default: '30'
    }
  },
  data() {
    return {
      selectedScriptId: this.scriptId,
      selectedTimeRange: this.timeRange
    };
  },
  watch: {
    scriptId(newVal) {
      this.selectedScriptId = newVal;
    },
    timeRange(newVal) {
      this.selectedTimeRange = newVal;
    }
  },
  methods: {
    handleScriptChange() {
      this.$emit('script-change', this.selectedScriptId);
    },
    handleTimeRangeChange() {
      this.$emit('time-range-change', this.selectedTimeRange);
    }
  }
};
</script>

<style lang="scss" scoped>
.trend-controls {
  display: flex;
  align-items: center;
}
</style>
