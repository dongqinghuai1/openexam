<template>
  <div class="role-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>角色管理</span>
          <el-button type="primary" @click="handleAdd">新增角色</el-button>
        </div>
      </template>

      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="name" label="角色名称" width="150" />
        <el-table-column prop="code" label="角色编码" width="120" />
        <el-table-column prop="description" label="描述" min-width="150" />
        <el-table-column prop="permissions" label="权限数量" width="100">
          <template #default="{ row }">{{ row.permissions?.length || 0 }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status ? 'success' : 'info'">{{ row.status ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="primary" link @click="handlePermission(row)">分配权限</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="角色编码" prop="code">
          <el-input v-model="form.code" :disabled="!!form.id" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.status" :active-value="true" :inactive-value="false" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="permDialogVisible" title="分配权限" width="500px">
      <el-tree
        ref="treeRef"
        :data="permissions"
        :props="{ label: 'name', children: 'children' }"
        show-checkbox
        node-key="id"
        :default-checked-keys="checkedPermissions"
      />
      <template #footer>
        <el-button @click="permDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handlePermSubmit">确定</el-button>
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
const permissions = ref([])
const dialogVisible = ref(false)
const permDialogVisible = ref(false)
const dialogTitle = ref('新增角色')
const formRef = ref()
const treeRef = ref()
const currentRoleId = ref(null)
const checkedPermissions = ref([])

const form = reactive({ id: null, name: '', code: '', description: '', status: true })
const rules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入角色编码', trigger: 'blur' }]
}

async function fetchData() {
  loading.value = true
  try {
    const res = await api.get('/users/roles/')
    tableData.value = res.data.results || res.data
  } catch (e) { ElMessage.error('获取数据失败') }
  finally { loading.value = false }
}

async function fetchPermissions() {
  try {
    const res = await api.get('/users/permissions/')
    permissions.value = res.data.results || res.data
  } catch (e) { console.error(e) }
}

function handleAdd() {
  dialogTitle.value = '新增角色'
  Object.assign(form, { id: null, name: '', code: '', description: '', status: true })
  dialogVisible.value = true
}

function handleEdit(row) {
  dialogTitle.value = '编辑角色'
  Object.assign(form, { ...row })
  dialogVisible.value = true
}

async function handlePermission(row) {
  currentRoleId.value = row.id
  checkedPermissions.value = row.permissions?.map(p => p.id) || []
  permDialogVisible.value = true
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定删除角色 "${row.name}" 吗?`, '提示', { type: 'warning' })
    await api.delete(`/users/roles/${row.id}/`)
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
          await api.put(`/users/roles/${form.id}/`, form)
          ElMessage.success('更新成功')
        } else {
          await api.post('/users/roles/', form)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchData()
      } catch (e) { ElMessage.error('操作失败') }
    }
  })
}

async function handlePermSubmit() {
  try {
    const checkedKeys = treeRef.value?.getCheckedKeys() || []
    await api.put(`/users/roles/${currentRoleId.value}/`, { permission_ids: checkedKeys })
    ElMessage.success('权限分配成功')
    permDialogVisible.value = false
  } catch (e) { ElMessage.error('操作失败') }
}

onMounted(() => { fetchData(); fetchPermissions() })
</script>

<style scoped>
.role-page { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>