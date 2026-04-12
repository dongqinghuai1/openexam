<template>
  <div class="base-table">
    <el-table
      :data="data"
      :loading="loading"
      :border="border"
      :stripe="stripe"
      :size="size"
      @row-click="handleRowClick"
      @selection-change="handleSelectionChange"
      class="table"
    >
      <el-table-column
        v-if="showSelection"
        type="selection"
        width="55"
      />
      <slot></slot>
    </el-table>
    <div v-if="showPagination" class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="pageSizes"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  border: {
    type: Boolean,
    default: true
  },
  stripe: {
    type: Boolean,
    default: true
  },
  size: {
    type: String,
    default: 'default'
  },
  showSelection: {
    type: Boolean,
    default: false
  },
  showPagination: {
    type: Boolean,
    default: true
  },
  total: {
    type: Number,
    default: 0
  },
  pageSize: {
    type: Number,
    default: 10
  },
  currentPage: {
    type: Number,
    default: 1
  },
  pageSizes: {
    type: Array,
    default: () => [10, 20, 50, 100]
  }
})

const emit = defineEmits(['row-click', 'selection-change', 'size-change', 'current-change'])

function handleRowClick(row) {
  emit('row-click', row)
}

function handleSelectionChange(selection) {
  emit('selection-change', selection)
}

function handleSizeChange(size) {
  emit('size-change', size)
}

function handleCurrentChange(page) {
  emit('current-change', page)
}
</script>

<style scoped>
.base-table {
  width: 100%;
  background: var(--openexam-bg-primary);
  border-radius: var(--openexam-radius-lg);
  border: 1px solid var(--openexam-border);
  overflow: hidden;
  box-shadow: var(--openexam-shadow);
}

.table {
  --el-table-border-color: var(--openexam-border) !important;
  --el-table-header-bg-color: var(--openexam-bg-tertiary) !important;
  --el-table-tr-bg-color: transparent !important;
  --el-table-row-hover-bg-color: rgba(59, 130, 246, 0.04) !important;
  --el-table-text-color: var(--openexam-text-primary) !important;
  --el-table-header-text-color: var(--openexam-text-secondary) !important;
}

.table th.el-table__cell {
  font-weight: var(--openexam-font-semibold);
  font-size: var(--openexam-font-xs);
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.table td.el-table__cell {
  vertical-align: middle;
  padding-top: var(--openexam-space-3) !important;
  padding-bottom: var(--openexam-space-3) !important;
}

.pagination {
  margin-top: var(--openexam-space-5);
  display: flex;
  justify-content: flex-end;
  padding: var(--openexam-space-4);
  background: var(--openexam-bg-primary);
  border-top: 1px solid var(--openexam-border);
}

.pagination .el-pagination {
  display: flex;
  align-items: center;
  gap: var(--openexam-space-3);
}

.pagination .el-pagination__sizes {
  margin-right: var(--openexam-space-2);
}

.pagination .el-pagination__jump {
  margin-left: var(--openexam-space-2);
}
</style>
