<template>
  <div class="menu-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>菜单管理</span>
          <el-button type="primary" @click="handleAdd">新增菜单</el-button>
        </div>
      </template>

      <el-table :data="tableData" v-loading="loading" row-key="id" default-expand-all stripe>
        <el-table-column prop="name" label="菜单名称" width="150" />
        <el-table-column prop="icon" label="图标" width="80">
          <template #default="{ row }">
            <el-icon v-if="row.icon"><component :is="row.icon" /></el-icon>
          </template>
        </el-table-column>
        <el-table-column prop="path" label="路由" width="150" />
        <el-table-column prop="component" label="组件" width="150" />
        <el-table-column prop="sort" label="排序" width="80" />
        <el-table-column prop="visible" label="可见" width="80">
          <template #default="{ row }">
            <el-tag :type="row.visible ? 'success' : 'info'">{{ row.visible ? '是' : '否' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="permission" label="权限标识" width="150" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="success" link @click="handleAddChild(row)">添加子菜单</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="菜单名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="父级菜单">
          <el-select v-model="form.parent" placeholder="顶级菜单" clearable>
            <el-option v-for="menu in tableData" :key="menu.id" :label="menu.name" :value="menu.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="图标">
          <el-input v-model="form.icon" placeholder="请输入图标名称" />
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
        <el-form-item label="权限标识">
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
import { api } from '../../stores/user'

const loading = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('新增菜单')
const formRef = ref()

const form = reactive({
  id: null, name: '', parent: null, icon: '', path: '', component: '', sort: 0, visible: true, permission: ''
})

const rules = {
  name: [{ required: true, message: '请输入菜单名称', trigger: 'blur' }]
}

async function fetchData() {
  loading.value = true
  try {
    const res = await api.get('/users/menus/')
    tableData.value = res.data.results || res.data
  } catch (e) { ElMessage.error('获取数据失败') }
  finally { loading.value = false }
}

function handleAdd() {
  dialogTitle.value = '新增菜单'
  Object.assign(form, { id: null, name: '', parent: null, icon: '', path: '', component: '', sort: 0, visible: true, permission: '' })
  dialogVisible.value = true
}

function handleEdit(row) {
  dialogTitle.value = '编辑菜单'
  Object.assign(form, { ...row, parent: row.parent?.id || row.parent })
  dialogVisible.value = true
}

function handleAddChild(row) {
  dialogTitle.value = '添加子菜单'
  Object.assign(form, { id: null, name: '', parent: row.id, icon: '', path: '', component: '', sort: 0, visible: true, permission: '' })
  dialogVisible.value = true
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定删除菜单 "${row.name}" 吗?`, '提示', { type: 'warning' })
    await api.delete(`/users/menus/${row.id}/`)
    ElMessage.success('删除成功')
    fetchData()
  } catch (e) { if (e !== 'cancel') ElMessage.error('删除失败') }
}

async function handleSubmit() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (form.id) {
          await api.put(`/users/menus/${form.id}/`, form)
          ElMessage.success('更新成功')
        } else {
          await api.post('/users/menus/', form)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchData()
      } catch (e) { ElMessage.error('操作失败') }
    }
  })
}

onMounted(() => { fetchData() })
</script>

<style scoped>
.menu-page { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>