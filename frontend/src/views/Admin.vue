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

        <el-tab-pane label="举报工单" name="reports">
          <el-table :data="reports" border>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="target" label="被举报对象" />
            <el-table-column prop="reason" label="原因" />
            <el-table-column prop="status" label="状态" width="120">
              <template #default="{ row }">
                <el-tag :type="row.status === 0 ? 'warning' : 'success'">
                  {{ row.status === 0 ? '待处理' : '已处理' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="160">
              <template #default="{ row }">
                <el-button size="small" @click="handleReport(row)">
                  处理
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <div class="muted" style="margin-top: 10px">
            举报处理将在 Admin/举报模块实现（PUT /api/v1/admin/reports/&#123;id&#125;）。
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import http from '@/api/http'

const activeTab = ref('audit')
const loading = ref(false)
const pendingItems = ref([])

const reports = ref([
  { id: 36, target: '商品 #1025', reason: '疑似虚假信息', status: 0 },
])

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

function handleReport(row) {
  ElMessage.info(`举报处理尚未实现（工单 ${row.id}）`)
}

onMounted(loadPending)
</script>
