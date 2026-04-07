<template>
  <div class="student-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>学生管理</span>
          <el-button type="primary" @click="handleAdd">新增学生</el-button>
        </div>
      </template>

      <el-form :inline="true" :model="queryForm" class="search-form">
        <el-form-item label="姓名">
          <el-input v-model="queryForm.name" placeholder="请输入姓名" clearable />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="queryForm.phone" placeholder="请输入手机号" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="queryForm.status" placeholder="请选择" clearable>
            <el-option label="在读" value="active" />
            <el-option label="休学" value="inactive" />
            <el-option label="退学" value="withdrawn" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQuery">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="tableData" border stripe>
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="phone" label="手机号" width="120" />
        <el-table-column prop="gender" label="性别" width="60" />
        <el-table-column prop="grade" label="年级" width="80" />
        <el-table-column prop="school" label="学校" min-width="120" />
        <el-table-column prop="parentName" label="家长姓名" width="100" />
        <el-table-column prop="parentPhone" label="家长手机" width="120" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : row.status === 'inactive' ? 'warning' : 'danger'">
              {{ row.status === 'active' ? '在读' : row.status === 'inactive' ? '休学' : '退学' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="enrollmentDate" label="入学日期" width="120" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="primary" link @click="handleView(row)">详情</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-select v-model="form.gender">
            <el-option label="男" value="male" />
            <el-option label="女" value="female" />
          </el-select>
        </el-form-item>
        <el-form-item label="年级" prop="grade">
          <el-input v-model="form.grade" />
        </el-form-item>
        <el-form-item label="学校">
          <el-input v-model="form.school" />
        </el-form-item>
        <el-form-item label="家长姓名" prop="parentName">
          <el-input v-model="form.parentName" />
        </el-form-item>
        <el-form-item label="家长手机" prop="parentPhone">
          <el-input v-model="form.parentPhone" />
        </el-form-item>
        <el-form-item label="入学日期" prop="enrollmentDate">
          <el-date-picker v-model="form.enrollmentDate" type="date" value-format="YYYY-MM-DD" />
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
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const queryForm = reactive({ name: '', phone: '', status: '' })
const pagination = ref({ page: 1, size: 10, total: 0 })
const tableData = ref([
  { id: 1, name: '张三', phone: '13800138000', gender: 'male', grade: '高三', school: '第一中学', parentName: '张父', parentPhone: '13900139000', status: 'active', enrollmentDate: '2023-09-01' },
  { id: 2, name: '李四', phone: '13800138001', gender: 'female', grade: '高二', school: '第二中学', parentName: '李母', parentPhone: '13900139001', status: 'active', enrollmentDate: '2023-09-01' }
])
const dialogVisible = ref(false)
const dialogTitle = ref('')
const formRef = ref()
const form = reactive({ id: null, name: '', phone: '', gender: '', grade: '', school: '', parentName: '', parentPhone: '', enrollmentDate: '' })
const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入手机号', trigger: 'blur' }],
  grade: [{ required: true, message: '请输入年级', trigger: 'blur' }],
  parentName: [{ required: true, message: '请输入家长姓名', trigger: 'blur' }],
  parentPhone: [{ required: true, message: '请输入家长手机', trigger: 'blur' }]
}

function handleQuery() {
  ElMessage.info('查询功能需要对接后端API')
}

function handleReset() {
  queryForm.name = ''
  queryForm.phone = ''
  queryForm.status = ''
}

function handleAdd() {
  dialogTitle.value = '新增学生'
  form.id = null
  Object.keys(form).forEach(key => form[key] = '')
  dialogVisible.value = true
}

function handleEdit(row) {
  dialogTitle.value = '编辑学生'
  Object.assign(form, row)
  dialogVisible.value = true
}

function handleView(row) {
  ElMessage.info('查看详情: ' + row.name)
}

function handleDelete(row) {
  ElMessageBox.confirm('确定删除该学生吗？', '提示', { type: 'warning' })
    .then(() => ElMessage.success('删除成功'))
    .catch(() => {})
}

async function handleSubmit() {
  if (!formRef.value) return
  await formRef.value.validate((valid) => {
    if (valid) {
      ElMessage.success(form.id ? '编辑成功' : '新增成功')
      dialogVisible.value = false
    }
  })
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}
</style>