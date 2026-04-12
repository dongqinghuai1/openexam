<template>
  <el-card
    :header="header"
    :body-style="bodyStyle"
    :shadow="shadow"
    class="base-card"
  >
    <template v-if="$slots.header" #header>
      <slot name="header"></slot>
    </template>
    <slot></slot>
  </el-card>
</template>

<script setup>
defineProps({
  header: {
    type: String,
    default: ''
  },
  bodyStyle: {
    type: Object,
    default: () => ({})
  },
  shadow: {
    type: String,
    default: 'hover'
  }
})
</script>

<style scoped>
.base-card {
  border-radius: var(--openexam-radius-lg);
  border: 1px solid var(--openexam-border);
  transition: all var(--openexam-transition-fast);
  overflow: hidden;
}

.base-card:hover {
  box-shadow: var(--openexam-shadow-md);
  transform: translateY(-2px);
}

.base-card .el-card__header {
  border-bottom: 1px solid var(--openexam-border);
  padding: var(--openexam-space-5) var(--openexam-space-6);
}

.base-card .el-card__body {
  padding: var(--openexam-space-6);
}
</style>
