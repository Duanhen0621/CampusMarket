<template>
  <div class="page">
    <el-card shadow="never">
      <h2 class="panel-title">管理后台</h2>
      <el-tabs v-model="activeTab">
        <el-tab-pane label="商品审核" name="audit">
          <el-table :data="pendingItems" border>
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="title" label="标题" />
            <el-table-column prop="student_id" label="发布者" width="140" />
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
          <div class="muted" style="margin-top: 10px">
            审核接口待实现（PUT /api/v1/admin/items/&#123;id&#125;/audit）。
          </div>
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
            举报处理接口待实现（PUT /api/v1/admin/reports/&#123;id&#125;）。
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const activeTab = ref('audit')

const pendingItems = ref([
  { id: 1024, title: '九成新山地自行车', student_id: '20210001', created_at: '2026-11-20 10:12' },
  { id: 1025, title: '求购：宿舍小冰箱', student_id: '20210002', created_at: '2026-11-21 09:30' },
])

const reports = ref([
  { id: 36, target: '商品 #1025', reason: '疑似虚假信息', status: 0 },
])

function audit(row, status) {
  ElMessage.info(`审核接口尚未实现（商品 ${row.id}，status=${status}）`)
}

function handleReport(row) {
  ElMessage.info(`举报处理接口尚未实现（工单 ${row.id}）`)
}
</script>
