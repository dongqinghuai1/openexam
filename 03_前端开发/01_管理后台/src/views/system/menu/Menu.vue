<template>
  <div class="menu-page page-shell">
    <el-card class="surface-card">
      <template #header>
        <div class="card-header">
          <div>
            <div class="page-title">菜单管理</div>
            <div class="page-subtitle">维护导航层级、显示状态与权限标识，保持信息架构清晰。</div>
          </div>
          <el-button type="primary" @click="handleAdd">新增菜单</el-button>
        </div>
      </template>

      <el-table :data="tableData" v-loading="loading" row-key="id" stripe>
        <el-table-column prop="name" label="菜单名称" min-width="240">
          <template #default="{ row }">
            <div class="menu-tree-cell" :style="{ paddingLeft: (row._level || 0) * 18 + 'px' }">
              <span class="menu-level-dot" :class="`level-${row._level || 0}`"></span>
              <span class="menu-name">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="path" label="路由" min-width="180" show-overflow-tooltip />
        <el-table-column prop="component" label="组件" min-width="200" show-overflow-tooltip />
        <el-table-column prop="sort" label="排序" width="90" align="center" />
        <el-table-column prop="visible" label="可见" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.visible ? 'success' : 'info'">{{ row.visible ? '是' : '否' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="permission" label="权限标识" min-width="180" show-overflow-tooltip />
        <el-table-column label="操作" width="220" fixed="right" class-name="operation-column">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="success" link @click="handleAddChild(row)">添加子菜单</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="760px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="96px" class="menu-form-grid">
        <el-form-item label="菜单名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="父级菜单">
          <el-select v-model="form.parent" placeholder="顶级菜单" clearable>
            <el-option v-for="menu in allMenus" :key="menu.id" :label="menu.label" :value="menu.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="图标">
          <el-input v-model="form.icon" placeholder="图标名称" />
        </el-form-item>
        <el-form-item label="路由路径">
          <el-input v-model="form.path" />
        </el-form-item>
        <el-form-item label="组件路径">
          <el-input v-model="form.component" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort" :min="0" />
        </el-form-item>
        <el-form-item label="是否可见">
          <el-switch v-model="form.visible" />
        </el-form-item>
        <el-form-item label="权限标识" class="full-span">
          <el-input v-model="form.permission" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '@/stores/user'
import { extractErrorMessage } from '@/utils/error'

const loading = ref(false)
const tableData = ref([])
const allMenus = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('新增菜单')
const formRef = ref()

const form = reactive({
  id: null, name: '', parent: undefined, icon: '', path: '', component: '', sort: 0, visible: true, permission: ''
})

const rules = {
  name: [{ required: true, message: '请输入菜单名称', trigger: 'blur' }]
}

function flattenTree(menus, level = 0) {
  let result = []
  for (const menu of menus) {
    const { children, ...rest } = menu
    result.push({ ...rest, _level: level })
    if (menu.children && menu.children.length > 0) {
      result = result.concat(flattenTree(menu.children, level + 1))
    }
  }
  return result
}

function flattenForSelect(menus, prefix = '') {
  let result = []
  for (const menu of menus) {
    const label = prefix ? `${prefix} / ${menu.name}` : menu.name
    result.push({ id: menu.id, label })
    if (menu.children && menu.children.length > 0) {
      result = result.concat(flattenForSelect(menu.children, label))
    }
  }
  return result
}

async function fetchData() {
  loading.value = true
  try {
    const res = await api.get('/users/menus/tree/')
    const treeData = res.data
    tableData.value = flattenTree(treeData)
    allMenus.value = flattenForSelect(treeData)
  } catch (e) { ElMessage.error(extractErrorMessage(e, '获取菜单数据失败')) }
  finally { loading.value = false }
}

function resetForm() {
  form.id = null
  form.name = ''
  form.parent = undefined
  form.icon = ''
  form.path = ''
  form.component = ''
  form.sort = 0
  form.visible = true
  form.permission = ''
}

function handleAdd() {
  dialogTitle.value = '新增菜单'
  resetForm()
  dialogVisible.value = true
}

function handleEdit(row) {
  dialogTitle.value = '编辑菜单'
  form.id = row.id
  form.name = row.name
  form.parent = row.parent || undefined
  form.icon = row.icon || ''
  form.path = row.path || ''
  form.component = row.component || ''
  form.sort = row.sort
  form.visible = row.visible
  form.permission = row.permission || ''
  dialogVisible.value = true
}

function handleAddChild(row) {
  dialogTitle.value = '添加子菜单'
  resetForm()
  form.parent = row.id
  dialogVisible.value = true
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定删除菜单 "${row.name}" 吗?`, '提示', { type: 'warning' })
    await api.delete(`/users/menus/${row.id}/`)
    ElMessage.success('删除成功')
    fetchData()
  } catch (e) { if (e !== 'cancel') ElMessage.error(extractErrorMessage(e, '删除菜单失败')) }
}

async function handleSubmit() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const data = {
          name: form.name,
          parent: form.parent,
          icon: form.icon || '',
          path: form.path || '',
          component: form.component || '',
          sort: form.sort,
          visible: form.visible,
          permission: form.permission || ''
        }

        if (form.id) {
          await api.put(`/users/menus/${form.id}/`, data)
          ElMessage.success('更新成功')
        } else {
          await api.post('/users/menus/', data)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchData()
      } catch (e) { ElMessage.error(extractErrorMessage(e, '保存菜单失败')) }
    }
  })
}

onMounted(() => { fetchData() })
</script>

<style scoped>
.menu-page { padding: 20px; }
.menu-tree-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.menu-level-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: #d0d5dd;
  flex-shrink: 0;
}

.menu-level-dot.level-0 { background: #2563eb; }
.menu-level-dot.level-1 { background: #7c3aed; }
.menu-level-dot.level-2 { background: #0ea5e9; }

.menu-name {
  font-weight: 550;
  color: #111827;
}

.menu-form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  column-gap: 18px;
}

.menu-form-grid :deep(.el-form-item) {
  margin-bottom: 18px;
}

.full-span {
  grid-column: 1 / -1;
}

@media (max-width: 900px) {
  .menu-form-grid {
    grid-template-columns: 1fr;
  }

  .full-span {
    grid-column: auto;
  }
}
</style>
