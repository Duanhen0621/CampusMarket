<template>
  <div class="page">
    <el-card shadow="never">
      <h2 class="panel-title">管理后台</h2>
      <el-tabs v-model="activeTab">
        <el-tab-pane label="商品审核" name="audit">
          <el-table v-loading="loading" :data="pendingItems" border>
            <el-table-column prop="id" label="ID" width="70" />
            <el-table-column prop="title" label="标题" />
            <el-table-column label="发布者" width="100">
              <template #default="{ row }">#{{ row.user_id }}</template>
            </el-table-column>
            <el-table-column label="价格" width="110">
              <template #default="{ row }">
                {{ row.price !== null ? `¥ ${row.price}` : '面议' }}
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="发布时间" width="180" />
            <el-table-column label="操作" width="180">
              <template #default="{ row }">
                <el-button size="small" type="success" @click="audit(row, 1)">
                  通过
                </el-button>
                <el-button size="small" type="danger" @click="audit(row, 2)">
                  驳回
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty
            v-if="!loading && !pendingItems.length"
            description="暂无待审核商品"
            :image-size="80"
          />
        </el-tab-pane>

        <el-tab-pane v-if="auth.isSuperAdmin" label="管理员申请" name="applications">
          <div style="margin-bottom: 12px">
            <el-select
              v-model="applicationStatus"
              placeholder="全部状态"
              clearable
              style="width: 170px"
              @change="loadApplications"
            >
              <el-option label="待审批" :value="0" />
              <el-option label="已通过" :value="1" />
              <el-option label="已驳回" :value="2" />
            </el-select>
          </div>
          <el-table v-loading="applicationLoading" :data="applications" border>
            <el-table-column prop="id" label="ID" width="70" />
            <el-table-column
              prop="applicant_student_id"
              label="申请人"
              width="130"
            />
            <el-table-column prop="reason" label="申请理由" />
            <el-table-column label="状态" width="110">
              <template #default="{ row }">
                <el-tag :type="applicationStatusMap[row.status]?.type || 'info'">
                  {{ applicationStatusMap[row.status]?.text || '未知' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="review_note" label="审批备注" width="180" />
            <el-table-column label="提交时间" width="170">
              <template #default="{ row }">
                {{ formatTime(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="170">
              <template #default="{ row }">
                <template v-if="row.status === 0">
                  <el-button
                    size="small"
                    type="success"
                    @click="reviewApplication(row, 1)"
                  >
                    通过
                  </el-button>
                  <el-button
                    size="small"
                    type="danger"
                    @click="reviewApplication(row, 2)"
                  >
                    驳回
                  </el-button>
                </template>
                <span v-else class="muted">—</span>
              </template>
            </el-table-column>
          </el-table>
          <el-empty
            v-if="!applicationLoading && !applications.length"
            description="暂无管理员申请"
            :image-size="80"
          />
        </el-tab-pane>

        <el-tab-pane label="举报工单" name="reports">
          <div style="margin-bottom: 12px">
            <el-select
              v-model="reportStatus"
              placeholder="全部状态"
              clearable
              style="width: 170px"
              @change="loadReports"
            >
              <el-option label="待处理" :value="0" />
              <el-option label="已处理 / 属实" :value="1" />
              <el-option label="已驳回 / 不属实" :value="2" />
            </el-select>
          </div>
          <el-table v-loading="reportLoading" :data="reports" border>
            <el-table-column prop="id" label="ID" width="70" />
            <el-table-column prop="reporter_student_id" label="举报人" width="130" />
            <el-table-column prop="target_label" label="举报对象" width="220" />
            <el-table-column prop="reason" label="举报原因" />
            <el-table-column label="状态" width="110">
              <template #default="{ row }">
                <el-tag :type="reportStatusMap[row.status]?.type || 'info'">
                  {{ reportStatusMap[row.status]?.text || '未知' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="handle_note" label="处理备注" width="180" />
            <el-table-column label="操作" width="170">
              <template #default="{ row }">
                <template v-if="row.status === 0">
                  <el-button size="small" type="success" @click="handle(row, 1)">
                    属实
                  </el-button>
                  <el-button size="small" type="danger" @click="handle(row, 2)">
                    不属实
                  </el-button>
                </template>
                <span v-else class="muted">—</span>
              </template>
            </el-table-column>
          </el-table>
          <el-empty
            v-if="!reportLoading && !reports.length"
            description="暂无举报工单"
            :image-size="80"
          />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import http from '@/api/http'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const activeTab = ref('audit')
const loading = ref(false)
const pendingItems = ref([])
const reports = ref([])
const reportLoading = ref(false)
const reportStatus = ref(null)
const applicationLoading = ref(false)
const applicationStatus = ref(null)
const applications = ref([])

const applicationStatusMap = {
  0: { text: '待审批', type: 'warning' },
  1: { text: '已通过', type: 'success' },
  2: { text: '已驳回', type: 'danger' },
}

function formatTime(value) {
  if (!value) return ''
  return value.replace('T', ' ').slice(0, 16)
}

const reportStatusMap = {
  0: { text: '待处理', type: 'warning' },
  1: { text: '已处理 / 属实', type: 'success' },
  2: { text: '已驳回 / 不属实', type: 'info' },
}

async function loadPending() {
  loading.value = true
  try {
    const { data } = await http.get('/admin/items/pending', {
      params: { page: 1, size: 50 },
    })
    pendingItems.value = data.data.list
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '加载待审核商品失败')
  } finally {
    loading.value = false
  }
}

async function audit(row, status) {
  try {
    let reason = null
    if (status === 2) {
      const { value } = await ElMessageBox.prompt('请输入驳回原因', '驳回商品', {
        inputPattern: /\S+/,
        inputErrorMessage: '请填写驳回原因',
      })
      reason = value
    } else {
      await ElMessageBox.confirm(`确定通过「${row.title}」吗？`, '审核商品', {
        type: 'warning',
      })
    }
    await http.put(`/admin/items/${row.id}/audit`, { status, reason })
    ElMessage.success('操作成功')
    loadPending()
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    }
  }
}

async function loadReports() {
  reportLoading.value = true
  try {
    const { data } = await http.get('/admin/reports', {
      params: {
        page: 1,
        size: 50,
        status:
          reportStatus.value === null || reportStatus.value === ''
            ? undefined
            : reportStatus.value,
      },
    })
    reports.value = data.data.list
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '加载举报工单失败')
  } finally {
    reportLoading.value = false
  }
}

async function handle(row, targetStatus) {
  try {
    const { value } = await ElMessageBox.prompt(
      targetStatus === 1 ? '处理备注（可选）' : '驳回说明（可选）',
      targetStatus === 1 ? '标记举报属实' : '标记举报不属实',
      { inputPlaceholder: '可留空' },
    )
    await http.put(`/admin/reports/${row.id}`, {
      status: targetStatus,
      handle_note: value || null,
    })
    ElMessage.success('处理成功')
    loadReports()
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      ElMessage.error(error.response?.data?.detail || '处理失败')
    }
  }
}

async function loadApplications() {
  applicationLoading.value = true
  try {
    const { data } = await http.get('/admin/applications', {
      params: {
        page: 1,
        size: 50,
        status:
          applicationStatus.value === null || applicationStatus.value === ''
            ? undefined
            : applicationStatus.value,
      },
    })
    applications.value = data.data.list
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '加载管理员申请失败')
  } finally {
    applicationLoading.value = false
  }
}

async function reviewApplication(row, targetStatus) {
  const label = targetStatus === 1 ? '通过' : '驳回'
  try {
    const { value } = await ElMessageBox.prompt(
      '审批备注（可选）',
      `确认${label}该申请`,
      { inputPlaceholder: '可留空' },
    )
    await http.put(`/admin/applications/${row.id}`, {
      status: targetStatus,
      review_note: value || null,
    })
    ElMessage.success(`已${label}`)
    loadApplications()
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      ElMessage.error(error.response?.data?.detail || '审批失败')
    }
  }
}

onMounted(() => {
  loadPending()
  loadReports()
  if (auth.isSuperAdmin) loadApplications()
})
</script>
