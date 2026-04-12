<template>
  <el-form
    :model="model"
    :rules="rules"
    :label-position="labelPosition"
    :label-width="labelWidth"
    :inline="inline"
    @submit.prevent="handleSubmit"
    class="base-form"
  >
    <slot></slot>
    <div v-if="showActions" class="form-actions">
      <el-button type="primary" @click="handleSubmit">提交</el-button>
      <el-button @click="handleReset">重置</el-button>
    </div>
  </el-form>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  model: {
    type: Object,
    required: true
  },
  rules: {
    type: Object,
    default: () => ({})
  },
  labelPosition: {
    type: String,
    default: 'top'
  },
  labelWidth: {
    type: String,
    default: '80px'
  },
  inline: {
    type: Boolean,
    default: false
  },
  showActions: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['submit', 'reset'])

function handleSubmit() {
  emit('submit')
}

function handleReset() {
  emit('reset')
}
</script>

<style scoped>
.base-form {
  background: var(--openexam-bg-primary);
  border-radius: var(--openexam-radius-lg);
  padding: var(--openexam-space-6);
  border: 1px solid var(--openexam-border);
}

.form-actions {
  margin-top: var(--openexam-space-5);
  display: flex;
  gap: var(--openexam-space-3);
  padding-top: var(--openexam-space-5);
  border-top: 1px solid var(--openexam-border);
}

.base-form .el-form-item {
  margin-bottom: var(--openexam-space-4);
}

.base-form .el-form-item__label {
  font-weight: var(--openexam-font-medium);
  color: var(--openexam-text-primary);
}

.base-form .el-input__wrapper,
.base-form .el-textarea__inner,
.base-form .el-select .el-input__wrapper {
  border-radius: var(--openexam-radius-md);
  border: 1px solid var(--openexam-border);
}

.base-form .el-input__wrapper:focus-within,
.base-form .el-textarea__inner:focus,
.base-form .el-select .el-input__wrapper:focus-within {
  border-color: var(--openexam-primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}
</style>
